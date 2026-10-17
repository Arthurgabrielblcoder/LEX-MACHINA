"""PARTE D — the authoritative firmware/ directory must rebuild the physically approved app (R2, 6e329c91…) WITHOUT copying any header from
another package. Builds firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE as is (copy to DEVICE_INTEGRATION/_tmp_fw_d3, gitignored), compares the app
image byte for byte with the approved binary and accepts ONLY the known build-metadata ranges (esp_app_desc ELF sha, core "Software Info"
__TIME__/__DATE__, image checksum + sha trailer). Never flashes. Writes FIRMWARE_BASELINE_REPRODUCIBILITY.json.
Usage: python verify_firmware_baseline.py
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SKETCH = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
HEADER = SKETCH / 'lex_ref_detail_data.h'
HEADER_SHA_LF = 'e420f4dec7923036448b4cf1129c6092a9489b8c36c8cef4921a5d534b6f55f8'      # RUN5 / R1 (b5ccf96), 124 fichas
APPROVED = ROOT / 'DEVICE_INTEGRATION/backups/references4_r1/build_cand/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin'
APPROVED_SHA = '6e329c91d22d84590d0c9ff1dc3945519513a0bfe7cbeeb6509b280372cfd31c'
TMP = ROOT / 'DEVICE_INTEGRATION/_tmp_fw_d3'
OUT = ROOT / 'DEVICE_INTEGRATION/backups/firmware_d3/build'
AC = Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe'
FQBN = 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default'
FLAGS = 'compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1'
INO = 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def metadata_only(a, b):
    diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    banner = a.find(b'Software Info:\n\x00')
    ok = [(0xb0, 0xd0), (banner + 15, banner + 15 + 21), (len(a) - 33, len(a))]
    return len(a) == len(b) and all(any(lo <= i < hi for lo, hi in ok) for i in diff), len(diff), ok


def main():
    hdr = HEADER.read_bytes().replace(b'\r\n', b'\n')
    count = int(re.search(rb'#define LEXV1_REF_DETAIL_COUNT (\d+)', hdr).group(1))
    if sha(hdr) != HEADER_SHA_LF or count != 124:
        raise SystemExit(f'FIRMWARE_HEADER_NOT_124 {count}')
    if TMP.exists():
        shutil.rmtree(TMP)
    shutil.copytree(SKETCH, TMP / SKETCH.name)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    r = subprocess.run([str(AC), 'compile', '--fqbn', FQBN, '--build-property', FLAGS, '--output-dir', str(OUT), str(TMP / SKETCH.name)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('COMPILE_FAILED')
    prog = int(re.search(r'Sketch uses (\d+) bytes', r.stdout).group(1))
    ram = int(re.search(r'Global variables use (\d+) bytes', r.stdout).group(1))
    new, old = (OUT / f'{INO}.bin').read_bytes(), APPROVED.read_bytes()
    if sha(old) != APPROVED_SHA:
        raise SystemExit('APPROVED_BINARY_MISSING_OR_CHANGED')
    ok, ndiff, ranges = metadata_only(old, new)
    rep = dict(phase='D', firmware_dir=SKETCH.relative_to(ROOT).as_posix(), header=dict(path=HEADER.relative_to(ROOT).as_posix(), fichas=count,
               sha256_lf=sha(hdr), origin='LEGAL_TARGET_ID/derived/export_test/run5_references4_r1_candidate/device_candidate/'
                                         'lex_ref_detail_data.RUN5_CANDIDATE.h (commit b5ccf96, R1)'),
               approved_app=dict(sha256=APPROVED_SHA, bytes=len(old), flashed='R2, 2026-10-16 (REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/firmware_flash.json)'),
               rebuild=dict(sha256=sha(new), bytes=len(new), program_bytes=prog, static_ram_bytes=ram),
               differing_bytes=ndiff, allowed_ranges=['esp_app_desc ELF sha (0xb0-0xd0)', 'core banner __TIME__/__DATE__', 'image checksum + sha trailer'],
               metadata_only=ok, FIRMWARE_SOURCE_BASELINE_REPRODUCIBLE='PASS' if ok and prog == 1100991 and ram == 126148 else 'FAIL',
               flashed=False)
    (HERE / 'FIRMWARE_BASELINE_REPRODUCIBILITY.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
