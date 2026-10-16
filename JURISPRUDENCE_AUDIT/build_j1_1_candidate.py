"""J1.1: HOST-ONLY SD candidate = current physical baseline (REFERENCES 4, 2026-10-16) + RUN6 (20 jurisprudence links removed), built with the
OFFICIAL staging generator (build_sd_staging), same profile/ENTENDA chain/runtime/TEXT_MAP as the physical baseline.

  - REF_LOOKUP.IDX / REF_PAYLOAD.IDX: RUN6 bytes (LEGAL_TARGET_ID/derived/export_test/run6_juris_j1_candidate/device_ready, committed blobs).
  - CF88_TARGETS.IDX: RUN6 bytes. The generator recomputes every flag; RUN6 may differ from that recomputation ONLY in position R ([4], not
    read by the firmware), kept as approved. Any other difference stops the build.
  - 99_RELATIONS_V2: physical baseline bytes, unchanged.  LEXV1.VER / LEX_DEVICE_MANIFEST.json: regenerated (GIT_COMMIT = --commit).
Proof first: the R1 package builder, re-run at its pinned commit, must reproduce the physical card (R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json).
Outputs: DEVICE_INTEGRATION/staging_sd_v1_juris_j1_1_candidate/ (gitignored) and JURISPRUDENCE_AUDIT/J1_1_CANDIDATE_HOST_ONLY/ (changed files,
rollback = physical bytes, manifest). Never writes to a removable volume.   Usage: python build_j1_1_candidate.py --commit <sha> [--runs N]
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DI = ROOT / 'DEVICE_INTEGRATION'
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'REFERENCE_COVERAGE_AUDIT'))
import build_sd_staging as S  # noqa: E402
import build_references4_r1_candidate as P  # noqa: E402

PROFILE = P.PROFILE
R1_COMMIT = '453922ffcbc5d15fb9bed832a9cfa5206348e3df'
RUN6_DEV = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run6_juris_j1_candidate/device_ready'
PHYSICAL = ROOT / 'REFERENCE_COVERAGE_AUDIT/R2_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
OUT = DI / 'staging_sd_v1_juris_j1_1_candidate'
TMP = DI / '_tmp_juris_j1_1_rebuild'
TMP_BASE = DI / '_tmp_juris_j1_1_physical_reproduction'
PKG = HERE / 'J1_1_CANDIDATE_HOST_ONLY'
ENGINE_VERSION = dict(tag='cf-reference-engine-run6-juris-j1', run='run6', status='RUN6_JURIS_J1_CANDIDATE_HOST_ONLY',
                      derived_from='run5 (REFERENCES 4 physically approved) − 20 jurisprudence false positives (CF88_LINK_EXCLUSIONS_J1, ratified 20/20)')
R_POS = 4
EXPECTED_CHANGED = ('99_LEX_V1/00_SYS/LEXV1.VER', '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX',
                    '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree(d):
    return {p.relative_to(d).as_posix(): sha(p) for p in sorted(Path(d).rglob('*')) if p.is_file()}


def physical():
    return {k: v['sha256'] for k, v in json.loads(PHYSICAL.read_text(encoding='utf-8'))['entries'].items()}


def physical_reproduced():
    try:
        P.build(TMP_BASE, R1_COMMIT)
        t, card = tree(TMP_BASE / 'SD'), physical()
        return all(card.get(k) == v for k, v in t.items()), t
    finally:
        shutil.rmtree(TMP_BASE, ignore_errors=True)


def build(out, commit):
    run6_targets = (RUN6_DEV / 'CF88_TARGETS.IDX').read_bytes()
    original = S.build_targets
    record = {}

    def targets_with_run6_bytes(sd, idx, status, entenda_lookup, ref_lookup):
        stats = original(sd, idx, status, entenda_lookup, ref_lookup)
        p = sd / '10_TARGETS/CF88_TARGETS.IDX'
        gen, cand = p.read_bytes().decode('utf-8').split('\n'), run6_targets.decode('utf-8').split('\n')
        if len(gen) != len(cand):
            raise SystemExit('TARGETS_SHAPE_DIFFERS')
        r_only = []
        for g, c in zip(gen, cand):
            if g == c:
                continue
            fg, fc = g.split('|'), c.split('|')
            if g.startswith('#') or fg[:3] != fc[:3] or fg[3][:R_POS] != fc[3][:R_POS] or fg[3][R_POS + 1:] != fc[3][R_POS + 1:]:
                raise SystemExit(f'TARGETS_DIFFER_BEYOND_R {fg[0]}')
            r_only.append(fg[0])
        p.write_bytes(run6_targets)
        record['targets_r_only_divergence_vs_generator'] = r_only
        return stats

    S.build_targets = targets_with_run6_bytes
    try:
        man = S.build(out, ref_dir=RUN6_DEV, require_committed_refs=True, reference_engine_version=ENGINE_VERSION, profile=PROFILE,
                      build_commit=commit)
    finally:
        S.build_targets = original
    rel_dir = Path(out) / 'SD/99_RELATIONS_V2/05_INDICES_ESP32_V2'
    rel_dir.mkdir(parents=True)
    for name in ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX'):
        (rel_dir / name).write_bytes((RUN6_DEV / name).read_bytes())
    return man, record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', required=True)
    ap.add_argument('--runs', type=int, default=2)
    a = ap.parse_args()
    ok, base_tree = physical_reproduced()
    if not ok:
        raise SystemExit('PHYSICAL_BASELINE_NOT_REPRODUCED')
    man, rec = build(OUT, a.commit)
    trees = [tree(OUT / 'SD')]
    try:
        for _ in range(a.runs - 1):
            build(TMP, a.commit)
            trees.append(tree(TMP / 'SD'))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    if not all(t == trees[0] for t in trees):
        raise SystemExit('STAGING_NOT_DETERMINISTIC')
    card = physical()
    if set(trees[0]) != set(base_tree):
        raise SystemExit('FILE_SET_DIFFERS_FROM_PHYSICAL_STAGING')
    changed = tuple(sorted(k for k in trees[0] if trees[0][k] != card[k]))
    if changed != EXPECTED_CHANGED:
        raise SystemExit(f'UNEXPECTED_DIFF_VS_PHYSICAL {changed}')
    for name, rel in (('REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'), ('REF_PAYLOAD.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'),
                      ('CF88_TARGETS.IDX', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX')):
        if trees[0][rel] != sha(RUN6_DEV / name):
            raise SystemExit(f'STAGING_NOT_RUN6 {rel}')
    m = json.loads((OUT / 'SD/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
    man_ok = all(trees[0].get(k) == v['sha256'] for k, v in m['files'].items() if k != '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json')
    if PKG.exists():
        shutil.rmtree(PKG)
    P.build(TMP_BASE, R1_COMMIT)                    # rollback bytes = current physical baseline (reproduced, checked against the card manifest)
    try:
        for rel in changed:
            for kind, src in (('candidate', OUT / 'SD' / rel), ('rollback', TMP_BASE / 'SD' / rel)):
                dst = PKG / kind / 'SD' / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(Path(src).read_bytes())
    finally:
        shutil.rmtree(TMP_BASE, ignore_errors=True)
    for rel in changed:
        if sha(PKG / 'rollback/SD' / rel) != card[rel]:
            raise SystemExit(f'ROLLBACK_NOT_PHYSICAL {rel}')
    diff = [dict(path='/' + rel, before_sha256=card[rel], before_bytes=(PKG / 'rollback/SD' / rel).stat().st_size, after_sha256=trees[0][rel],
                 after_bytes=(PKG / 'candidate/SD' / rel).stat().st_size) for rel in changed]
    report = dict(profile=PROFILE, package='JURIS_J1_1', status='HOST_ONLY_CANDIDATE', physical_approved=False, card_touched=False,
                  device_flashed=False, firmware_change='NONE (SD only; boot DIAG cases do not use the affected targets)',
                  staging=OUT.relative_to(ROOT).as_posix(), build_id=man['build_id'], git_commit=man['git_commit'], reference_engine=ENGINE_VERSION,
                  physical_baseline_reproduced=True, deterministic_runs=a.runs, byte_identical_rebuild=True,
                  targets_r_only_divergence_vs_generator=rec['targets_r_only_divergence_vs_generator'], device_manifest_matches_package=man_ok,
                  changed_vs_physical=list(changed), file_diff=diff, file_count=len(trees[0]),
                  files=[dict(path='/' + k, sha256=v, same_as_physical=card[k] == v) for k, v in trees[0].items()])
    (PKG / 'J1_1_PACKAGE_MANIFEST.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in report.items() if k not in ('files',)}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
