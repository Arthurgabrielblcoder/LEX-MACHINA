"""J2I — controlled flash of the GENERIC tribunal/classe firmware (app0 @ 0x10000 ONLY). One step per call, every step gated, nothing is
assumed. The microSD must stay OUT of the device during the whole mission.

  detect   list serial ports; exactly one CH343 1A86:55D3 (serial 5C38165292, project history) or STOP
  chip     esptool flash-id: ESP32-S3, flash size, MAC == R2 record
  pre      read partitions (0x8000), otadata (0xe000), nvs (0x9000) and the FULL app0 partition (0x10000, size from the partition table
           read from the chip); app0 must start with the approved app 6e329c91… (frozen copy + R2 record); partitions/otadata == R2
  flash    gates (frozen generic binary sha == J2H record; size <= app0; firmware source gate PASS; generic prototype PASS, RAM delta 0)
           then: esptool write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 generic_app.bin  (NO erase, NO other region)
  verify   read app0 again (full partition): first len(generic) bytes == generic binary; partitions/otadata unchanged
  boot     hard reset into the new app WITHOUT microSD and capture the serial log (115200) for N seconds; classify PASS / EXPECTED_SD_ERROR / FAIL
Backups (gitignored): DEVICE_INTEGRATION/backups/j2i_physical_flash/ (never overwritten). Evidence: JURISPRUDENCE_AUDIT/J2I_PHYSICAL_FLASH/.
Usage: python j2i_flash_generic_firmware.py <step> [--port COMx] [--seconds N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BK = ROOT / 'DEVICE_INTEGRATION/backups/j2i_physical_flash'
EV = HERE / 'J2I_PHYSICAL_FLASH'
FROZEN = ROOT / 'DEVICE_INTEGRATION/backups/j2i_flash_candidate'
GENERIC = FROZEN / 'generic_app.bin'
APPROVED = FROZEN / 'current_approved_app_6e329c91.bin'
R2 = ROOT / 'REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/firmware_flash.json'
PROTO = HERE / 'JURIS_TYPE_PROTOTYPE/JURIS_TYPE_PROTOTYPE_BUILD.json'
FWBASE = HERE / 'FIRMWARE_REPRODUCIBILITY/FIRMWARE_BASELINE_REPRODUCIBILITY.json'
J2H_PRE = HERE / 'J2H_PHYSICAL_DEPLOY/physical_pre.json'
J2H_VAL = HERE / 'J2H_PHYSICAL_DEPLOY/physical_validation.json'
APPROVED_SHA = '6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c'
VIDPID, SERIAL_NO = '1A86:55D3', '5C38165292'
MAC = 'e0:72:a1:f4:fd:28'
APP0 = 0x10000
FQBN = 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default'


def stop(m):
    raise SystemExit('PARAR: ' + m)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def esptool(port, *args, after='no-reset', log=None):
    cmd = [sys.executable, '-m', 'esptool', '--chip', 'esp32s3', '-p', port, '-b', '460800', '--after', after, *args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if log:
        (BK / log).write_text(' '.join(cmd) + '\n\n' + out, encoding='utf-8')
    if r.returncode != 0:
        stop(f'esptool falhou ({" ".join(args[:1])}): ' + out[-1500:])
    return ' '.join(cmd[2:]), out


def dump(name, value):
    EV.mkdir(parents=True, exist_ok=True)
    (EV / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(value, ensure_ascii=False)[:3000])


def load(name):
    return json.loads((EV / name).read_text(encoding='utf-8'))


def detect(_a):
    from serial.tools import list_ports
    ports = list(list_ports.comports())
    cands = [p for p in ports if p.vid == 0x1A86 and p.pid == 0x55D3]
    rec = dict(ports=[dict(device=p.device, description=p.description, hwid=p.hwid) for p in ports])
    if len(cands) != 1 or cands[0].serial_number != SERIAL_NO:
        stop('porta ambígua ou ausente: ' + json.dumps(rec, ensure_ascii=False))
    rec.update(ESP32_PORT=cands[0].device, vid_pid=VIDPID, serial_number=cands[0].serial_number, description=cands[0].description,
               identification='único CH343 1A86:55D3 presente; número de série 5C38165292 = instância COM3 do histórico (R2/J2G)')
    BK.mkdir(parents=True, exist_ok=True)
    dump('01_detect.json', rec)


def chip(a):
    port = load('01_detect.json')['ESP32_PORT']
    cmd, out = esptool(port, 'flash-id', log='flash_id.log')
    keys = {k: next((l.split(':', 1)[1].strip() for l in out.splitlines() if l.strip().startswith(k)), None)
            for k in ('Chip type', 'Features', 'Crystal frequency', 'MAC', 'Detected flash size', 'Manufacturer', 'Device')}
    ok = (keys['Chip type'] or '').startswith('ESP32-S3') and keys['MAC'] == MAC and keys['Detected flash size'] == '16MB'
    rec = dict(command=cmd, **keys, CHIP='ESP32-S3' if (keys['Chip type'] or '').startswith('ESP32-S3') else keys['Chip type'],
               MATCHES_R2_DEVICE=ok, fqbn_of_approved_and_generic_builds=FQBN, core='esp32:esp32 3.3.11', arduino_cli='1.5.1',
               build_property='compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1')
    dump('02_chip.json', rec)
    if not ok:
        stop('chip/MAC/flash não correspondem ao aparelho do R2')


def partitions(b: bytes) -> dict:
    out = {}
    for i in range(0, len(b), 32):
        e = b[i:i + 32]
        if e[:2] != b'\xaa\x50':
            break
        t, st, off, sz = struct.unpack('<BBII', e[2:12])
        out[e[12:28].rstrip(b'\0').decode()] = dict(type=t, subtype=st, offset=off, size=sz)
    return out


def pre(a):
    port = load('01_detect.json')['ESP32_PORT']
    if load('02_chip.json')['MATCHES_R2_DEVICE'] is not True:
        stop('chip não validado')
    if (BK / 'app0_pre_flash.bin').exists():
        stop('backup PRE já existe; não sobrescrever: ' + str(BK))
    r2 = json.loads(R2.read_text(encoding='utf-8'))
    esptool(port, 'read-flash', '0x8000', '0xC00', str(BK / 'partitions_pre.bin'), log='read_partitions_pre.log')
    pt_b = (BK / 'partitions_pre.bin').read_bytes()
    pt = partitions(pt_b)
    app0 = pt.get('app0')
    if not app0 or app0['offset'] != APP0:
        stop('tabela de partições sem app0 em 0x10000: ' + json.dumps(pt))
    esptool(port, 'read-flash', '0xe000', '0x2000', str(BK / 'otadata_pre.bin'), log='read_otadata_pre.log')
    esptool(port, 'read-flash', '0x9000', '0x5000', str(BK / 'nvs_pre.bin'), log='read_nvs_pre.log')
    esptool(port, 'read-flash', hex(APP0), hex(app0['size']), str(BK / 'app0_pre_flash.bin'), log='read_app0_pre.log')
    esptool(port, 'read-flash', hex(APP0), hex(app0['size']), str(BK / 'app0_pre_flash_verify.bin'), log='read_app0_pre_verify.log')
    full, again = (BK / 'app0_pre_flash.bin').read_bytes(), (BK / 'app0_pre_flash_verify.bin').read_bytes()
    approved = APPROVED.read_bytes()
    rec = dict(partition_table=pt, partitions_sha256=sha(pt_b), partitions_match_r2=sha(pt_b) == r2['post']['partitions'],
               otadata_sha256=sha((BK / 'otadata_pre.bin').read_bytes()), otadata_match_r2=sha((BK / 'otadata_pre.bin').read_bytes()) == r2['post']['otadata'],
               nvs_sha256=sha((BK / 'nvs_pre.bin').read_bytes()),
               app0_partition_size=app0['size'], app0_full_sha256=sha(full), app0_double_read_identical=full == again,
               approved_frozen_sha256=sha(approved), approved_frozen_is_6e329c91=sha(approved) == APPROVED_SHA,
               r2_recorded_app_sha256=r2['post']['app0_readback_sha256'],
               CURRENT_APP_PRE_HASH=sha(full[:len(approved)]),
               app0_tail_after_app_sha256=sha(full[len(approved):]),
               backup=dict(dir=str(BK), app0='app0_pre_flash.bin', partitions='partitions_pre.bin', otadata='otadata_pre.bin', nvs='nvs_pre.bin'))
    rec['CURRENT_APP_MATCHES_APPROVED'] = 'PASS' if (rec['CURRENT_APP_PRE_HASH'] == APPROVED_SHA == rec['r2_recorded_app_sha256']
                                                     and rec['approved_frozen_is_6e329c91'] and rec['app0_double_read_identical']) else 'FAIL'
    dump('03_pre.json', rec)
    if rec['CURRENT_APP_MATCHES_APPROVED'] != 'PASS' or not rec['partitions_match_r2'] or not rec['otadata_match_r2']:
        stop('estado do chip não é o aprovado (app/partições/otadata)')


def gates() -> dict:
    p, fb = json.loads(PROTO.read_text(encoding='utf-8')), json.loads(FWBASE.read_text(encoding='utf-8'))
    gen = GENERIC.read_bytes()
    pre_rec = load('03_pre.json')
    j2h = json.loads(J2H_PRE.read_text(encoding='utf-8'))['gates']['firmware']
    r = subprocess.run([sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', 'tests.test_juris_types', 'tests.test_hc_prototype', 'tests.test_j2h'],
                       capture_output=True, text=True, cwd=HERE)
    g = dict(GENERIC_APP_BIN=str(GENERIC.relative_to(ROOT)), GENERIC_APP_SHA256=sha(gen), GENERIC_APP_SIZE=len(gen),
             expected_sha256_j2h=j2h['generic_app_sha256'], expected_sha256_build=p['types_build']['app_sha256'],
             GENERIC_BINARY_HASH='EXPECTED' if sha(gen) == j2h['generic_app_sha256'] == p['types_build']['app_sha256'] else 'MISMATCH',
             APP_PARTITION_SIZE=pre_rec['app0_partition_size'], FREE_BYTES=pre_rec['app0_partition_size'] - len(gen),
             image_magic_ok=gen[:1] == b'\xe9',
             FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE=fb['FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE'],
             STATIC_RAM_DELTA=p['delta_vs_base']['static_ram_bytes'], PROGRAM_DELTA=p['delta_vs_base']['program_bytes'],
             GENERIC_FIRMWARE_TESTS='PASS' if r.returncode == 0 else 'FAIL', tests_tail=(r.stdout + r.stderr).strip().splitlines()[-3:],
             sd_card_state=json.loads(J2H_VAL.read_text(encoding='utf-8'))['result'])
    ok = (g['GENERIC_BINARY_HASH'] == 'EXPECTED' and g['GENERIC_APP_SIZE'] <= g['APP_PARTITION_SIZE'] and g['image_magic_ok']
          and g['FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE'] == 'PASS' and g['STATIC_RAM_DELTA'] == 0 and g['GENERIC_FIRMWARE_TESTS'] == 'PASS')
    g['ALL_GATES'] = 'PASS' if ok else 'FAIL'
    return g


def flash(a):
    port = load('01_detect.json')['ESP32_PORT']
    if load('03_pre.json')['CURRENT_APP_MATCHES_APPROVED'] != 'PASS':
        stop('PRE não aprovado')
    if (EV / '05_flash.json').exists():
        stop('flash já registrado; não repetir')
    g = gates()
    dump('04_gates.json', g)
    if g['ALL_GATES'] != 'PASS':
        stop('gates do flash não passaram')
    cmd, out = esptool(port, 'write-flash', '--flash-mode', 'keep', '--flash-freq', 'keep', '--flash-size', 'keep', hex(APP0), str(GENERIC),
                       log='write_flash.log')
    ok = 'Hash of data verified' in out
    dump('05_flash.json', dict(command=cmd, FLASH_ADDRESS=hex(APP0), FLASH_SCOPE='APP_ONLY', image=str(GENERIC.relative_to(ROOT)),
                               image_sha256=g['GENERIC_APP_SHA256'], bytes=g['GENERIC_APP_SIZE'], erase_flash_used=False,
                               esptool_hash_verified=ok, output_tail=out.strip().splitlines()[-8:]))
    if not ok:
        stop('esptool não confirmou o hash da gravação')


def verify(a):
    port = load('01_detect.json')['ESP32_PORT']
    if not (EV / '05_flash.json').exists():
        stop('flash não registrado')
    pre_rec = load('03_pre.json')
    esptool(port, 'read-flash', hex(APP0), hex(pre_rec['app0_partition_size']), str(BK / 'app0_post_flash.bin'), log='read_app0_post.log')
    esptool(port, 'read-flash', '0x8000', '0xC00', str(BK / 'partitions_post.bin'), log='read_partitions_post.log')
    esptool(port, 'read-flash', '0xe000', '0x2000', str(BK / 'otadata_post.bin'), log='read_otadata_post.log')
    post, gen = (BK / 'app0_post_flash.bin').read_bytes(), GENERIC.read_bytes()
    pre_full = (BK / 'app0_pre_flash.bin').read_bytes()
    rec = dict(app0_post_full_sha256=sha(post), APP0_READBACK_SHA256=sha(post[:len(gen)]), GENERIC_APP_SHA256=sha(gen),
               FLASH_READBACK_HASH='EXACT' if post[:len(gen)] == gen else 'MISMATCH',
               tail_beyond_new_image_unchanged=post[len(gen):] == pre_full[len(gen):],
               partitions_unchanged=sha((BK / 'partitions_post.bin').read_bytes()) == pre_rec['partitions_sha256'],
               otadata_unchanged=sha((BK / 'otadata_post.bin').read_bytes()) == pre_rec['otadata_sha256'])
    rec['FLASH_READBACK_HASH_MATCH'] = 'YES' if rec['FLASH_READBACK_HASH'] == 'EXACT' else 'NO'
    dump('06_verify.json', rec)
    if rec['FLASH_READBACK_HASH'] != 'EXACT' or not rec['partitions_unchanged'] or not rec['otadata_unchanged']:
        stop('verificação pós-flash falhou')


def boot(a):
    if a.reclassify:                                    # classify the log already captured (no new reset)
        txt = (BK / 'boot_without_sd.log').read_text(encoding='utf-8')
        buf = txt.encode('utf-8')
    else:
        import serial
        port = load('01_detect.json')['ESP32_PORT']
        if load('06_verify.json')['FLASH_READBACK_HASH'] != 'EXACT':
            stop('readback não exato; não dar boot')
        s = serial.Serial(port, 115200, timeout=0.2)
        s.dtr = False                                   # EN/IO0 auto-reset (CH343): IO0 high, pulse EN -> normal boot
        s.rts = True
        time.sleep(0.2)
        s.rts = False
        t0, buf = time.time(), bytearray()
        while time.time() - t0 < a.seconds:
            buf += s.read(4096)
        s.close()
        txt = buf.decode('utf-8', 'replace')
        (BK / 'boot_without_sd.log').write_text(txt, encoding='utf-8')
    low = txt.lower()
    panic = any(k in txt for k in ('Guru Meditation', 'panic', 'abort()', 'Backtrace:', 'Brownout', 'stack overflow', 'assert failed'))
    resets = txt.count('ESP-ROM:')                      # one ROM banner per boot (rst:0x is on the same banner)
    started = 'LEX MACHINA' in txt or 'TESTE CONTEXTO JURIDICO' in txt
    sd_err = 'sd indisponivel' in low or ('sd_montado' in low and 'fail' in low)
    res = 'FAIL' if panic or resets > 1 or not started else ('EXPECTED_SD_ERROR' if sd_err else 'PASS')
    rec = dict(seconds=a.seconds, reclassified_from_saved_log=a.reclassify, classifier_note='v2: 1 banner ESP-ROM por boot (v1 contava '
               'ESP-ROM e rst:0x do MESMO boot como 2 e classificou FAIL por engano)', bytes=len(buf), firmware_started=started, boot_banners=resets, panic_or_abort=panic, sd_error_lines=[
        l for l in txt.splitlines() if ('sd' in l.lower() or 'cart' in l.lower()) and len(l) < 200][:20],
        first_lines=txt.splitlines()[:40], last_lines=txt.splitlines()[-25:], BOOT_WITHOUT_SD=res, log=str(BK / 'boot_without_sd.log'))
    dump('07_boot_without_sd.json', rec)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('step', choices=('detect', 'chip', 'pre', 'flash', 'verify', 'boot'))
    ap.add_argument('--seconds', type=float, default=25)
    ap.add_argument('--reclassify', action='store_true')
    a = ap.parse_args()
    {'detect': detect, 'chip': chip, 'pre': pre, 'flash': flash, 'verify': verify, 'boot': boot}[a.step](a)
