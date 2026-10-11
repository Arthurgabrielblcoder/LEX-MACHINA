"""FULL CF ENTENDA (final reconciliation Macro07 x Macro08): SD overlay candidate on the PC only.

Inputs (approved, read-only):
  - every ACTIVE HUMAN_APPROVED_T1 ENTENDA of the approved chain of branch reconcile-macro07-macro08 (profile FULL_CF_ENTENDA_810 of
    build_sd_staging.py: main corpus + Batches 01-03 finals + Batch04-06 + Macro07 + Macro08; selection derived from the corpora)
  - everything else exactly as the physically approved BATCH04_RUN3 package: CF88_RUNTIME, TEXT_MAP, RUN3 pair, ARTICLE_SEARCH indexes
Outputs:
  - DEVICE_INTEGRATION/staging_sd_v1_full_entenda_810_candidate/  (SD/99_LEX_V1 tree + _host diagnostics + STAGING_FILE_MANIFEST.json)
Firmware: unchanged (no source candidate is produced). Never writes to a removable volume.
Usage: python build_full_entenda_810_candidate.py [--runs N]   (default 3 byte-identical builds)
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
ROOT = DI.parent
sys.path.insert(0, str(HERE))
import build_sd_staging as S  # noqa: E402
import build_batch04_run3_candidate as B  # noqa: E402

PROFILE = 'FULL_CF_ENTENDA_810'
OUT = DI / 'staging_sd_v1_full_entenda_810_candidate'
TMP = DI / '_tmp_full_entenda_810_rebuild'
BASE = B.OUT                                                   # physically approved BATCH04_RUN3 package (220 ENTENDA)
BUILD_COMMIT = 'fa9719a6bd335275252473a5f154e4e11f5532f4'      # reconcile-macro07-macro08: source of the 810 approved ENTENDA
EXPECTED_CHANGED = ('00_SYS/LEXV1.VER', '00_SYS/LEX_DEVICE_MANIFEST.json', '10_TARGETS/CF88_TARGETS.IDX', '30_ENTENDA/ENTENDA_LOOKUP.IDX',
                    '30_ENTENDA/ENTENDA_PAYLOAD.DAT')


def build(out):
    return S.build(out, ref_dir=B.RUN3, require_committed_refs=False, reference_engine_version=B.ENGINE_VERSION, profile=PROFILE,
                   build_commit=BUILD_COMMIT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=int, default=3)
    a = ap.parse_args()
    sums, _ = B.run3_approved()
    if not (BASE / 'SD/99_LEX_V1/00_SYS/LEXV1.VER').is_file():
        raise SystemExit('BASELINE_BATCH04_RUN3_STAGING_MISSING (run build_batch04_run3_candidate.py first)')
    man = build(OUT)
    trees = [B.tree(OUT / 'SD')]
    try:
        for _ in range(a.runs - 1):
            build(TMP)
            trees.append(B.tree(TMP / 'SD'))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    identical = all(t == trees[0] for t in trees)
    if not identical:
        raise SystemExit('STAGING_NOT_DETERMINISTIC')
    sd, base = OUT / 'SD/99_LEX_V1', BASE / 'SD/99_LEX_V1'
    files = []
    for p in sorted(sd.rglob('*')):
        if p.is_file():
            rel = p.relative_to(sd).as_posix()
            same = (base / rel).is_file() and B.sha(base / rel) == B.sha(p)
            files.append(dict(path=f'/99_LEX_V1/{rel}', bytes=p.stat().st_size, sha256=B.sha(p), role=B.ROLES.get(rel, '?'),
                              same_as_physical_baseline=same, baseline_sha256=B.sha(base / rel) if (base / rel).is_file() else None))
    changed = sorted(f['path'][len('/99_LEX_V1/'):] for f in files if not f['same_as_physical_baseline'])
    if tuple(changed) != EXPECTED_CHANGED:
        raise SystemExit(f'UNEXPECTED_DIFF_VS_PHYSICAL_BASELINE {changed}')
    refs = {n: B.sha(sd / '20_REFERENCES' / n) == sums[n] for n in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX')}
    if not all(refs.values()):
        raise SystemExit(f'REFS_NOT_RUN3 {refs}')
    report = dict(profile=PROFILE, staging=OUT.relative_to(ROOT).as_posix(), baseline=BASE.relative_to(ROOT).as_posix(), build_id=man['build_id'],
                  git_commit=man['git_commit'], deterministic_runs=a.runs, byte_identical_rebuild=identical, refs_equal_run3=refs,
                  entenda_explanations=man['entenda_explanation_count'], entenda_lookup_rows=man['entenda_version']['lookup_rows'],
                  entenda_scope=man['entenda_scope'], changed_vs_physical_baseline=changed, firmware_change="NONE (SD only; the approved flag1 app reads ENTENDA_COUNT and the files dynamically)",
                  file_count=len(files), total_bytes=sum(f['bytes'] for f in files), files=files)
    (OUT / '_host/STAGING_FILE_MANIFEST.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, ensure_ascii=False, indent=1))
    for f in files:
        print(f"{f['bytes']:>8} {f['sha256'][:16]} {'=' if f['same_as_physical_baseline'] else '*'} {f['path']}")


if __name__ == '__main__':
    main()
