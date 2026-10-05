"""ENTENDA Batch05 HOST candidate (CF88 arts. 37-41): never deployable, never written to a removable volume.

The approved package selection (build_sd_staging.approved_entenda: Batches 01-04 + 9 pilots, 220 HUMAN_APPROVED_T1) is reused as is;
the 69 Batch05 explanations are added either all PENDING_HUMAN_REVIEW (draft set) or all HUMAN_APPROVED_T1 (after the human rounds).
The candidate is host-only (never written to a removable volume); physical staging is a separate, explicitly authorized step.
Checks: 3 builds BYTE_IDENTICAL; every approved explanation keeps the same payload block and the same lookup row (except OFFSET) as the
physically approved ENTENDA pair; only Batch05 targets are added; no approved target is removed.
Usage: python build_entenda_batch05_candidate.py
"""
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
ROOT = DI.parent
sys.path.insert(0, str(HERE))
import build_sd_staging as S  # noqa: E402

E = S.E
OUT = DI / 'staging_entenda_batch05_candidate'
BD = ROOT / 'ENTENDA_ENGINE/derived/production_batch_05'
APPROVED = DI / 'staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/30_ENTENDA'
APPROVED_BATCHES = S.BATCHES + ('production_batch_04',)
EXPECTED_APPROVED, EXPECTED_NEW = 220, 69


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rows():
    ctx = E.NormContext('CF88')
    approved = S.approved_entenda(ctx, APPROVED_BATCHES, EXPECTED_APPROVED, 36)
    spec = json.loads((BD / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
    new = [r for r in E.load_corpus(BD / spec['batch_corpus']) if r['status'] == 'ACTIVE']
    states = {r['review_status'] for r in new}
    if len(new) != EXPECTED_NEW or states not in ({'PENDING_HUMAN_REVIEW'}, {'HUMAN_APPROVED_T1'}):
        raise SystemExit(f'BATCH05_MIXED_OR_INCOMPLETE {len(new)} {sorted(states)}')
    if {r['target_id'] for r in new} & {r['target_id'] for r in approved}:
        raise SystemExit('BATCH05_DUPLICATES_APPROVED_TARGET')
    return ctx, approved, new


def build_once(ctx, corpus, out):
    out.mkdir(parents=True, exist_ok=True)
    return E.build_entenda_index(ctx, corpus, out)


def blocks(d):
    lk = [l.split('|') for l in (d / 'ENTENDA_LOOKUP.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    pl = (d / 'ENTENDA_PAYLOAD.DAT').read_bytes()
    return {r[0]: dict(row=r[2:], block=pl[int(r[1]):int(r[1]) + int(r[2])]) for r in lk}


def main():
    ctx, approved, new = rows()
    corpus = approved + new
    builds = []
    with tempfile.TemporaryDirectory() as t:
        for k in range(3):
            d = Path(t) / f'b{k}'
            build_once(ctx, corpus, d)
            builds.append({n: (d / n).read_bytes() for n in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT', 'ENTENDA_BUILD_MANIFEST.json')})
    identical = builds[0] == builds[1] == builds[2]
    if not identical:
        raise SystemExit('ENTENDA_CANDIDATE_NOT_DETERMINISTIC')
    if OUT.exists():
        shutil.rmtree(OUT)
    sd = OUT / 'SD/99_LEX_V1/30_ENTENDA'
    host = OUT / '_host'
    sd.mkdir(parents=True)
    host.mkdir(parents=True)
    for n in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT'):
        (sd / n).write_bytes(builds[0][n])
    (host / 'ENTENDA_BUILD_MANIFEST.json').write_bytes(builds[0]['ENTENDA_BUILD_MANIFEST.json'])
    old, cand = blocks(APPROVED), blocks(sd)
    removed = sorted(set(old) - set(cand))
    changed = sorted(t for t in old if t in cand and (old[t]['row'] != cand[t]['row'] or old[t]['block'] != cand[t]['block']))
    added = sorted(set(cand) - set(old))
    new_targets = {r['target_id'] for r in new} | {c for r in new for c in r['granularity'].get('covered_targets', [])}
    ok = not removed and not changed and set(added) == new_targets
    review = {}
    for t in cand.values():
        review[t['row'][4]] = review.get(t['row'][4], 0) + 1
    all_approved = all(r['review_status'] == 'HUMAN_APPROVED_T1' for r in new)
    status = dict(
        schema_version=1, candidate='ENTENDA_CF_PRODUCTION_BATCH_05',
        status='HOST_CANDIDATE_ALL_APPROVED_NOT_STAGED' if all_approved else 'HOST_CANDIDATE_NOT_DEPLOYABLE',
        reason=('69 explicacoes HUMAN_APPROVED_T1; candidato apenas no host: staging fisico e teste fisico dependem de autorizacao explicita'
                if all_approved else '69 explicacoes PENDING_HUMAN_REVIEW; o builder fisico (build_sd_staging) recusa explicacoes nao aprovadas'),
        explanations=dict(approved_reused=len(approved), **({'batch05_approved': len(new)} if all_approved else {'batch05_pending': len(new)}),
                          total=len(corpus), total_human_approved_t1=sum(1 for r in corpus if r['review_status'] == 'HUMAN_APPROVED_T1')),
        lookup_rows=len(cand), lookup_rows_by_review=dict(sorted(review.items())),
        approved_pair=dict(path=APPROVED.relative_to(ROOT).as_posix(),
                           lookup_sha256=sha((APPROVED / 'ENTENDA_LOOKUP.IDX').read_bytes()),
                           payload_sha256=sha((APPROVED / 'ENTENDA_PAYLOAD.DAT').read_bytes()), lookup_rows=len(old)),
        candidate_pair={n: dict(bytes=len(builds[0][n]), sha256=sha(builds[0][n])) for n in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT')},
        rebuilds=3, byte_identical=identical,
        diff_vs_approved=dict(removed=removed, changed_except_offset=changed, added=len(added), added_equals_batch05_targets=set(added) == new_targets),
        preservation_ok=ok)
    (host / 'CANDIDATE_STATUS.json').write_bytes((json.dumps(status, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps(status, ensure_ascii=False, indent=1))
    if not ok:
        raise SystemExit('APPROVED_ENTENDA_NOT_PRESERVED')


if __name__ == '__main__':
    main()
