"""FASE C — HOST-ONLY prototype of a native HC jurisprudence type for the LEX DEVICE V1 firmware. NEVER flashes, NEVER touches firmware/.

Reproducible base = exactly the sketch of the physically approved app (R2, 6e329c91…): firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE (unchanged since
e9c7d53, working-tree bytes) with lex_ref_detail_data.h replaced by the versioned 124-ficha header
LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h (NOT the 122-ficha
header still in firmware/). The base is compiled and compared byte for byte with the approved app: it must differ ONLY in build metadata
(__TIME__/__DATE__ of the core banner, ELF sha in esp_app_desc, image checksum/sha trailer).
HC patch (4 exact-anchor edits, fail closed): enum JTIPO_HC; "hc"/"habeas_corpus" -> JTIPO_HC; label "HC <NUMERO>"; counted with the
control/acórdão group. Everything else byte-identical.
Sketches and binaries: DEVICE_INTEGRATION/_tmp_fw_hc/ and DEVICE_INTEGRATION/backups/hc_prototype/ (both gitignored).
Writes JURISPRUDENCE_AUDIT/HC_FIRMWARE_PROTOTYPE/HC_PROTOTYPE_BUILD.json (+ hc_type.patch).   Usage: python build_hc_firmware_prototype.py
"""
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
HEADER124 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_candidate/lex_ref_detail_data.RUN5_CANDIDATE.h'
APPROVED_BIN = ROOT / 'DEVICE_INTEGRATION/backups/references4_r1/build_cand/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin'
APPROVED_SHA = '6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c'
TMP = ROOT / 'DEVICE_INTEGRATION/_tmp_fw_hc'
BK = ROOT / 'DEVICE_INTEGRATION/backups/hc_prototype'
INO = 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
FQBN = 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default'
FLAGS = 'compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1'
APP_PARTITION = 1310720
AC = Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe'
EOL = '\r\n'
PATCH = [  # (anchor, replacement) — each anchor must occur exactly once in the .ino
    ('  JTIPO_ACORDAO, JTIPO_OUTRO' + EOL, '  JTIPO_ACORDAO, JTIPO_HC, JTIPO_OUTRO' + EOL),
    ('  if(tipo=="acordao") return JTIPO_ACORDAO;' + EOL,
     '  if(tipo=="acordao") return JTIPO_ACORDAO;' + EOL + '  if(tipo=="hc" || tipo=="habeas_corpus") return JTIPO_HC;' + EOL),
    ('    case JTIPO_ACORDAO: return "ACORDAO "+r.numero;' + EOL,
     '    case JTIPO_ACORDAO: return "ACORDAO "+r.numero;' + EOL + '    case JTIPO_HC: return "HC "+r.numero;' + EOL),
    ('    case JTIPO_ADPF: totalAcordaosArtigo++; break;' + EOL,
     '    case JTIPO_ADPF:' + EOL + '    case JTIPO_HC: totalAcordaosArtigo++; break;' + EOL),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def assemble(dest):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SRC, dest / SRC.name)
    (dest / SRC.name / 'lex_ref_detail_data.h').write_bytes(HEADER124.read_bytes())
    return dest / SRC.name


def compile_sketch(sketch, out):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    r = subprocess.run([str(AC), 'compile', '--fqbn', FQBN, '--build-property', FLAGS, '--output-dir', str(out), str(sketch)],
                       capture_output=True, text=True)
    (out.parent / f'compile_{out.name}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    if r.returncode != 0:
        raise SystemExit(f'COMPILE_FAILED {out.name}')
    prog = int(re.search(r'Sketch uses (\d+) bytes', r.stdout).group(1))
    ram = int(re.search(r'Global variables use (\d+) bytes', r.stdout).group(1))
    b = (out / f'{INO}.bin').read_bytes()
    return dict(program_bytes=prog, static_ram_bytes=ram, app_bin_bytes=len(b), app_sha256=sha(b), app_partition_bytes=APP_PARTITION,
                app_partition_free=APP_PARTITION - len(b)), b


def metadata_only_diff(a, b):
    """Offsets of differing bytes; True if all of them are build metadata (app desc ELF sha, core banner time/date, image trailer)."""
    diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    banner = a.find(b'Software Info:\n\x00')
    ok_ranges = [(0xb0, 0xd0), (banner + 15, banner + 15 + 21), (len(a) - 33, len(a))]
    return len(a) == len(b) and all(any(lo <= i < hi for lo, hi in ok_ranges) for i in diff), len(diff)


def main():
    if not AC.is_file():
        raise SystemExit('ARDUINO_CLI_NOT_FOUND')
    base = assemble(TMP / 'base')
    hc = assemble(TMP / 'hc')
    text = (hc / INO).read_bytes().decode('utf-8')
    for anchor, repl in PATCH:
        if text.count(anchor) != 1:
            raise SystemExit(f'ANCHOR_NOT_UNIQUE {anchor.strip()}')
        text = text.replace(anchor, repl)
    (hc / INO).write_bytes(text.encode('utf-8'))
    orig = (base / INO).read_bytes().decode('utf-8').replace('\r\n', '\n').splitlines(keepends=True)
    new = text.replace('\r\n', '\n').splitlines(keepends=True)
    patch = ''.join(difflib.unified_diff(orig, new, f'a/{INO}', f'b/{INO}', n=2))
    (HERE / 'hc_type.patch').write_text(patch, encoding='utf-8', newline='\n')
    others_identical = all((base / p.relative_to(hc)).read_bytes() == p.read_bytes() for p in hc.rglob('*') if p.is_file() and p.name != INO)
    base_info, base_bin = compile_sketch(base, BK / 'build_base')
    hc_info, hc_bin = compile_sketch(hc, BK / 'build_hc')
    approved = APPROVED_BIN.read_bytes() if APPROVED_BIN.is_file() else None
    same_meta, ndiff = metadata_only_diff(approved, base_bin) if approved else (None, None)
    labels_in_bin = dict(base_has_HC_label=b'HC \x00' in base_bin or b'"HC "' in base_bin, hc_has_HC_label=b'HC ' in hc_bin)
    report = dict(
        phase='C', status='HOST_ONLY_PROTOTYPE', flashed=False, firmware_dir_modified=False, physical_approval=False,
        toolchain=dict(arduino_cli=str(AC.name), core='esp32:esp32 3.3.11', fqbn=FQBN, build_property=FLAGS),
        reproducibility=dict(source='firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE (sem mudança desde e9c7d53)',
                             header=dict(path=HEADER124.relative_to(ROOT).as_posix(), sha256=sha(HEADER124.read_bytes()), fichas=124),
                             header_in_firmware_dir=dict(sha256=sha((SRC / 'lex_ref_detail_data.h').read_bytes()), fichas=122,
                                                         note='dívida conhecida: NÃO usado neste build'),
                             approved_app_sha256=APPROVED_SHA, approved_bin_available=approved is not None,
                             approved_bin_sha_matches=approved is not None and sha(approved) == APPROVED_SHA,
                             base_rebuild=base_info, base_vs_approved_differing_bytes=ndiff, base_vs_approved_metadata_only=same_meta,
                             FIRMWARE_BASELINE_REPRODUCED='YES (idêntico exceto metadados de build)' if same_meta else 'NO'),
        hc_patch=dict(file='JURISPRUDENCE_AUDIT/HC_FIRMWARE_PROTOTYPE/hc_type.patch', edits=len(PATCH), other_files_identical=others_identical,
                      ino_sha256_base=sha((base / INO).read_bytes()), ino_sha256_hc=sha((hc / INO).read_bytes())),
        hc_build=hc_info, delta_vs_base=dict(program_bytes=hc_info['program_bytes'] - base_info['program_bytes'],
                                             static_ram_bytes=hc_info['static_ram_bytes'] - base_info['static_ram_bytes'],
                                             app_bin_bytes=hc_info['app_bin_bytes'] - base_info['app_bin_bytes']),
        labels_in_bin=labels_in_bin,
        not_verified=['teste físico (boot, lista, ficha, BACK)', 'tempo de boot', 'PSRAM em execução', 'BLE'],
        binaries='DEVICE_INTEGRATION/backups/hc_prototype/{build_base,build_hc} (fora do Git)')
    (HERE / 'HC_PROTOTYPE_BUILD.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report[k] for k in ('reproducibility', 'hc_build', 'delta_vs_base', 'hc_patch')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
