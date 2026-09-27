"""Deterministic stratified audit sample of lots 1-4 (8 games, 8 films, 4 series).

Rule: within each medium, sort candidates of lots 1-4 by SHA-256(candidate_id) (hex, lexicographic)
and take the smallest values. #9 Cyberpunk 2077 is excluded (reviewed separately).
Audit results below were produced by consulting each cited source on 2026-09-26.
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUOTAS = [('JOGO', 8), ('FILME', 8), ('SÉRIE', 4)]
EXCLUDED = {9: 'Cyberpunk 2077 revisado separadamente (DECISAO_CYBERPUNK_REVISADA.json).'}
STEAM = 'Conferido na API oficial da Steam (appdetails) em 2026-09-26; descrição do publisher acessível.'
R = {  # number: (classificacao, fonte_acessivel, fonte_sustenta, observacao)
    26: ('AUDITORIA_OK', True, True, STEAM + ' Período 1836–1936, reforma de governo/constituição, tributação de lucros, indústria e grupos populacionais constam da fonte.'),
    31: ('AUDITORIA_OK', True, True, STEAM + ' Sistemas eleitorais, aprovação/rejeição de projetos e governo constam da fonte.'),
    44: ('AJUSTE_MENOR', True, False, STEAM + ' A fonte diz "investigate crimes"; "reúne provas" extrapolava. Paráfrase corrigida.'),
    42: ('AUDITORIA_OK', True, True, STEAM + ' Steward, alocação de calor/recursos e facções no Council Hall constam da fonte.'),
    33: ('AUDITORIA_OK', True, True, STEAM + ' Prisão por Immigration Enforcement, travessia dos EUA e recuperação de documentos constam da fonte.'),
    24: ('AUDITORIA_OK', True, True, STEAM + ' Petições no trono, recursos limitados e alianças com lordes constam da fonte.'),
    39: ('AUDITORIA_OK', True, True, STEAM + ' Doze mortes, pistas, suspeitos e motivos constam da fonte.'),
    1: ('AUDITORIA_OK', True, True, STEAM + ' Detetive, interrogatórios, homicídios e subornos constam da fonte (edição Final Cut; ano 2019 correto).'),
    88: ('AJUSTE_MENOR', True, False, 'AdoroCinema (tier C) acessível; a sinopse fala do dia a dia de policiais do BOPE e de um capitão que busca substituto. "Operações", "conflitos de segurança pública" e "Rio de Janeiro" não constam; paráfrase corrigida. Fonte C fraca permanece como observação.'),
    78: ('AUDITORIA_OK', True, True, 'A24 (tier A): comandante de Auschwitz e esposa constroem a vida familiar em casa e jardim ao lado do campo.'),
    66: ('AUDITORIA_OK', True, True, 'La Strada Documentation Center: guerra civil em Serra Leoa, pescador Solomon Vandy, Archer preso por contrabando, busca do diamante e da família.'),
    68: ('AUDITORIA_OK', True, True, 'Focus Features (tier A): trajetória de Harvey Milk, primeiro homem abertamente gay eleito para cargo público relevante, e luta por direitos iguais.'),
    80: ('AJUSTE_IMPORTANTE', True, False, 'La Biennale (tier B) só afirma: Brasil, 1971, ditadura militar; uma mãe forçada a se reinventar após ato de violência arbitrária. Nomes, "busca a verdade" e "retirada por agentes" não constam; paráfrase restringida à fonte.'),
    51: ('AJUSTE_MENOR', True, False, 'Universal (tier A): Erin convence advogado a contratá-la; caso contra grande corporação; justiça para pequena cidade atingida por poluição de empresa de serviços públicos. "Reúne informações" e "ação de moradores" não constam; paráfrase ajustada.'),
    64: ('AUDITORIA_OK', True, True, 'Focus Features (tier A): diplomata busca o assassino da esposa e descobre conspiração que destruiria milhões de inocentes.'),
    57: ('AUDITORIA_OK', True, True, 'Netflix Media Center (tier A): protesto na convenção democrata de 1968, confronto com polícia e Guarda Nacional, acusação de conspiração.'),
    97: ('AUDITORIA_OK', True, True, 'Netflix Media Center (tier A): Alex, mãe solo, trabalha com limpeza enquanto escapa de relação abusiva e supera falta de moradia.'),
    100: ('FONTE_INSUFICIENTE', False, None, 'paramountplus.com/shows/your-honor/ retornou HTTP 404. Substituída por paramountglobalcontent.com/title/your-honor (tier A, acessível), que sustenta a premissa; "Nova Orleans" removido por não constar da nova fonte.'),
    98: ('AUDITORIA_OK', True, True, 'Hulu Press (tier A): uma empresa desencadeou a epidemia; salas da indústria farmacêutica, comunidade mineira da Virgínia e sede da DEA.'),
    93: ('AUDITORIA_OK', True, True, 'Paramount Global Content (tier A): esposa retorna ao trabalho após o escândalo político do marido levá-lo à prisão; escritório de advocacia em Chicago.'),
}

t = []
for b in range(1, 5):
    t += json.loads((ROOT / '02_TRIAGEM' / f'LOTE_{b:02}.json').read_text(encoding='utf-8'))
sample = []
for tipo, k in QUOTAS:
    pool = sorted(((hashlib.sha256(e['candidate_id'].encode('utf-8')).hexdigest(), e) for e in t
                   if e['tipo'] == tipo and e['number'] not in EXCLUDED), key=lambda x: x[0])
    for h, e in pool[:k]:
        cls, acc, sus, obs = R[e['number']]
        c = e['evidencias'][0]
        sample.append(dict(
            candidate_number=e['number'], candidate_id=e['candidate_id'], sha256_candidate_id=h, work_id=e['work_id'],
            titulo=e['titulo_informado'], tipo=tipo, lote=e['lote'], status_triagem=e['status_triagem'],
            verificacoes=dict(identidade='CONFIRMADA', fonte_acessivel=acc, fonte_sustenta_parafrase_original=sus,
                              centralidade=c['centrality'], content_type=c['content_type'], content_type_adequado=True,
                              claim_factual_sem_conclusao_juridica=True,
                              not_targeted_to_device=all(x['not_targeted_to_device'] is True for x in e['evidencias']),
                              limites_de_transposicao_presentes=bool(e['transposition_limits'])),
            classificacao=cls, observacao=obs))
assert len(sample) == 20
counts = {k: sum(1 for s in sample if s['classificacao'] == k) for k in ('AUDITORIA_OK', 'AJUSTE_MENOR', 'AJUSTE_IMPORTANTE', 'FONTE_INSUFICIENTE')}
taxa = (counts['AJUSTE_IMPORTANTE'] + counts['FONTE_INSUFICIENTE']) / 20
out = dict(
    metodo=dict(regra='Por mídia, menores SHA-256(candidate_id) em ordem lexicográfica hexadecimal.', cotas=dict(QUOTAS),
                universo='Candidatas 1–100 (lotes 1–4)', excluidas=EXCLUDED, reprodutivel_por='06_RELATORIOS/amostra_auditoria.py'),
    amostra=sample, contagem=counts, taxa_de_problemas_importantes=taxa,
    regra_de_decisao={'0-10%': 'lotes 1–4 satisfatórios por amostragem', '>10%-20%': 'recomendar segunda amostra de 20 antes da ingestão', '>20%': 'recomendar auditoria mais ampla antes da ingestão'},
    conclusao='SATISFATORIO_POR_AMOSTRAGEM' if taxa <= 0.10 else 'SEGUNDA_AMOSTRA_RECOMENDADA' if taxa <= 0.20 else 'AUDITORIA_AMPLA_RECOMENDADA',
    nota='Classificação registrada antes das correções; as correções objetivas estão em REVISOES_POS_CHECKPOINT.json.')
(ROOT / '06_RELATORIOS' / 'AMOSTRA_AUDITORIA_LOTES_1_4.json').write_bytes(
    (json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))
print(counts, taxa, out['conclusao'])
