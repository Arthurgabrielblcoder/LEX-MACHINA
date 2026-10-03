"""BATCH04 + RUN3 CONSOLIDATION (final predeploy): one SD overlay candidate + one firmware source candidate, on the PC only.

Inputs (approved, read-only):
  - performance baseline sketch firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE (tag lex-device-v1-performance-approved-2026-10-03)
  - ENTENDA Batches 01-03 finals + 9 pilots + Batch04 (57 round-approved explanations, CF88 arts. 25-36 incl. 29-A)
  - Reference Engine RUN3 export (LEGAL_TARGET_ID/derived/export_test/run3, checked against its SHA256SUMS.txt) - consumed, never rebuilt
  - physically validated ARTICLE_SEARCH indexes CF88 + CC2002 (byte copies, hash-checked)
Outputs:
  - DEVICE_INTEGRATION/staging_sd_v1_batch04_run3_candidate/  (SD/99_LEX_V1 tree + _host diagnostics + STAGING_FILE_MANIFEST.json)
  - DEVICE_INTEGRATION/backups/batch04_run3/src_candidate/LEX_MACHINA_DEVICE_V1_CANDIDATE/  (sketch copy whose lex_ref_detail_data.h is
    the RUN3 rich header; the repository sketch keeps the baseline header)
Never writes to a removable volume. Usage: python build_batch04_run3_candidate.py
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
ROOT = DI.parent
sys.path.insert(0, str(HERE))
import build_sd_staging as S  # noqa: E402

PROFILE = 'BATCH04_RUN3'
OUT = DI / 'staging_sd_v1_batch04_run3_candidate'
TMP = DI / '_tmp_batch04_run3_rebuild'
BASE = DI / 'staging_sd_v1'                                   # physically approved overlay (RUN1, 163 ENTENDA)
RUN1 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1'
RUN2 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run2'
RUN3 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run3'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json'
FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
SRC = DI / 'backups/batch04_run3/src_candidate/LEX_MACHINA_DEVICE_V1_CANDIDATE'
HEADER = 'lex_ref_detail_data.h'
RUN3_HEADER = RUN3 / 'device_candidate/lex_ref_detail_data.RUN3_CANDIDATE.h'
BUILD_COMMIT = '6d0194b8ba82f0612ca73aa75a4377fa5b2b635a'      # base commit of the physically approved package (GIT_COMMIT in LEXV1.VER)
ENGINE_VERSION = dict(tag='cf-reference-engine-run3', run='run3', status='RUN3_APPROVED_CONSUMED_BY_CONSOLIDATION',
                      derived_from='run2 + CF88_WORK_REFERENCE_ADDITIONS (REFERENCE_EXPANSION_01)')
ROLES = {'00_SYS/LEXV1.VER': 'version (schema 3)', '00_SYS/LEX_DEVICE_MANIFEST.json': 'package manifest',
         '05_TEXT/CF88_RUNTIME.txt': 'runtime text CF+ADCT (displayed bytes)', '10_TARGETS/CF88_TARGETS.IDX': 'target table + layer flags',
         '10_TARGETS/CF88_TEXT_MAP.IDX': 'offset -> target map', '10_TARGETS/CF88_ARTICLE_SEARCH.IDX': 'article search index CF88+ADCT',
         '10_TARGETS/CC2002_ARTICLE_SEARCH.IDX': 'article search index Codigo Civil', '20_REFERENCES/REF_LOOKUP.IDX': 'Reference RUN3 lookup',
         '20_REFERENCES/REF_PAYLOAD.IDX': 'Reference RUN3 payload', '30_ENTENDA/ENTENDA_LOOKUP.IDX': 'ENTENDA lookup (Batches 01-04 + pilots)',
         '30_ENTENDA/ENTENDA_PAYLOAD.DAT': 'ENTENDA payload'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree(d):
    return {p.relative_to(d).as_posix(): sha(p) for p in sorted(Path(d).rglob('*')) if p.is_file()}


def run3_approved():
    sums = dict(reversed(l.split('  ', 1)) for l in (RUN3 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if l.strip())
    bad = {n: h for n, h in sums.items() if sha(RUN3 / n) != h}
    if bad:
        raise SystemExit(f'RUN3_NOT_THE_APPROVED_EXPORT {sorted(bad)}')
    man = json.loads((RUN3 / 'RUN3_MANIFEST.json').read_text(encoding='utf-8'))
    prev = {'run1': RUN1, 'run2': RUN2}
    for run, d in prev.items():
        for n, h in man['previous_runs'][run]['files'].items():
            if sha(d / n) != h:
                raise SystemExit(f'{run.upper()}_CHANGED {n}')
    return sums, man


def header_twice():
    outs = []
    with tempfile.TemporaryDirectory() as t:
        for k in ('a', 'b'):
            o = Path(t) / f'{k}.h'
            subprocess.run([sys.executable, str(HERE / 'build_ref_detail_header.py'), '--payload', str(RUN3 / 'REF_PAYLOAD.IDX'),
                            '--additions', str(ADDITIONS), '--out', str(o)], check=True, capture_output=True)
            outs.append(o.read_bytes())
    if outs[0] != outs[1] or outs[0] != RUN3_HEADER.read_bytes():
        raise SystemExit('RUN3_HEADER_NOT_REPRODUCED')
    return hashlib.sha256(outs[0]).hexdigest()


def source_candidate():
    if SRC.exists():
        shutil.rmtree(SRC)
    shutil.copytree(FW, SRC, ignore=shutil.ignore_patterns('*.bin', 'build', '__pycache__'))
    shutil.copyfile(RUN3_HEADER, SRC / HEADER)
    return {p.relative_to(SRC).as_posix(): sha(p) for p in sorted(SRC.rglob('*')) if p.is_file()}


def main():
    sums, run3man = run3_approved()
    S.build(OUT, ref_dir=RUN3, require_committed_refs=False, reference_engine_version=ENGINE_VERSION, profile=PROFILE, build_commit=BUILD_COMMIT)
    try:
        S.build(TMP, ref_dir=RUN3, require_committed_refs=False, reference_engine_version=ENGINE_VERSION, profile=PROFILE, build_commit=BUILD_COMMIT)
        identical = tree(TMP) == tree(OUT)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    if not identical:
        raise SystemExit('STAGING_NOT_DETERMINISTIC')
    sd = OUT / 'SD/99_LEX_V1'
    unchanged = {n: sha(sd / n) == sha(BASE / 'SD/99_LEX_V1' / n) for n in ('05_TEXT/CF88_RUNTIME.txt', '10_TARGETS/CF88_TEXT_MAP.IDX')}
    if not all(unchanged.values()):
        raise SystemExit(f'RUNTIME_OR_TEXT_MAP_CHANGED {unchanged}')                 # Lei Seca / CF runtime / ADCT: fail closed
    refs = {n: sha(sd / '20_REFERENCES' / n) == sums[n] for n in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX')}
    if not all(refs.values()):
        raise SystemExit(f'REFS_NOT_RUN3 {refs}')
    hdr = header_twice()
    src = source_candidate()
    man = json.loads((sd / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
    files = []
    for p in sorted(sd.rglob('*')):
        if p.is_file():
            rel = p.relative_to(sd).as_posix()
            src_of = ('RUN3 export (byte copy)' if rel.startswith('20_REFERENCES') else
                      'physically validated index (byte copy)' if rel.endswith('_ARTICLE_SEARCH.IDX') else
                      'ENTENDA build (Batches 01-04 + pilots)' if rel.startswith('30_ENTENDA') else
                      'CF88_RUNTIME export (unchanged vs approved staging_sd_v1)' if rel in unchanged else
                      'build_sd_staging.py profile ' + PROFILE)
            files.append(dict(path=f'/99_LEX_V1/{rel}', bytes=p.stat().st_size, sha256=sha(p), role=ROLES.get(rel, '?'), source=src_of,
                              same_as_physical_baseline=(BASE / 'SD/99_LEX_V1' / rel).is_file() and sha(BASE / 'SD/99_LEX_V1' / rel) == sha(p)))
    report = dict(profile=PROFILE, staging=OUT.relative_to(ROOT).as_posix(), build_id=man['build_id'], git_commit=man['git_commit'],
                  byte_identical_rebuild=identical, runtime_unchanged=unchanged, refs_equal_run3=refs, run3_counts=run3man['counts']['run3'],
                  entenda_explanations=man['entenda_explanation_count'], entenda_lookup_rows=man['entenda_version']['lookup_rows'],
                  rich_header_sha256=hdr, rich_header_reproduced=True, source_candidate=dict(path=SRC.relative_to(ROOT).as_posix(), files=src),
                  file_count=len(files), total_bytes=sum(f['bytes'] for f in files), files=files)
    (OUT / '_host/STAGING_FILE_MANIFEST.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in report.items() if k not in ('files', 'source_candidate')}, ensure_ascii=False, indent=1))
    for f in files:
        print(f"{f['bytes']:>8} {f['sha256'][:16]} {'=' if f['same_as_physical_baseline'] else '*'} {f['path']}")


if __name__ == '__main__':
    main()
