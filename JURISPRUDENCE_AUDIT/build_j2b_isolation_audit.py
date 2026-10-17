"""J2B — isolation audit of the host-only candidate: installed card (J1.4, J1.5 11/11) × J2B package. Read-only, deterministic.

Checks: the 256 current JURISPRUDENCE rows are byte-identical in the candidate; exactly the 5 ratified ADI rows are added; Correlatas / work
references / ENTENDA / CORRELATA files untouched; only flag J changes (4 targets that gain their first link); legacy JURISPRUDENCIA.IDX and
JUR_LOOKUP.IDX are append-only; the firmware PSRAM cache rules hold (offsets aligned, sum of quantities == records); a mirror of the firmware
path (REF_LOOKUP -> REF_PAYLOAD -> key in JURISPRUDENCIA.IDX -> "ADI <NUMERO>" -> 03_CONTEUDO/<id>.TXT) resolves every ADI link.
Writes JURISPRUDENCE_AUDIT/J2B_ISOLATION_AUDIT.json.   Usage: python build_j2b_isolation_audit.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = HERE / 'J1_4_CANDIDATE_HOST_ONLY/candidate/SD'        # installed bytes (99_LEX_V1)
PKG = HERE / 'J2B_CANDIDATE_HOST_ONLY'
LEGACY = Path('C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE')
CARD = HERE / 'J1_5_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADI_ADDITIONS_J2B.json'
OUT = HERE / 'J2B_ISOLATION_AUDIT.json'
POS = dict(E=0, C=1, J=2, W=3, R=4, X=5)
IDX = '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'
LOOKUP = '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX'
LABEL = dict(adi='ADI', repercussao_geral='RG TEMA', sumula_vinculante='SV', sv='SV', rg='RG TEMA')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rows(b):
    return [l.split('|') for l in b.decode('utf-8').split('\n') if l and not l.startswith('#')]


def cand(rel):
    p = PKG / 'candidate/SD' / rel
    return p.read_bytes() if p.is_file() else None


def query_keys(tid):                      # mirror of lexV1QueryKeysForActiveTarget
    if tid.startswith('CF88:ART.') and ':' not in tid[len('CF88:ART.'):]:
        return [tid, tid + ':CAPUT']
    return [tid]


def cache_rules(idx, lookup):             # mirror of carregarCacheJurisCF validation
    records = max(0, idx.count(b'\n') - 1)
    total = 0
    for r in rows(lookup):
        off, q = int(r[5]), int(r[6])
        if off >= len(idx) or (off > 0 and idx[off - 1:off] != b'\n') or not 0 < q <= 255:
            return False, records, total
        cur = off
        for _ in range(q):
            nl = idx.find(b'\n', cur)
            if nl < 0:
                return False, records, total
            cur = nl + 1
        total += q
    return total == records, records, total


def resolve(tid, payload, idx, card_files, new_files):
    """Firmware mirror: JURISPRUDENCE rows of the query keys -> legacy line by key -> label and ficha path."""
    out, seen = [], set()
    for k in query_keys(tid):
        for r in payload:
            if r[0] != k or r[1] != 'JURISPRUDENCE' or r[2] != 'CURRENT_VISIBLE' or r[5] in seen:
                continue
            seen.add(r[5])
            key = r[4].split(':', 1)[1].rsplit('@', 1)[0]
            line = next((l for l in idx.decode('utf-8').split('\n') if l.startswith(key + '|')), None)
            if line is None:
                out.append(dict(source=r[5], resolved=False))
                continue
            f = line.split('|')
            ficha = '99_JURISPRUDENCIA_V2/03_CONTEUDO/' + f[6].replace(':', '_').replace('/', '_') + '.TXT'
            out.append(dict(source=r[5], resolved=True, list_label=f"{LABEL.get(f[1].lower(), 'OUTRO')} {f[3]}", status=f[4],
                            ficha=ficha, ficha_present=ficha in card_files or ficha in new_files))
    return out


def build():
    card = {k: v['sha256'] for k, v in json.loads(CARD.read_text(encoding='utf-8'))['entries'].items()}
    m = json.loads((PKG / 'J2B_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    doc = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    pb, pc = BASE / '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX', cand('99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')
    b_rows, c_rows = rows(pb.read_bytes()), rows(pc)
    bset, cset = {'|'.join(r) for r in b_rows}, {'|'.join(r) for r in c_rows}
    by = lambda rs, t: {'|'.join(r) for r in rs if r[1] == t}  # noqa: E731
    added = sorted(cset - bset)
    expected = {f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}" for r in doc['records']}
    tb = {r[0]: r for r in rows((BASE / '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX').read_bytes())}
    tc = {r[0]: r for r in rows(cand('99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX'))}
    flags = {k: sorted(t for t in tb if tb[t][3][i] != tc[t][3][i]) for k, i in POS.items()}
    jvis = {r[0] for r in c_rows if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE'}
    lookup_targets = {r[0] for r in rows(cand('99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'))}
    idx_b, idx_c = (LEGACY / IDX).read_bytes(), cand(IDX)
    lk_b, lk_c = (LEGACY / LOOKUP).read_bytes(), cand(LOOKUP)
    cache_ok, n_rec, n_sum = cache_rules(idx_c, lk_c)
    new_files = {a['path'].lstrip('/') for a in m['file_additions']}
    sim = {r['target_id']: resolve(r['target_id'], c_rows, idx_c, card, new_files) for r in doc['records']}
    regress = {t: resolve(t, c_rows, idx_c, card, new_files) for t in ('CF88:ART.100:PAR.5', 'CF88:ART.40', 'CF88:ART.16', 'CF88:ART.37:INC.XI')}
    regress_base = {t: resolve(t, b_rows, idx_b, card, set()) for t in regress}
    jv = lambda rs: [r for r in rs if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']  # noqa: E731
    v = dict(
        CURRENT_256_BYTE_IDENTICAL=all(('|'.join(r) in cset) for r in jv(b_rows)) and len(jv(b_rows)) == 256,
        JURIS_RELATIONS_BEFORE=len(jv(b_rows)), JURIS_RELATIONS_AFTER=len(jv(c_rows)),
        JURIS_TARGETS_BEFORE=len({r[0] for r in jv(b_rows)}), JURIS_TARGETS_AFTER=len(jvis),
        ROWS_REMOVED=len(bset - cset), ROWS_ADDED=len(added),
        ADDED_EQUALS_RATIFIED_5={r.split('|')[4] for r in added} == expected and all(r.split('|')[1] == 'JURISPRUDENCE' for r in added),
        CORRELATA_RELATION_SET_CHANGED=len(by(b_rows, 'CORRELATA') ^ by(c_rows, 'CORRELATA')),
        WORK_REFERENCE_SET_CHANGED=len(by(b_rows, 'WORK_REFERENCE') ^ by(c_rows, 'WORK_REFERENCE')),
        **{f'{k}_FLAGS_CHANGED': len(flags[k]) for k in POS}, J_FLAG_CHANGED_TARGETS=flags['J'],
        J_FLAG_EQUALS_VISIBLE_JURIS={t for t, r in tc.items() if r[3][POS['J']] == 'J'} == jvis,
        NON_FLAG_FIELDS_CHANGED=sum(1 for t in tb if tb[t][:3] != tc[t][:3]), TARGET_SET_UNCHANGED=set(tb) == set(tc),
        R_FLAG_KNOWN_DIVERGENCE=sum(1 for t, r in tc.items() if (r[3][POS['R']] == 'R') != (t in lookup_targets)),
        CORRELATA_FILES_BYTE_IDENTICAL=not any(k.startswith('99_RELATIONS_V2/') for k in m['changed_vs_physical'] + m['added_vs_physical']),
        ENTENDA_FILES_BYTE_IDENTICAL=not any('/30_ENTENDA/' in k for k in m['changed_vs_physical'] + m['added_vs_physical']),
        LEGACY_IDX_APPEND_ONLY=idx_c.startswith(idx_b) and sha(idx_b) == card[IDX],
        LEGACY_LOOKUP_APPEND_ONLY=lk_c.startswith(lk_b) and sha(lk_b) == card[LOOKUP],
        LEGACY_ROWS_ADDED=idx_c.count(b'\n') - idx_b.count(b'\n'), LEGACY_LOOKUPS_ADDED=lk_c.count(b'\n') - lk_b.count(b'\n'),
        FIRMWARE_CACHE_RULES_HOLD=cache_ok, LEGACY_RECORDS=n_rec, LOOKUP_QUANTITY_SUM=n_sum,
        ALL_ADI_LINKS_RESOLVE=all(x['resolved'] and x['ficha_present'] for xs in sim.values() for x in xs if x['source'].startswith('STF:ADI:')),
        REGRESSION_TARGETS_UNCHANGED=regress == regress_base,
        FILES_CHANGED=len(m['changed_vs_physical']), FILES_ADDED=len(m['added_vs_physical']))
    return dict(artifact='J2B_ISOLATION_AUDIT', base='J1_4_CANDIDATE_HOST_ONLY (instalado; J1.5 11/11) + legado J4.6 (== cartão)',
                candidate='J2B_CANDIDATE_HOST_ONLY', package_build_id=m['build_id'], verdict=v, device_simulation=sim, regression_simulation=regress)


if __name__ == '__main__':
    b = (json.dumps(build(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(json.dumps(json.loads(b)['verdict'], ensure_ascii=False, indent=1))
