"""RATIFICAÇÃO 03–09 — Parte D: reconcile "301" × "261" from the J2C card bytes (installed package = J2B.1 candidate, checked against the
physical manifest). Read-only, deterministic. Writes J2_BASELINE_RECONCILIATION.json.   Usage: python build_baseline_reconciliation.py [--check]

Definitions:
  PHYSICAL_BASELINE_RELATIONS = REF_PAYLOAD lines with TIPO=JURISPRUDENCE and VIS=CURRENT_VISIBLE (what the device lists)
  PHYSICAL_BASELINE_TARGETS   = distinct TARGET among those lines
  LEGACY_JURIS_RECORDS        = data rows of the legacy JURISPRUDENCIA.IDX (precedent records; one row per legacy key), NOT relations
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD = HERE / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD'
PHYSICAL = HERE / 'J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
PAYLOAD = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
IDX = '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'
LOOKUP = '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX'
OUT = HERE / 'J2_BASELINE_RECONCILIATION.json'
PHYSICAL_BASELINE = (261, 160)


def rows(b):
    return [l.split('|') for l in b.decode('utf-8').split('\n') if l and not l.startswith('#')]


def key(ref_id):
    return ref_id.split(':', 1)[1].rsplit('@', 1)[0]


def build():
    card = {k: v['sha256'] for k, v in json.loads(PHYSICAL.read_text(encoding='utf-8'))['entries'].items()}
    b = {rel: (CARD / rel).read_bytes() for rel in (PAYLOAD, IDX, LOOKUP)}
    for rel, x in b.items():
        if hashlib.sha256(x).hexdigest() != card[rel]:
            raise SystemExit(f'NOT_CARD_BYTES {rel}')
    pay, idx, lk = rows(b[PAYLOAD]), rows(b[IDX]), rows(b[LOOKUP])
    jur = [r for r in pay if r[1] == 'JURISPRUDENCE']
    vis = [r for r in jur if r[2] == 'CURRENT_VISIBLE']
    hid = [r for r in jur if r[2] != 'CURRENT_VISIBLE']
    ids = {r[0] for r in idx}
    ref_keys = {key(r[4]) for r in jur}
    vis_keys = {key(r[4]) for r in vis}
    multi = {k: n for k, n in collections.Counter(key(r[4]) for r in vis).items() if n > 1}
    rel, tgt = len(vis), len({r[0] for r in vis})
    doc = dict(
        artifact='J2_BASELINE_RECONCILIATION', source='bytes do pacote J2B.1 = cartão J2C (sha256 conferido no manifesto físico)',
        PHYSICAL_BASELINE_RELATIONS=rel, PHYSICAL_BASELINE_TARGETS=tgt,
        PHYSICAL_BASELINE_RECONCILED='PASS' if (rel, tgt) == PHYSICAL_BASELINE else 'FAIL',
        ref_payload=dict(jurisprudence_lines=len(jur), current_visible=len(vis), historical_hidden=len(hid),
                         hidden_targets=sorted({r[0] for r in hid})),
        legacy_index=dict(LEGACY_JURIS_RECORDS=len(idx), distinct_identifiers=len({r[6] for r in idx}),
                          by_type=dict(sorted(collections.Counter(r[1] for r in idx).items())), lookup_rows=len(lk),
                          lookup_quantity_sum=sum(int(r[6]) for r in lk)),
        decomposition_of_301=dict(
            records_referenced_by_visible_relations=len(vis_keys),
            records_referenced_only_by_hidden_historical_relations=len((ref_keys - vis_keys) & ids),
            records_not_referenced_by_ref_payload=len(ids - ref_keys),
            visible_relations_sharing_a_record=sum(multi.values()) - len(multi), shared_records=sorted(multi)),
        WHAT_WAS_301=('301 = número de LINHAS (registros de precedente) do índice legado JURISPRUDENCIA.IDX do cartão J2C, e não de vínculos. '
                      'Inclui registros usados por vínculos visíveis, registros usados só por vínculos históricos ocultos e registros legados que '
                      'nenhum vínculo V1 referencia (o caminho V1 resolve só pela chave do REF_PAYLOAD). O baseline físico de VÍNCULOS é 261 '
                      '(REF_PAYLOAD, JURISPRUDENCE, CURRENT_VISIBLE) em 160 targets. O erro foi de texto: o JURIS_TYPE_ARCHITECTURE.md chamou as '
                      '301 linhas de "vínculos"/"linhas legadas instaladas", e a resposta final da operação pós-noturna repetiu "301 vínculos já '
                      'instalados".'),
        CANDIDATE_BASELINE_RULE='Todo builder J2F parte de PHYSICAL_BASELINE = 261/160 (REF_PAYLOAD do cartão J2C). 301 é só a contagem de '
                                'registros do índice legado (LEGACY_JURIS_RECORDS_J2C) e nunca é baseline de vínculos.')
    d = doc['decomposition_of_301']
    if d['records_referenced_by_visible_relations'] + d['records_referenced_only_by_hidden_historical_relations'] + \
            d['records_not_referenced_by_ref_payload'] != len(idx) or not ref_keys <= ids:
        raise SystemExit('DECOMPOSITION_DOES_NOT_ADD_UP')
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    print(json.dumps({k: d[k] for k in ('PHYSICAL_BASELINE_RELATIONS', 'PHYSICAL_BASELINE_TARGETS', 'PHYSICAL_BASELINE_RECONCILED', 'legacy_index',
                                         'decomposition_of_301')}, ensure_ascii=False, indent=1))
