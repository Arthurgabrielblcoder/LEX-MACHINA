"""Tela vermelha (TFT 3,2" ILI9341): reprodução do firmware aprovado f7e6b190 + candidato INVON=0. Host-only; nunca faz flash.

Baseline: .ino do Content V2 aprovado (bba91c1 / c2c0647) + headers/assets de firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE,
FQBN e flag idênticos aos do gate físico de 21/10/2026. Candidato: a mesma fonte com PAINEL_PRECISA_INVON 1 -> 0, e nada mais.

Uso:  python build_tela_vermelha.py [--approved-bin CAMINHO]   compila baseline + candidato e grava relatório
      python build_tela_vermelha.py --check                    confere fontes e hashes já gerados (sem compilar)
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INO = 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
APPROVED_INO = ROOT / 'JURISPRUDENCE_ENGINE/firmware_turma_content_v2/candidate' / INO
APPROVED_INO_SHA = 'b78d910b4a9c8760ceb9503f4cfdaa91887a1dca16048574f95c861da197525e'   # CRLF, = TURMA_CONTENT_V2_FIRMWARE_BUILD.json
APPROVED_APP_SHA = 'f7e6b1908e8c91c99582c377b6db3a46b06f18d4f59f2cddeb1b4666514b09f9'
SRC = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
HEADERS = {   # SHA-256 com finais de linha normalizados para LF (o checkout pode ter CRLF ou LF; o binário não muda)
    'contexto_juridico.h': 'd3dd321be292bf7e5823459f998b9b28c4291e1db426395e4467b7fb793374bc',
    'lex_device_v1.h': 'bb846dbc36ad97033825d2e9d092f984eaec44aa7d7ba46ee0ef0b82c1297ea7',
    'lex_leitor_scroll.h': '9ff3573b92101ade96a2c03af151e5b855b4b3ddbbc89c77c939266d2451aa1d',
    'lex_ref_detail_data.h': 'e420f4dec7923036448b4cf1129c6092a9489b8c36c8cef4921a5d534b6f55f8',
    'assets/lex_boot_screen.h': '9304383b6d1c178bf9ed30f3a1541d60ce2e44e469bdd343474b7907be25cfad',
}
FQBN = 'esp32:esp32:esp32s3:PSRAM=opi,FlashSize=4M,PartitionScheme=default'
FLAGS = 'compiler.cpp.extra_flags=-DLEX_DEVICE_V1_ENABLED=1'
APP_PARTITION = 1310720
AC = Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe'
TMP = Path(tempfile.gettempdir()) / 'lex_machina_tela_vermelha'   # scratch, fora do repositório
OUT = HERE / 'candidate_invon0'
PATCH_FILE = HERE / 'invon0.patch'
REPORT = HERE / 'TELA_VERMELHA_INVON0_BUILD.json'
# Evidência local (não versionada) do gate de 21/10, no checkout principal que compartilha o .git deste worktree
DEFAULT_APPROVED_BIN = 'JURISPRUDENCE_ENGINE/firmware_turma_content_v2/_local/physical_gate_20261021_102243/content_v2_candidate_f7e6b190.bin'
E = '\r\n'
INVON_ANCHOR = '#define PAINEL_PRECISA_INVON 1' + E
INVON_REPL = '#define PAINEL_PRECISA_INVON 0' + E


def sha(b):
    return hashlib.sha256(b).hexdigest()


def approved_source():
    raw = APPROVED_INO.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')   # fonte aprovada foi gravada em CRLF
    if sha(raw) != APPROVED_INO_SHA:
        raise SystemExit(f'APPROVED_INO_SHA_MISMATCH {sha(raw)}')
    for name, want in HEADERS.items():
        got = sha((SRC / name).read_bytes().replace(b'\r\n', b'\n'))
        if got != want:
            raise SystemExit(f'HEADER_SHA_MISMATCH {name} {got}')
    return raw.decode('utf-8')


def invon0_text(base):
    if base.count(INVON_ANCHOR) != 1:
        raise SystemExit('INVON_ANCHOR_NOT_UNIQUE')
    return base.replace(INVON_ANCHOR, INVON_REPL)


def assemble(name, text):
    dest = TMP / f'src_{name}'
    if dest.exists():
        shutil.rmtree(dest)
    sketch = dest / SRC.name
    sketch.mkdir(parents=True)
    for rel in HEADERS:   # só o que o sketch inclui (LEIA_ME.txt não entra no build)
        (sketch / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SRC / rel, sketch / rel)
    (sketch / INO).write_bytes(text.encode('utf-8'))
    return sketch


def compile_sketch(sketch, name):
    out = TMP / f'build_{name}'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    r = subprocess.run([str(AC), 'compile', '--fqbn', FQBN, '--build-property', FLAGS, '--build-path', str(out), str(sketch)],
                       capture_output=True, text=True)
    (TMP / f'compile_{name}.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    if r.returncode != 0:
        raise SystemExit(f'COMPILE_FAILED {name} (log: {TMP / f"compile_{name}.log"})')
    prog = int(re.search(r'Sketch uses (\d+) bytes', r.stdout).group(1))
    ram = int(re.search(r'Global variables use (\d+) bytes', r.stdout).group(1))
    b = (out / f'{INO}.bin').read_bytes()
    return dict(program_bytes=prog, static_ram_bytes=ram, app_bin_bytes=len(b), app_sha256=sha(b),
                app_partition_bytes=APP_PARTITION, app_partition_free=APP_PARTITION - len(b)), b, out


def metadata_ranges(a):
    """Mesmas faixas do verificador do projeto: SHA do ELF no app_desc, data/hora do banner, checksum + SHA final."""
    banner = a.find(b'Software Info:\n\x00')
    return [(0xb0, 0xd0), (banner + 15, banner + 15 + 21), (len(a) - 33, len(a))]


def diff_bytes(a, b):
    diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    ok = metadata_ranges(a)
    outside = [i for i in diff if not any(lo <= i < hi for lo, hi in ok)]
    return dict(same_length=len(a) == len(b), differing_bytes=len(diff), outside_metadata=len(outside),
                outside_metadata_offsets=[hex(i) for i in outside],
                metadata_only=len(a) == len(b) and not outside)


def toolchain_info():
    v = subprocess.run([str(AC), 'version'], capture_output=True, text=True).stdout.strip()
    cores = subprocess.run([str(AC), 'core', 'list'], capture_output=True, text=True).stdout
    libs = subprocess.run([str(AC), 'lib', 'list'], capture_output=True, text=True).stdout
    core = next((l.split()[1] for l in cores.splitlines() if l.startswith('esp32:esp32')), '?')
    used = ('Adafruit BusIO', 'Adafruit GFX Library', 'Adafruit ILI9341', 'EspBle')
    lib = {n: l[len(n):].split()[0] for l in libs.splitlines() for n in used if l.startswith(n + ' ')}
    return dict(arduino_cli=v, core=f'esp32:esp32 {core}', fqbn=FQBN, build_property=FLAGS, libraries=lib)


def unified(base, cand):
    return ''.join(difflib.unified_diff(base.replace(E, '\n').splitlines(True), cand.replace(E, '\n').splitlines(True),
                                        f'a/{INO} (Content V2 aprovado f7e6b190)', f'b/{INO} (tela vermelha INVON=0)'))


def find_approved_bin(arg):
    if arg:
        return Path(arg)
    common = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            capture_output=True, text=True).stdout.strip()
    return Path(common).parent / DEFAULT_APPROVED_BIN


def main():
    if '--check' in sys.argv:
        rep = json.loads(REPORT.read_text(encoding='utf-8'))
        cand = invon0_text(approved_source()).encode('utf-8')
        ok = (OUT / INO).read_bytes() == cand and sha(cand) == rep['candidate']['source_sha256']
        ok = ok and sha((OUT / f'{INO}.bin').read_bytes()) == rep['candidate']['app_sha256']
        ok = ok and PATCH_FILE.read_text(encoding='utf-8') == unified(approved_source(), cand.decode('utf-8'))
        print('UP_TO_DATE' if ok else 'STALE')
        return 0 if ok else 1
    if not AC.is_file():
        raise SystemExit(f'ARDUINO_CLI_NOT_FOUND {AC}')
    arg = sys.argv[sys.argv.index('--approved-bin') + 1] if '--approved-bin' in sys.argv else None
    approved_path = find_approved_bin(arg)
    approved = approved_path.read_bytes()
    if sha(approved) != APPROVED_APP_SHA:
        raise SystemExit(f'APPROVED_BIN_SHA_MISMATCH {approved_path}')
    base = approved_source()
    cand = invon0_text(base)
    if TMP.exists():
        shutil.rmtree(TMP)
    base_info, base_bin, _ = compile_sketch(assemble('baseline', base), 'baseline')
    cand_info, cand_bin, cand_build = compile_sketch(assemble('invon0', cand), 'invon0')
    repro = diff_bytes(base_bin, approved)
    if not repro['metadata_only']:
        raise SystemExit('BASELINE_NOT_REPRODUCED ' + json.dumps(repro))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / INO).write_bytes(cand.encode('utf-8'))
    (OUT / f'{INO}.bin').write_bytes(cand_bin)
    for ext in ('elf', 'map'):   # locais (gitignored), para análise de símbolos
        shutil.copyfile(cand_build / f'{INO}.{ext}', OUT / f'{INO}.{ext}')
    PATCH_FILE.write_text(unified(base, cand), encoding='utf-8')
    report = dict(
        schema_version=1, status='HOST_ONLY_CANDIDATE', flashed=False, sd_changed=False,
        purpose='Tela TFT vermelha 3,2" (ILI9341): primeiro candidato só desliga INVON (cores normais).',
        toolchain=toolchain_info(),
        approved=dict(app_sha256=APPROVED_APP_SHA, source=str(APPROVED_INO.relative_to(ROOT)).replace('\\', '/'),
                      source_sha256=APPROVED_INO_SHA, source_commit='bba91c1f647de360542552f76015250b212d4dd5',
                      headers_dir=str(SRC.relative_to(ROOT)).replace('\\', '/'), headers_sha256=HEADERS),
        reproduction=dict(baseline=base_info, vs_approved=repro,
                          verdict='REPRODUCED (idêntico exceto metadados de build)'),
        candidate=dict(source=str((OUT / INO).relative_to(ROOT)).replace('\\', '/'), source_sha256=sha(cand.encode('utf-8')),
                       binary=str((OUT / f'{INO}.bin').relative_to(ROOT)).replace('\\', '/'), patch=PATCH_FILE.name,
                       **cand_info),
        candidate_vs_baseline=dict(diff_bytes(base_bin, cand_bin),
                                   program_bytes=cand_info['program_bytes'] - base_info['program_bytes'],
                                   static_ram_bytes=cand_info['static_ram_bytes'] - base_info['static_ram_bytes'],
                                   app_bin_bytes=cand_info['app_bin_bytes'] - base_info['app_bin_bytes']),
    )
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(reproduction=report['reproduction'], candidate=report['candidate'],
                          candidate_vs_baseline={k: v for k, v in report['candidate_vs_baseline'].items()
                                                 if k != 'outside_metadata_offsets'}), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
