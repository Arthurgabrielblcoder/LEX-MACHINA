"""Applies the short sanitation mission (pending decisions + objective audit fixes).

Touches only the triage/identity/source/dossier records of the affected candidates
(#9, #41, #113, #142 decisions; #44, #51, #80, #88, #100 audit fixes) and records
every change with before/after hashes in REVISOES_POS_CHECKPOINT.json.
Cards are built with the same structure as 02_TRIAGEM/editorial.py. No engine, no device links.
"""
import datetime, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
ACC = '2026-09-26'
BASE_LIMIT = 'Áreas potenciais são metadados editoriais; não constituem correspondência com dispositivo.'


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def write(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def card(e, j, f):
    ct = f['content_type']
    pred = f.get('predicate', 'ANALISAR' if 'ARGUMENTO' in ct else 'CONTROLAR' if ct == 'MECANICA_INTERATIVA' else 'VIVENCIAR')
    c = dict(evidence_id=f"{e['work_id']}-E{j + 1:02}", work_id=e['work_id'], centrality=f['centrality'], content_type=ct,
             not_targeted_to_device=True,
             claim=dict(predicate=pred, objects=[], participants=[], subjects=[], context=f.get('context', []), effects=[],
                        factual_description=f['text']),
             ONTOLOGY_GAP=dict(status='REVISAO_SEMANTICA_PRE_INGESTAO', description='Descrição factual preservada. Objetos, participantes e qualificadores não preenchidos não devem ser inferidos; mapear explicitamente na ontologia congelada antes da ingestão.'),
             source=dict(e['fontes'][f['source_index']], paraphrase=f['text']), state='DOCUMENTADA_PRELIMINAR',
             provenance=dict(collection='EXPANSAO_200', candidate_id=e['candidate_id'], engine_executed=False,
                             source_basis='Fonte concreta consultada; paráfrase editorial', revisao='SANEAMENTO_PRE_ENRIQUECIMENTO_V1'),
             transposition_limits=e['transposition_limits'])
    if f.get('unidade_documental'):
        c['unidade_documental'] = f['unidade_documental']
        c['escopo_centralidade'] = 'EPISODIO'
    return c


def dossier(e):
    return dict(e, titulo=e['titulo_canonico'], pais=e['pais_origem'], criadores=e['criador_principal'],
                provenance=dict(candidate_id=e['candidate_id'], batch=e['lote'], ontology_changed=False, ingestion_ready=False,
                                revisao='SANEAMENTO_PRE_ENRIQUECIMENTO_V1'))


def src(url, tier, locator, supports, verif='PAGINA_CONSULTADA', **kw):
    return dict(url=url, tier=tier, locator=locator, supports=supports, verificacao=verif, accessed_on=ACC, **kw)


# ------------------------------------------------------------------ decisions
DECISIONS = {
    9: dict(
        status='APTA_COM_RESSALVA',
        add_sources=[src('https://www.cyberpunk.net/us/en/cyberpunk-2077', 'A', 'CD PROJEKT RED — site oficial: Story, Gameplay e fichas de personagens (V)',
                         ['fato_central', 'fato_complementar'], snapshot_sha256='06f339b8f3ed333fbf6d6864a9b26faacff51f4b971e33fa28a15da6858464b2')],
        facts=[dict(text='O mercenário V participa de um roubo de um implante protótipo considerado a chave da imortalidade; o plano fracassa e V fica com o chip experimental implantado na cabeça, que sobrescreve aos poucos sua personalidade com a de Johnny Silverhand, tornando a sobrevivência sua nova missão.',
                    content_type='EVENTO_NARRATIVO', centrality='CENTRAL', source_ref='cyberpunk.net'),
               dict(text='O jogador constrói o personagem instalando implantes que aprimoram o corpo e usando habilidades de hacking, combinados a armas, para cumprir trabalhos (gigs) como mercenário.',
                    content_type='MECANICA_INTERATIVA', centrality='FORTE', source_ref='cyberpunk.net')],
        areas=['personalidade', 'integridade corporal', 'tecnologia'],
        objetos=['implante cerebral que altera a personalidade', 'aprimoramento corporal por implantes', 'identidade pessoal'],
        riscos=['Ficção científica; a ambientação geral (poder corporativo, desigualdade, "obsessão por modificação corporal") não foi usada como evidência.'],
        limits=['Não equivale a procedimento ou instituição brasileira.', 'A mecânica documentada descreve possibilidades do jogo, sem afirmar que toda partida contém o mesmo evento.',
                'Trabalhos (gigs) do jogo não equivalem a contratos em sentido jurídico.', BASE_LIMIT],
        nota='Revisão: a rejeição anterior decorria da fonte (descrição Steam ampla e promocional), não da obra. O site oficial da CD PROJEKT RED documenta evento narrativo e mecânica delimitados.'),
    41: dict(
        status='APTA_COM_RESSALVA',
        add_sources=[src('https://www.deepsilver.com/games/kingdom-come-deliverance-ii', 'A', 'Deep Silver (publisher) — página oficial do jogo (destino de kingdomcomerpg.com)', ['identidade', 'fato_central']),
                     src('https://www.playstation.com/en-us/games/kingdom-come-deliverance-ii/', 'A', 'PlayStation Store — descrição oficial', ['identidade', 'fato_central'])],
        facts=[dict(text='Em meio a uma guerra civil na Boêmia do século XV, Henry, filho de um ferreiro, busca vingar os pais mortos quando forças de Sigismundo atacam sua aldeia e passa a integrar a resistência contra os invasores.',
                    content_type='EVENTO_NARRATIVO', centrality='CENTRAL', source_ref='deepsilver.com')],
        areas=['conflito armado', 'história'],
        objetos=['guerra civil', 'violência contra população civil'],
        riscos=['Ficção histórica; a afirmação oficial de que "as ações moldam como o mundo reage" é genérica e não foi usada como evidência mecânica.'],
        limits=['Não equivale a procedimento ou instituição brasileira.', 'Guerra narrada não se converte em norma internacional específica.', BASE_LIMIT],
        nota='Revisão: fontes oficiais do publisher confirmam e delimitam a premissa narrativa pretendida; nenhuma mecânica específica documentada.'),
    113: dict(
        status='APTA_COM_RESSALVA',
        add_sources=[src('https://www.netflix.com/tudum/articles/black-mirror-best-episodes', 'A', 'Netflix Tudum — guia oficial de episódios (T1E3, T3E1, T7E1)',
                         ['fato_central'], snapshot_sha256='af0b443c754c6e30aa81a8def7c5bc66c619e51301aca95d2c570e41d462c74a')],
        facts=[dict(text="No episódio 'Nosedive', toda interação humana é avaliada em um aplicativo, e a nota geral de cada pessoa determina onde ela pode trabalhar e morar.",
                    content_type='EVENTO_NARRATIVO', centrality='CENTRAL', source_ref='netflix.com/tudum', unidade_documental="T3E1 'Nosedive'", context=["Episódio T3E1 'Nosedive'"]),
               dict(text="No episódio 'The Entire History of You', implantes gravam tudo o que a pessoa vê e permitem reproduzir qualquer momento para si ou para uma plateia; um advogado passa a vasculhar as próprias memórias em busca de evidências da infidelidade da esposa.",
                    content_type='EVENTO_NARRATIVO', centrality='CENTRAL', source_ref='netflix.com/tudum', unidade_documental="T1E3 'The Entire History of You'", context=["Episódio T1E3 'The Entire History of You'"]),
               dict(text="No episódio 'Common People', a sobrevivência de Amanda depende de um contrato de assinatura com a empresa Rivermind, que guarda parte de sua consciência na nuvem; quando o plano encarece, ela passa a reproduzir anúncios e não pode sair da área de cobertura do serviço.",
                    content_type='EVENTO_NARRATIVO', centrality='CENTRAL', source_ref='netflix.com/tudum', unidade_documental="T7E1 'Common People'", context=["Episódio T7E1 'Common People'"])],
        areas=['digital', 'privacidade', 'consumo', 'personalidade'],
        objetos=['pontuação social que condiciona trabalho e moradia', 'gravação integral de memórias', 'contrato de assinatura de serviço de que depende a vida'],
        riscos=['Antologia: cada card vale apenas para o episódio indicado; não representa a série inteira nem autoriza tema genérico de "tecnologia".'],
        limits=['A centralidade é relativa ao episódio (escopo_centralidade = EPISODIO).', 'Ficção especulativa; não equivale a procedimento ou instituição brasileira.', BASE_LIMIT],
        nota='Estrutura escolhida: opção A — Black Mirror permanece obra agregadora única; evidências explicitamente associadas a episódios (unidade_documental). Nenhum episódio vira obra do catálogo. Máximo de 3 episódios.'),
    142: dict(
        status='APTA_COM_RESSALVA',
        add_sources=[src('https://epublications.marquette.edu/zuckerberg_files_videos/242/', 'B', 'Marquette University e-Publications — The Zuckerberg Files, registro do filme', ['fato_central']),
                     src('https://thenextweb.com/news/qa-terms-and-conditions-may-apply-director-cullen-hoback-on-the-attempted-death-of-privacy', 'C', 'The Next Web — entrevista com o diretor (2013)', ['fato_complementar']),
                     src('http://tacma.net/', 'A', 'Site oficial do filme (Hyrax Films)', ['identidade', 'distribuidora'])],
        facts=[dict(text='O documentário expõe o que empresas e governos descobrem sobre as pessoas a partir do uso da internet e do celular.',
                    content_type='ARGUMENTO_DOCUMENTAL', centrality='CENTRAL', source_ref='marquette.edu', predicate='DOCUMENTAR'),
               dict(text='Segundo o diretor, o filme examina os termos de serviço pelos quais usuários consentem, sem saber, com a coleta e o controle de seus dados por empresas de tecnologia, e o acesso de órgãos governamentais a esses dados.',
                    content_type='ARGUMENTO_DOCUMENTAL', centrality='FORTE', source_ref='thenextweb.com', predicate='ANALISAR')],
        publisher=['Hyrax Films'],
        areas=['digital', 'proteção de dados', 'consumo'],
        objetos=['termos de serviço', 'consentimento para coleta de dados', 'acesso governamental a dados privados'],
        riscos=['Tese do realizador; contexto norte-americano. O card FORTE vem de entrevista (tier C).'],
        limits=['Não demonstra regime brasileiro de proteção de dados.', 'Acesso governamental a dados não equivale automaticamente a interceptação de comunicações.', BASE_LIMIT],
        nota='Revisão: fontes consultáveis localizadas (arquivo institucional da Marquette University, entrevista primária com o diretor e site oficial). Snippets de busca anteriores mantidos apenas como apoio de identidade.'),
}

# ------------------------------------------------------------------ audit fixes (objective)
FIXES = {
    44: dict(tipo='AJUSTE_MENOR', text='O chefe de polícia administra agentes, atende emergências e investiga crimes, sob pressão da prefeitura e de organizações criminosas.',
             motivo='A fonte diz "investigate crimes"; "reúne provas" ia além do texto oficial.'),
    51: dict(tipo='AJUSTE_MENOR', text='Erin convence um advogado a contratá-la e se empenha em obter justiça, em um grande caso contra uma corporação, para uma pequena cidade atingida pela poluição de uma empresa de serviços públicos.',
             motivo='A fonte não menciona "reunir informações" nem "ação de moradores"; paráfrase ajustada ao texto oficial.'),
    80: dict(tipo='AJUSTE_IMPORTANTE', text='No Brasil de 1971, sob a ditadura militar, uma mãe é forçada a se reinventar quando a vida da família é destruída por um ato de violência arbitrária.',
             motivo='A paráfrase anterior (nomes, busca da verdade, retirada do marido por agentes) não era sustentada pela fonte citada (La Biennale); restringida ao que a fonte afirma.'),
    88: dict(tipo='AJUSTE_MENOR', text='O filme acompanha o dia a dia de um grupo de policiais do BOPE e de um capitão que quer deixar a corporação e tenta encontrar um substituto para seu posto.',
             motivo='"Operações", "conflitos de segurança pública" e "Rio de Janeiro" não estavam na fonte (tier C); paráfrase ajustada à sinopse consultada.'),
    100: dict(tipo='FONTE_INSUFICIENTE', text='Um juiz confronta suas convicções mais profundas quando o filho se envolve em um atropelamento com fuga que envolve uma família do crime organizado.',
              new_source=src('https://paramountglobalcontent.com/title/your-honor', 'A', 'Paramount Global Content — sinopse oficial (Showtime, 2020–2023)', ['identidade', 'fato_central']),
              motivo='A URL original (paramountplus.com/shows/your-honor/) retornou 404 na auditoria; substituída por página oficial acessível. "Nova Orleans" removido por não constar da nova fonte.'),
}

candidates = {c['number']: c for c in load(ROOT / '00_ENTRADA' / 'CANDIDATAS_200.json')}
lot_of = lambda n: (n - 1) // 25 + 1  # noqa: E731
touched = sorted({lot_of(n) for n in list(DECISIONS) + list(FIXES)})
paths = []
for b in touched:
    paths += [ROOT / '02_TRIAGEM' / f'LOTE_{b:02}.json', ROOT / '01_IDENTIDADE' / f'LOTE_{b:02}.json']
for n in list(DECISIONS) + list(FIXES):
    wid = candidates[n]['work_id']
    paths += [ROOT / '03_FONTES' / f'{wid}.json', ROOT / '04_DOSSIERS' / f'{wid}.json']
before = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}

log = []
for b in touched:
    tp = ROOT / '02_TRIAGEM' / f'LOTE_{b:02}.json'
    ip = ROOT / '01_IDENTIDADE' / f'LOTE_{b:02}.json'
    tri, ide = load(tp), load(ip)
    for i, e in enumerate(tri):
        n = e['number']
        if n in DECISIONS:
            d = DECISIONS[n]
            old = dict(status=e['status_triagem'], cards=len(e['evidencias']), motivo=e.get('motivo'))
            e['fontes'] = e['fontes'] + d['add_sources']
            idx = {s['url'].split('//')[1].split('/')[0].replace('www.', ''): k for k, s in enumerate(e['fontes'])}
            e['status_triagem'] = d['status']
            e['areas_potenciais'], e['objetos_juridicos_potenciais'] = d['areas'], d['objetos']
            e['riscos'], e['transposition_limits'] = d['riscos'], d['limits']
            if d.get('publisher'):
                e['publisher_distribuidor_editora'] = d['publisher']
            e['revisao_editorial'] = dict(missao='SANEAMENTO_PRE_ENRIQUECIMENTO_V1', data=ACC, status_anterior=old['status'], motivo_anterior=old['motivo'], nota=d['nota'])
            e.pop('motivo', None)
            facts = []
            for f in d['facts']:
                f = dict(f)
                ref = f.pop('source_ref')
                f['source_index'] = next(k for h, k in idx.items() if ref in h or h in ref)
                facts.append(f)
            e['evidencias'] = [card(e, j, f) for j, f in enumerate(facts)]
            e['resumo_factual_curto'] = ' '.join(c['claim']['factual_description'] for c in e['evidencias'])
            write(ROOT / '04_DOSSIERS' / f"{e['work_id']}.json", dossier(e))
            log.append(dict(candidate_number=n, work_id=e['work_id'], tipo='MUDANCA_DE_DECISAO', status_anterior=old['status'],
                            status_novo=e['status_triagem'], cards_antes=old['cards'], cards_depois=len(e['evidencias'])))
        elif n in FIXES:
            fx = FIXES[n]
            c0 = e['evidencias'][0]
            old_text, old_url = c0['claim']['factual_description'], c0['source']['url']
            if fx.get('new_source'):
                e['fontes'][0] = dict(fx['new_source'], paraphrase=fx['text'], fonte_substituida=e['fontes'][0]['url'])
            else:
                e['fontes'][0] = dict(e['fontes'][0], paraphrase=fx['text'])
            c0['claim']['factual_description'] = fx['text']
            c0['source'] = dict(e['fontes'][0], paraphrase=fx['text'])
            c0['provenance']['revisao'] = 'AUDITORIA_LOTES_1_4'
            e['resumo_factual_curto'] = ' '.join(c['claim']['factual_description'] for c in e['evidencias'])
            e['revisao_editorial'] = dict(missao='AUDITORIA_LOTES_1_4', data=ACC, classificacao=fx['tipo'], motivo=fx['motivo'])
            dp = ROOT / '04_DOSSIERS' / f"{e['work_id']}.json"
            dd = load(dp)
            dd.update(fontes=e['fontes'], evidencias=e['evidencias'], resumo_factual_curto=e['resumo_factual_curto'], revisao_editorial=e['revisao_editorial'])
            write(dp, dd)
            log.append(dict(candidate_number=n, work_id=e['work_id'], tipo='CORRECAO_AUDITORIA', classificacao=fx['tipo'],
                            texto_anterior=old_text, texto_novo=fx['text'], fonte_anterior=old_url, fonte_nova=c0['source']['url'], motivo=fx['motivo']))
        else:
            continue
        write(ROOT / '03_FONTES' / f"{e['work_id']}.json", e['fontes'])
        tri[i] = e
        k = next(k for k, x in enumerate(ide) if x['number'] == n)
        ide[k] = {kk: vv for kk, vv in e.items() if kk not in ['evidencias', 'resumo_factual_curto', 'facts']}
    write(tp, tri)
    write(ip, ide)

after = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
write(ROOT / '06_RELATORIOS' / 'REVISOES_POS_CHECKPOINT.json', dict(
    missao='SANEAMENTO_PRE_ENRIQUECIMENTO_V1', aplicado_em=NOW,
    nota='CHECKPOINT_LOTES.json preserva o estado histórico de fechamento de cada lote; estas revisões posteriores são rastreadas aqui com hashes antes/depois.',
    lotes_afetados=touched, alteracoes=log,
    hashes=[dict(path=k, sha256_antes=before[k], sha256_depois=after[k]) for k in sorted(before)]))
print(json.dumps(log, ensure_ascii=False, indent=1))
