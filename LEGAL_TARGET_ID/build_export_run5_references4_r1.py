"""Reference Engine RUN5_REFERENCES4_R1_CANDIDATE_HOST_ONLY: RUN4/C3B.2 device_ready + the two WORK_REFERENCE approvals of REFERÊNCIAS Nº 4 R1.

NOT a baseline, NOT physical, NOT deployed. Every input is only read:
  base          derived/export_test/run4_candidate/device_ready  (bytes == physically approved C3B.2 package; checked against SHA256SUMS and
                                                                    CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate)
  new links     reference_engine.build_links() with the overlay derived/CF88_WORK_REFERENCE_ADDITIONS_R1.json and the registry
                REFERENCE_REGISTRY/WORK_REGISTRY_V3.json (same fail-closed validation as RUN3); only the links of that overlay are taken
Rules (Correlatas 1 is frozen):
  - the RUN4 device links are reconstructed from the RUN4 export and re-exported byte-identically BEFORE anything is added (fidelity proof);
  - RUN5 links = RUN4 links + the overlay links, same order key as the engine (structural order ; type ; label ; reference_id);
  - REF_LOOKUP/REF_PAYLOAD/CF88_REFERENCES_EXPORT.json written by reference_engine.export (official writer);
  - CF88_TARGETS.IDX: C3B.2 bytes with ONLY position [3] (W) recomputed: 'W' iff the exact target has a CURRENT_VISIBLE WORK_REFERENCE in the
    device export (same rule as build_sd_staging.build_targets). E, C, J, R, X are never touched (R stays as approved in C3B.2);
  - RELACOES.IDX, REL_LOOKUP.IDX, EXT_ARTIGOS.IDX: byte copies of RUN4 (CORRELATA files, not regenerated).
Deterministic (no clock). Usage: python build_export_run5_references4_r1.py [--out DIR]
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import reference_engine as E  # noqa: E402

D = HERE / 'derived'
NORM = 'CF88'
RUN4 = D / 'export_test/run4_candidate'
RUN4_DEV = RUN4 / 'device_ready'
C3B2 = ROOT / 'CORRELATA_COVERAGE_AUDIT/C3B2_PHYSICAL_TEST_PACKAGE/candidate/SD'
C3B2_MAP = {'CF88_TARGETS.IDX': '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', 'REF_LOOKUP.IDX': '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX',
            'REF_PAYLOAD.IDX': '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX', 'RELACOES.IDX': '99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX',
            'REL_LOOKUP.IDX': '99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX': '99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX'}
ADDITIONS_RUN3 = D / 'CF88_WORK_REFERENCE_ADDITIONS.json'
ADDITIONS_R1 = 'derived/CF88_WORK_REFERENCE_ADDITIONS_R1.json'
REGISTRY_V3 = '../REFERENCE_REGISTRY/WORK_REGISTRY_V3.json'
OUT = D / 'export_test/run5_references4_r1_candidate'
STATUS = 'RUN5_REFERENCES4_R1_CANDIDATE_HOST_ONLY'
COPIED = ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX')
W_POS = 3


class Run5Error(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def run4_inputs():
    """RUN4 device_ready, verified against its SHA256SUMS and against the physically approved C3B.2 package (fail closed)."""
    sums = dict(reversed(l.split('  ', 1)) for l in (RUN4 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if l)
    out = {}
    for p in sorted(RUN4_DEV.iterdir()):
        b = p.read_bytes()
        if sha(b) != sums.get(f'device_ready/{p.name}'):
            raise Run5Error('RUN4_SHA256SUMS_MISMATCH', p.name)
        if p.name in C3B2_MAP and b != (C3B2 / C3B2_MAP[p.name]).read_bytes():
            raise Run5Error('RUN4_NOT_C3B2', p.name)
        out[p.name] = b
    return out


def sort_key(reg):
    return lambda l: (reg.order(NORM, l['target_id']), E.TYPE_ORDER.get(l['reference_type'], 9), l['label'], l['reference_id'])


def r1_registry(reg):
    """Same engine configuration with the R1 overlay and registry V3 (the RUN3 overlay is not edited)."""
    clone = E._without(reg, NORM)
    clone.cfg['norms'][NORM]['work_reference_additions'] = ADDITIONS_R1
    clone.cfg['norms'][NORM]['work_registry'] = REGISTRY_V3
    return clone


def retarget_w_flags(targets_bytes, work_targets):
    """CF88_TARGETS.IDX with ONLY position [3] recomputed ('W' iff exact target has a visible WORK_REFERENCE). Every other byte is kept."""
    out, changes = [], []
    known = set()
    for line in targets_bytes.decode('utf-8').split('\n'):
        if line and not line.startswith('#'):
            tid, kind, status, flags = line.split('|')
            known.add(tid)
            want = 'W' if tid in work_targets else '-'
            if flags[W_POS] != want:
                after = flags[:W_POS] + want + flags[W_POS + 1:]
                changes.append(dict(target_id=tid, before=flags, after=after, change='GAINED_W' if want == 'W' else 'LOST_W'))
                line = '|'.join((tid, kind, status, after))
        out.append(line)
    missing = sorted(set(work_targets) - known)
    if missing:
        raise Run5Error('WORK_TARGET_NOT_IN_DEVICE_TARGETS', missing[0])
    return '\n'.join(out).encode('utf-8'), changes


def flat(doc):
    return [l for ls in doc['references'].values() for l in ls]


def build(out):
    out = Path(out)
    base = run4_inputs()
    reg = E.TargetRegistry()
    E.build_links(NORM, reg)                                    # loads the registry (structural order) with the RUN3 configuration
    run4_doc = json.loads(base['CF88_REFERENCES_EXPORT.json'].decode('utf-8'))
    adds_run3 = load(ADDITIONS_RUN3)['records']
    excluded = run4_doc['excluded_links']
    run4_links = sorted(flat(run4_doc), key=sort_key(reg))
    # fidelity proof: the reconstructed RUN4 links re-exported by the official writer give the RUN4 bytes
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        E.export(NORM, run4_links, t, excluded, adds_run3)
        for name in ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            if (Path(t) / name).read_bytes() != base[name]:
                raise Run5Error('RUN4_NOT_REPRODUCED', name)
    # the two approved links, validated by the engine (registry V3, target status, duplicates)
    reg1 = r1_registry(reg)
    adds_r1 = E.work_reference_additions(NORM, reg1)
    wanted = {f"WORK_REFERENCE:{a['work_id']}@{a['target_id']}" for a in adds_r1}
    new = [l for l in E.build_links(NORM, reg1) if l['reference_id'] in wanted]
    if {l['reference_id'] for l in new} != wanted:
        raise Run5Error('R1_LINKS_NOT_BUILT', sorted(wanted - {l['reference_id'] for l in new}))
    existing = {l['reference_id'] for l in run4_links}
    for l in new:
        if l['reference_id'] in existing:
            raise Run5Error('R1_LINK_ALREADY_PUBLISHED', l['reference_id'])
        if l['visibility'] != 'CURRENT_VISIBLE':
            raise Run5Error('R1_LINK_NOT_VISIBLE', l['reference_id'])
    links = sorted(run4_links + new, key=sort_key(reg))
    dev = out / 'device_ready'
    files = E.export(NORM, links, dev, excluded, list(adds_run3) + list(adds_r1))
    work_targets = {l['target_id'] for l in links if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE'}
    base_w = {l.split('|')[0] for l in base['CF88_TARGETS.IDX'].decode('utf-8').split('\n')
              if l and not l.startswith('#') and l.split('|')[3][W_POS] == 'W'}
    run4_w = {l['target_id'] for l in run4_links if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE'}
    if base_w != run4_w:
        raise Run5Error('BASELINE_W_NOT_DERIVED_FROM_RUN4', sorted(base_w ^ run4_w)[:3])
    targets_b, w_changes = retarget_w_flags(base['CF88_TARGETS.IDX'], work_targets)
    (dev / 'CF88_TARGETS.IDX').write_bytes(targets_b)
    for name in COPIED:
        (dev / name).write_bytes(base[name])

    def by_type(ls):
        return dict(sorted(collections.Counter(f"{l['reference_type']}|{l['visibility']}" for l in ls).items()))
    wl = [l for l in links if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE']
    w4 = [l for l in run4_links if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE']
    summary = dict(
        status=STATUS, base='RUN4 device_ready == C3B.2 physically approved package', principle='LEGAL_APPROVED != DEVICE_READY',
        run4_reproduced=True, added_links=sorted(wanted),
        links_by_type=dict(run4=by_type(run4_links), run5=by_type(links)),
        work_reference=dict(relations_before=len(w4), relations_after=len(wl), works_used_before=len({l['source_id'] for l in w4}),
                            works_used_after=len({l['source_id'] for l in wl}), w_targets_before=len(base_w), w_targets_after=len(work_targets)),
        target_flag_changes=w_changes, untouched_files=list(COPIED),
        files={**files, **{n: dict(sha256=sha((dev / n).read_bytes()), bytes=(dev / n).stat().st_size) for n in ('CF88_TARGETS.IDX',) + COPIED}})
    (out / 'RUN5_SUMMARY.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    sums = sorted((p.relative_to(out).as_posix(), sha(p.read_bytes())) for p in out.rglob('*')
                  if p.is_file() and p.name != 'SHA256SUMS.txt' and 'device_candidate' not in p.relative_to(out).parts)
    (out / 'SHA256SUMS.txt').write_bytes(''.join(f'{h}  {n}\n' for n, h in sums).encode('utf-8'))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    s = build(ap.parse_args().out)
    print(json.dumps({k: s[k] for k in ('added_links', 'links_by_type', 'work_reference', 'target_flag_changes')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
