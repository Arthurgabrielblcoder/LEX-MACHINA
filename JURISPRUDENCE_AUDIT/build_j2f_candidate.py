"""J2F: HOST-ONLY SD candidates of the RATIFIED jurisprudence (Batch02 J2E + Batches 03–09) over the CURRENT physical card
(J2C 12/12, PHYSICAL_BASELINE 261/160). Never writes to a removable volume; never flashes.

  J2_CURRENT_FW_CANDIDATE (A): RUN11-A — every ratified relation the CURRENT firmware shows correctly (RG, SV, ADI).
  J2_GENERIC_FW_CANDIDATE (B): RUN11-B — A + group B (HC, MS, AP, AI, Inq, Rcl, ADPF, súmula comum, TSE…); ONLY usable with the generic
                               tribunal/classe firmware (JURIS_TYPE_PROTOTYPE, compiled host-only, NOT flashed, NOT physically approved).
Both: /99_LEX_V1 by the OFFICIAL staging generator (build_sd_staging, same profile) with RUN11 bytes (CF88_TARGETS may differ from the generator
only in position R); legacy JURISPRUDENCIA.IDX / JUR_LOOKUP.IDX = J2C card bytes + rows APPENDED (card offsets unchanged; a lookup tuple that
already exists gets a second row -> LOOKUP_TUPLE_SHARED, boot-cache sum stays valid); new fichas only for identifiers without a ficha on the
card. Temas 367/387 fichas are NOT touched (UI_IMPROVEMENT_PROPOSAL only). Everything else on the card unchanged.
Proof first: the J2B.1 package builder, re-run at its pinned commit, must reproduce the J2C physical card manifest.
Usage: python build_j2f_candidate.py --commit <sha> [--runs N]
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
sys.path.insert(0, str(HERE))
import build_sd_staging as S  # noqa: E402
import build_j2b_1_candidate  # noqa: E402,F401  (configures build_j2b_candidate for the J2B.1 = J2C card)
import build_j2b_candidate as B  # noqa: E402
import build_j2e_candidate as E2  # noqa: E402  (pinned J2B.1 commit, physical manifest, card package)

ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json'
IDX, LOOKUP, CONTENT = B.IDX, B.LOOKUP, B.CONTENT
PKG_ROOT = HERE / 'J2F_CANDIDATES_HOST_ONLY'
FW = HERE / 'JURIS_TYPE_PROTOTYPE'
V = {'A': dict(dev=ROOT / 'LEGAL_TARGET_ID/derived/export_test/run11_juris_j2f_a_candidate/device_ready', pkg='J2_CURRENT_FW_CANDIDATE',
               out=DI / 'staging_sd_v1_juris_j2f_a_candidate', include=('A',),
               firmware='CURRENT (app aprovado 6e329c91…, gravado no R2; sem mudança)'),
     'B': dict(dev=ROOT / 'LEGAL_TARGET_ID/derived/export_test/run11_juris_j2f_b_candidate/device_ready', pkg='J2_GENERIC_FW_CANDIDATE',
               out=DI / 'staging_sd_v1_juris_j2f_b_candidate', include=('A', 'B'),
               firmware='REQUIRES the generic tribunal/classe firmware (JURIS_TYPE_PROTOTYPE/juris_types.patch; compiled host-only; NOT flashed; '
                        'NOT physically approved)')}
TMP = DI / '_tmp_juris_j2f_rebuild'
TMP_BASE = DI / '_tmp_juris_j2f_physical_reproduction'
R_POS = 4
UNTOUCHABLE = ('STF_RG_367.TXT', 'STF_RG_387.TXT')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def legacy_files(variant):
    card = E2.physical()
    base = {rel: (E2.CARD_PKG / rel).read_bytes() for rel in (IDX, LOOKUP)}
    for rel, b in base.items():
        if hashlib.sha256(b).hexdigest() != card[rel]:
            raise SystemExit(f'LEGACY_BASE_NOT_J2C_CARD {rel}')
    doc = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    idx, lookup = bytearray(base[IDX]), bytearray(base[LOOKUP])
    keys = {l.split(b'|', 1)[0] for l in bytes(idx).split(b'\n') if l}
    looks = {tuple(l.split(b'|')[:5]) for l in bytes(lookup).split(b'\n') if l and not l.startswith(b'#')}
    shared, files = [], {}
    for r in doc['records']:
        if r['group'] not in V[variant]['include']:
            continue
        row = r['legacy_idx_row'].encode('utf-8')
        k = row.split(b'|', 1)[0]
        lk = tuple(x.encode('utf-8') for x in r['legacy_lookup'])
        if k in keys or b'\r' in row or b'\n' in row:
            raise SystemExit(f'LEGACY_KEY_EXISTS {k.decode()}')
        if lk in looks:
            shared.append('|'.join(r['legacy_lookup']))
        offset = len(idx)
        idx += row + b'\n'
        lookup += b'|'.join(lk + (str(offset).encode(), b'1')) + b'\n'
        keys.add(k)
        looks.add(lk)
        if r['new_ficha']:
            rel = f"{CONTENT}/{B.ficha_name(r['new_ficha'])}"
            if rel in card or Path(rel).name in UNTOUCHABLE:
                raise SystemExit(f'FICHA_ALREADY_ON_CARD {rel}')
            files[rel] = doc['fichas'][r['new_ficha']].encode('utf-8')
    files[IDX], files[LOOKUP] = bytes(idx), bytes(lookup)
    return files, shared


def build(out, commit, variant):
    dev = V[variant]['dev']
    targets = (dev / 'CF88_TARGETS.IDX').read_bytes()
    original, record = S.build_targets, {}

    def with_run11_bytes(sd, idx, status, entenda_lookup, ref_lookup):
        stats = original(sd, idx, status, entenda_lookup, ref_lookup)
        p = sd / '10_TARGETS/CF88_TARGETS.IDX'
        gen, cand = p.read_bytes().decode('utf-8').split('\n'), targets.decode('utf-8').split('\n')
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
        p.write_bytes(targets)
        record['r_only'] = r_only
        return stats

    S.build_targets = with_run11_bytes
    try:
        man = S.build(out, ref_dir=dev, require_committed_refs=True, profile=B.PROFILE, build_commit=commit,
                      reference_engine_version=dict(tag=f'cf-reference-engine-run11-juris-j2f-{variant.lower()}', run='run11',
                                                    status=f'RUN11_JURIS_J2F_{variant}_CANDIDATE_HOST_ONLY',
                                                    derived_from='run9 (J2B.1 installed, J2C 12/12, 261/160) + Batch02 (J2E) + Batches 03-09 '
                                                                 'ratified (J2F)'))
    finally:
        S.build_targets = original
    rel_dir = Path(out) / 'SD/99_RELATIONS_V2/05_INDICES_ESP32_V2'
    rel_dir.mkdir(parents=True)
    for name in ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX'):
        (rel_dir / name).write_bytes((dev / name).read_bytes())
    files, shared = legacy_files(variant)
    for rel, b in files.items():
        p = Path(out) / 'SD' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    record['shared'] = shared
    return man, record


def package(variant, commit, runs, reproduced_files):
    cfg = V[variant]
    man, rec = build(cfg['out'], commit, variant)
    trees = [B.tree(cfg['out'] / 'SD')]
    try:
        for _ in range(runs - 1):
            build(TMP, commit, variant)
            trees.append(B.tree(TMP / 'SD'))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    if not all(t == trees[0] for t in trees):
        raise SystemExit('STAGING_NOT_DETERMINISTIC')
    card = E2.physical()
    added = tuple(sorted(k for k in trees[0] if k not in card))
    changed = tuple(sorted(k for k in trees[0] if k in card and trees[0][k] != card[k]))
    expected_changed = (IDX, LOOKUP, '99_LEX_V1/00_SYS/LEXV1.VER', '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX',
                        '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')
    if changed != tuple(sorted(expected_changed)) or not all(k.startswith(CONTENT + '/') for k in added):
        raise SystemExit(f'UNEXPECTED_DIFF_VS_PHYSICAL {changed} {added}')
    for name, rel in (('REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'), ('REF_PAYLOAD.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'),
                      ('CF88_TARGETS.IDX', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX')):
        if trees[0][rel] != sha(cfg['dev'] / name):
            raise SystemExit(f'STAGING_NOT_RUN11 {rel}')
    for rel in (IDX, LOOKUP):
        if not (cfg['out'] / 'SD' / rel).read_bytes().startswith((E2.CARD_PKG / rel).read_bytes()):
            raise SystemExit(f'LEGACY_NOT_APPEND_ONLY {rel}')
    m = json.loads((cfg['out'] / 'SD/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
    man_ok = all(trees[0].get(k) == v['sha256'] for k, v in m['files'].items() if k != '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json')
    pkg = PKG_ROOT / cfg['pkg']
    if pkg.exists():
        shutil.rmtree(pkg)
    B.build(TMP_BASE, E2.J2B1_COMMIT)                 # rollback bytes = J2C card (reproduced and checked against the card manifest)
    try:
        for rel in changed + added:
            dst = pkg / 'candidate/SD' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((cfg['out'] / 'SD' / rel).read_bytes())
        for rel in changed:
            dst = pkg / 'rollback/SD' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((TMP_BASE / 'SD' / rel).read_bytes())
    finally:
        shutil.rmtree(TMP_BASE, ignore_errors=True)
    for rel in changed:
        if sha(pkg / 'rollback/SD' / rel) != card[rel]:
            raise SystemExit(f'ROLLBACK_NOT_PHYSICAL {rel}')
    fw = None
    if variant == 'B':
        (pkg / 'firmware').mkdir(parents=True)
        for name in ('juris_types.patch', 'JURIS_TYPE_PROTOTYPE_BUILD.json'):
            (pkg / 'firmware' / name).write_bytes((FW / name).read_bytes().replace(b'\r\n', b'\n'))
        fw = dict(patch='firmware/juris_types.patch', build='firmware/JURIS_TYPE_PROTOTYPE_BUILD.json', flashed=False, physical_approved=False,
                  binary='DEVICE_INTEGRATION/backups/juris_type_prototype/build_types (fora do Git; não gravado)')
    report = dict(profile=B.PROFILE, package=cfg['pkg'], variant=variant, status='HOST_ONLY_CANDIDATE', physical_approved=False,
                  card_touched=False, device_flashed=False, firmware=cfg['firmware'], firmware_files=fw,
                  staging=cfg['out'].relative_to(ROOT).as_posix(), build_id=man['build_id'], git_commit=man['git_commit'],
                  physical_baseline='J2C 261/160 (J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json; J2_BASELINE_RECONCILIATION.json)',
                  physical_baseline_reproduced=True, physical_files_reproduced=reproduced_files, deterministic_runs=runs, byte_identical_rebuild=True,
                  legacy_append_only=True, lookup_tuples_shared=rec['shared'], targets_r_only_divergence_vs_generator=rec['r_only'],
                  device_manifest_matches_package=man_ok, temas_367_387_fichas_untouched=not any(Path(k).name in UNTOUCHABLE for k in changed + added),
                  changed_vs_physical=list(changed), added_vs_physical=list(added),
                  file_diff=[dict(path='/' + r, before_sha256=card[r], before_bytes=(pkg / 'rollback/SD' / r).stat().st_size, after_sha256=trees[0][r],
                                  after_bytes=(pkg / 'candidate/SD' / r).stat().st_size) for r in changed],
                  file_additions=[dict(path='/' + r, after_sha256=trees[0][r], after_bytes=(pkg / 'candidate/SD' / r).stat().st_size,
                                       rollback='DELETE') for r in added],
                  files=[dict(path='/' + k, sha256=v, same_as_physical=card.get(k) == v) for k, v in trees[0].items()])
    (pkg / 'J2F_PACKAGE_MANIFEST.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return {k: v for k, v in report.items() if k not in ('files', 'file_diff', 'file_additions')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', required=True)
    ap.add_argument('--runs', type=int, default=2)
    a = ap.parse_args()
    ok, n = E2.physical_reproduced()
    if not ok:
        raise SystemExit('PHYSICAL_BASELINE_NOT_REPRODUCED')
    out = {v: package(v, a.commit, a.runs, n) for v in ('A', 'B')}
    print(json.dumps({v: {k: o[k] for k in ('package', 'build_id', 'changed_vs_physical', 'lookup_tuples_shared')} | dict(added=len(o['added_vs_physical']))
                      for v, o in out.items()}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
