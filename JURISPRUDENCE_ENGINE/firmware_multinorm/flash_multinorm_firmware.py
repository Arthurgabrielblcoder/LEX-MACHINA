"""MULTINORMA — first physical flash of the multinorm firmware (app0 @ 0x10000 ONLY) over the UNCHANGED J2I card. One step per call,
every step gated, nothing assumed. The microSD stays INSIDE the device and is never written (no D:, no copy).

  freeze   copy the multinorm build (sha recorded in MULTINORM_PROTOTYPE_BUILD.json) to a frozen, gitignored location; never recompiled after
  gates    host gates: engine + jurisprudence suites, patched source == recorded build source, partitions.bin of the build == J2I chip table
  detect   exactly one CH343 1A86:55D3 with the project serial, or STOP
  chip     esptool flash-id: ESP32-S3, MAC and flash size == project device
  pre      read partitions, otadata, nvs and the FULL app0 (twice); app0 must start with the J2I approved app 1371e69a… (full sha-256)
  flash    write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x10000 multinorm_app.bin (NO erase, NO other region)
  verify   read app0 again; first len(bin) bytes == frozen binary; partitions/otadata unchanged
  boot     hard reset WITH the J2I card inside; capture serial; classify boot, SD, juris cache and the legacy fallback
Backups (gitignored): DEVICE_INTEGRATION/backups/multinorm_physical_flash/ (never overwritten). Evidence: firmware_multinorm/PHYSICAL_FLASH/.
Usage: python flash_multinorm_firmware.py <step> [--seconds N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENG = HERE.parent
ROOT = ENG.parent
BUILD_JSON = HERE / 'MULTINORM_PROTOTYPE_BUILD.json'
SRC_BUILD = Path(tempfile.gettempdir()) / 'lex_machina_fw_multinorm/build_multinorm'
FROZEN = ROOT / 'DEVICE_INTEGRATION/backups/multinorm_flash_candidate'
BIN = FROZEN / 'multinorm_app.bin'
J2I_APP = ROOT / 'DEVICE_INTEGRATION/backups/j2i_flash_candidate/generic_app.bin'
BK = ROOT / 'DEVICE_INTEGRATION/backups/multinorm_physical_flash'
EV = HERE / 'PHYSICAL_FLASH'
J2I_EV = ROOT / 'JURISPRUDENCE_AUDIT/J2I_PHYSICAL_FLASH'
J2I_APP_SHA = '1371e69a0ef3b16773c36e240b166ee99f73d48c2629d11ebf09191701de2b6c'
J2I_PARTITIONS_SHA = '148b959cbff1c38aa8e1d5c0ba9d612c54997b945e56a63f41223eef650653a1'
J2I_OTADATA_SHA = 'f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0'
VIDPID, SERIAL_NO, MAC = '1A86:55D3', '5C38165292', 'e0:72:a1:f4:fd:28'
APP0 = 0x10000
INO = 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'


def stop(m):
    raise SystemExit('PARAR: ' + m)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def dump(name, value):
    EV.mkdir(parents=True, exist_ok=True)
    (EV / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(value, ensure_ascii=False)[:3500])


def load(name):
    return json.loads((EV / name).read_text(encoding='utf-8'))


def esptool(port, *args, after='no-reset', log=None):
    cmd = [sys.executable, '-m', 'esptool', '--chip', 'esp32s3', '-p', port, '-b', '460800', '--after', after, *args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if log:
        BK.mkdir(parents=True, exist_ok=True)
        (BK / log).write_text(' '.join(cmd) + '\n\n' + out, encoding='utf-8')
    if r.returncode != 0:
        stop(f'esptool falhou ({args[0]}): ' + out[-1500:])
    return ' '.join(cmd[2:]), out


def partitions(b: bytes) -> dict:
    out = {}
    for i in range(0, len(b), 32):
        e = b[i:i + 32]
        if e[:2] != b'\xaa\x50':
            break
        t, st, off, sz = struct.unpack('<BBII', e[2:12])
        out[e[12:28].rstrip(b'\0').decode()] = dict(type=t, subtype=st, offset=off, size=sz)
    return out


def freeze(_a):
    b = json.loads(BUILD_JSON.read_text(encoding='utf-8'))
    if BIN.exists():
        stop('binário já congelado; não sobrescrever: ' + str(BIN))
    src = SRC_BUILD / f'{INO}.bin'
    data = src.read_bytes()
    if sha(data) != b['builds']['multinorm']['app_sha256'] or len(data) != b['builds']['multinorm']['app_bin_bytes']:
        stop('o build em disco não é o registrado em MULTINORM_PROTOTYPE_BUILD.json')
    FROZEN.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, BIN)
    shutil.copyfile(SRC_BUILD / f'{INO}.partitions.bin', FROZEN / 'multinorm_partitions.bin')
    rec = dict(MULTINORM_APP_BIN=str(BIN.relative_to(ROOT)), MULTINORM_APP_SHA256=sha(BIN.read_bytes()), MULTINORM_APP_SIZE=len(data),
               build_partitions_sha256=sha((FROZEN / 'multinorm_partitions.bin').read_bytes()), source_ino_sha256=b['patch']['ino_sha256'],
               patch_edits=b['patch']['edits'], program_bytes=b['builds']['multinorm']['program_bytes'], static_ram_bytes=b['builds']['multinorm']['static_ram_bytes'],
               PROGRAM_DELTA=b['delta']['program_bytes'], RAM_DELTA=b['delta']['static_ram_bytes'], APP_FREE=b['builds']['multinorm']['app_partition_free'],
               toolchain=b['toolchain'], recompiled_after_freeze=False)
    dump('00_freeze.json', rec)


def gates(_a):
    fr = load('00_freeze.json')
    sys.path.insert(0, str(HERE))
    import build_multinorm_prototype as BP
    src_sha = sha(BP.multinorm_text(BP.types_module().patched_text()).encode('utf-8'))
    suites = {}
    for d in ('JURISPRUDENCE_ENGINE', 'JURISPRUDENCE_AUDIT', 'LEGAL_TARGET_ID'):
        r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', f'{d}/tests'], capture_output=True, text=True, cwd=ROOT)
        suites[d] = dict(ok=r.returncode == 0, tail=[l for l in (r.stdout + r.stderr).splitlines() if l.startswith(('Ran', 'OK', 'FAILED'))])
    sys.path.insert(0, str(ROOT / 'JURISPRUDENCE_AUDIT'))
    import build_j2_batch as G
    vis = G.j2i_baseline()
    g = dict(BINARY_FROZEN_SHA_MATCH=sha(BIN.read_bytes()) == fr['MULTINORM_APP_SHA256'], SOURCE_EQUALS_RECORDED_BUILD=src_sha == fr['source_ino_sha256'],
             BUILD_PARTITIONS_EQUAL_J2I_CHIP=fr['build_partitions_sha256'] == J2I_PARTITIONS_SHA, image_magic_ok=BIN.read_bytes()[:1] == b'\xe9',
             J2I_ROLLBACK_APP_PRESENT=J2I_APP.is_file() and sha(J2I_APP.read_bytes()) == J2I_APP_SHA,
             CF_SEMANTICS=f'{len(vis)}/{len({r[0] for r in vis})}', suites=suites)
    g['HOST_GATES'] = 'PASS' if (all(v for k, v in g.items() if isinstance(v, bool)) and g['CF_SEMANTICS'] == '315/198'
                                 and all(s['ok'] for s in suites.values())) else 'FAIL'
    dump('01_gates.json', g)
    if g['HOST_GATES'] != 'PASS':
        stop('gates host falharam')


def detect(_a):
    from serial.tools import list_ports
    ports = list(list_ports.comports())
    cands = [p for p in ports if p.vid == 0x1A86 and p.pid == 0x55D3]
    rec = dict(ports=[dict(device=p.device, description=p.description, hwid=p.hwid) for p in ports])
    if len(cands) != 1 or cands[0].serial_number != SERIAL_NO:
        stop('porta ambígua ou ausente: ' + json.dumps(rec, ensure_ascii=False))
    rec.update(ESP32_PORT=cands[0].device, vid_pid=VIDPID, serial_number=cands[0].serial_number, description=cands[0].description)
    dump('02_detect.json', rec)


def chip(_a):
    port = load('02_detect.json')['ESP32_PORT']
    cmd, out = esptool(port, 'flash-id', log='flash_id.log')
    keys = {k: next((l.split(':', 1)[1].strip() for l in out.splitlines() if l.strip().startswith(k)), None)
            for k in ('Chip type', 'Features', 'Crystal frequency', 'MAC', 'Detected flash size', 'Manufacturer', 'Device')}
    ok = (keys['Chip type'] or '').startswith('ESP32-S3') and keys['MAC'] == MAC and keys['Detected flash size'] == '16MB'
    dump('03_chip.json', dict(command=cmd, **keys, MATCHES_PROJECT_DEVICE=ok))
    if not ok:
        stop('chip/MAC/flash não correspondem ao aparelho do projeto')


def pre(_a):
    port = load('02_detect.json')['ESP32_PORT']
    if load('03_chip.json')['MATCHES_PROJECT_DEVICE'] is not True:
        stop('chip não validado')
    if (BK / 'app0_pre_flash.bin').exists():
        stop('backup PRE já existe; não sobrescrever: ' + str(BK))
    esptool(port, 'read-flash', '0x8000', '0xC00', str(BK / 'partitions_pre.bin'), log='read_partitions_pre.log')
    pt_b = (BK / 'partitions_pre.bin').read_bytes()
    pt = partitions(pt_b)
    app0 = pt.get('app0')
    if not app0 or app0['offset'] != APP0:
        stop('sem app0 em 0x10000: ' + json.dumps(pt))
    esptool(port, 'read-flash', '0xe000', '0x2000', str(BK / 'otadata_pre.bin'), log='read_otadata_pre.log')
    esptool(port, 'read-flash', '0x9000', '0x5000', str(BK / 'nvs_pre.bin'), log='read_nvs_pre.log')
    esptool(port, 'read-flash', hex(APP0), hex(app0['size']), str(BK / 'app0_pre_flash.bin'), log='read_app0_pre.log')
    esptool(port, 'read-flash', hex(APP0), hex(app0['size']), str(BK / 'app0_pre_flash_verify.bin'), log='read_app0_pre_verify.log')
    full, again = (BK / 'app0_pre_flash.bin').read_bytes(), (BK / 'app0_pre_flash_verify.bin').read_bytes()
    j2i = J2I_APP.read_bytes()
    rec = dict(partition_table=pt, app0_offset=hex(app0['offset']), app0_partition_size=app0['size'], app0_partition_size_hex=hex(app0['size']),
               partitions_sha256=sha(pt_b), otadata_sha256=sha((BK / 'otadata_pre.bin').read_bytes()), nvs_sha256=sha((BK / 'nvs_pre.bin').read_bytes()),
               app0_full_sha256=sha(full), PRE_APP_READ_STABLE='PASS' if full == again else 'FAIL',
               CURRENT_APP_PRE_HASH=sha(full[:len(j2i)]), J2I_APPROVED_APP_SHA256=J2I_APP_SHA, j2i_frozen_copy_sha256=sha(j2i))
    rec['CURRENT_APP_MATCHES_J2I_APPROVED'] = 'YES' if (rec['CURRENT_APP_PRE_HASH'] == J2I_APP_SHA == rec['j2i_frozen_copy_sha256']
                                                        and rec['PRE_APP_READ_STABLE'] == 'PASS') else 'NO'
    rec['PARTITION_LAYOUT_MATCH'] = 'PASS' if (rec['partitions_sha256'] == J2I_PARTITIONS_SHA == load('00_freeze.json')['build_partitions_sha256']) else 'FAIL'
    rec['OTADATA_MATCH_J2I'] = rec['otadata_sha256'] == J2I_OTADATA_SHA
    rec['FITS_APP0'] = len(BIN.read_bytes()) <= app0['size']
    dump('04_pre.json', rec)
    if rec['CURRENT_APP_MATCHES_J2I_APPROVED'] != 'YES' or rec['PARTITION_LAYOUT_MATCH'] != 'PASS' or not rec['FITS_APP0']:
        stop('estado do chip não é o aprovado J2I (app/partições) ou o binário não cabe')


def flash(_a):
    port = load('02_detect.json')['ESP32_PORT']
    if load('01_gates.json')['HOST_GATES'] != 'PASS' or load('04_pre.json')['CURRENT_APP_MATCHES_J2I_APPROVED'] != 'YES':
        stop('gates/PRE não aprovados')
    if (EV / '05_flash.json').exists():
        stop('flash já registrado; não repetir')
    fr = load('00_freeze.json')
    if sha(BIN.read_bytes()) != fr['MULTINORM_APP_SHA256']:
        stop('binário congelado mudou')
    cmd, out = esptool(port, 'write-flash', '--flash-mode', 'keep', '--flash-freq', 'keep', '--flash-size', 'keep', hex(APP0), str(BIN),
                       log='write_flash.log')
    ok = 'Hash of data verified' in out
    dump('05_flash.json', dict(command=cmd, FLASH_ADDRESS=hex(APP0), FLASH_SCOPE='APP_ONLY', image=str(BIN.relative_to(ROOT)),
                               image_sha256=fr['MULTINORM_APP_SHA256'], bytes=fr['MULTINORM_APP_SIZE'], erase_flash_used=False,
                               esptool_hash_verified=ok, output_tail=out.strip().splitlines()[-8:]))
    if not ok:
        stop('esptool não confirmou o hash da gravação')


def verify(_a):
    port = load('02_detect.json')['ESP32_PORT']
    if not (EV / '05_flash.json').exists():
        stop('flash não registrado')
    p = load('04_pre.json')
    esptool(port, 'read-flash', hex(APP0), hex(p['app0_partition_size']), str(BK / 'app0_post_flash.bin'), log='read_app0_post.log')
    esptool(port, 'read-flash', '0x8000', '0xC00', str(BK / 'partitions_post.bin'), log='read_partitions_post.log')
    esptool(port, 'read-flash', '0xe000', '0x2000', str(BK / 'otadata_post.bin'), log='read_otadata_post.log')
    post, img = (BK / 'app0_post_flash.bin').read_bytes(), BIN.read_bytes()
    rec = dict(app0_post_full_sha256=sha(post), APP0_READBACK_SHA256=sha(post[:len(img)]), MULTINORM_APP_SHA256=sha(img),
               FLASH_READBACK_MATCH='EXACT' if post[:len(img)] == img else 'MISMATCH',
               partitions_unchanged=sha((BK / 'partitions_post.bin').read_bytes()) == p['partitions_sha256'],
               otadata_unchanged=sha((BK / 'otadata_post.bin').read_bytes()) == p['otadata_sha256'])
    dump('06_verify.json', rec)
    if rec['FLASH_READBACK_MATCH'] != 'EXACT' or not rec['partitions_unchanged'] or not rec['otadata_unchanged']:
        stop('verificação pós-flash falhou')


def boot(a):
    import serial
    port = load('02_detect.json')['ESP32_PORT']
    if load('06_verify.json')['FLASH_READBACK_MATCH'] != 'EXACT':
        stop('readback não exato; não dar boot')
    s = serial.Serial(port, 115200, timeout=0.2)
    s.dtr = False                                       # CH343 auto-reset: IO0 high, pulse EN -> normal boot
    s.rts = True
    time.sleep(0.2)
    s.rts = False
    t0, buf = time.time(), bytearray()
    while time.time() - t0 < a.seconds:
        buf += s.read(4096)
    s.close()
    txt = buf.decode('utf-8', 'replace')
    (BK / 'boot_with_j2i_sd.log').write_text(txt, encoding='utf-8')
    low = txt.lower()
    panic = any(k in txt for k in ('Guru Meditation', 'panic', 'abort()', 'Backtrace:', 'Brownout', 'stack overflow', 'assert failed'))
    banners = txt.count('ESP-ROM:')
    started = 'LEX MACHINA' in txt or 'TESTE CONTEXTO JURIDICO' in txt
    sd_missing = 'sd indisponivel' in low
    cache = re.search(r'JUR CACHE: lookups=(\d+) registros=(\d+) bytes=(\d+) .*?PSRAM_livre_antes=(\d+) PSRAM_livre_depois=(\d+)', txt)
    normalized = 'camada normalizada multinorma' in low
    alloc_err = any(k in low for k in ('alocacao psram', 'falhou', 'corrompid', 'inconsistente'))
    rec = dict(seconds=a.seconds, bytes=len(buf), firmware_started=started, boot_banners=banners, panic_or_abort=panic, sd_unavailable=sd_missing,
               jur_cache=dict(lookups=int(cache.group(1)), registros=int(cache.group(2)), bytes=int(cache.group(3)), psram_free_before=int(cache.group(4)),
                              psram_free_after=int(cache.group(5)), psram_used=int(cache.group(4)) - int(cache.group(5))) if cache else None,
               normalized_layer_used=normalized, allocation_or_cache_error=alloc_err,
               jur_lines=[l for l in txt.splitlines() if 'JUR' in l or 'LEXV1' in l or 'PSRAM' in l][:30],
               first_lines=txt.splitlines()[:40], last_lines=txt.splitlines()[-30:], log=str(BK / 'boot_with_j2i_sd.log'))
    rec['BOOT_WITH_J2I_SD'] = 'PASS' if (started and not panic and banners == 1 and not sd_missing and cache and not alloc_err) else 'FAIL'
    rec['LEGACY_J2I_FALLBACK'] = 'PASS' if (cache and not normalized and rec['jur_cache']['lookups'] == 237 and rec['jur_cache']['registros'] == 355) else 'FAIL'
    dump('07_boot_with_j2i_sd.json', rec)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('step', choices=('freeze', 'gates', 'detect', 'chip', 'pre', 'flash', 'verify', 'boot'))
    ap.add_argument('--seconds', type=float, default=30)
    a = ap.parse_args()
    {'freeze': freeze, 'gates': gates, 'detect': detect, 'chip': chip, 'pre': pre, 'flash': flash, 'verify': verify, 'boot': boot}[a.step](a)
