# -*- coding: utf-8 -*-
"""REFERÊNCIAS Nº 4 — R1: materializes the two approvals held as APPROVED_PENDING_WORK_IDENTITY in REFERENCE_EXPANSION_01
(P20 SOS Saúde/Sicko -> CF88:ART.196; P21 Pro Dia Nascer Feliz -> CF88:ART.206:INC.I) now that R1A gave their works an identity.

Reads (never edits): REFERENCE_EXPANSION_ROUND1_DECISIONS.json (the human decisions, FINAL), WORK_REGISTRY_V2.json (73 works),
R1A_WORK_IDENTITY/R1A_WORK_IDENTITY_CATALOG.json (identity records, CATALOGO_EXPANSAO_200 schema).
Writes:
  REFERENCE_REGISTRY/WORK_REGISTRY_V3.json                   V2 records byte-equal (as JSON values) + the 2 promoted works (75)
  LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS_R1.json  the 2 approved links (engine overlay, same record schema as RUN3's)
Promotion applies the checks of apply_reference_expansion_round1.promote() (identity, duplicates, title/type/year vs the decision).
The only check with a documented exception is the year of P21 (sources disagree; user decision recorded in the identity record).
No new editorial relation: only decisions P20/P21 with status HUMAN_APPROVED_REFERENCE_V1 are read. Deterministic (no clock, no network).
Usage: python apply_references4_r1.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import apply_reference_expansion_round1 as R1E  # noqa: E402  (helpers + constants of the round that took the decisions)

DECISIONS = R1E.DECISIONS
REGISTRY_V2 = R1E.REGISTRY_V2
REGISTRY_V3 = ROOT / 'REFERENCE_REGISTRY/WORK_REGISTRY_V3.json'
IDENTITY = HERE / 'R1A_WORK_IDENTITY/R1A_WORK_IDENTITY_CATALOG.json'
ADDITIONS_R1 = ROOT / 'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS_R1.json'
ROUND = 'REFERENCES_4_R1'
HELD_IDS = ('REFERENCE_EXPANSION_01-P20', 'REFERENCE_EXPANSION_01-P21')
PROMOTED = 'PROMOTED_FROM_R1A_IDENTITY'
YEAR_EXCEPTION = {'REFERENCE_EXPANSION_01-P21'}      # see ano_decisao in the identity record


def promote(d, reg, ident):
    """Approved held decision -> registry record (same shape as R1E.promote) + check log. Fail closed."""
    rows = [o for o in ident['obras'] if o['required_by']['decision_id'] == d['decision_id']]
    if len(rows) != 1 or rows[0]['required_by']['target_id'] != d['target_id']:
        raise SystemExit(f'IDENTITY_RECORD_MISMATCH {d["decision_id"]}')
    o, p = rows[0], d['original_proposal']
    wid, cid = o['work_id'], o['candidate_id']
    titulo = o['titulo']
    aliases = sorted({x for x in (o['titulo'], o['titulo_original'], o['titulo_informado'], o['titulo_ptbr'], o.get('titulo_internacional'),
                                  p['obra'], titulo) if x} - {titulo})
    names = {R1E.norm(x) for x in [titulo, *aliases]} | {R1E.norm(p['obra'])}
    reg_names = {}
    for r in reg:
        for x in (r['titulo'], r.get('titulo_original'), *(r.get('aliases') or []), (r.get('registro_origem_integral') or {}).get('nome')):
            if x:
                reg_names.setdefault(R1E.norm(x), set()).add(r['id'])
    dup_reg = sorted({i for n in names for i in reg_names.get(n, ())})
    year_ok = o['ano'] == p['ano']
    checks = dict(titulo=R1E.norm(o['titulo_informado']) in names and R1E.norm(p['obra']) == R1E.norm(o['titulo_informado']),
                  tipo=o['tipo'] == p['tipo'],
                  ano=year_ok or (d['decision_id'] in YEAR_EXCEPTION and o.get('ano_decisao', {}).get('value') == o['ano']),
                  id_free_in_registry=wid not in {r['id'] for r in reg}, not_in_registry=not dup_reg,
                  identity_source=any('identidade' in f['supports'] and f['verificacao'] == 'PAGINA_CONSULTADA' for f in o['fontes']),
                  status_triagem_apta=o['status_triagem'] in ('APTA', 'APTA_COM_RESSALVA'),
                  status_catalogo=o['status_catalogo'] == 'CANDIDATO_NAO_INTEGRADO')
    if not all(checks.values()):
        raise SystemExit(f'PROMOTION_CHECK_FAILED {wid} {checks} reg={dup_reg}')
    rec = dict(schema='REFERENCIA_CANONICA_V1', id=wid, titulo=titulo, titulo_original=o['titulo_original'], aliases=aliases,
               tipo=o['tipo'], ano=o['ano'], origem=o['pais'] or 'NAO_INFORMADO', criadores=o['criadores'],
               origem_catalogo='R1A_WORK_IDENTITY', status_humano=R1E.REVIEW_STATUS,
               extensoes_origem=dict(descricao_factual=o['resumo_factual_curto'], fontes=o['fontes'], riscos=o['riscos'],
                                     transposition_limits=o['transposition_limits'], metadata_pendente=o['metadata_pendente'],
                                     titulo_ptbr_nota=None),
               provenance=dict(status=PROMOTED, editorial_approval=R1E.EDITORIAL_APPROVAL, approval_method=R1E.APPROVAL_METHOD,
                               round=ROUND, decision_round=R1E.ROUND, decided_on=R1E.DECIDED_ON, decision_id=d['decision_id'], candidate_id=cid,
                               candidate_status_triagem=o['status_triagem'], candidate_catalog=IDENTITY.relative_to(ROOT).as_posix(),
                               candidate_catalog_sha256=R1E.sha(IDENTITY),
                               candidate_record_sha256=hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest(),
                               required_by=d['target_id']),
               registro_origem_integral=o)
    log = dict(status=PROMOTED, decision_id=d['decision_id'], work_id=wid, candidate_id=cid, target_id=d['target_id'], checks=checks,
               year_exception=None if year_ok else dict(decision_value=p['ano'], registry_value=o['ano'], basis=o['ano_decisao']),
               duplicates_in_registry=dup_reg)
    return rec, log


def build():
    dec = json.loads(DECISIONS.read_text(encoding='utf-8'))
    if dec['status'] != 'FINAL' or dec['round'] != R1E.ROUND:
        raise SystemExit('DECISIONS_NOT_FINAL')
    held = [d for d in dec['decisions'] if d['decision_id'] in HELD_IDS]
    for d in held:
        if (d['decision'], d['final_status'], d.get('integration'), d.get('work_id')) != ('APPROVE', R1E.REVIEW_STATUS, R1E.HELD, None):
            raise SystemExit(f'NOT_A_HELD_APPROVAL {d["decision_id"]}')
    if len(held) != 2:
        raise SystemExit('HELD_COUNT')
    v2 = json.loads(REGISTRY_V2.read_text(encoding='utf-8'))
    ident = json.loads(IDENTITY.read_text(encoding='utf-8'))
    promoted, logs = [], []
    for d in held:
        rec, log = promote(d, v2['obras'], ident)
        promoted.append(rec)
        logs.append(log)
    v3 = dict(schema='WORK_REGISTRY_V3', status='OFFICIAL_REGISTRY', round=ROUND,
              supersedes=dict(path=REGISTRY_V2.relative_to(ROOT).as_posix(), sha256=R1E.sha(REGISTRY_V2), total=v2['total'],
                              note='Registros do V2 copiados sem alteração (mesmos valores JSON); o V2 permanece versionado como base do RUN3.'),
              promotion_policy='Somente obras exigidas por vínculos aprovados e retidos (APPROVED_PENDING_WORK_IDENTITY) do REFERENCE_EXPANSION_01, '
                               'com identidade registrada no R1A_WORK_IDENTITY (fontes consultadas).',
              total_before=v2['total'], promoted=[r['id'] for r in promoted], total=v2['total'] + len(promoted), promotion_log=logs,
              obras=v2['obras'] + promoted)
    ids = [o['id'] for o in v3['obras']]
    if len(ids) != len(set(ids)):
        raise SystemExit('REGISTRY_DUPLICATE_ID')
    v3_bytes = R1E.jdump(v3)
    by_id = {r['id']: r for r in promoted}
    additions = []
    for d, log in zip(held, logs):
        f, w = d['final'], by_id[log['work_id']]
        additions.append(dict(
            addition_id=f"{d['decision_id']}@{d['target_id']}", target_id=d['target_id'], work_id=w['id'], obra=w['titulo'],
            tipo=w['tipo'], ano=w['ano'], score_editorial=f['score'], conexao_juridica=f['conexao_juridica'], sobre=R1E.sobre_of(w),
            sobre_fonte='registry: descricao_factual da obra (fonte documental do R1A_WORK_IDENTITY)', por_que_esta_aqui=f['por_que_esta_aqui'],
            alcance_neste_dispositivo=f['alcance_neste_dispositivo'], limites=f['limites'], confidence=f['confidence'],
            review_status=R1E.REVIEW_STATUS, approval_method=d['approval_method'], reviewer_decision=d['reviewer_decision'],
            decision=d['decision'], decision_id=d['decision_id'], work_registry_status=PROMOTED,
            external_verification=f.get('external_verification'), external_editorial_support=f.get('external_editorial_support'),
            provenance=dict(round=ROUND, decision_round=R1E.ROUND, decided_on=R1E.DECIDED_ON, decisions_file=DECISIONS.relative_to(ROOT).as_posix(),
                            decisions_sha256=R1E.sha(DECISIONS), identity_file=IDENTITY.relative_to(ROOT).as_posix(),
                            identity_sha256=R1E.sha(IDENTITY))))
    add_bytes = R1E.jdump(dict(
        schema_version=1, norma_id='CF88', round=ROUND, status=R1E.REVIEW_STATUS, reference_type='WORK_REFERENCE',
        policy='Overlay editorial R1: somente as duas aprovações humanas retidas por falta de identidade de obra (P20, P21). Nenhuma relação '
               'nova. Aplicado pelo build RUN5 sobre o RUN4/C3B.2; o overlay RUN3 (CF88_WORK_REFERENCE_ADDITIONS.json) não é alterado.',
        work_registry=REGISTRY_V3.relative_to(ROOT).as_posix(), work_registry_sha256=hashlib.sha256(v3_bytes).hexdigest(), total=len(additions),
        records=additions))
    return v3_bytes, add_bytes


if __name__ == '__main__':
    v3_bytes, add_bytes = build()
    if '--check' in sys.argv:
        ok = REGISTRY_V3.is_file() and REGISTRY_V3.read_bytes() == v3_bytes and ADDITIONS_R1.is_file() and ADDITIONS_R1.read_bytes() == add_bytes
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    REGISTRY_V3.write_bytes(v3_bytes)
    ADDITIONS_R1.write_bytes(add_bytes)
    print(REGISTRY_V3.name, hashlib.sha256(v3_bytes).hexdigest(), ADDITIONS_R1.name, hashlib.sha256(add_bytes).hexdigest())
