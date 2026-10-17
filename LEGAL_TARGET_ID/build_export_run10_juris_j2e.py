"""Reference Engine RUN10_JURIS_J2E (variants A and B), HOST-ONLY: RUN9 (installed, J2C 12/12) plus the BATCH02 links ratified by the user
(J2D ratified 2026-10-17). Variant A = links the current firmware shows correctly (7). Variant B = A + HC 232627 (requires a firmware
candidate with a native HC type). NOT a baseline, NOT physical, NOT deployed. Inputs are only read:
  base       derived/export_test/run9_juris_j2b_1_candidate/device_ready (checked against SHA256SUMS and the installed J2B.1 package bytes)
  additions  derived/CF88_JURIS_ADDITIONS_J2E.json
Rules: RUN9 re-exported byte-identically first; RUN10 = RUN9 + additions of the variant (nothing removed); each link validated by
reference_engine.validate_link and CURRENT_VISIBLE; CF88_TARGETS: only position [2] (J) recomputed; CORRELATA files byte copies.
Deterministic.   Usage: python build_export_run10_juris_j2e.py --variant A|B [--out DIR]
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

D = HERE / 'derived'
NORM = 'CF88'
RUN9 = D / 'export_test/run9_juris_j2b_1_candidate'
RUN9_DEV = RUN9 / 'device_ready'
INSTALLED = ROOT / 'JURISPRUDENCE_AUDIT/J2B_1_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
ADDITIONS = D / 'CF88_JURIS_ADDITIONS_J2E.json'
DECISIONS = ROOT / 'JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json'
OUT = {'A': D / 'export_test/run10_juris_j2e_a_candidate', 'B': D / 'export_test/run10_juris_j2e_b_candidate'}
STATUS = 'RUN10_JURIS_J2E_{}_CANDIDATE_HOST_ONLY'
VARIANTS = {'A': ('A',), 'B': ('A', 'B')}


class Run10Error(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def run9_inputs():
    sums = dict(reversed(l.split('  ', 1)) for l in (RUN9 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if l)
    out = {}
    for p in sorted(RUN9_DEV.iterdir()):
        b = p.read_bytes()
        if sha(b) != sums.get(f'device_ready/{p.name}'):
            raise Run10Error('RUN9_SHA256SUMS_MISMATCH', p.name)
        if p.name in R6.APPROVED_MAP and b != (INSTALLED / R6.APPROVED_MAP[p.name]).read_bytes():
            raise Run10Error('RUN9_NOT_INSTALLED_BYTES', p.name)
        out[p.name] = b
    return out


def adi_links(reg, doc, sources, variant):
    links = []
    for r in doc['records']:
        if r['variant'] not in VARIANTS[variant]:
            continue
        status = reg.status(NORM, r['target_id'])
        link = dict(norma_id=NORM, target_id=r['target_id'], reference_id=f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}",
                    reference_type='JURISPRUDENCE', source_id=r['source_id'], source_reference_id=r['source_reference_id'],
                    provenance=dict(system='J2E (J2D BATCH02, ratificado por Arthur em 2026-10-17)', tribunal='STF', tipo=r['payload']['tipo'],
                                    numero=r['payload']['numero'], ratified_decisions=r['ratified_decisions'], ratification=r['ratification'],
                                    joint=r['joint'], joint_with=r['joint_with'], temporal_version=r['temporal_version'],
                                    variant=r['variant'], requires_firmware=r['requires_firmware'],
                                    sources=[dict(id=s, url=sources[s]['url'], sha256=sources[s].get('dom_text_sha256') or sources[s].get('snapshot_sha256'))
                                             for s in r['sources']]),
                    status=status, visibility=E._visibility(reg.cfg, status), label=E._clean(r['label']), payload=r['payload'],
                    migration='ADDED_J2E', validation_status='VALIDATED', routes=[], duplicate_class='DISTINCT')
        E.validate_link(link, reg)
        if link['visibility'] != 'CURRENT_VISIBLE':
            raise Run10Error('ADI_LINK_NOT_VISIBLE', link['reference_id'])
        links.append(link)
    return links


def build(out, variant):
    out = Path(out)
    base = run9_inputs()
    reg = E.TargetRegistry()
    E.build_links(NORM, reg)
    key = R6.sort_key(reg)
    run9_doc = json.loads(base['CF88_REFERENCES_EXPORT.json'].decode('utf-8'))
    added = load(R6.EFFECTIVE_ADDITIONS)['records']
    excluded9 = run9_doc['excluded_links']
    run9_links = sorted(R6.flat(run9_doc), key=key)
    with tempfile.TemporaryDirectory() as t:                     # fidelity proof
        E.export(NORM, run9_links, t, excluded9, added)
        for name in ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            if (Path(t) / name).read_bytes() != base[name]:
                raise Run10Error('RUN9_NOT_REPRODUCED', name)
    new = adi_links(reg, load(ADDITIONS), load(DECISIONS)['sources'], variant)
    have = {l['reference_id'] for l in run9_links}
    pairs = {(l['target_id'], l['source_id']) for l in run9_links}
    for l in new:
        if l['reference_id'] in have or (l['target_id'], l['source_id']) in pairs:
            raise Run10Error('ADI_LINK_ALREADY_PRESENT', l['reference_id'])
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
    jv = lambda ls: [l for l in ls if l['reference_type'] == 'JURISPRUDENCE' and l['visibility'] == 'CURRENT_VISIBLE']  # noqa: E731
    summary = dict(status=STATUS.format(variant), variant=variant, base='RUN9 device_ready == candidato J2B.1 instalado (J2C 12/12)', run9_reproduced=True,
                   removed_links=[], added_links=sorted(l['reference_id'] for l in new),
                   links_by_type=dict(run9=by_type(run9_links), run10=by_type(links)),
                   jurisprudence=dict(relations_before=len(jv(run9_links)), relations_after=len(jv(links)),
                                      targets_before=len(vis(run9_links, 'JURISPRUDENCE')), targets_after=len(vis(links, 'JURISPRUDENCE'))),
                   target_flag_changes=j_changes, untouched_files=list(R6.COPIED),
                   files={**files, **{n: dict(sha256=sha((dev / n).read_bytes()), bytes=(dev / n).stat().st_size) for n in ('CF88_TARGETS.IDX',) + R6.COPIED}})
    (out / 'RUN10_SUMMARY.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    sums = sorted((p.relative_to(out).as_posix(), sha(p.read_bytes())) for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (out / 'SHA256SUMS.txt').write_bytes(''.join(f'{h}  {n}\n' for n, h in sums).encode('utf-8'))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', choices=('A', 'B'), required=True)
    ap.add_argument('--out')
    a = ap.parse_args()
    s = build(a.out or OUT[a.variant], a.variant)
    print(json.dumps({k: s[k] for k in ('added_links', 'jurisprudence', 'target_flag_changes')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
