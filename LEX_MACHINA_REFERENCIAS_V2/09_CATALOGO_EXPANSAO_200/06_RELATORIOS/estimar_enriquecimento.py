"""Estimate (not execute) evidence-card enrichment needs for usable works.

Transparent heuristic over the dossiers; produces ESTIMATIVA_ENRIQUECIMENTO.json.
No card is created or changed.
"""
import collections, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cat = json.loads((ROOT / '07_CATALOGO_CANDIDATO' / 'CATALOGO_EXPANSAO_200.json').read_text(encoding='utf-8'))

# Works whose already-consulted official material visibly documents several independent systems/arguments/units.
RICOS = {
    1: 'RPG com sistema de habilidades, subornos, interrogatórios e escolhas políticas documentados na página oficial.',
    25: 'Grande estratégia: sucessão dinástica, títulos, territórios e herdeiros.',
    26: 'Grande estratégia: reforma constitucional, tributação, trabalho, diplomacia.',
    27: 'Grande estratégia: território, diplomacia, comércio, religião.',
    28: 'Grande estratégia: produção industrial, alianças, guerra.',
    29: 'Grande estratégia: assentamentos, tecnologia, diplomacia/conquista.',
    30: 'Simulação política: candidatura, legislação, orçamento.',
    31: 'Simulação política: sistemas eleitorais, gerrymandering, parlamento, orçamento.',
    42: 'Gestão urbana: conselho de facções, alocação de calor, pesquisa, leis.',
    44: 'Gestão policial: equipe, emergências, investigação, depoimento como testemunha, máfia/prefeitura.',
    102: 'Antologia de 3 temporadas; só a 1ª documentada.',
    138: 'Série documental em episódios independentes (VW, HSBC, payday loans, Trump Inc.).',
    161: 'Oito princípios já listados num card; capítulos permitem cards por princípio só se houver fonte por princípio.',
    164: 'Obra em dois volumes com temas distintos (associações, centralização, maioria).',
    165: 'Três partes independentes: antissemitismo, imperialismo, totalitarismo.',
    167: 'Instituições inclusivas × extrativas; casos históricos comparados.',
    169: 'Casos independentes (Tanzânia, URSS, Brasília, China).',
    179: 'Conceitos independentes (excedente comportamental, mercados de futuros comportamentais).',
}
estim = []
for w in cat['obras']:
    n, k = w['candidate_number'], len(w['evidencias'])
    types = {c['content_type'] for c in w['evidencias']}
    if n in RICOS:
        cls, why = '+2_OU_MAIS', RICOS[n]
    elif k >= 2:
        cls, why = 'COMPLETA_PROVAVEL', 'Já possui 2+ cards de fatos independentes.'
    elif w['tipo'] == 'JOGO' and types == {'MECANICA_INTERATIVA'}:
        cls, why = '+1', 'Jogo com card só mecânico; a descrição oficial costuma trazer premissa narrativa independente.'
    elif w['tipo'] == 'JOGO' and types == {'EVENTO_NARRATIVO'}:
        cls, why = '+1', 'Jogo com card só narrativo; verificar mecânica repetível documentada.'
    elif w['tipo'] in ('DOCUMENTÁRIO', 'LIVRO'):
        cls, why = '+1', 'Obra não ficcional com um único card; costuma haver segundo fato/argumento independente na fonte oficial.'
    else:
        cls, why = 'COMPLETA_PROVAVEL', 'Ficção com premissa única bem delimitada; card adicional só se a fonte trouxer fato independente.'
    estim.append(dict(candidate_number=n, work_id=w['work_id'], titulo=w['titulo'], tipo=w['tipo'], cards_atuais=k, estimativa=cls, justificativa=why))
cnt = collections.Counter(e['estimativa'] for e in estim)
por_tipo = {t: dict(collections.Counter(e['estimativa'] for e in estim if e['tipo'] == t)) for t in sorted({e['tipo'] for e in estim})}
out = dict(aviso='Estimativa heurística. NÃO é meta e NÃO foi executada. Cada card adicional exige fato independente e fonte concreta.',
           total_obras=len(estim), cards_atuais=sum(e['cards_atuais'] for e in estim), contagem=dict(cnt), por_tipo=por_tipo,
           cards_adicionais_estimados=dict(minimo=cnt['+1'] + 2 * cnt['+2_OU_MAIS'], maximo_indicativo=cnt['+1'] + 3 * cnt['+2_OU_MAIS']),
           obras=estim)
(ROOT / '06_RELATORIOS' / 'ESTIMATIVA_ENRIQUECIMENTO.json').write_bytes((json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))
print(dict(cnt), por_tipo, out['cards_adicionais_estimados'])
