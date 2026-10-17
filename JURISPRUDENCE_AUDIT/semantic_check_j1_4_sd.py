"""J1.5: semantic check of the J1.4 SD files — base 99_LEX_V1 (card backup PRE) × other 99_LEX_V1 (package candidate or the card itself).
Reads only. Checks the J1.5 invariants: only JURISPRUDENCE changes (−4 ratified, +3 relocations), 256 relations / 156 targets, only the J flag of
CF88:ART.100:PAR.1 changes, Correlatas / work references / ENTENDA untouched, R divergence 38.

Usage: python semantic_check_j1_4_sd.py <base 99_LEX_V1> <other 99_LEX_V1> [--correlata-base DIR --correlata-other DIR] [--out FILE]
"""
import argparse
import hashlib
import json
from pathlib import Path

POS = dict(E=0, C=1, J=2, W=3, R=4, X=5)
REMOVED = {'JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.1', 'JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.1',
           'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.4', 'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.5'}
ADDED = {'JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.5', 'JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.5',
         'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40'}
ENTENDA = ('30_ENTENDA/ENTENDA_LOOKUP.IDX', '30_ENTENDA/ENTENDA_PAYLOAD.DAT')
CORRELATA = ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX')


def rows(p):
    return [l.split('|') for l in Path(p).read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(base, other, cbase=None, cother=None):
    base, other = Path(base), Path(other)
    pb, po = rows(base / '20_REFERENCES/REF_PAYLOAD.IDX'), rows(other / '20_REFERENCES/REF_PAYLOAD.IDX')
    by = lambda rs, t: {tuple(r) for r in rs if r[1] == t}  # noqa: E731
    juris_vis = [r for r in po if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    jb, jo = by(pb, 'JURISPRUDENCE'), by(po, 'JURISPRUDENCE')
    tb = {r[0]: r for r in rows(base / '10_TARGETS/CF88_TARGETS.IDX')}
    to = {r[0]: r for r in rows(other / '10_TARGETS/CF88_TARGETS.IDX')}
    flags = {k: sorted(t for t in tb if tb[t][3][i] != to.get(t, tb[t])[3][i]) for k, i in POS.items()}
    lookup_targets = {r[0] for r in rows(other / '20_REFERENCES/REF_LOOKUP.IDX')}
    r_div = sorted(t for t, r in to.items() if (r[3][POS['R']] == 'R') != (t in lookup_targets))
    jvis_targets = {r[0] for r in juris_vis}
    at = lambda t: sorted(r[5] for r in juris_vis if r[0] == t)  # noqa: E731
    sem = dict(
        JURIS_RELATIONS_INSTALLED=len(juris_vis), JURIS_TARGETS_INSTALLED=len(jvis_targets),
        JURIS_REMOVED_EQUALS_RATIFIED_4={r[4] for r in jb - jo} == REMOVED, JURIS_ADDED_EQUALS_RELOCATIONS_3={r[4] for r in jo - jb} == ADDED,
        CORRELATA_RELATIONS_CHANGED=len(by(pb, 'CORRELATA') ^ by(po, 'CORRELATA')),
        WORK_REFERENCE_RELATIONS_CHANGED=len(by(pb, 'WORK_REFERENCE') ^ by(po, 'WORK_REFERENCE')),
        OTHER_REFERENCE_TYPES_CHANGED=len({tuple(r) for r in pb if r[1] not in ('JURISPRUDENCE', 'CORRELATA', 'WORK_REFERENCE')}
                                          ^ {tuple(r) for r in po if r[1] not in ('JURISPRUDENCE', 'CORRELATA', 'WORK_REFERENCE')}),
        FLAG_CHANGES={k: len(v) for k, v in flags.items()}, J_FLAG_CHANGED_TARGETS=flags['J'],
        J_FLAG_EQUALS_VISIBLE={t for t, r in to.items() if r[3][POS['J']] == 'J'} == jvis_targets,
        TARGET_SET_UNCHANGED=set(tb) == set(to),
        NON_FLAG_FIELDS_CHANGED=sum(1 for t in tb if t in to and tb[t][:3] + tb[t][4:] != to[t][:3] + to[t][4:]),
        R_FLAG_KNOWN_DIVERGENCE=len(r_div),
        ENTENDA_DATA_CHANGED=any(sha(base / f) != sha(other / f) for f in ENTENDA),
        ART_100_PAR_1=at('CF88:ART.100:PAR.1'), ART_100_PAR_5=at('CF88:ART.100:PAR.5'), ART_40=at('CF88:ART.40'),
        ART_40_PAR_4=at('CF88:ART.40:PAR.4'), ART_40_PAR_5=at('CF88:ART.40:PAR.5'), ART_16=at('CF88:ART.16'),
        LEXV1_VER=[l for l in (other / '00_SYS/LEXV1.VER').read_text(encoding='utf-8').splitlines()
                   if l.split('|')[0] in ('BUILD_ID', 'GIT_COMMIT', 'ENTENDA_COUNT', 'REFERENCE_ENGINE')])
    if cbase and cother:
        sem['CORRELATA_FILES_BYTE_IDENTICAL'] = all(sha(Path(cbase) / f) == sha(Path(cother) / f) for f in CORRELATA)
    ok = (sem['JURIS_RELATIONS_INSTALLED'], sem['JURIS_TARGETS_INSTALLED']) == (256, 156) and sem['JURIS_REMOVED_EQUALS_RATIFIED_4'] \
        and sem['JURIS_ADDED_EQUALS_RELOCATIONS_3'] and sem['CORRELATA_RELATIONS_CHANGED'] == 0 and sem['WORK_REFERENCE_RELATIONS_CHANGED'] == 0 \
        and sem['OTHER_REFERENCE_TYPES_CHANGED'] == 0 and sem['FLAG_CHANGES'] == dict(E=0, C=0, J=1, W=0, R=0, X=0) \
        and sem['J_FLAG_CHANGED_TARGETS'] == ['CF88:ART.100:PAR.1'] and sem['J_FLAG_EQUALS_VISIBLE'] and sem['TARGET_SET_UNCHANGED'] \
        and sem['NON_FLAG_FIELDS_CHANGED'] == 0 and sem['R_FLAG_KNOWN_DIVERGENCE'] == 38 and not sem['ENTENDA_DATA_CHANGED'] \
        and sem['ART_100_PAR_1'] == [] and {'STF:SV:17', 'STF:RG:147', 'STF:RG:1037', 'STF:RG:1335'} <= set(sem['ART_100_PAR_5']) \
        and 'STF:RG:594' in sem['ART_40'] and 'STF:RG:594' not in sem['ART_40_PAR_4'] + sem['ART_40_PAR_5'] \
        and {'STF:RG:367', 'STF:RG:387'} <= set(sem['ART_16']) and sem.get('CORRELATA_FILES_BYTE_IDENTICAL', True)
    sem['RESULT'] = 'PASS' if ok else 'FAIL'
    return sem


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('other')
    ap.add_argument('--correlata-base')
    ap.add_argument('--correlata-other')
    ap.add_argument('--out')
    a = ap.parse_args()
    s = check(a.base, a.other, a.correlata_base, a.correlata_other)
    txt = json.dumps(s, ensure_ascii=False, indent=1) + '\n'
    if a.out:
        Path(a.out).write_text(txt, encoding='utf-8', newline='\n')
    print(txt)
    raise SystemExit(0 if s['RESULT'] == 'PASS' else 3)
