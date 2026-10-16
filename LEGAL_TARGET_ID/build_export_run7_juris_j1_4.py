"""Reference Engine RUN7_JURIS_J1_4_CANDIDATE_HOST_ONLY: RUN6 (installed and physically validated in J1.2) minus the 4 jurisprudence links
attached to a target whose current wording is not the one the precedent interprets, plus their 3 relocations (J1.3 decisions ratified in J1.4).

NOT a baseline, NOT physical, NOT deployed. Inputs are only read:
  base         derived/export_test/run6_juris_j1_candidate/device_ready (checked against SHA256SUMS and the installed J1.1 package bytes)
  exclusions   derived/CF88_LINK_EXCLUSIONS_J1_4.json (validated by reference_engine.link_exclusions; each record = exactly one built link)
  relocations  derived/CF88_JURIS_RELOCATIONS_J1_4.json (same precedent, same link key -> device opens the same thesis; new target; temporal note)
Rules: RUN6 re-exported byte-identically first; RUN7 = RUN6 - 4 + 3 (all JURISPRUDENCE); every relocated link is a copy of the removed link with
only target/reference_id/status/visibility/migration and the temporal note changed, validated by reference_engine.validate_link; CF88_TARGETS:
only position [2] (J) recomputed; CORRELATA files byte copies. Deterministic.   Usage: python build_export_run7_juris_j1_4.py [--out DIR]
"""
import argparse
import collections
import copy
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
RUN6 = D / 'export_test/run6_juris_j1_candidate'
RUN6_DEV = RUN6 / 'device_ready'
INSTALLED = ROOT / 'JURISPRUDENCE_AUDIT/J1_1_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
INSTALLED_MAP = R6.APPROVED_MAP
EFFECTIVE_ADDITIONS = R6.EFFECTIVE_ADDITIONS
EXCLUSIONS = 'derived/CF88_LINK_EXCLUSIONS_J1_4.json'
RELOCATIONS = D / 'CF88_JURIS_RELOCATIONS_J1_4.json'
OUT = D / 'export_test/run7_juris_j1_4_candidate'
STATUS = 'RUN7_JURIS_J1_4_CANDIDATE_HOST_ONLY'
COPIED = R6.COPIED


class Run7Error(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def run6_inputs():
    sums = dict(reversed(l.split('  ', 1)) for l in (RUN6 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if l)
    out = {}
    for p in sorted(RUN6_DEV.iterdir()):
        b = p.read_bytes()
        if sha(b) != sums.get(f'device_ready/{p.name}'):
            raise Run7Error('RUN6_SHA256SUMS_MISMATCH', p.name)
        if p.name in INSTALLED_MAP and b != (INSTALLED / INSTALLED_MAP[p.name]).read_bytes():
            raise Run7Error('RUN6_NOT_INSTALLED_BYTES', p.name)
        out[p.name] = b
    return out


def build(out):
    out = Path(out)
    base = run6_inputs()
    reg = E.TargetRegistry()
    E.build_links(NORM, reg)
    key = R6.sort_key(reg)
    run6_doc = json.loads(base['CF88_REFERENCES_EXPORT.json'].decode('utf-8'))
    added = load(EFFECTIVE_ADDITIONS)['records']
    excluded6 = run6_doc['excluded_links']
    run6_links = sorted(R6.flat(run6_doc), key=key)
    with tempfile.TemporaryDirectory() as t:                     # fidelity proof
        E.export(NORM, run6_links, t, excluded6, added)
        for name in ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            if (Path(t) / name).read_bytes() != base[name]:
                raise Run7Error('RUN6_NOT_REPRODUCED', name)
    clone = E._without(reg, NORM)
    clone.cfg['norms'][NORM]['link_exclusions'] = EXCLUSIONS
    excl = E.link_exclusions(NORM, clone)
    by_id = {l['reference_id']: l for l in run6_links}
    for r in excl:
        l = by_id.get(r['reference_id'])
        if not l or l['reference_type'] != 'JURISPRUDENCE' or l['visibility'] != 'CURRENT_VISIBLE':
            raise Run7Error('EXCLUSION_NOT_A_VISIBLE_RUN6_JURIS_LINK', r['reference_id'])
    gone = {r['reference_id'] for r in excl}
    kept = [l for l in run6_links if l['reference_id'] not in gone]
    pairs = {(l['target_id'], l['source_id']) for l in kept}
    new = []
    relocs = load(RELOCATIONS)['records']
    covered = sorted(r for x in relocs for r in x['relocated_from'])
    if covered != sorted(gone):
        raise Run7Error('RELOCATIONS_DO_NOT_MATCH_EXCLUSIONS')
    for x in relocs:
        src = by_id[x['relocated_from'][0]]
        if src['source_reference_id'] != x['source_reference_id'] or src['source_id'] != x['source_id']:
            raise Run7Error('RELOCATION_SOURCE_MISMATCH', x['relocation_id'])
        if (x['target_id'], x['source_id']) in pairs:
            raise Run7Error('RELOCATION_DUPLICATES_EXISTING_LINK', x['relocation_id'])
        l = copy.deepcopy(src)
        status = reg.status(NORM, x['target_id'])
        l.update(target_id=x['target_id'], reference_id=x['reference_id'], status=status, visibility=E._visibility(reg.cfg, status),
                 migration='RELOCATED_J1_4', routes=[], duplicate_class='DISTINCT')
        l['provenance'] = dict(src['provenance'], relocation=dict(relocation_id=x['relocation_id'], relocated_from=x['relocated_from'],
                                                                   temporal_note=x['temporal_note'], review_status=x['review_status'],
                                                                   main_source=x['main_source']))
        l['payload'] = dict(src['payload'], nota_temporal=x['temporal_note'])
        E.validate_link(l, reg)
        if l['visibility'] != 'CURRENT_VISIBLE':
            raise Run7Error('RELOCATED_LINK_NOT_VISIBLE', x['relocation_id'])
        new.append(l)
        pairs.add((x['target_id'], x['source_id']))
    links = sorted(kept + new, key=key)
    if len({l['reference_id'] for l in links}) != len(links):
        raise Run7Error('DUPLICATE_REFERENCE_ID')
    dev = out / 'device_ready'
    files = E.export(NORM, links, dev, list(excluded6) + list(excl), added)
    vis = lambda ls, t: {l['target_id'] for l in ls if l['reference_type'] == t and l['visibility'] == 'CURRENT_VISIBLE'}  # noqa: E731
    base_j = {l.split('|')[0] for l in base['CF88_TARGETS.IDX'].decode('utf-8').split('\n')
              if l and not l.startswith('#') and l.split('|')[3][R6.J_POS] == 'J'}
    if base_j != vis(run6_links, 'JURISPRUDENCE'):
        raise Run7Error('BASELINE_J_NOT_DERIVED_FROM_RUN6')
    targets_b, j_changes = R6.retarget_j_flags(base['CF88_TARGETS.IDX'], vis(links, 'JURISPRUDENCE'))
    (dev / 'CF88_TARGETS.IDX').write_bytes(targets_b)
    for name in COPIED:
        (dev / name).write_bytes(base[name])

    def by_type(ls):
        return dict(sorted(collections.Counter(f"{l['reference_type']}|{l['visibility']}" for l in ls).items()))
    jv = lambda ls: [l for l in ls if l['reference_type'] == 'JURISPRUDENCE' and l['visibility'] == 'CURRENT_VISIBLE']  # noqa: E731
    summary = dict(status=STATUS, base='RUN6 device_ready == candidato J1.1 instalado e validado fisicamente (J1.2 10/10)', run6_reproduced=True,
                   removed_links=sorted(gone), added_links=sorted(l['reference_id'] for l in new),
                   links_by_type=dict(run6=by_type(run6_links), run7=by_type(links)),
                   jurisprudence=dict(relations_before=len(jv(run6_links)), relations_after=len(jv(links)),
                                      targets_before=len(vis(run6_links, 'JURISPRUDENCE')), targets_after=len(vis(links, 'JURISPRUDENCE'))),
                   target_flag_changes=j_changes, untouched_files=list(COPIED),
                   files={**files, **{n: dict(sha256=sha((dev / n).read_bytes()), bytes=(dev / n).stat().st_size) for n in ('CF88_TARGETS.IDX',) + COPIED}})
    (out / 'RUN7_SUMMARY.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    sums = sorted((p.relative_to(out).as_posix(), sha(p.read_bytes())) for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (out / 'SHA256SUMS.txt').write_bytes(''.join(f'{h}  {n}\n' for n, h in sums).encode('utf-8'))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    s = build(ap.parse_args().out)
    print(json.dumps({k: s[k] for k in ('removed_links', 'added_links', 'jurisprudence', 'target_flag_changes')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
