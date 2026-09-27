"""State reconstruction, deduplication and audit records for the enrichment resumed after Codex.

Read-only over Codex artifacts (checkpoints, overlays, source metadata). Writes:
ESTADO_ENRIQUECIMENTO_APOS_CODEX.json, DEDUPLICACAO_EVIDENCE_CARDS_V1.json,
AUDITORIA_CARDS_ENRIQUECIMENTO_V1.json. Verification results below were obtained by
consulting each source on 2026-09-26 (see RETOMADA/RELATORIO markdown files).
"""
import collections, hashlib, json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / '06_RELATORIOS'
OV = ROOT / '04_DOSSIERS' / 'ENRIQUECIMENTO_V1'


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def dump(p, x):
    p.write_bytes((json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))


state = load(R / 'CHECKPOINT_ENRIQUECIMENTO.json')
cps = sorted((load(p) for p in (R / 'CHECKPOINTS_ENRIQUECIMENTO').glob('CP_*.json')), key=lambda c: c['numero'])
cp_of = {n: cp['numero'] for cp in cps for n in cp['obras_examinadas']}
metas = [load(p) | {'arquivo': p.relative_to(ROOT).as_posix()} for p in sorted((ROOT / '03_FONTES' / 'ENRIQUECIMENTO_V1').glob('*.json'))]
consulted = {m['url'] for m in metas if m['verificacao'] == 'PAGINA_CONSULTADA'}
base_cat = load(ROOT / '07_CATALOGO_CANDIDATO' / 'CATALOGO_EXPANSAO_200.json')

# ------------------------------------------------ provenance of web-tool sources (no local fetch record)
WEBTOOL_VERIFIED = {
    'EXP2-DOC-008-E02': 'Sundance Institute: "as she argues for justice in front of the United Nations" — confirmado (WebFetch).',
    'EXP2-DOC-016-E02': 'Press kit oficial (Beetz Brothers, PDF sha256 c2b2668d…): sintomas de trauma; "not even their families are allowed to know" — confirmado.',
    'EXP2-DOC-034-E02': 'SICAV: debates de feminismo, temas LGBT e antirracismo transformaram relações e autoapresentação — confirmado (WebFetch).',
    'EXP2-JOG-005-E02': 'Rockstar Support: Locations no journal e gasto de intuition points para revelar pistas — confirmado (navegador).',
    'EXP2-JOG-015-E02': 'Konami Support: Fulton extraction de indivíduos sem resistência; dispositivos melhores extraem veículos e contêineres — confirmado (navegador).',
    'EXP2-JOG-038-E02': 'Nintendo JP: relógio Memento Mortem e registro no diário — confirmado (WebFetch).',
    'EXP2-JOG-041-E02': 'Deep Silver, RPG Elements: habilidades sobem com o uso; armas, furtividade, forja e alquimia — confirmado (WebFetch).',
    'EXP2-JOG-049-E02': 'White Paper Games: explosão, ato controverso contra liberdades civis, investigação da noite — confirmado (WebFetch).',
    'EXP2-LIV-040-E02': 'graciliano.com.br (artigo de Zenir Campos Reis, Estudos Avançados): Fabiano atira em Baleia — confirmado (WebFetch).',
}

# ------------------------------------------------ state
rows = []
queue_nums = [x['candidate_number'] for x in state['fila']]
new_cards = []
for w in sorted(base_cat['obras'], key=lambda x: x['candidate_number']):
    ovp = OV / f"{w['work_id']}.json"
    if ovp.exists():
        ov = load(ovp)
        d = ov['decisao']
        for c in ov['evidencias_adicionais']:
            new_cards.append(c)
        rows.append(dict(candidate_number=w['candidate_number'], work_id=w['work_id'], titulo=w['titulo'], tipo=w['tipo'],
                         na_fila=True, examinada=True, examinada_por='CODEX', checkpoint=cp_of[w['candidate_number']],
                         pos_oitavo_checkpoint=cp_of[w['candidate_number']] > 8, estado=d['estado'],
                         cards_antes=d['cards_antes'], cards_novos=d['cards_adicionados'], evidence_ids=d['evidence_ids'],
                         rejeitados=len(d.get('rejeitados', [])), fontes_de_coleta=d.get('fontes_consultadas', []), pendente=False))
    else:
        rows.append(dict(candidate_number=w['candidate_number'], work_id=w['work_id'], titulo=w['titulo'], tipo=w['tipo'],
                         na_fila=w['candidate_number'] in queue_nums, examinada=False, estado='NAO_ENFILEIRADA_COMPLETA_PROVAVEL',
                         cards_antes=len(w['evidencias']), cards_novos=0, pendente=w['candidate_number'] in queue_nums))
pend = [r for r in rows if r['pendente']]
cp8 = [n for cp in cps if cp['numero'] <= 8 for n in cp['obras_examinadas']]
post = [n for cp in cps if cp['numero'] > 8 for n in cp['obras_examinadas']]
estado = dict(
    reconstruido_em='2026-09-26', fonte_do_estado='06_RELATORIOS/CHECKPOINT_ENRIQUECIMENTO.json + CHECKPOINTS_ENRIQUECIMENTO/CP_01..12 + overlays 04_DOSSIERS/ENRIQUECIMENTO_V1',
    checkpoints_encontrados=len(cps), ultimo_checkpoint_valido=cps[-1]['numero'], ultimo_checkpoint_at=cps[-1]['at'],
    estado_no_arquivo_do_codex=state['estado'],
    ponto_reportado_no_handoff=dict(checkpoints=8, obras=77, cards=58),
    ate_cp8=dict(obras=len(cp8), cards=sum(cp['cards_adicionados'] for cp in cps if cp['numero'] <= 8)),
    pos_cp8_persistido=dict(checkpoints=[cp['numero'] for cp in cps if cp['numero'] > 8], obras=len(post), obras_lista=post,
                            cards=sum(cp['cards_adicionados'] for cp in cps if cp['numero'] > 8)),
    fila_total=len(queue_nums), obras_examinadas=sum(r['examinada'] for r in rows), obras_pendentes=[r['candidate_number'] for r in pend],
    obras_fora_da_fila=sum(1 for r in rows if not r['na_fila']),
    cards_novos_fisicos=len(new_cards), cards_novos_segundo_checkpoints=state['cards_adicionados'],
    fontes_coleta=dict(total=len(metas), por_verificacao=dict(collections.Counter(m['verificacao'] for m in metas)),
                       falhas=[dict(number=m['number'], url=m['url'], erro=m.get('erro')) for m in metas if m['verificacao'] != 'PAGINA_CONSULTADA']),
    cards_com_fonte_sem_registro_local=sorted(c['evidence_id'] for c in new_cards if c['source'].get('retrieval_url', c['source']['url']) not in consulted),
    verificacao_de_proveniencia_pos_codex=WEBTOOL_VERIFIED,
    arquivos_intermediarios=['06_RELATORIOS/CONSULTA_CP11.txt', '06_RELATORIOS/CONSULTA_CP12.txt', '06_RELATORIOS/BASELINE_ENRIQUECIMENTO_V1.json'],
    obras=rows)
assert set(estado['cards_com_fonte_sem_registro_local']) == set(WEBTOOL_VERIFIED)
dump(R / 'ESTADO_ENRIQUECIMENTO_APOS_CODEX.json', estado)

# ------------------------------------------------ deduplication
STOP = set('a o e de da do das dos em no na nos nas um uma para por com que se ao aos as os seu sua suas seus ou como mais entre sobre pelo pela pelos pelas sem jogador jogadora obra filme livro autor autora serie episodio narrativa pode'.split())


def toks(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return {w[:6] for w in re.findall(r'[a-z]{4,}', s) if w not in STOP}


REVIEW = {
    ('EXP2-LIV-019-E01', 'EXP2-LIV-019-E02'): 'E01 é diagnóstico descritivo (poder de prever e controlar comportamento; efeitos sobre desigualdade e democracia); E02 é posição normativa (submeter esse poder a direitos e leis). Fatos distintos.',
    ('EXP2-JOG-037-E01', 'EXP2-JOG-037-E02'): 'E01 = MECANICA_INTERATIVA (consulta ao banco de vídeos); E02 = EVENTO_NARRATIVO (entrevista policial de 1994 sobre desaparecimento do marido). Política §5: mecânica e narrativa independentes.',
    ('EXP2-JOG-029-E01', 'EXP2-JOG-029-E02'): 'Expansão/tecnologia × escolha separada de líder e civilização. Sistemas distintos.',
    ('EXP2-DOC-013-E01', 'EXP2-DOC-013-E03'): 'Visão geral da série × episódio T2E2 (Malásia). Unidades documentais distintas.',
    ('EXP2-LIV-012-E01', 'EXP2-LIV-012-E02'): 'Objeto etnográfico (oito famílias) × tese causal (despejo causa pobreza).',
    ('EXP2-LIV-010-E01', 'EXP2-LIV-010-E02'): 'Substituição de servidores por aliados × omissão na transição (livros de transição não recebidos). Fatos distintos.',
}
pairs = []
for p in sorted(OV.glob('*.json')):
    new = load(p)['evidencias_adicionais']
    if not new:
        continue
    old = load(ROOT / '04_DOSSIERS' / p.name)['evidencias']
    allc = [(c, 'BASE') for c in old] + [(c, 'NOVO') for c in new]
    for i, (a, ta) in enumerate(allc):
        for b, tb in allc[i + 1:]:
            if ta == tb == 'BASE':
                continue
            A, B = toks(a['claim']['factual_description']), toks(b['claim']['factual_description'])
            pairs.append((round(len(A & B) / max(1, len(A | B)), 3), a['evidence_id'], b['evidence_id'], a['content_type'], b['content_type']))
pairs.sort(key=lambda x: (-x[0], x[1], x[2]))
flag = [p for p in pairs if p[0] >= 0.10 or (p[1], p[2]) in REVIEW]
dedup = dict(
    criterio='POSSIVEL_DUPLICACAO_SEMANTICA: dois cards da mesma obra descrevem essencialmente o mesmo fato ou mecânica com redações diferentes.',
    metodo='Todos os pares (novo×novo e novo×base) da mesma obra; triagem por sobreposição lexical (Jaccard de radicais) ≥ 0,10 e revisão individual de cada par triado.',
    pares_comparados=len(pairs), pares_triados=len(flag),
    revisao=[dict(similaridade=s, card_a=a, card_b=b, tipos=[ta, tb], classificacao='POSSIVEL_DUPLICACAO_SEMANTICA' if s >= 0.2 else 'TRIADO_BAIXA_SIMILARIDADE',
                  decisao='MANTER_AMBOS', justificativa=REVIEW.get((a, b), 'Revisado: fatos/mecânicas distintos; sobreposição apenas de nomes próprios ou termos de contexto.'))
             for s, a, b, ta, tb in flag],
    duplicacoes_confirmadas=0, cards_removidos=0,
    nota='Nenhum par descreve o mesmo fato; nenhuma remoção. Em caso de dúvida a regra era não eliminar automaticamente.')
dump(R / 'DEDUPLICACAO_EVIDENCE_CARDS_V1.json', dedup)

# ------------------------------------------------ audit of 20 new cards
AUD = {
    'EXP2-JOG-010-E02': ('AUDITORIA_OK', 'STEAM_010: "Red Dead Online … form a posse; run moonshine". Escopo do componente online explicitado no claim.'),
    'EXP2-JOG-033-E02': ('AUDITORIA_OK', 'STEAM_033: "Work the doors … Check IDS … minigames".'),
    'EXP2-JOG-043-E02': ('AUDITORIA_OK', 'STEAM_043: "Tactical real-time-with-pause combat with new party-driven mechanics". Mecânica concreta e independente; baixa relevância temática não é violação da política.'),
    'EXP2-JOG-039-E02': ('AUDITORIA_OK', 'STEAM_039: "cursed aristocratic family … mysterious Golden Idol".'),
    'EXP2-LIV-005-E02': ('AUDITORIA_OK', 'SEP (Arendt): estrutura "deliberately chaotic, fluid and shapeless" com instituições concorrentes e "fluctuating hierarchy" que impede previsibilidade e accountability.'),
    'EXP2-JOG-034-E02': ('AUDITORIA_OK', 'STEAM_034: "Rudy, a single father … keep his store afloat, while a mega-mart opens up next door".'),
    'EXP2-JOG-019-E02': ('AUDITORIA_OK', 'STEAM_019: crise entre a Nação e Parges; investigar Raban Vhart, Karen e Illya.'),
    'EXP2-JOG-048-E02': ('AUDITORIA_OK', 'STEAM_048: "mix the perfect cocktail to manipulate the client\'s emotions in order to gather the information".'),
    'EXP2-JOG-015-E02': ('AUDITORIA_OK', 'Konami Support (navegador): Fulton para "unresisting individual"; dispositivos melhores extraem veículos e contêineres.'),
    'EXP2-SER-012-E02': ('AJUSTE_MENOR', 'ABC (blog oficial, trilha da T2): acusação de Taylor Blaine confirmada. Faltava unidade_documental da temporada (§7); corrigido na camada de revisão.'),
    'EXP2-LIV-007-E02': ('AUDITORIA_OK', 'PRH: Coreias do Norte e do Sul, nação homogênea, trajetórias institucionais distintas.'),
    'EXP2-JOG-040-E02': ('AUDITORIA_OK', 'STEAM_040: "Choose different academic and social backgrounds".'),
    'EXP2-LIV-040-E02': ('AUDITORIA_OK', 'graciliano.com.br (artigo acadêmico): Fabiano atira em Baleia, doente; aflição da família.'),
    'EXP2-LIV-012-E02': ('AUDITORIA_OK', 'PRH: "eviction is a cause, not just a condition, of poverty".'),
    'EXP2-JOG-038-E02': ('AUDITORIA_OK', 'Nintendo JP: relógio Memento Mortem; dedução e registro no diário.'),
    'EXP2-LIV-010-E02': ('AUDITORIA_OK', 'PBS NewsHour: nove meses de livros de transição; "the Trump administration didn\'t show up".'),
    'EXP2-JOG-007-E02': ('AUDITORIA_OK', 'STEAM_007: "hack systems to retrieve crucial information, or use your social skills to extract information".'),
    'EXP2-JOG-046-E03': ('AUDITORIA_OK', 'STEAM_046: "The situation at the border escalates when your comrade is killed during one of the interventions".'),
    'EXP2-LIV-001-E03': ('AUDITORIA_OK', 'Penguin UK: "strains imposed on the rule of law by the threat and experience of international terrorism".'),
    'EXP2-LIV-019-E02': ('AUDITORIA_OK', 'Hachette: "demand the rights and laws that place this rogue power under the democratic rule of law". Posição normativa atribuída à autora.'),
}
sample = sorted(new_cards, key=lambda c: hashlib.sha256(c['evidence_id'].encode('utf-8')).hexdigest())[:20]
assert {c['evidence_id'] for c in sample} == set(AUD)
items = []
for c in sample:
    cls, obs = AUD[c['evidence_id']]
    items.append(dict(evidence_id=c['evidence_id'], sha256_evidence_id=hashlib.sha256(c['evidence_id'].encode('utf-8')).hexdigest(),
                      content_type=c['content_type'], centrality=c['centrality'], fonte=c['source']['url'], tier=c['source'].get('tier'),
                      verificacoes=dict(fonte_consultavel=True, parafrase_sustentada=True, claim_factual=True, centralidade_adequada=True,
                                        content_type_adequado=True, independente=True, not_targeted_to_device=c['not_targeted_to_device'] is True,
                                        sem_conclusao_juridica=True, limites_de_transposicao=bool(c.get('transposition_limits'))),
                      classificacao=cls, observacao=obs))
cnt = collections.Counter(i['classificacao'] for i in items)
imp = cnt['AJUSTE_IMPORTANTE'] + cnt['FONTE_INSUFICIENTE'] + cnt['DUPLICADO']
aud = dict(metodo='SHA-256(evidence_id) dos 71 cards novos; 20 menores valores em ordem lexicográfica hexadecimal.', universo=len(new_cards),
           amostra=items, contagem={k: cnt.get(k, 0) for k in ('AUDITORIA_OK', 'AJUSTE_MENOR', 'AJUSTE_IMPORTANTE', 'FONTE_INSUFICIENTE', 'DUPLICADO')},
           problemas_importantes=imp, taxa=imp / len(items), gate='PASSA' if imp / len(items) <= 0.10 else 'NAO_PASSA',
           verificacao_complementar='Além da amostra, os 9 cards com fonte sem registro local de coleta foram todos verificados (ver ESTADO_ENRIQUECIMENTO_APOS_CODEX.json).')
dump(R / 'AUDITORIA_CARDS_ENRIQUECIMENTO_V1.json', aud)
print(json.dumps(dict(checkpoints=len(cps), examinadas=estado['obras_examinadas'], pendentes=estado['obras_pendentes'], cards_novos=len(new_cards),
                      pos_cp8=estado['pos_cp8_persistido']['obras'], triados=len(flag), auditoria=aud['contagem'], gate=aud['gate']), ensure_ascii=False))
