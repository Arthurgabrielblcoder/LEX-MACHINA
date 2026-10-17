"""Reference Engine RUN11_JURIS_J2F (variants A and B), HOST-ONLY: RUN9 (installed, J2C 12/12 = PHYSICAL_BASELINE 261/160) plus the RATIFIED
jurisprudence relations of Batch02 (J2E) and Batches 03–09 (J2F, ratified 2026-10-17). Variant A = group A only (types the CURRENT firmware
shows correctly: RG, SV, ADI). Variant B = A + group B (HC, MS, AP, AI, Inq, Rcl, ADPF, súmula comum, TSE…; requires the generic
tribunal/classe firmware). NOT a baseline, NOT physical, NOT deployed. Inputs are only read:
  base       derived/export_test/run9_juris_j2b_1_candidate/device_ready (checked against SHA256SUMS and the installed J2B.1 package bytes)
  additions  derived/CF88_JURIS_ADDITIONS_J2F.json (includes the J2E records)
Rules (same as RUN10): RUN9 re-exported byte-identically first; RUN11 = RUN9 + additions of the variant (nothing removed); each link validated by
reference_engine.validate_link and CURRENT_VISIBLE; CF88_TARGETS: only position [2] (J) recomputed; CORRELATA files byte copies. Deterministic.
Usage: python build_export_run11_juris_j2f.py --variant A|B [--out DIR]
"""
import argparse
import collections
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import reference_engine as E  # noqa: E402
import build_export_run6_juris_j1 as R6  # noqa: E402
import build_export_run10_juris_j2e as R10  # noqa: E402  (RUN9 input checks)

D = HERE / 'derived'
NORM = 'CF88'
ADDITIONS = D / 'CF88_JURIS_ADDITIONS_J2F.json'
OUT = {'A': D / 'export_test/run11_juris_j2f_a_candidate', 'B': D / 'export_test/run11_juris_j2f_b_candidate'}
STATUS = 'RUN11_JURIS_J2F_{}_CANDIDATE_HOST_ONLY'
VARIANTS = {'A': ('A',), 'B': ('A', 'B')}
PHYSICAL_BASELINE = (261, 160)


class Run11Error(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def links_for(reg, doc, variant):
    links = []
    for r in doc['records']:
        if r['group'] not in VARIANTS[variant]:
            continue
        status = reg.status(NORM, r['target_id'])
        if r['origin'] == 'J2E':
            prov = dict(system='J2E (J2D BATCH02, ratificado por Arthur em 2026-10-17)', ratified_decisions=r['ratified_decisions'],
                        ratification=r['ratification'], joint=r['joint'], joint_with=r['joint_with'], requires_firmware=r['requires_firmware'])
        else:
            prov = dict(system='J2F (Batches 03–09, ratificados por Arthur em 2026-10-17)', ratified_decisions=r['ratified_decisions'],
                        batches=r['batches'], members=r['members'], provisional=r['provisional'], sources=r['sources'])
        prov.update(tribunal=r['payload']['tribunal'], tipo=r['payload']['tipo'], numero=r['payload']['numero'], group=r['group'],
                    temporal_version=r['temporal_version'])
        link = dict(norma_id=NORM, target_id=r['target_id'], reference_id=f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}",
                    reference_type='JURISPRUDENCE', source_id=r['source_id'], source_reference_id=r['source_reference_id'], provenance=prov,
                    status=status, visibility=E._visibility(reg.cfg, status), label=E._clean(r['label']), payload=r['payload'],
                    migration=f"ADDED_{r['origin']}", validation_status='VALIDATED', routes=[], duplicate_class='DISTINCT')
        E.validate_link(link, reg)
        if link['visibility'] != 'CURRENT_VISIBLE':
            raise Run11Error('LINK_NOT_VISIBLE', link['reference_id'])
        links.append(link)
    return links


def build(out, variant):
    out = Path(out)
    base = R10.run9_inputs()
    reg = E.TargetRegistry()
    E.build_links(NORM, reg)
    key = R6.sort_key(reg)
    run9_doc = json.loads(base['CF88_REFERENCES_EXPORT.json'].decode('utf-8'))
    added = json.loads(R6.EFFECTIVE_ADDITIONS.read_text(encoding='utf-8'))['records']
    excluded9 = run9_doc['excluded_links']
    run9_links = sorted(R6.flat(run9_doc), key=key)
    jv = lambda ls: [l for l in ls if l['reference_type'] == 'JURISPRUDENCE' and l['visibility'] == 'CURRENT_VISIBLE']  # noqa: E731
    if (len(jv(run9_links)), len({l['target_id'] for l in jv(run9_links)})) != PHYSICAL_BASELINE:
        raise Run11Error('BASE_IS_NOT_PHYSICAL_BASELINE_261_160')
    with tempfile.TemporaryDirectory() as t:                     # fidelity proof
        E.export(NORM, run9_links, t, excluded9, added)
        for name in ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            if (Path(t) / name).read_bytes() != base[name]:
                raise Run11Error('RUN9_NOT_REPRODUCED', name)
    doc = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    new = links_for(reg, doc, variant)
    have = {l['reference_id'] for l in run9_links}
    pairs = {(l['target_id'], l['source_id']) for l in run9_links}
    seen = set()
    for l in new:
        if l['reference_id'] in have or (l['target_id'], l['source_id']) in pairs or l['reference_id'] in seen:
            raise Run11Error('LINK_ALREADY_PRESENT', l['reference_id'])
        seen.add(l['reference_id'])
    links = sorted(run9_links + new, key=key)
    dev = out / 'device_ready'
    files = E.export(NORM, links, dev, excluded9, added)
    vis = lambda ls, t: {l['target_id'] for l in ls if l['reference_type'] == t and l['visibility'] == 'CURRENT_VISIBLE'}  # noqa: E731
    targets_b, j_changes = R6.retarget_j_flags(base['CF88_TARGETS.IDX'], vis(links, 'JURISPRUDENCE'))
    (dev / 'CF88_TARGETS.IDX').write_bytes(targets_b)
    for name in R6.COPIED:
        (dev / name).write_bytes(base[name])

    def by_type(ls):
        return dict(sorted(collections.Counter(f"{l['reference_type']}|{l['visibility']}" for l in ls).items()))
    j2e = [l for l in new if l['migration'] == 'ADDED_J2E']
    j2f = [l for l in new if l['migration'] == 'ADDED_J2F']
    summary = dict(status=STATUS.format(variant), variant=variant, groups=list(VARIANTS[variant]),
                   base='RUN9 device_ready == candidato J2B.1 instalado (J2C 12/12); PHYSICAL_BASELINE 261/160', run9_reproduced=True,
                   removed_links=[], added_links=sorted(l['reference_id'] for l in new),
                   added_by_origin=dict(J2E_BATCH02=len(j2e), J2F_BATCHES_03_09=len(j2f)),
                   links_by_type=dict(run9=by_type(run9_links), run11=by_type(links)),
                   jurisprudence=dict(relations_before=len(jv(run9_links)), relations_after=len(jv(links)),
                                      targets_before=len(vis(run9_links, 'JURISPRUDENCE')), targets_after=len(vis(links, 'JURISPRUDENCE')),
                                      new_targets_with_j=sorted(vis(links, 'JURISPRUDENCE') - vis(run9_links, 'JURISPRUDENCE')),
                                      new_targets_with_j_from_j2f=sorted({l['target_id'] for l in j2f} - vis(run9_links + j2e, 'JURISPRUDENCE'))),
                   target_flag_changes=j_changes, untouched_files=list(R6.COPIED),
                   files={**files, **{n: dict(sha256=sha((dev / n).read_bytes()), bytes=(dev / n).stat().st_size) for n in ('CF88_TARGETS.IDX',) + R6.COPIED}})
    (out / 'RUN11_SUMMARY.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    sums = sorted((p.relative_to(out).as_posix(), sha(p.read_bytes())) for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (out / 'SHA256SUMS.txt').write_bytes(''.join(f'{h}  {n}\n' for n, h in sums).encode('utf-8'))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', choices=('A', 'B'), required=True)
    ap.add_argument('--out')
    a = ap.parse_args()
    s = build(a.out or OUT[a.variant], a.variant)
    print(json.dumps({k: s[k] for k in ('added_by_origin', 'jurisprudence')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
