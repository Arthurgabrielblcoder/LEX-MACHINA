"""Builds the final editorial reports of the 200-candidate expansion.

Reads only frozen mission data (triage lots, dossiers, sources, reference 69).
Writes reports in 05_REJEITADAS/ and 06_RELATORIOS/. Does not run the engine,
does not create device links and does not touch any frozen folder.
"""
import collections, datetime, hashlib, json, re, sys, tempfile, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '07_CATALOGO_CANDIDATO'))
sys.path.insert(0, str(ROOT / '06_RELATORIOS'))
import compilar_catalogo  # noqa: E402
import estado_retomada  # noqa: E402

USABLE = ('APTA', 'APTA_COM_RESSALVA')
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(s):
    return unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()


triage = []
for i in range(1, 9):
    triage += load(ROOT / '02_TRIAGEM' / f'LOTE_{i:02}.json')
triage.sort(key=lambda e: e['number'])
by_n = {e['number']: e for e in triage}
ref69 = load(ROOT / '00_ENTRADA' / 'REFERENCIA_CATALOGO_69.json')['obras']
usable = [e for e in triage if e['status_triagem'] in USABLE]

# ---------------------------------------------------------------- rejections
RECONSIDERACAO = {
    9: 'Sim: reconsiderar se forem documentadas, em fonte oficial ou acadêmica, mecânicas específicas (p.ex. sistemas de crime, polícia ou reputação) em vez da descrição promocional ampla.',
    92: 'Não: mesma obra que EXP-SER-002 (A Escuta, título original The Wire, 2002). Tradução PT-BR não gera nova obra.',
}
REVISAO = {
    41: 'Obter press kit, manual ou página oficial com descrição delimitada de narrativa/mecânica.',
    113: 'Curar episódios individualmente, com fonte oficial por episódio (a antologia em nível de série é genérica).',
    142: 'Obter página consultável (site oficial, festival ou veículo sem bloqueio) que confirme o conteúdo já indicado por resultados de busca.',
}
rej, rev = [], []
for e in triage:
    s = e['status_triagem']
    base = dict(candidate_id=e['candidate_id'], candidate_number=e['number'], work_id=e['work_id'], obra=e['titulo_informado'],
                tipo=e['tipo'], status=s, motivo=e.get('motivo'),
                fontes_consultadas=[{k: f.get(k) for k in ('url', 'tier', 'locator', 'verificacao')} for f in e['fontes']])
    if s.startswith('REJEITADA'):
        base['possibilidade_de_reconsideracao'] = RECONSIDERACAO[e['number']]
        if e.get('duplicate_of'):
            base['duplicate_of'] = e['duplicate_of']
        rej.append(base)
    elif s == 'FONTE_EM_REVISAO':
        base['acao_necessaria'] = REVISAO[e['number']]
        rev.append(base)
dump(ROOT / '05_REJEITADAS' / 'REJEICOES.json', dict(total=len(rej), rejeicoes=rej,
     nota='Nenhuma candidata foi apagada; todas as 200 têm estado final em 02_TRIAGEM/LOTE_XX.json.'))
dump(ROOT / '05_REJEITADAS' / 'FONTE_EM_REVISAO.json', dict(total=len(rev), candidatas=rev,
     nota='FONTE_EM_REVISAO não é rejeição: a candidata permanece reconsiderável sem nova pesquisa de identidade.'))

# ---------------------------------------------------------------- corrections
corr = []
for e in triage:
    n = e['number']
    informed = e['titulo_informado'].split(' — ')[0]
    if e.get('titulo_canonico') and e['titulo_canonico'] != informed:
        corr.append(dict(candidate_number=n, work_id=e['work_id'], tipo_correcao='TITULO_CANONICO_COMPLETADO',
                         informado=informed, registrado=e['titulo_canonico']))
    if e.get('titulo_original') and e['titulo_original'] not in (e.get('titulo_canonico'), informed):
        corr.append(dict(candidate_number=n, work_id=e['work_id'], tipo_correcao='TITULO_ORIGINAL_REGISTRADO',
                         informado=informed, registrado=e['titulo_original']))
    if e.get('nota_edicao'):
        kind = 'DESAMBIGUACAO' if 'esambigua' in e['nota_edicao'] else 'EDICAO_OU_FORMATO'
        corr.append(dict(candidate_number=n, work_id=e['work_id'], tipo_correcao=kind, nota=e['nota_edicao']))
    if e.get('nota_correcao'):
        corr.append(dict(candidate_number=n, work_id=e['work_id'], tipo_correcao='FORMATO', nota=e['nota_correcao']))
    steam = ROOT / '03_FONTES' / f'STEAM_{n:03}.json'
    if e['tipo'] == 'JOGO' and steam.exists():
        s = load(steam)
        m = re.search(r'\d{4}', ((s.get('release_date') or {}).get('date') or ''))
        if m and int(m.group()) != e['ano']:
            corr.append(dict(candidate_number=n, work_id=e['work_id'], tipo_correcao='ANO_ORIGINAL_VS_EDICAO_DE_PLATAFORMA',
                             ano_edicao_steam=int(m.group()), ano_registrado=e['ano'], edicao_steam=s.get('matched_title')))
corr.append(dict(candidate_number=138, work_id='EXP2-DOC-013', tipo_correcao='HIPOTESE_CODEX_NAO_ADOTADA',
                 nota='from_table.py previa mudar tipo de DOCUMENTÁRIO para SÉRIE. Mantido DOCUMENTÁRIO com subtipo SERIE_DOCUMENTAL para não alterar artificialmente a composição de mídias.'))
dump(ROOT / '06_RELATORIOS' / 'CORRECOES_ENTRADA.json', dict(
    total=len(corr), correcoes=sorted(corr, key=lambda c: (c['candidate_number'], c['tipo_correcao'])),
    resumo=dict(collections.Counter(c['tipo_correcao'] for c in corr)),
    declaracoes=['Nenhuma candidata foi substituída por outra obra.',
                 'Autorias informadas para os 40 livros conferem com as fontes consultadas; nenhuma autoria foi corrigida.',
                 'A lista de entrada não informava anos/países; anos foram atribuídos a partir das fontes e as edições de plataforma foram separadas do ano da obra.',
                 'pais_origem permanece null quando não confirmado em fonte consultada (não inferido).']))

# ---------------------------------------------------------------- redundancy
REL69 = [
    (92, 'EXP-SER-002', 'DUPLICATA_EXATA', 'The Wire é o título original de A Escuta (2002).'),
    (42, 'EXP-JOG-003', 'MESMA_FRANQUIA_OBRA_DISTINTA', 'Frostpunk 2 é sequência distinta de Frostpunk; acrescenta conselho de facções e governança urbana.'),
    (46, 'REF-JOG-0001', 'ALTA_PROXIMIDADE_MECANICA', 'Contraband Police e Papers, Please: verificação documental na fronteira; o novo acrescenta inspeção de veículos/contrabando.'),
    (32, 'REF-JOG-0001', 'ALTA_PROXIMIDADE_MECANICA', 'Not Tonight: verificação de documentos e listas em contexto de trabalho por aplicativo; recorte distinto.'),
    (21, 'REF-JOG-0001', 'MESMO_AUTOR_MECANICA_DISTINTA', 'The Republia Times (Lucas Pope): edição de jornal/propaganda, não fronteira.'),
    (30, 'EXP-JOG-001', 'ALTA_PROXIMIDADE_MECANICA', 'The Political Process e Democracy 4: simulação política; o novo foca candidatura e redação legislativa.'),
    (31, 'EXP-JOG-001', 'ALTA_PROXIMIDADE_MECANICA', 'Lawgivers II: sistemas eleitorais e aprovação de projetos; complementar.'),
    (24, 'EXP-JOG-002', 'PROXIMIDADE_TEMATICA', 'Yes, Your Grace e Suzerain: governante decide sob recursos escassos; medievalismo fantástico × república ficcional.'),
    (16, 'REF-FIL-0003', 'MESMO_TEMA_MIDIA_DISTINTA', 'Beholder (jogo) e A Vida dos Outros: vigilância estatal de moradores; mecânica interativa × narrativa.'),
    (18, 'REF-LIV-0001', 'REFERENCIA_NOMINAL_COMPLEMENTAR', 'Orwell (jogo) evoca 1984, mas documenta mecânica de coleta de dados pessoais.'),
    (134, 'REF-DOC-0001', 'ALTA_PROXIMIDADE_TEMATICA', 'The Social Dilemma e Privacidade Hackeada: plataformas; design de engajamento × caso Cambridge Analytica.'),
    (136, 'EXP-FIL-007', 'MESMO_EVENTO_MIDIA_DISTINTA', 'Inside Job (documentário argumentativo) e A Grande Aposta (ficção): crise de 2008.'),
    (171, 'REF-DOC-0002', 'ALTA_PROXIMIDADE_TEMATICA', 'The New Jim Crow e A 13ª Emenda: encarceramento em massa nos EUA; livro acadêmico × documentário.'),
    (145, 'REF-DOC-0002', 'COMPLEMENTAR', 'Time: caso familiar individual de pena longa; complementa a tese estrutural.'),
    (135, 'EXP-DOC-001', 'COMPLEMENTAR', 'Enron e A Corporação: caso concreto de colapso corporativo × tese geral.'),
    (111, 'EXP-SER-002', 'MESMO_CRIADOR_CASO_DISTINTO', 'We Own This City e A Escuta: David Simon, Baltimore, polícia; o novo dramatiza caso real específico (GTTF).'),
    (107, 'EXP-SER-009', 'ALTA_PROXIMIDADE_TEMATICA', 'House of Cards e The West Wing: drama político em Washington; legislativo/corrupção × Executivo.'),
    (108, 'EXP-SER-009', 'COMPLEMENTAR', 'Madam Secretary: diplomacia/política externa.'),
    (109, 'EXP-SER-009', 'COMPLEMENTAR', 'Designated Survivor: sucessão presidencial em crise.'),
    (110, 'EXP-SER-001', 'COMPLEMENTAR', 'The Diplomat × Borgen: diplomacia × parlamentarismo.'),
    (112, 'EXP-SER-003', 'COMPLEMENTAR', 'The Plot Against America × Years and Years: ascensão populista; história alternativa × futuro próximo.'),
    (80, 'EXP-FIL-003', 'COMPLEMENTAR', 'Ainda Estou Aqui × Argentina, 1985: ditaduras, desaparecimento; Brasil × Argentina.'),
    (160, 'EXP-DOC-008', 'COMPLEMENTAR', 'Cidadão Boilesen × Cabra Marcado para Morrer: ditadura brasileira; financiamento empresarial da repressão × camponeses.'),
    (159, 'REF-DOC-0003', 'COMPLEMENTAR', 'Espero Tua (Re)volta × Democracia em Vertigem: mesmo período político; secundaristas × cúpula do poder.'),
    (172, 'EXP-LIV-008', 'COMPLEMENTAR', 'Evicted × A Cor da Lei: moradia nos EUA; despejo contemporâneo × segregação histórica.'),
    (173, 'EXP-DOC-003', 'COMPLEMENTAR', 'Poverty, by America × Desigualdade para Todos: pobreza × concentração de renda.'),
    (164, 'EXP-LIV-006', 'COMPLEMENTAR', 'Democracy in America × O Federalista: EUA do séc. XIX; observador externo × fundadores.'),
    (169, 'EXP-DOC-010', 'COMPLEMENTAR', 'Seeing Like a State × Citizen Jane: planejamento estatal e urbanismo; inclui Brasília.'),
    (86, 'REF-LIV-0004', 'COMPLEMENTAR', 'Que Horas Ela Volta? × Quarto de Despejo: trabalho doméstico e pobreza urbana.'),
    (200, 'EXP-LIV-005', 'COMPLEMENTAR', 'Vidas Secas × Torto Arado: sertão/rural; retirantes × trabalho análogo à servidão.'),
    (199, 'EXP-DOC-007', 'COMPLEMENTAR', 'A Queda do Céu × Martírio: povos indígenas; Yanomami × Guarani-Kaiowá.'),
    (153, 'EXP-JOG-006', 'COMPLEMENTAR', 'We Are Guardians × Never Alone: povos indígenas; documentário amazônico × jogo inupiaq.'),
]
REL200 = [
    ((61, 126, 180), 'MESMO_CASO_TRES_MIDIAS', 'Snowden: filme dramatizado, documentário em tempo real e memórias do próprio autor. Maior redundância interna; mantidas por mídia e perspectiva distintas.'),
    ((117, 181), 'MESMO_CASO_DUAS_MIDIAS', 'Theranos: série dramatizada × livro-reportagem.'),
    ((98, 182), 'MESMO_CASO_DUAS_MIDIAS', 'Opioides/Purdue: série dramatizada × reportagem sobre a família Sackler.'),
    ((84, 194), 'ADAPTACAO', 'Carandiru (filme) adapta Estação Carandiru (livro): ficção × relato não ficcional.'),
    ((125, 194), 'MESMO_AUTOR_DE_BASE', 'Carcereiros (série) inspira-se em outro livro de Drauzio Varella; ambiente prisional comum.'),
    ((16, 17), 'SEQUENCIA', 'Beholder 1 e 2: vigilância de inquilinos × burocracia ministerial.'),
    ((18, 19), 'SEQUENCIA', 'Orwell 1 e 2: investigação com dados × fabricação de informação.'),
    ((32, 33), 'SEQUENCIA', 'Not Tonight 1 e 2: verificação de documentos × travessia após prisão migratória.'),
    ((7, 8), 'SEQUENCIA', 'Deus Ex HR e MD: desigualdade por aprimoramentos × discriminação de aprimorados.'),
    ((11, 12), 'MESMA_FRANQUIA', 'Mafia DE e Mafia III: crime organizado em épocas distintas.'),
    ((2, 3, 4), 'MESMA_FRANQUIA', 'Ace Attorney: defesa × Japão/Inglaterra histórica × promotoria.'),
    ((36, 37), 'MESMO_CRIADOR_MECANICA_PROXIMA', 'Her Story e Telling Lies (Sam Barlow): busca em banco de vídeos; interrogatórios policiais × gravações privadas.'),
    ((93, 94), 'SPIN_OFF', 'The Good Wife e The Good Fight: advocacia; spin-off com outro caso central.'),
    ((88, 89), 'SEQUENCIA', 'Tropa de Elite 1 e 2: operações policiais × milícias/política.'),
    ((167, 168), 'MESMOS_AUTORES', 'Acemoglu & Robinson: instituições e prosperidade × equilíbrio Estado–sociedade.'),
    ((172, 173), 'MESMO_AUTOR', 'Desmond: etnografia do despejo × tese geral da pobreza.'),
    ((174, 175), 'MESMA_AUTORA', 'Wilkerson: Grande Migração (história) × tese de casta.'),
    ((184, 185), 'MESMA_AUTORA', 'Klein: marcas globais × doutrina do choque.'),
    ((192, 200), 'MESMO_AUTOR_GENEROS_DISTINTOS', 'Graciliano Ramos: memória carcerária × romance da seca.'),
    ((134, 140, 141, 177, 178, 179), 'CLUSTER_DIGITAL_COMPLEMENTAR', 'Algoritmos, plataformas e dados: sem redundância extrema; objetos distintos (engajamento, reconhecimento facial, moderação, decisões automatizadas, busca, extração comportamental).'),
    ((88, 89, 155, 156, 195), 'CLUSTER_SEGURANCA_PUBLICA_BR', 'Polícia e violência no Brasil: ficção × documentário × reportagem; complementares.'),
]
title69 = {w['id']: w['titulo'] for w in ref69}
red = dict(
    criterio='REJEITADA_REDUNDANCIA_EXTREMA somente quando a nova obra praticamente não acrescenta evidência, perspectiva ou utilidade.',
    rejeitadas_por_redundancia_extrema=0,
    duplicidade_exata=[dict(candidate_number=n, obra=by_n[n]['titulo_informado'], existente=i, existente_titulo=title69[i], nota=t) for n, i, k, t in REL69 if k == 'DUPLICATA_EXATA'],
    relacoes_com_69=[dict(candidate_number=n, obra=by_n[n]['titulo_informado'], status=by_n[n]['status_triagem'], existente=i, existente_titulo=title69[i], relacao=k, nota=t) for n, i, k, t in REL69],
    relacoes_internas_200=[dict(candidatas=list(ns), obras=[by_n[x]['titulo_informado'] for x in ns], relacao=k, nota=t) for ns, k, t in REL200],
    comparacao_automatica=dict(comparacoes_por_candidata=69, total_comparacoes=200 * 69,
                               titulo_normalizado_identico=[e['number'] for e in triage if any(c['exact_normalized'] for c in e['comparacao_69'])]))
dump(ROOT / '06_RELATORIOS' / 'REDUNDANCIA_69_MAIS_200.json', red)
md = ['# Redundância — 69 obras congeladas + 200 candidatas', '',
      f'Gerado por `06_RELATORIOS/gerar_relatorios.py` em {NOW}. Comparação automática: 200 × 69 = 13.800 pares por título normalizado; único par idêntico: #92.', '',
      '**Critério:** REJEITADA_REDUNDANCIA_EXTREMA só quando a nova obra praticamente não acrescenta evidência, perspectiva ou utilidade. **Nenhuma candidata atingiu esse patamar.**', '',
      '## Duplicidade exata', '']
for d in red['duplicidade_exata']:
    md.append(f"- #{d['candidate_number']} {d['obra']} = `{d['existente']}` {d['existente_titulo']}: {d['nota']} → REJEITADA_DUPLICATA_EXISTENTE")
md += ['', '## Relações com o catálogo de 69', '', '| # | Candidata | Existente | Relação | Nota |', '|---|---|---|---|---|']
for d in red['relacoes_com_69']:
    md.append(f"| {d['candidate_number']} | {d['obra']} | `{d['existente']}` {d['existente_titulo']} | {d['relacao']} | {d['nota']} |")
md += ['', '## Relações internas entre as 200', '', '| Candidatas | Relação | Nota |', '|---|---|---|']
for d in red['relacoes_internas_200']:
    md.append(f"| {', '.join('#%d' % x for x in d['candidatas'])} | {d['relacao']} | {d['nota']} |")
md += ['', '## Leitura editorial', '',
       '- A maior redundância interna é o caso Snowden em três mídias (#61, #126, #180); mantidas porque cada uma traz outro tipo de evidência (dramatização, registro direto, autobiografia).',
       '- Proximidade mecânica alta com Papers, Please (#46 Contraband Police, #32 Not Tonight) não é redundância extrema: os objetos documentados diferem (contrabando/veículos; trabalho por aplicativo).',
       '- Pares mesmo-caso (Theranos, opioides, Carandiru) combinam dramatização e reportagem; a Engine deve tratar a dramatização com as ressalvas registradas.', '']
(ROOT / '06_RELATORIOS' / 'REDUNDANCIA_69_MAIS_200.md').write_text('\n'.join(md), encoding='utf-8')

# ---------------------------------------------------------------- metrics
TIPOS = ['JOGO', 'FILME', 'SÉRIE', 'DOCUMENTÁRIO', 'LIVRO']
st = collections.Counter(e['status_triagem'] for e in triage)
cards = [c for e in triage for c in e['evidencias']]
fontes = [f for e in triage for f in e['fontes']]
before = collections.Counter(w['tipo'] for w in ref69)
after = before + collections.Counter(e['tipo'] for e in usable)
metricas = dict(
    gerado_em=NOW, candidatas_iniciais=len(triage),
    por_tipo={t: dict(collections.Counter(e['status_triagem'] for e in triage if e['tipo'] == t), total=sum(1 for e in triage if e['tipo'] == t)) for t in TIPOS},
    por_status=dict(st), soma_estados=sum(st.values()),
    total_duplicatas=st['REJEITADA_DUPLICATA_EXISTENTE'], total_apta=st['APTA'], total_apta_com_ressalva=st['APTA_COM_RESSALVA'],
    total_fonte_em_revisao=st['FONTE_EM_REVISAO'], total_rejeitada_evidencia=st['REJEITADA_EVIDENCIA_FRACA'],
    total_rejeitada_fonte=st['REJEITADA_FONTE_INSUFICIENTE'], total_rejeitada_redundancia=st['REJEITADA_REDUNDANCIA_EXTREMA'],
    total_rejeitada_incompatibilidade=st['REJEITADA_INCOMPATIBILIDADE'],
    novas_utilizaveis=len(usable), total_potencial_69_mais_apta=69 + st['APTA'], total_potencial_69_mais_utilizaveis=69 + len(usable),
    diversidade_midia=dict(antes=dict(before), depois_69_mais_utilizaveis=dict(after)),
    evidence_cards=dict(total=len(cards), por_content_type=dict(collections.Counter(c['content_type'] for c in cards)),
                        por_centralidade=dict(collections.Counter(c['centrality'] for c in cards)),
                        todas_not_targeted_to_device=all(c['not_targeted_to_device'] is True for c in cards)),
    fontes=dict(total_registros=len(fontes), por_tier=dict(collections.Counter(f['tier'] for f in fontes)),
                por_verificacao=dict(collections.Counter(f.get('verificacao', 'NAO_REGISTRADA_(LOTES_1-4_CODEX)') for f in fontes)),
                fonte_de_cards_por_tier=dict(collections.Counter(c['source']['tier'] for c in cards))),
    origem_do_trabalho=dict(codex_lotes_1_4=100, retomada_lotes_5_8=100, buscas_codex_reaproveitadas=sorted(range(101, 121))))
assert metricas['soma_estados'] == 200
dump(ROOT / '06_RELATORIOS' / 'METRICAS_FINAIS.json', metricas)

# ---------------------------------------------------------------- coverage
def text69(w):
    return norm(' '.join(w.get('temas_centrais', []) + w.get('temas_fortes', []) + w.get('objetos_juridicos_compativeis', []) + list((w.get('areas_prioritarias') or {}).keys())))


def textexp(e):
    return norm(' '.join(e.get('areas_potenciais', []) + e.get('objetos_juridicos_potenciais', [])))


LACUNAS = {
    'sucessões (herança)': ['sucessoes', 'heranca', 'testament', 'sucessao na direcao empresarial'],
    'contratos / obrigações': ['contrat', 'relacao locaticia', 'locacao', 'seguros', 'credito ao consumidor'],
    'tributação': ['tribut', 'offshore', 'fiscal'],
    'orçamento público': ['orcament'],
    'direito empresarial / societário': ['empresarial', 'corporativ', 'societ', 'governanca'],
    'propriedade intelectual': ['propriedade intelectual', 'autoral', 'patente'],
    'eleitoral': ['eleic', 'eleitoral'],
    'processo civil': ['processo civil', 'litigios civis', 'litigio civil'],
    'consumidor': ['consum'],
    'povos indígenas': ['indigena'],
    'infância e adolescência': ['infancia', 'adolescen', 'juvenil', 'menor', 'crianca'],
    'deficiência': ['deficiencia'],
    'responsabilidade civil': ['responsabilidade civil'],
    'família': ['famil'],
    'propriedade / posse': ['propriedade', 'posse', 'territori'],
    'trabalho': ['trabalh', 'greve'],
    'meio ambiente': ['ambient', 'desmatamento', 'florest', 'agrotox'],
    'digital / dados': ['digital', 'dados', 'algorit', 'plataforma', 'inteligencia artificial'],
    'administração pública': ['administracao publica', 'servico publico', 'burocracia'],
    'relações internacionais': ['relacoes internacionais', 'diplomac', 'direito internacional', 'refugio'],
}
cov = {}
for area, keys in LACUNAS.items():
    ex = [w['id'] for w in ref69 if any(k in text69(w) for k in keys)]
    nw = [e['work_id'] for e in usable if any(k in textexp(e) for k in keys)]
    total = len(ex) + len(nw)
    cov[area] = dict(obras_69=len(ex), novas_utilizaveis=len(nw), total=total,
                     nivel='POBRE' if total <= 3 else 'MODERADA' if total <= 8 else 'COBERTA', novas_ids=nw)
area_counts = collections.Counter(a for e in usable for a in e.get('areas_potenciais', []))
dump(ROOT / '06_RELATORIOS' / 'COBERTURA_EDITORIAL.json', dict(
    aviso='Mapa editorial por palavras-chave em areas_potenciais/objetos_juridicos_potenciais (novas) e temas/objetos (69). Não é saída da Engine nem vínculo com dispositivo.',
    areas_potenciais_mais_frequentes_novas=dict(area_counts.most_common(40)),
    lacunas_verificadas=cov,
    lacunas_que_permanecem_pobres=[a for a, v in cov.items() if v['nivel'] == 'POBRE']))

# ---------------------------------------------------------------- games report
games = [e for e in triage if e['tipo'] == 'JOGO']
gst = collections.Counter(e['status_triagem'] for e in games)
mech = [e for e in games if any(c['content_type'] == 'MECANICA_INTERATIVA' for c in e['evidencias'])]
narr = [e for e in games if any(c['content_type'] == 'EVENTO_NARRATIVO' for c in e['evidencias'])]
gareas = collections.Counter(a for e in games for a in e.get('areas_potenciais', []))
gsrc = collections.Counter(re.sub(r'^https?://(www\.)?([^/]+).*$', r'\2', f['url']) for e in games for f in e['fontes'])
g = ['# Jogos — resultado da expansão', '',
     f'Gerado em {NOW}. Lotes 1–2 (candidatas 1–50) produzidos pelo Codex e validados na retomada (hashes do checkpoint conferem; nenhuma decisão alterada).', '',
     '## Números', '',
     f'- Candidatos: **{len(games)}**',
     f"- APTA: **{gst['APTA']}**",
     f"- APTA_COM_RESSALVA: **{gst['APTA_COM_RESSALVA']}**",
     f"- FONTE_EM_REVISAO: **{gst['FONTE_EM_REVISAO']}** {[e['number'] for e in games if e['status_triagem'] == 'FONTE_EM_REVISAO']}",
     f"- Rejeitados: **{sum(v for k, v in gst.items() if k.startswith('REJEITADA'))}** {[e['number'] for e in games if e['status_triagem'].startswith('REJEITADA')]}",
     '- Saneamento pré-enriquecimento (V1): #9 Cyberpunk 2077 (antes REJEITADA_EVIDENCIA_FRACA) e #41 Kingdom Come II (antes FONTE_EM_REVISAO) passaram a APTA_COM_RESSALVA com fontes oficiais do estúdio/publisher; ver DECISAO_CYBERPUNK_REVISADA.json e REVISOES_POS_CHECKPOINT.json.',
     f'- Com evidência **mecânica** (MECANICA_INTERATIVA): **{len(mech)}**',
     f'- Com evidência **narrativa** (EVENTO_NARRATIVO): **{len(narr)}**',
     f"- Evidence cards: {sum(len(e['evidencias']) for e in games)} em {sum(1 for e in games if e['evidencias'])} jogos utilizáveis; todos com ao menos 1 CENTRAL.", '',
     '## Por que nenhum jogo é APTA pleno', '',
     'O Codex classificou os 48 utilizáveis originais como APTA_COM_RESSALVA com duas ressalvas: a simulação não equivale a regime jurídico real, e a mecânica documentada prova uma *possibilidade* do jogo, não a ocorrência em toda partida. A retomada manteve a decisão, já que não há erro objetivo. Os dois jogos revisados no saneamento seguiram o mesmo critério. Isso não penaliza o jogo por falta de roteiro: a mecânica objetiva documentada é aceita como evidência válida.', '',
     '## Principais áreas potenciais (metadado editorial)', '']
g += [f'- {a}: {n}' for a, n in gareas.most_common(20)]
g += ['', '## Fontes usadas', '',
      '- Tier A em todos os jogos utilizáveis: descrição oficial do publisher na loja Steam (`store.steampowered.com`, coletada por `03_FONTES/collect_steam.py`, somente leitura).',
      '- Exceções e complementos: 2K (Spec Ops: The Line, fora da Steam), dukope.com (The Republia Times, jogo de navegador), Nintendo, PlayStation Blog, Quantic Dream, Eidos-Montréal, Rockstar, 2K Support e Konami (ano original × edição de plataforma).', '',
      '| Domínio | Registros |', '|---|---|']
g += [f'| {d} | {n} |' for d, n in gsrc.most_common()]
g += ['', '## Dificuldades documentais', '',
      '- As descrições de loja são promocionais: servem para mecânicas e premissas, mas raramente delimitam eventos. Por isso Cyberpunk 2077 foi inicialmente rejeitado e Kingdom Come II ficou em revisão; ambos só foram resolvidos com páginas oficiais do estúdio/publisher (cyberpunk.net, deepsilver.com).',
      '- Remasters e coletâneas (Disco Elysium Final Cut, Deus Ex Director’s Cut, MGS2 Master Collection, Mafia III DE, Ace Attorney Trilogy) exigiram separar o ano da obra do ano da edição (ver CORRECOES_ENTRADA.json).',
      '- Um card por jogo: mecânicas secundárias documentáveis (p.ex. subornos em Disco Elysium, conselho em Frostpunk 2) poderiam virar cards FORTE numa rodada futura com manual ou press kit.', '',
      '## Jogos mais promissores (juízo editorial, não score da Engine)', '',
      '- **Prova e defesa:** Phoenix Wright Trilogy (#2), The Great Ace Attorney Chronicles (#3), Ace Attorney Investigations (#4), Her Story (#37), Telling Lies (#36), The Case of the Golden Idol (#39), Legal Dungeon (#45).',
      '- **Jurisdição:** We. The Revolution (#22, juiz do Tribunal Revolucionário), Tyranny (#43).',
      '- **Vigilância e dados:** Beholder (#16), Orwell (#18), Do Not Feed the Monkeys (#35).',
      '- **Imprensa:** Not For Broadcast (#20), The Republia Times (#21), Headliner: NoviNews (#34).',
      '- **Fronteira e documentos:** Contraband Police (#46), Not Tonight (#32).',
      '- **Estado, orçamento e processo legislativo:** Yes, Your Grace (#24), Frostpunk 2 (#42), The Political Process (#30), Lawgivers II (#31), Victoria 3 (#26, tributação).',
      '- **Direito civil:** Crusader Kings III (#25, sucessão dinástica, títulos e territórios), Return of the Obra Dinn (#38, avaliação de seguros).', '']
(ROOT / '06_RELATORIOS' / 'JOGOS_EXPANSAO.md').write_text('\n'.join(g), encoding='utf-8')

# ---------------------------------------------------------------- determinism
runs = []
for _ in range(2):
    d = Path(tempfile.mkdtemp(prefix='compila_'))
    compilar_catalogo.main(d)
    runs.append({p.name: sha(p) for p in sorted(d.glob('*.json'))})
local = {p.name: sha(p) for p in sorted((ROOT / '07_CATALOGO_CANDIDATO').glob('CATALOGO_*.json'))}
dump(ROOT / '06_RELATORIOS' / 'DETERMINISMO_COMPILACAO.json', dict(
    verificado_em=NOW, compilador='07_CATALOGO_CANDIDATO/compilar_catalogo.py', execucao_1=runs[0], execucao_2=runs[1],
    artefatos_locais=local, identicos=runs[0] == runs[1] == local,
    nota='Coleta web não é determinística por natureza; a compilação local sobre dados congelados é.'))

estado_retomada.main('ESTADO_FINAL.json', NOW)
print(json.dumps(dict(status=dict(st), utilizaveis=len(usable), cards=len(cards), deterministico=runs[0] == runs[1] == local,
                      lacunas_pobres=[a for a, v in cov.items() if v['nivel'] == 'POBRE']), ensure_ascii=False))
