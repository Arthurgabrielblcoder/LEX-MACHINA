"""J2F — isolation audit of the ratified-content candidates (A: current firmware; B: generic tribunal/classe firmware) against the J2C physical
card (PHYSICAL_BASELINE 261/160). Read-only, deterministic.

Firmware mirror (build_j2b_isolation_audit): query keys -> REF_PAYLOAD -> key in JURISPRUDENCIA.IDX -> label -> ficha, PSRAM cache rules.
Labels for two firmwares: CURRENT (approved app: adi/repercussao_geral/sumula_vinculante, everything else "OUTRO <n>") and GENERIC
(juris_types.label = JURIS_TYPE_PROTOTYPE patch). Writes J2F_CANDIDATES_HOST_ONLY/J2F_ISOLATION_AUDIT.json.   Usage: [--check]
"""
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_j2b_isolation_audit as A  # noqa: E402
import juris_types as JT  # noqa: E402

CARD_PKG = HERE / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD'
PHYSICAL = HERE / 'J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
PKG_ROOT = HERE / 'J2F_CANDIDATES_HOST_ONLY'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json'
PROV = HERE / 'J2_PROVISIONAL_REGISTRY.json'
INO = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'
OUT = PKG_ROOT / 'J2F_ISOLATION_AUDIT.json'
VARIANTS = {'A': ('J2_CURRENT_FW_CANDIDATE', ('A',), 'CURRENT'), 'B': ('J2_GENERIC_FW_CANDIDATE', ('A', 'B'), 'GENERIC')}
PAYLOAD, TARGETS, LOOKUP_REF = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'
REGRESSION = ('CF88:ART.100:PAR.5', 'CF88:ART.40', 'CF88:ART.16', 'CF88:ART.37:INC.XI', 'CF88:ART.100:PAR.12', 'CF88:ART.100:PAR.9',
              'CF88:ART.166:PAR.9', 'CF88:ART.166:PAR.11', 'CF88:ART.166-A', 'CF88:ART.5:INC.XXXVIII', 'CF88:ART.14:PAR.5', 'CF88:ART.63:INC.I')
REQUIRED_GENERIC = ('HC 232627', 'HC 70648', 'MS 21689', 'AP 694', 'AI 343461', 'Inq 4781', 'Rcl 84738', 'ADPF 378', 'ADPF 964', 'Súmula 9 TSE')


def fw_define(name):
    return int(re.search(rf'#define {name} (\d+)', INO.read_text(encoding='utf-8')).group(1))


def label(tipo, tribunal, numero, fw):
    if fw == 'CURRENT':
        return f"{A.LABEL.get(tipo.lower(), 'OUTRO')} {numero}"
    try:
        return JT.label(tipo, tribunal, numero)
    except ValueError:
        return f'OUTRO {numero}'


def view(t, rows, idx_lines, files, fw):
    out = []
    for k in A.query_keys(t):
        for r in rows:
            if r[0] != k or r[1] != 'JURISPRUDENCE' or r[2] != 'CURRENT_VISIBLE':
                continue
            key = r[4].split(':', 1)[1].rsplit('@', 1)[0]
            f = idx_lines.get(key)
            if f is None:
                out.append(dict(source=r[5], resolved=False))
                continue
            ficha = '99_JURISPRUDENCIA_V2/03_CONTEUDO/' + JT.ficha(f[6])
            out.append(dict(source=r[5], resolved=True, label=label(f[1], f[2], f[3], fw), ficha=ficha, ficha_present=ficha in files,
                            id_accepted_by_firmware=f[0].startswith('STF:') if fw == 'CURRENT' else JT.id_accepted(f[0], f[2])))
    return out


def build():
    card = {k: v['sha256'] for k, v in json.loads(PHYSICAL.read_text(encoding='utf-8'))['entries'].items()}
    add = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    prov_ids = sorted(x['source_id'] for x in json.loads(PROV.read_text(encoding='utf-8'))['items'])
    base_rows = A.rows((CARD_PKG / PAYLOAD).read_bytes())
    tb = {r[0]: r for r in A.rows((CARD_PKG / TARGETS).read_bytes())}
    jv = lambda rs: [r for r in rs if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']  # noqa: E731
    by = lambda rs, t: {'|'.join(r) for r in rs if r[1] == t}  # noqa: E731
    itens_max, rel_max = fw_define('LEXV1_REF_ITENS_MAX'), fw_define('MAX_RELACOES_ARTIGO')
    res = {}
    for v, (pkgname, inc, native_fw) in VARIANTS.items():
        pkg = PKG_ROOT / pkgname
        m = json.loads((pkg / 'J2F_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
        rd = lambda rel: (pkg / 'candidate/SD' / rel).read_bytes()  # noqa: E731
        rows, idx, lk = A.rows(rd(PAYLOAD)), rd(A.IDX), rd(A.LOOKUP)
        idx_lines = {l.split('|')[0]: l.split('|') for l in idx.decode('utf-8').split('\n') if l and not l.startswith('#')}
        tc = {r[0]: r for r in A.rows(rd(TARGETS))}
        flags = {k: sorted(t for t in tb if tb[t][3][i] != tc[t][3][i]) for k, i in A.POS.items()}
        sb, sc = {'|'.join(r) for r in base_rows}, {'|'.join(r) for r in rows}
        recs = [r for r in add['records'] if r['group'] in inc]
        expected = {f"JURISPRUDENCE:{r['source_reference_id']}@{r['target_id']}" for r in recs}
        files = set(card) | {a['path'].lstrip('/') for a in m['file_additions']}
        cache_ok, n_rec, n_sum = A.cache_rules(idx, lk)
        lookup_targets = {r[0] for r in A.rows(rd(LOOKUP_REF))}
        new_targets = sorted({r['target_id'] for r in recs})
        sim = {fw: {t: view(t, rows, idx_lines, files, fw) for t in new_targets + list(REGRESSION)} for fw in ('CURRENT', 'GENERIC')}
        reg_now = {t: view(t, rows, idx_lines, files, 'CURRENT') for t in REGRESSION}
        base_lines = {l.split('|')[0]: l.split('|') for l in (CARD_PKG / A.IDX).read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')}
        reg_card = {t: view(t, base_rows, base_lines, set(card), 'CURRENT') for t in REGRESSION}
        all_juris_targets = sorted({r[0] for r in jv(rows)})
        native = {t: view(t, rows, idx_lines, files, native_fw) for t in all_juris_targets}
        native_labels = [x['label'] for xs in native.values() for x in xs if x['resolved']]
        vis_by = collections.Counter(r[0] for r in rows if r[2] == 'CURRENT_VISIBLE')
        jur_by = collections.Counter(r[0] for r in jv(rows))
        per_target_juris = {t: sum(jur_by[k] for k in A.query_keys(t)) for t in tc}       # firmware loads every query key of the target
        per_target_all = {t: sum(vis_by[k] for k in A.query_keys(t)) for t in tc}
        gen_labels = sorted({x['label'] for xs in sim['GENERIC'].values() for x in xs if x['resolved']})
        verdict = dict(
            LEGACY_261_RELATIONS_UNCHANGED=all('|'.join(r) in sc for r in jv(base_rows)) and len(jv(base_rows)) == 261,
            BASE_IS_PHYSICAL_261_160=(len(jv(base_rows)), len({r[0] for r in jv(base_rows)})) == (261, 160),
            ROWS_REMOVED=len(sb - sc), ROWS_ADDED=len(sc - sb),
            ONLY_RATIFIED_RELATIONS_ADDED={r.split('|')[4] for r in sc - sb} == expected,
            JURIS_RELATIONS=len(jv(rows)), JURIS_TARGETS=len({r[0] for r in jv(rows)}),
            CORRELATA_RELATION_SET_CHANGED=len(by(base_rows, 'CORRELATA') ^ by(rows, 'CORRELATA')),
            WORK_REFERENCE_SET_CHANGED=len(by(base_rows, 'WORK_REFERENCE') ^ by(rows, 'WORK_REFERENCE')),
            ENTENDA_SET_CHANGED=len(by(base_rows, 'ENTENDA') ^ by(rows, 'ENTENDA')),
            **{f'{k}_FLAGS_CHANGED': len(x) for k, x in flags.items()}, NEW_TARGETS_WITH_J=len(flags['J']),
            J_FLAG_EQUALS_VISIBLE_JURIS={t for t, r in tc.items() if r[3][A.POS['J']] == 'J'} == {r[0] for r in jv(rows)},
            R_FLAG_KNOWN_DIVERGENCE=sum(1 for t, r in tc.items() if (r[3][A.POS['R']] == 'R') != (t in lookup_targets)),
            LEGACY_PREFIX_IDENTICAL=idx.startswith((CARD_PKG / A.IDX).read_bytes()) and lk.startswith((CARD_PKG / A.LOOKUP).read_bytes()),
            FIRMWARE_CACHE_RULES_HOLD=cache_ok, LEGACY_RECORDS=n_rec, LOOKUP_QUANTITY_SUM=n_sum,
            ALL_NEW_RELATIONS_RESOLVE_WITH_FICHA=all(x['resolved'] and x['ficha_present'] for t in new_targets for x in sim[native_fw][t]),
            ALL_IDS_ACCEPTED_BY_TARGET_FIRMWARE=all(x['id_accepted_by_firmware'] for xs in native.values() for x in xs if x['resolved']),
            NO_OUTRO_LABEL_ON_TARGET_FIRMWARE=not [l for l in native_labels if l.startswith('OUTRO')],
            OUTRO_LABELS_IF_SHOWN_WITH_CURRENT_FIRMWARE=sorted({x['label'] for xs in sim['CURRENT'].values() for x in xs
                                                                if x['resolved'] and x['label'].startswith('OUTRO')}),
            GENERIC_TYPES_LABELS_CORRECT=('PASS' if all(any(l == q or l.startswith(q + ' (') for l in gen_labels) for q in REQUIRED_GENERIC) else 'FAIL')
            if v == 'B' else 'N/A',
            REQUIRED_GENERIC_LABELS_FOUND={q: sorted(l for l in gen_labels if l == q or l.startswith(q + ' (')) for q in REQUIRED_GENERIC} if v == 'B' else None,
            PROVISIONAL_LABELS=sorted({x['label'] for xs in sim[native_fw].values() for x in xs if x['resolved'] and '(' in x['label']}),
            PROVISIONAL_SOURCES_IN_CANDIDATE=sorted({r['source_id'] for r in recs if r.get('provisional')} | ({'STF:ADI:7697'} & {r[5] for r in rows})),
            PROVISIONAL_REGISTRY_ITEMS=prov_ids,
            STJ_SUMULA_403_ABSENT=not any('STJ:SUMULA:403' in '|'.join(r) for r in rows) and b'STJ:SUMULA:403' not in idx,
            TEMAS_367_387_FICHAS_UNTOUCHED=not any(Path(p).name in ('STF_RG_367.TXT', 'STF_RG_387.TXT') for p in m['changed_vs_physical'] + m['added_vs_physical']),
            REGRESSION_LEGACY_ITEMS_PRESERVED=all(all(x in reg_now[t] for x in reg_card[t]) for t in REGRESSION),
            REGRESSION_TARGETS_WITHOUT_NEW_RELATIONS_IDENTICAL=all(reg_now[t] == reg_card[t] for t in REGRESSION if t not in new_targets),
            MAX_JURIS_PER_TARGET=max(per_target_juris.values()), MAX_RELACOES_ARTIGO=rel_max,
            MAX_VISIBLE_ITEMS_PER_TARGET=max(per_target_all.values()), LEXV1_REF_ITENS_MAX=itens_max,
            FIRMWARE_LIMITS_OK=max(per_target_juris.values()) <= rel_max and max(per_target_all.values()) <= itens_max,
            FILES_MODIFIED=len(m['changed_vs_physical']), FILES_CREATED=len(m['added_vs_physical']))
        res[v] = dict(package=pkgname, native_firmware=native_fw, build_id=m['build_id'], verdict=verdict,
                      device_simulation={t: [x.get('label') for x in xs] for t, xs in sim[native_fw].items()})
    return dict(artifact='J2F_ISOLATION_AUDIT', base='J2C card (PHYSICAL_BASELINE 261/160)', variants=res)


if __name__ == '__main__':
    b = (json.dumps(build(), ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    for v, r in d['variants'].items():
        print(v, json.dumps(r['verdict'], ensure_ascii=False, indent=1))
