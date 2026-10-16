"""Reference Engine RUN6_JURIS_J1_CANDIDATE_HOST_ONLY: RUN5 (physically approved, REFERENCES 4 baseline) minus the 20 jurisprudence
false positives ratified in J1.1 (overlay derived/CF88_LINK_EXCLUSIONS_J1.json).

NOT a baseline, NOT physical, NOT deployed. Every input is only read:
  base     derived/export_test/run5_references4_r1_candidate/device_ready (bytes == physically approved package of 2026-10-16; checked against
           SHA256SUMS and REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate)
  overlay  derived/CF88_LINK_EXCLUSIONS_J1.json, validated by reference_engine.link_exclusions() (each record = exactly one built link)
Rules (CORRELATAS 1, REFERENCES 4 and ENTENDA are frozen):
  - RUN5 links are reconstructed from the RUN5 export and re-exported byte-identically BEFORE anything is removed (fidelity proof);
  - RUN6 links = RUN5 links minus exactly the 20 overlay links (all JURISPRUDENCE / CURRENT_VISIBLE); nothing is added or relocated;
  - REF_LOOKUP/REF_PAYLOAD/CF88_REFERENCES_EXPORT.json written by reference_engine.export (official writer);
  - CF88_TARGETS.IDX: RUN5 bytes with ONLY position [2] (J) recomputed: 'J' iff the exact target keeps a CURRENT_VISIBLE JURISPRUDENCE link
    (same rule as build_sd_staging.build_targets). E, C, W, R, X never touched (R stays as approved);
  - RELACOES.IDX, REL_LOOKUP.IDX, EXT_ARTIGOS.IDX: byte copies of RUN5.
Deterministic (no clock). Usage: python build_export_run6_juris_j1.py [--out DIR]
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

D = HERE / 'derived'
NORM = 'CF88'
RUN5 = D / 'export_test/run5_references4_r1_candidate'
RUN5_DEV = RUN5 / 'device_ready'
APPROVED = ROOT / 'REFERENCE_COVERAGE_AUDIT/REFERENCES_4_FINAL_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1'
APPROVED_MAP = {'CF88_TARGETS.IDX': '10_TARGETS/CF88_TARGETS.IDX', 'REF_LOOKUP.IDX': '20_REFERENCES/REF_LOOKUP.IDX',
                'REF_PAYLOAD.IDX': '20_REFERENCES/REF_PAYLOAD.IDX'}
EFFECTIVE_ADDITIONS = RUN5 / 'CF88_WORK_REFERENCE_ADDITIONS_RUN5_EFFECTIVE.json'
EXCLUSIONS_J1 = 'derived/CF88_LINK_EXCLUSIONS_J1.json'
OUT = D / 'export_test/run6_juris_j1_candidate'
STATUS = 'RUN6_JURIS_J1_CANDIDATE_HOST_ONLY'
COPIED = ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX')
J_POS = 2
EXPECTED_REMOVALS = 20


class Run6Error(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def run5_inputs():
    sums = dict(reversed(l.split('  ', 1)) for l in (RUN5 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if l)
    out = {}
    for p in sorted(RUN5_DEV.iterdir()):
        b = p.read_bytes()
        if sha(b) != sums.get(f'device_ready/{p.name}'):
            raise Run6Error('RUN5_SHA256SUMS_MISMATCH', p.name)
        if p.name in APPROVED_MAP and b != (APPROVED / APPROVED_MAP[p.name]).read_bytes():
            raise Run6Error('RUN5_NOT_PHYSICALLY_APPROVED_BYTES', p.name)
        out[p.name] = b
    return out


def sort_key(reg):
    return lambda l: (reg.order(NORM, l['target_id']), E.TYPE_ORDER.get(l['reference_type'], 9), l['label'], l['reference_id'])


def retarget_j_flags(targets_bytes, juris_targets):
    """CF88_TARGETS.IDX with ONLY position [2] recomputed ('J' iff exact target has a visible JURISPRUDENCE link). Every other byte kept."""
    out, changes, known = [], [], set()
    for line in targets_bytes.decode('utf-8').split('\n'):
        if line and not line.startswith('#'):
            tid, kind, status, flags = line.split('|')
            known.add(tid)
            want = 'J' if tid in juris_targets else '-'
            if flags[J_POS] != want:
                after = flags[:J_POS] + want + flags[J_POS + 1:]
                changes.append(dict(target_id=tid, before=flags, after=after, change='GAINED_J' if want == 'J' else 'LOST_J'))
                line = '|'.join((tid, kind, status, after))
        out.append(line)
    missing = sorted(set(juris_targets) - known)
    if missing:
        raise Run6Error('JURIS_TARGET_NOT_IN_DEVICE_TARGETS', missing[0])
    return '\n'.join(out).encode('utf-8'), changes


def flat(doc):
    return [l for ls in doc['references'].values() for l in ls]


def build(out):
    out = Path(out)
    base = run5_inputs()
    reg = E.TargetRegistry()
    E.build_links(NORM, reg)
    run5_doc = json.loads(base['CF88_REFERENCES_EXPORT.json'].decode('utf-8'))
    added = load(EFFECTIVE_ADDITIONS)['records']
    excluded5 = run5_doc['excluded_links']
    run5_links = sorted(flat(run5_doc), key=sort_key(reg))
    with tempfile.TemporaryDirectory() as t:                     # fidelity proof
        E.export(NORM, run5_links, t, excluded5, added)
        for name in ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            if (Path(t) / name).read_bytes() != base[name]:
                raise Run6Error('RUN5_NOT_REPRODUCED', name)
    clone = E._without(reg, NORM)                                 # overlay validated by the engine (fail closed)
    clone.cfg['norms'][NORM]['link_exclusions'] = EXCLUSIONS_J1
    excl = E.link_exclusions(NORM, clone)
    if len(excl) != EXPECTED_REMOVALS:
        raise Run6Error('EXCLUSION_COUNT', len(excl))
    by_id = collections.Counter(l['reference_id'] for l in run5_links)
    links5 = {l['reference_id']: l for l in run5_links}
    for r in excl:
        l = links5.get(r['reference_id'])
        if by_id[r['reference_id']] != 1 or l['reference_type'] != 'JURISPRUDENCE' or l['visibility'] != 'CURRENT_VISIBLE' \
                or (l['target_id'], l['source_id']) != (r['target_id'], r['source_id']):
            raise Run6Error('EXCLUSION_NOT_A_VISIBLE_RUN5_JURIS_LINK', r['reference_id'])
    gone = {r['reference_id'] for r in excl}
    links = [l for l in run5_links if l['reference_id'] not in gone]
    dev = out / 'device_ready'
    files = E.export(NORM, links, dev, list(excluded5) + list(excl), added)
    vis = lambda ls, t: {l['target_id'] for l in ls if l['reference_type'] == t and l['visibility'] == 'CURRENT_VISIBLE'}  # noqa: E731
    base_j = {l.split('|')[0] for l in base['CF88_TARGETS.IDX'].decode('utf-8').split('\n')
              if l and not l.startswith('#') and l.split('|')[3][J_POS] == 'J'}
    if base_j != vis(run5_links, 'JURISPRUDENCE'):
        raise Run6Error('BASELINE_J_NOT_DERIVED_FROM_RUN5', sorted(base_j ^ vis(run5_links, 'JURISPRUDENCE'))[:3])
    targets_b, j_changes = retarget_j_flags(base['CF88_TARGETS.IDX'], vis(links, 'JURISPRUDENCE'))
    (dev / 'CF88_TARGETS.IDX').write_bytes(targets_b)
    for name in COPIED:
        (dev / name).write_bytes(base[name])

    def by_type(ls):
        return dict(sorted(collections.Counter(f"{l['reference_type']}|{l['visibility']}" for l in ls).items()))
    summary = dict(
        status=STATUS, base='RUN5 device_ready == pacote físico aprovado (lex-device-v1-references4-physical-approved-2026-10-16)',
        run5_reproduced=True, removed_links=sorted(gone), removals=len(gone),
        links_by_type=dict(run5=by_type(run5_links), run6=by_type(links)),
        jurisprudence=dict(relations_before=len([l for l in run5_links if l['reference_type'] == 'JURISPRUDENCE' and l['visibility'] == 'CURRENT_VISIBLE']),
                           relations_after=len([l for l in links if l['reference_type'] == 'JURISPRUDENCE' and l['visibility'] == 'CURRENT_VISIBLE']),
                           targets_before=len(vis(run5_links, 'JURISPRUDENCE')), targets_after=len(vis(links, 'JURISPRUDENCE'))),
        target_flag_changes=j_changes, untouched_files=list(COPIED),
        files={**files, **{n: dict(sha256=sha((dev / n).read_bytes()), bytes=(dev / n).stat().st_size) for n in ('CF88_TARGETS.IDX',) + COPIED}})
    (out / 'RUN6_SUMMARY.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    sums = sorted((p.relative_to(out).as_posix(), sha(p.read_bytes())) for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (out / 'SHA256SUMS.txt').write_bytes(''.join(f'{h}  {n}\n' for n, h in sums).encode('utf-8'))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    s = build(ap.parse_args().out)
    print(json.dumps({k: s[k] for k in ('removals', 'links_by_type', 'jurisprudence', 'target_flag_changes')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
