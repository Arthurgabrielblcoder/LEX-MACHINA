"""Reference Engine RUN8_JURIS_J2B_CANDIDATE_HOST_ONLY: RUN7 (installed, J1.5 11/11) plus the 5 ADI links of J2A BATCH01 ratified by the user
(6 decisions; ADI 7047/7064 = one joint-judgment record). NOT a baseline, NOT physical, NOT deployed. Inputs are only read:
  base       derived/export_test/run7_juris_j1_4_candidate/device_ready (checked against SHA256SUMS and the installed J1.4 package bytes)
  additions  derived/CF88_JURIS_ADI_ADDITIONS_J2B.json (JURISPRUDENCE links of type adi; legacy key = source_reference_id)
Rules: RUN7 re-exported byte-identically first; RUN8 = RUN7 + 5 (nothing removed, nothing else changed); each link validated by
reference_engine.validate_link and must be CURRENT_VISIBLE; CF88_TARGETS: only position [2] (J) recomputed; CORRELATA files byte copies.
Deterministic.   Usage: python build_export_run8_juris_j2b.py [--out DIR]
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
RUN7 = D / 'export_test/run7_juris_j1_4_candidate'
RUN7_DEV = RUN7 / 'device_ready'
INSTALLED = ROOT / 'JURISPRUDENCE_AUDIT/J1_4_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
ADDITIONS = D / 'CF88_JURIS_ADI_ADDITIONS_J2B.json'
DECISIONS = ROOT / 'JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json'
OUT = D / 'export_test/run8_juris_j2b_candidate'
STATUS = 'RUN8_JURIS_J2B_CANDIDATE_HOST_ONLY'


class Run8Error(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def run7_inputs():
    sums = dict(reversed(l.split('  ', 1)) for l in (RUN7 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if l)
    out = {}
    for p in sorted(RUN7_DEV.iterdir()):
        b = p.read_bytes()
        if sha(b) != sums.get(f'device_ready/{p.name}'):
            raise Run8Error('RUN7_SHA256SUMS_MISMATCH', p.name)
        if p.name in R6.APPROVED_MAP and b != (INSTALLED / R6.APPROVED_MAP[p.name]).read_bytes():
            raise Run8Error('RUN7_NOT_INSTALLED_BYTES', p.name)
        out[p.name] = b
    return out


def adi_links(reg, doc, sources):
    links = []
    for r in doc['records']:
        status = reg.status(NORM, r['target_id'])
        link = dict(norma_id=NORM, target_id=r['target_id'], reference_id=f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}",
                    reference_type='JURISPRUDENCE', source_id=r['source_id'], source_reference_id=r['source_reference_id'],
                    provenance=dict(system='J2B (J2A BATCH01, ratificado por Arthur em 2026-10-16)', tribunal='STF', tipo='adi',
                                    numero=r['payload']['numero'], aliases=r['aliases'], status_processual=r['status_processual'],
                                    provisional=r['provisional'], ratified_decisions=r['ratified_decisions'], ratification=r['ratification'],
                                    joint_judgment=r['joint_judgment'],
                                    sources=[dict(id=s, url=sources[s]['url'], sha256=sources[s].get('dom_text_sha256') or sources[s].get('snapshot_sha256'))
                                             for s in r['sources']],
                                    revalidation='JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2B_REVALIDATION_REGISTRY.json' if r['provisional'] else None),
                    status=status, visibility=E._visibility(reg.cfg, status), label=E._clean(r['label']), payload=r['payload'],
                    migration='ADDED_J2B', validation_status='VALIDATED', routes=[], duplicate_class='DISTINCT')
        E.validate_link(link, reg)
        if link['visibility'] != 'CURRENT_VISIBLE':
            raise Run8Error('ADI_LINK_NOT_VISIBLE', link['reference_id'])
        links.append(link)
    return links


def build(out):
    out = Path(out)
    base = run7_inputs()
    reg = E.TargetRegistry()
    E.build_links(NORM, reg)
    key = R6.sort_key(reg)
    run7_doc = json.loads(base['CF88_REFERENCES_EXPORT.json'].decode('utf-8'))
    added = load(R6.EFFECTIVE_ADDITIONS)['records']
    excluded7 = run7_doc['excluded_links']
    run7_links = sorted(R6.flat(run7_doc), key=key)
    with tempfile.TemporaryDirectory() as t:                     # fidelity proof
        E.export(NORM, run7_links, t, excluded7, added)
        for name in ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            if (Path(t) / name).read_bytes() != base[name]:
                raise Run8Error('RUN7_NOT_REPRODUCED', name)
    new = adi_links(reg, load(ADDITIONS), load(DECISIONS)['sources'])
    have = {l['reference_id'] for l in run7_links}
    pairs = {(l['target_id'], l['source_id']) for l in run7_links}
    for l in new:
        if l['reference_id'] in have or (l['target_id'], l['source_id']) in pairs:
            raise Run8Error('ADI_LINK_ALREADY_PRESENT', l['reference_id'])
    links = sorted(run7_links + new, key=key)
    dev = out / 'device_ready'
    files = E.export(NORM, links, dev, excluded7, added)
    vis = lambda ls, t: {l['target_id'] for l in ls if l['reference_type'] == t and l['visibility'] == 'CURRENT_VISIBLE'}  # noqa: E731
    targets_b, j_changes = R6.retarget_j_flags(base['CF88_TARGETS.IDX'], vis(links, 'JURISPRUDENCE'))
    (dev / 'CF88_TARGETS.IDX').write_bytes(targets_b)
    for name in R6.COPIED:
        (dev / name).write_bytes(base[name])

    def by_type(ls):
        return dict(sorted(collections.Counter(f"{l['reference_type']}|{l['visibility']}" for l in ls).items()))
    jv = lambda ls: [l for l in ls if l['reference_type'] == 'JURISPRUDENCE' and l['visibility'] == 'CURRENT_VISIBLE']  # noqa: E731
    summary = dict(status=STATUS, base='RUN7 device_ready == candidato J1.4 instalado e validado fisicamente (J1.5 11/11)', run7_reproduced=True,
                   removed_links=[], added_links=sorted(l['reference_id'] for l in new),
                   links_by_type=dict(run7=by_type(run7_links), run8=by_type(links)),
                   jurisprudence=dict(relations_before=len(jv(run7_links)), relations_after=len(jv(links)),
                                      targets_before=len(vis(run7_links, 'JURISPRUDENCE')), targets_after=len(vis(links, 'JURISPRUDENCE'))),
                   target_flag_changes=j_changes, untouched_files=list(R6.COPIED),
                   files={**files, **{n: dict(sha256=sha((dev / n).read_bytes()), bytes=(dev / n).stat().st_size) for n in ('CF88_TARGETS.IDX',) + R6.COPIED}})
    (out / 'RUN8_SUMMARY.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    sums = sorted((p.relative_to(out).as_posix(), sha(p.read_bytes())) for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (out / 'SHA256SUMS.txt').write_bytes(''.join(f'{h}  {n}\n' for n, h in sums).encode('utf-8'))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    s = build(ap.parse_args().out)
    print(json.dumps({k: s[k] for k in ('added_links', 'jurisprudence', 'target_flag_changes')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
