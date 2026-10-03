# -*- coding: utf-8 -*-
"""REFERENCE_EXPANSION_01 (round 1): applies the final human editorial decisions to the 25 proposals of
REFERENCE_EXPANSION_CANDIDATES.json (evidence, never edited) and writes:

  REFERENCE_COVERAGE_AUDIT/REFERENCE_EXPANSION_ROUND1_DECISIONS.json   25 decisions (original proposal + final decision)
  REFERENCE_REGISTRY/WORK_REGISTRY_V2.json                            official registry = the 69 works of CATALOGO_69_CANONICO
                                                                      (byte-preserved records) + works promoted from the
                                                                      candidate catalog ONLY when an approved link needs them
  LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json           approved WORK_REFERENCE links (Reference Engine overlay)
  REFERENCE_COVERAGE_AUDIT/REFERENCE_EXPANSION_REVIEW.md               checkboxes marked; original proposal text kept

Authority: decisions of Arthur (ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW), transcribed below. Two approved proposals whose work
has no identity in any repository catalog (SOS Saude/Sicko, Pro Dia Nascer Feliz) are HELD (APPROVED_PENDING_WORK_IDENTITY):
no id is invented, so they do not enter the registry nor RUN3 (decision of Arthur, 2026-10-02).
CATALOGO_69_CANONICO.json is protected (CLEANUP_AUDIT/PROTEGIDO_NAO_TOCAR.json) and is only read.
Deterministic (no wall clock). Usage: python apply_reference_expansion_round1.py
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CANDIDATES = HERE / 'REFERENCE_EXPANSION_CANDIDATES.json'
REVIEW = HERE / 'REFERENCE_EXPANSION_REVIEW.md'
DECISIONS = HERE / 'REFERENCE_EXPANSION_ROUND1_DECISIONS.json'
REGISTRY69 = ROOT / 'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json'
CAND_CATALOG = ROOT / 'LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json'
REGISTRY_V2 = ROOT / 'REFERENCE_REGISTRY/WORK_REGISTRY_V2.json'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json'

DECIDED_ON = '2026-10-02'
ROUND = 'REFERENCE_EXPANSION_01'
REVIEW_STATUS = 'HUMAN_APPROVED_REFERENCE_V1'
APPROVAL_METHOD = 'ASSISTED_RISK_BASED_HUMAN_REVIEW'
REVIEWER_DECISION = 'ARTHUR_AUTHORIZED_CHATGPT_EDITORIAL_REVIEW'
EDITORIAL_APPROVAL = 'ARTHUR_AUTHORIZED_CHATGPT_REVIEW'
PROMOTED = 'PROMOTED_FROM_EXPANSION_CATALOG'
HELD = 'APPROVED_PENDING_WORK_IDENTITY'
REJECTED = 'REJECTED_EDITORIAL_WEAK_CONNECTION'

# ---- final decisions (key = (target_id, obra) of the proposal) --------------------------------------------------------
APPROVE = {
    ('CF88:ART.37:CAPUT', 'Os Donos do Poder'), ('CF88:ART.37:CAPUT', 'Raízes do Brasil'),
    ('CF88:ART.43:CAPUT', 'Formação Econômica do Brasil'), ('CF88:ART.43:PAR.2:INC.IV', 'Vidas Secas'),
    ('CF88:ART.201:INC.I', 'Eu, Daniel Blake'), ('CF88:ART.86:CAPUT', 'Excelentíssimos'), ('CF88:ART.52:INC.I', 'O Processo'),
    ('CF88:ART.58:PAR.3', 'Tropa de Elite 2: O Inimigo Agora É Outro'), ('CF88:ART.134:CAPUT', 'Luta por Justiça (Just Mercy)'),
    ('CF88:ART.144:PAR.5', 'Tropa de Elite'), ('CF88:ART.144:PAR.7', 'A Escuta'), ('CF88:ART.145:PAR.1', 'O Triunfo da Injustiça'),
    ('CF88:ART.182:CAPUT', 'Citizen Jane: Battle for the City'), ('CF88:ART.182:PAR.1', 'Cities: Skylines'),
    ('CF88:ART.184:CAPUT', 'Cabra Marcado para Morrer'), ('CF88:ART.192', 'A Grande Aposta'), ('CF88:ART.196', 'SOS Saúde (Sicko)'),
    ('CF88:ART.206:INC.I', 'Pro Dia Nascer Feliz'), ('CF88:ART.215:PAR.1', 'Never Alone (Kisima Inŋitchuŋa)'),
    ('CF88:ART.231:CAPUT', 'Martírio'),
}
ADJUST = {
    ('CF88:ART.62:CAPUT', 'Suzerain'): dict(
        score=7.4,
        conexao_juridica='Medida provisória como instrumento normativo do Presidente em situação de relevância e urgência, sujeito ao controle do Congresso Nacional.',
        por_que_esta_aqui='Suzerain coloca o jogador na posição de Presidente e permite o uso de atos executivos e decretos dentro de um sistema de freios institucionais. A experiência ajuda a visualizar a tensão entre rapidez decisória do Executivo e controle pelos demais Poderes, que também está presente no regime constitucional das medidas provisórias.',
        alcance_neste_dispositivo='Serve como analogia institucional. O sistema do jogo não reproduz o regime brasileiro das medidas provisórias, seus prazos, limitações materiais, trancamento de pauta ou processo de conversão em lei.',
        limites='Sistema político fictício; conexão analógica (ação normativa urgente do Executivo x controle institucional), não um regime de medida provisória.',
        score_justificativa='Conexão analógica confirmada externamente: o jogo possui decretos presidenciais, controle judicial e possibilidade de reação/superação institucional pelo Legislativo. Não reproduz o regime brasileiro das medidas provisórias.',
        confidence='HIGH_AFTER_EXTERNAL_VERIFICATION',
        external_verification=dict(
            status='VERIFIED_EXTERNALLY', verified_by=EDITORIAL_APPROVAL, verified_on=DECIDED_ON,
            confirmed=['mecanismos de decretos presidenciais', 'controle judicial',
                       'possibilidade de reação/superação institucional pelo Legislativo'],
            not_claimed='O jogo NÃO possui "medida provisória brasileira"; a conexão é analógica.'),
        why='Score ajustado 6.8 -> 7.4 após verificação externa da mecânica de decretos; textos finais definidos na decisão.'),
    ('ADCT:ART.68', 'Torto Arado'): dict(
        score=9.2,
        conexao_juridica='Propriedade definitiva das terras ocupadas por remanescentes das comunidades dos quilombos (ADCT, art. 68).',
        confidence='HIGH',
        external_editorial_support=dict(
            kind='EXTERNAL_EDITORIAL_SUPPORT',
            note='Existe produção acadêmica jurídica relacionando Torto Arado, quilombos, constitucionalismo e o art. 68 do ADCT.',
            role='Apoio editorial à força da conexão; NÃO é fonte da obra nem evidência da ficha.',
            recorded_by=EDITORIAL_APPROVAL, recorded_on=DECIDED_ON),
        why='Score ajustado 8.4 -> 9.2; primeira WORK_REFERENCE do ADCT.'),
    ('CF88:ART.7:INC.XXXIII', 'Frostpunk'): dict(
        score=7.8,
        limites='Mundo fictício. A mecânica ajuda a problematizar o trabalho infantil, mas não reproduz as idades, exceções e o contrato de aprendizagem previstos no direito brasileiro.',
        confidence='HIGH_AFTER_EXTERNAL_VERIFICATION',
        external_verification=dict(
            status='VERIFIED_EXTERNALLY', verified_by=EDITORIAL_APPROVAL, verified_on=DECIDED_ON,
            confirmed=['o jogador pode permitir trabalho infantil', 'há gradação entre trabalhos considerados seguros e trabalhos perigosos',
                       'a escolha possui consequências']),
        why='Score ajustado 7.2 -> 7.8; mecânica confirmada externamente; LIMITES atualizados.'),
}
REJECT = {
    ('CF88:ART.76', 'Borgen'): 'A série retrata parlamentarismo dinamarquês. A ligação com o art. 76 depende de comparação por contraste com o presidencialismo brasileiro. Associação excessivamente indireta.',
    ('CF88:ART.142:CAPUT', 'Argentina, 1985'): 'A obra trata primordialmente do julgamento e responsabilização de integrantes das juntas militares argentinas. Não representa adequadamente a finalidade, organização ou regime constitucional das Forças Armadas previsto no art. 142.',
}
GAPS = {
    'CF88:ART.98': 'Nenhuma obra adequada foi encontrada sem forçar vínculo (juizados especiais / justiça de paz).',
    'CF88:ART.202': 'Nenhuma obra adequada foi encontrada sem forçar vínculo (previdência complementar privada).',
}
# Approved proposals whose work has to be promoted: the candidate-catalog id is parsed from the proposal's candidate_catalog_id
# ("CAND200-200 (EXP2-LIV-040, ...)") and must exist in CATALOGO_EXPANSAO_200 with the same title/type/year. Without it: HELD.
PT_TITLES = {'EXP2-FIL-006': ('Luta por Justiça', 'Título brasileiro definido na decisão editorial (proposta "Luta por Justiça (Just Mercy)"); o catálogo candidato não confirmou título PT-BR.')}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jdump(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def norm(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def proposals():
    c = json.loads(CANDIDATES.read_text(encoding='utf-8'))
    out = c['priority'] + c['additional']
    assert len(out) == 25 and c['counts']['total'] == 25
    return c, out


def decide(i, p):
    key = (p['target_id'], p['obra'])
    final = dict(score=p['score_proposto'], conexao_juridica=p['conexao_juridica'], por_que_esta_aqui=p['por_que_esta_aqui'],
                 alcance_neste_dispositivo=p['alcance_neste_dispositivo'], limites=p['limites_de_transposicao'],
                 score_justificativa=p['score_justificativa'], confidence=p['confidence'])
    rec = dict(decision_id=f'{ROUND}-P{i:02d}', proposal_number=i, target_id=p['target_id'], obra=p['obra'], tipo=p['tipo'], ano=p['ano'],
               original_proposal=p)
    hits = (key in APPROVE) + (key in ADJUST) + (key in REJECT)
    if hits != 1:
        raise SystemExit(f'DECISION_NOT_UNIQUE {key}')
    if key in REJECT:
        rec.update(decision='REJECT', final_status=REJECTED, reason=REJECT[key], final=None, integration='NOT_INTEGRATED')
        return rec
    if key in ADJUST:
        adj = dict(ADJUST[key])
        why = adj.pop('why')
        extra = {k: adj.pop(k) for k in ('external_verification', 'external_editorial_support') if k in adj}
        before = dict(final)
        final.update(adj)
        final.update(extra)
        rec.update(decision='ADJUST_APPROVE', adjustment=why, changed_fields=sorted(k for k in adj if adj[k] != before[k]))
    else:
        rec.update(decision='APPROVE')
    rec.update(final_status=REVIEW_STATUS, final=final, approval_method=APPROVAL_METHOD, reviewer_decision=REVIEWER_DECISION)
    return rec


def promote(p, reg, cand):
    """Approved NEW_CANDIDATE proposal -> (registry record, validation) or (None, reason) when the work has no catalog identity."""
    m = re.match(r'^(CAND200-\d+) \((EXP2-[A-Z]+-\d+),', p['candidate_catalog_id'] or '')
    if not m:
        return None, dict(status=HELD, reason='Obra inexistente no catálogo candidato (CATALOGO_EXPANSAO_200) e no registry oficial: '
                                              'candidate_catalog_id nulo na proposta. Nenhum ID é inventado.')
    cid, wid = m.groups()
    rows = [o for o in cand['obras'] if o['candidate_id'] == cid]
    if len(rows) != 1 or rows[0]['work_id'] != wid:
        raise SystemExit(f'CANDIDATE_ID_MISMATCH {cid} {wid}')
    o = rows[0]
    pt = PT_TITLES.get(wid)
    titulo = pt[0] if pt else o['titulo']
    aliases = sorted({x for x in (o['titulo'], o['titulo_original'], o['titulo_informado'], o['titulo_ptbr'], p['obra'], titulo) if x} - {titulo})
    # identity / duplicity against the official registry (titles, original titles, aliases) and inside the candidate catalog
    names = {norm(x) for x in [titulo, *aliases]} | {norm(p['obra'])}
    reg_names = {}
    for r in reg:
        for x in (r['titulo'], r.get('titulo_original'), (r.get('registro_origem_integral') or {}).get('nome')):
            if x:
                reg_names.setdefault(norm(x), set()).add(r['id'])
    dup_reg = sorted({i for n in names for i in reg_names.get(n, ())})
    dup_cand = sorted(x['candidate_id'] for x in cand['obras'] if x['candidate_id'] != cid and
                      ({norm(x['titulo']), norm(x['titulo_original'])} & {norm(o['titulo']), norm(o['titulo_original'])}))
    checks = dict(titulo=norm(o['titulo']) in names, tipo=o['tipo'] == p['tipo'], ano=o['ano'] == p['ano'],
                  id_free_in_registry=wid not in {r['id'] for r in reg}, not_in_registry=not dup_reg, unique_in_candidate_catalog=not dup_cand,
                  status_triagem_apta=o['status_triagem'] in ('APTA', 'APTA_COM_RESSALVA'),
                  status_catalogo=o['status_catalogo'] == 'CANDIDATO_NAO_INTEGRADO')
    if not all(checks.values()):
        raise SystemExit(f'PROMOTION_CHECK_FAILED {wid} {checks} reg={dup_reg} cand={dup_cand}')
    rec = dict(schema='REFERENCIA_CANONICA_V1', id=wid, titulo=titulo, titulo_original=o['titulo_original'], aliases=aliases,
               tipo=o['tipo'], ano=o['ano'], origem=o['pais'] or 'NAO_INFORMADO', criadores=o['criadores'],
               origem_catalogo='CATALOGO_EXPANSAO_200', status_humano=REVIEW_STATUS,
               extensoes_origem=dict(descricao_factual=o['resumo_factual_curto'], fontes=o['fontes'], riscos=o['riscos'],
                                     transposition_limits=o['transposition_limits'], metadata_pendente=o['metadata_pendente'],
                                     titulo_ptbr_nota=pt[1] if pt else None),
               provenance=dict(status=PROMOTED, editorial_approval=EDITORIAL_APPROVAL, approval_method=APPROVAL_METHOD, round=ROUND,
                               decided_on=DECIDED_ON, candidate_id=cid, candidate_status_triagem=o['status_triagem'],
                               candidate_catalog=CAND_CATALOG.relative_to(ROOT).as_posix(), candidate_catalog_sha256=sha(CAND_CATALOG),
                               candidate_record_sha256=hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest(),
                               required_by=p['target_id']),
               registro_origem_integral=o)
    return rec, dict(status=PROMOTED, work_id=wid, candidate_id=cid, checks=checks, duplicates_in_registry=dup_reg,
                     duplicates_in_candidate_catalog=dup_cand, link_score=None)


def sobre_of(work):
    e = work.get('extensoes_origem') or {}
    s = e.get('descricao_factual') or (work.get('registro_origem_integral') or {}).get('resumo')
    if not s:
        raise SystemExit(f'WORK_WITHOUT_FACTUAL_DESCRIPTION {work["id"]}')
    return s


def mark_review(decisions):
    md = REVIEW.read_text(encoding='utf-8')
    if 'DECISÃO FINAL (REFERENCE_EXPANSION_01' in md:
        return md                                                   # already applied (idempotent)
    box = '- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR'
    parts = md.split(box)
    if len(parts) != 26:
        raise SystemExit('REVIEW_CHECKBOXES_NOT_FOUND')
    out = [parts[0]]
    for d, rest in zip(decisions, parts[1:]):
        mark = {'APPROVE': '- [x] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR', 'ADJUST_APPROVE': '- [x] APROVAR   - [x] AJUSTAR   - [ ] REJEITAR',
                'REJECT': '- [ ] APROVAR   - [ ] AJUSTAR   - [x] REJEITAR'}[d['decision']]
        f = d['final']
        lines = [mark, '', f"> **DECISÃO FINAL (REFERENCE_EXPANSION_01, {DECIDED_ON}):** `{d['decision']}` · `{d['final_status']}` · {REVIEWER_DECISION}"]
        if d['decision'] == 'REJECT':
            lines.append(f"> MOTIVO: {d['reason']} Vínculo não criado.")
        else:
            if d['decision'] == 'ADJUST_APPROVE':
                lines.append(f"> AJUSTE: {d['adjustment']} SCORE FINAL: **{f['score']}** (proposto: {d['original_proposal']['score_proposto']}). CONFIDENCE: {f['confidence']}.")
                for k, lab in (('conexao_juridica', 'CONEXÃO JURÍDICA FINAL'), ('por_que_esta_aqui', 'POR QUE ESTÁ AQUI (final)'),
                               ('alcance_neste_dispositivo', 'ALCANCE (final)'), ('limites', 'LIMITES (final)')):
                    if f.get(k) and f[k] != d['original_proposal'].get({'limites': 'limites_de_transposicao'}.get(k, k)):
                        lines.append(f'> {lab}: {f[k]}')
            else:
                lines.append(f"> SCORE FINAL: **{f['score']}** (sem ajuste).")
            if d['integration'] == HELD:
                lines.append(f"> INTEGRAÇÃO: `{HELD}` — {d['integration_reason']} Fora do RUN3.")
            else:
                lines.append(f"> INTEGRAÇÃO: RUN3 · obra `{d['work_id']}` ({d['work_registry_status']}).")
        out.append('\n'.join(lines) + rest)
    md = ''.join(out)
    md = md.replace('# REFERÊNCIAS — candidatos de expansão (PENDING_HUMAN_REVIEW)',
                    '# REFERÊNCIAS — candidatos de expansão (DECIDIDO — REFERENCE_EXPANSION_01)\n\n'
                    f'> Decisões humanas aplicadas em {DECIDED_ON} (`REFERENCE_EXPANSION_ROUND1_DECISIONS.json`): 20 APROVAR, 3 AJUSTAR E APROVAR, '
                    '2 REJEITAR. 21 vínculos integrados ao RUN3; 2 aprovados ficam retidos (`APPROVED_PENDING_WORK_IDENTITY`: obra sem identidade em '
                    'nenhum catálogo). O texto original de cada proposta foi preservado abaixo; a decisão final aparece após as caixas.', 1)
    md = md.rstrip('\n') + '\n\n## Lacunas confirmadas (REFERENCE_EXPANSION_01)\n\n' + ''.join(
        f'- **{t}:** `CONFIRMED_REFERENCE_GAP` — {r} Não preencher artificialmente.\n' for t, r in GAPS.items())
    return md


def main():
    c, props = proposals()
    reg_doc = json.loads(REGISTRY69.read_text(encoding='utf-8'))
    reg = reg_doc['obras']
    reg_by_id = {o['id']: o for o in reg}
    cand = json.loads(CAND_CATALOG.read_text(encoding='utf-8'))
    decisions, promoted, additions, promotion_log = [], [], [], []
    for i, p in enumerate(props, 1):
        d = decide(i, p)
        if d['decision'] != 'REJECT':
            if p['source'] == 'EXISTING_CATALOG':
                w = reg_by_id[p['work_id']]
                if (w['titulo'], w['tipo']) != (p['obra'], p['tipo']):
                    raise SystemExit(f'REGISTRY_MISMATCH {p["work_id"]}')
                d.update(work_id=w['id'], work_registry_status='EXISTING_WORK_REUSE', integration='RUN3')
            else:
                rec, log = promote(p, reg, cand)
                log.update(proposal=d['decision_id'], obra=p['obra'], target_id=p['target_id'], link_score=d['final']['score'])
                promotion_log.append(log)
                if rec is None:
                    d.update(work_id=None, work_registry_status='NO_WORK_IDENTITY', integration=HELD, integration_reason=log['reason'])
                else:
                    if rec['id'] not in {x['id'] for x in promoted}:
                        promoted.append(rec)
                    d.update(work_id=rec['id'], work_registry_status=PROMOTED, integration='RUN3')
        decisions.append(d)

    counts = {k: sum(1 for d in decisions if d['decision'] == k) for k in ('APPROVE', 'ADJUST_APPROVE', 'REJECT')}
    if counts != {'APPROVE': 20, 'ADJUST_APPROVE': 3, 'REJECT': 2}:
        raise SystemExit(f'DECISION_COUNTS {counts}')

    # ---- registry V2 (69 records byte-equal + promoted)
    reg_v2 = dict(schema='WORK_REGISTRY_V2', status='OFFICIAL_REGISTRY', round=ROUND,
                  base=dict(path=REGISTRY69.relative_to(ROOT).as_posix(), sha256=sha(REGISTRY69), total=len(reg), protected=True,
                            note='Registro original de 69 obras preservado sem alteração; os registros abaixo são cópias exatas.'),
                  promotion_policy='Somente obras exigidas por vínculos aprovados no REFERENCE_EXPANSION_01 e com identidade real no catálogo candidato.',
                  total_before=len(reg), promoted=[r['id'] for r in promoted], total=len(reg) + len(promoted),
                  obras=reg + promoted)
    ids = [o['id'] for o in reg_v2['obras']]
    if len(ids) != len(set(ids)):
        raise SystemExit('REGISTRY_DUPLICATE_ID')

    # ---- engine overlay: one record per integrated link
    by_id = {o['id']: o for o in reg_v2['obras']}
    for d in decisions:
        if d.get('integration') != 'RUN3':
            continue
        f, w = d['final'], by_id[d['work_id']]
        additions.append(dict(
            addition_id=f"{d['decision_id']}@{d['target_id']}", target_id=d['target_id'], work_id=w['id'], obra=w['titulo'],
            tipo=w['tipo'], ano=w['ano'], score_editorial=f['score'], conexao_juridica=f['conexao_juridica'], sobre=sobre_of(w),
            sobre_fonte='registry: descricao_factual da obra (fonte documental do catálogo)', por_que_esta_aqui=f['por_que_esta_aqui'],
            alcance_neste_dispositivo=f['alcance_neste_dispositivo'], limites=f['limites'], confidence=f['confidence'],
            review_status=REVIEW_STATUS, approval_method=APPROVAL_METHOD, reviewer_decision=REVIEWER_DECISION,
            decision=d['decision'], decision_id=d['decision_id'], work_registry_status=d['work_registry_status'],
            external_verification=f.get('external_verification'), external_editorial_support=f.get('external_editorial_support'),
            provenance=dict(round=ROUND, decided_on=DECIDED_ON, proposal_file=CANDIDATES.relative_to(ROOT).as_posix(),
                            proposal_sha256=sha(CANDIDATES), decisions_file=DECISIONS.relative_to(ROOT).as_posix())))
    keys = [(a['target_id'], a['work_id']) for a in additions]
    if len(keys) != len(set(keys)):
        raise SystemExit('ADDITION_DUPLICATE')

    doc = dict(schema_version=1, round=ROUND, status='FINAL', decided_on=DECIDED_ON, authority=REVIEWER_DECISION,
               evidence=dict(proposals=CANDIDATES.relative_to(ROOT).as_posix(), proposals_sha256=sha(CANDIDATES),
                             review=REVIEW.relative_to(ROOT).as_posix()),
               counts=dict(proposals=len(decisions), **counts, integrated_run3=len(additions),
                           held_pending_work_identity=sum(1 for d in decisions if d.get('integration') == HELD),
                           promoted_works=len(promoted)),
               confirmed_reference_gaps=[dict(target_id=t, status='CONFIRMED_REFERENCE_GAP', reason=r) for t, r in GAPS.items()],
               promotion_log=promotion_log, decisions=decisions)
    DECISIONS.write_bytes(jdump(doc))
    REGISTRY_V2.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_V2.write_bytes(jdump(reg_v2))
    ADDITIONS.write_bytes(jdump(dict(
        schema_version=1, norma_id='CF88', round=ROUND, status=REVIEW_STATUS, reference_type='WORK_REFERENCE',
        policy='Overlay editorial de vínculos obra <-> dispositivo aprovados por revisão humana. O catálogo canônico não é editado; o '
               'reference_engine adiciona cada registro como um vínculo WORK_REFERENCE (fail closed: target inexistente, target não vigente, '
               'obra fora do registry oficial ou vínculo já existente interrompem o build).',
        work_registry=REGISTRY_V2.relative_to(ROOT).as_posix(), work_registry_sha256=sha(REGISTRY_V2), total=len(additions),
        records=additions)))
    REVIEW.write_bytes(mark_review(decisions).encode('utf-8'))
    print(json.dumps(dict(doc['counts'], registry_before=len(reg), registry_after=reg_v2['total'], promoted=reg_v2['promoted'],
                          held=[d['obra'] for d in decisions if d.get('integration') == HELD]), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
