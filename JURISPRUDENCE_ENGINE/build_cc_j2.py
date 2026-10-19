"""CC-J2 — second REAL jurisprudence batch of the Código Civil (CC2002), built on the generic batch engine. Host-only; nothing published;
every decision AWAITING_USER_RATIFICATION; nothing materialized, deployed or flashed.

Batch = CONFIG (channels, exclusions derived from the CC-J1 ratification, themes of the CC) + REVIEW (human reading of the official evidence).
Channels (official only): Planalto "Vide" (fresh download, 2026-10-18), STF search Q1 (pilot capture + re-check of the RG-suffixed merit rows on
the official theme pages), STJ súmulas (official PDF index), STJ qualified precedents (official open-data Temas.csv — new adapter #4).
Writes CC_J2_DECISIONS.json, CC_J2_REVIEW.md, CC_J2_RATIFICATION_DOSSIER.md/.json, CC_J2_SCALE_METRICS.json, CC_J2_SIMULATION_REPORT.md,
cc_j2/CC_J2_BACKLOG.json and the SIMULATION_ONLY package cc_j2_simulation/.   Usage: python build_cc_j2.py [--check] [--select-only]
"""
import collections
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'pilot_cc')]
import batch_engine as E  # noqa: E402
import cc_pilot_evidence as EV  # noqa: E402
from cc_j2_review import REVIEW, BATCH_NOTES  # noqa: E402

NORM, PREFIX, N = 'CC2002', 'CCJ2', 30
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
PLANALTO = HERE / 'cc_j2/PLANALTO_CC2002_2026-10-18.json'
STF_RECHECK = HERE / 'cc_j2/STF_Q1_RECHECK.json'
STJ_SUM = HERE / 'stj/STJ_SUMULAS_INDEX.json'
STJ_PREC = HERE / 'stj/STJ_PRECEDENTES_INDEX.json'
CCJ1_REC = HERE / 'CC_J1_RATIFICATION_RECORD.json'
CCJ1_DEC = HERE / 'CC_J1_DECISIONS.json'
PHYSICAL_SD = HERE / 'CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD'          # = card bytes (CC_J1_PHYSICAL_DEPLOY: DEPLOYED_HASHES EXACT)
CARD = HERE / 'CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
PROBE = '/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
OUT_SIM = HERE / 'cc_j2_simulation'
CHANNELS = ('PLANALTO_VIDE', 'STF_SEARCH_Q1', 'STF_Q1_RECHECK', 'STJ_SUMULAS_PDF', 'STJ_PRECEDENTES_DADOS_ABERTOS')
JOINT = {'STF:ADI:6792': 'STF:ADI:6792-7055', 'STF:ADI:7055': 'STF:ADI:6792-7055'}
THEMES = [('PERSONALIDADE', 11, 21), ('PARTE_GERAL', 1, 10), ('PARTE_GERAL', 22, 188), ('PRESCRICAO_DECADENCIA', 189, 211),
          ('PARTE_GERAL', 212, 232), ('OBRIGACOES', 233, 420), ('CONTRATOS', 421, 853), ('OBRIGACOES', 854, 926),
          ('RESPONSABILIDADE_CIVIL', 927, 954), ('OBRIGACOES', 955, 965), ('EMPRESA', 966, 1195), ('COISAS', 1196, 1510),
          ('FAMILIA', 1511, 1783), ('SUCESSOES', 1784, 2027), ('TRANSICAO', 2028, 2046)]
AREAS = [('PARTE_GERAL', 1, 232), ('OBRIGACOES', 233, 965), ('EMPRESA', 966, 1195), ('COISAS', 1196, 1510), ('FAMILIA', 1511, 1783),
         ('SUCESSOES', 1784, 2027), ('DISPOSICOES_FINAIS_TRANSITORIAS', 2028, 2046)]
# CC-J1 dossier options the human saw and did not take (target, precedent): an equivalent decision already exists.
CCJ1_OPTIONS_DECLINED = {('CC2002:ART.1698', 'STJ:SUMULA:596'): 'CCJ1-29: o dossiê nomeou o art. 1.698 como alvo adicional possível; '
                                                                 'a ratificação aprovou só o art. 1.696.'}


def stf_pairs(amend_years):
    al = {a: pid for pid, f in EV.PRECEDENTS.items() for a in f.get('alias', [])}
    out = []

    def fact(pid, channel, target, cite):
        base = 'STF:ADI:6792' if pid == 'STF:ADI:6792-7055' else pid
        f = EV.PRECEDENTS[base]
        s = EV.SOURCES[f['sources'][0]]
        klass = pid.split(':')[1]
        return dict(channel=channel, precedent=pid, target=target, tribunal='STF', klass=klass, number=pid.split(':')[2].replace('-', '/'),
                    device_label=E.JT.label('repercussao_geral' if klass == 'RG' else klass.lower(), 'STF', pid.split(':')[2].replace('-', '/')),
                    judgment_year=f['judgment_year'], current=True, final=True, merit=True, status_text=f['status_text'], judgment=f['status_text'],
                    evidence=f['evidence'], source=dict(id='+'.join(f['sources']), url=s['url'], sha256=s['sha256'], tier='A'),
                    text_names_article=True, ficha_kind='STF', cited_as=cite)
    for a in E.load(PLANALTO)['annotations']:                                      # adapter #1 on the fresh Planalto download
        raw = f"STF:{a['klass']}:{a['number']}"
        pid = JOINT.get(raw, al.get(raw, raw))
        if pid in {JOINT.get(k, k) for k in EV.PRECEDENTS}:
            out.append(fact(pid, 'PLANALTO_VIDE', a['target_id'], a['annotation']))
    for head, org, _, tema, arts, cite in EV.Q1_ROWS:                              # adapter #2, pilot capture (pilot rule)
        if org != 'Tribunal Pleno' or not tema or head.endswith(' RG') or not arts:
            continue
        for art in arts:
            m = re.match(r'([\d.]+)(?:,\s*§\s*(\d+))?', art)
            out.append(fact(f'STF:RG:{tema}', 'STF_SEARCH_Q1', E.T.format_target_id(NORM, m.group(1).replace('.', ''), paragraph=m.group(2)), cite))
    for r in E.load(STF_RECHECK)['rows']:                                          # RG-suffixed merit rows, re-checked on the theme page
        s = r['sources'][0]
        for t in r['discovered_targets']:
            out.append(dict(channel='STF_Q1_RECHECK', precedent=r['precedent'], target=t, tribunal='STF', klass='RG', number=r['precedent'].split(':')[2],
                            device_label=E.JT.label('repercussao_geral', 'STF', r['precedent'].split(':')[2]), judgment_year=r['judgment_year'],
                            current=True, final=True, merit=r['merit'], status_text=r['status_text'], judgment=r['status_text'], evidence=r['evidence'],
                            source=dict(id='+'.join(x['id'] for x in r['sources']), url=s['url'], sha256=s['sha256'], tier='A',
                                        extra=r['sources'][1:]), text_names_article=True, ficha_kind='STF', cited_as=r['q1_row']))
    return out


def build():
    index_doc = E.load(CC_INDEX)
    index = {t['target_id'] for t in index_doc['targets']}
    pl = E.load(PLANALTO)
    amend = {t: pl['amendments'].get(t, []) for t in index}                       # complete scope: absent = current wording, no note
    stj_sum, stj_prec = E.load(STJ_SUM), E.load(STJ_PREC)
    _, _, rows = E.physical_layer(PHYSICAL_SD)
    base_pairs = {(r['target_id'], r['precedent_id']) for r in rows}
    cov = collections.Counter(r['target_id'] for r in rows if E.namespace_of(r['target_id']) == NORM)
    pairs = stf_pairs(amend) + E.pairs_from_stj_sumulas(stj_sum, NORM) + E.pairs_from_stj_precedentes(stj_prec, NORM)
    pexc, qexc = E.exclusions_from_ratification(E.load(CCJ1_REC), E.load(CCJ1_DEC)['decisions'], 'CCJ1', CCJ1_OPTIONS_DECLINED, stj_prec)
    cands, excluded, corrob = E.backlog(pairs, NORM, index, amend, base_pairs, pexc, qexc)
    sel, remaining = E.select(cands, N, THEMES, cov, CHANNELS)
    backlog = dict(schema_version=1, batch='CC-J2', norm=NORM, mode='HOST_ONLY_BACKLOG', channels=list(CHANNELS),
                   discovered_pairs=len(pairs), cross_channel_corroborations=corrob, excluded=excluded,
                   excluded_by_code=dict(sorted(collections.Counter(x['code'] for x in excluded).items())),
                   candidates=[dict(precedent=c['precedent'], channel=c['channel'], theme=c['theme'], score=c['score'], score_parts=c['score_parts'],
                                    discovered_targets=c['discovered_targets'], selected=c in sel) for c in sorted(cands, key=lambda c: c['precedent'])],
                   CANDIDATE_PRECEDENTS=len(cands), SELECTED=len(sel), REMAINING_FOR_NEXT_BATCH=[c['precedent'] for c in remaining])
    if '--select-only' in sys.argv:
        return dict(backlog=backlog, selected=sel)
    decisions = E.apply_review(sel, REVIEW, NORM, index, PREFIX)
    by = {c['precedent']: c for c in sel}
    for x in decisions:                                   # automatic ficha draft from the official text (simulation only) or ficha already on card
        x['steps']['AUTO_FICHA_DRAFTED'] = x['decision'] in E.LINKING
    rels = E.relations(decisions)
    new_records, new_fichas = {}, {}
    for x in decisions:
        if x['decision'] in E.LINKING:
            rec, body = E.draft_record_and_ficha(dict(by[x['precedent']], **x), 'CC-J2')
            new_records[x['precedent']] = rec
            new_fichas[E.JT.ficha(x['precedent'])] = body
    card_fichas = {k.split('/')[-1] for k in E.load(CARD)['entries'] if k.startswith(E.P.CONTENT + '/')}
    new_rels = [dict(norm=NORM, target_id=t, precedent_id=p, origin='CC-J2 (SIMULATION_ONLY)') for t, p in rels]
    prov = E.P.provisional_ids() + [x['precedent'] for x in decisions if x['decision'] == 'PROMOTE_PROVISIONAL_RECOMMENDED']
    files, sim = E.simulate(PHYSICAL_SD, card_fichas, new_rels, new_records, new_fichas, prov, E.P.known_targets(), PROBE, NORM)
    base_cc = sorted(p for p in base_pairs if E.namespace_of(p[0]) == NORM)
    proj = sorted(set(base_cc) | set(rels))
    green = sorted(set(base_cc) | set(E.relations(decisions, ('GREEN',))))
    cover = dict(CURRENT=E.coverage(base_cc, index_doc['targets'], THEMES, AREAS), PROJECTED=E.coverage(proj, index_doc['targets'], THEMES, AREAS))
    g = collections.Counter(x['group'] for x in decisions)
    d = collections.Counter(x['decision'] for x in decisions)
    metrics = dict(CC_J2_CANDIDATES=len(decisions), GREEN=g['GREEN'], YELLOW=g['YELLOW'], RED=g['RED'],
                   PROMOTE_RECOMMENDED=d['PROMOTE_RECOMMENDED'], PROMOTE_PROVISIONAL_RECOMMENDED=d['PROMOTE_PROVISIONAL_RECOMMENDED'],
                   REALLOCATE_RECOMMENDED=d['REALLOCATE_RECOMMENDED'], MULTI_TARGET_RECOMMENDED=d['MULTI_TARGET_RECOMMENDED'],
                   CONTEXTUAL_RECOMMENDED=d['CONTEXTUAL_RECOMMENDED'], REJECT_RECOMMENDED=sum(v for k, v in d.items() if k.startswith('REJECT')),
                   ALREADY_COVERED=d['ALREADY_COVERED'], DUPLICATE_RECOMMENDATION=d['DUPLICATE_RECOMMENDATION'],
                   UNRESOLVED=sum(v for k, v in d.items() if k.startswith('UNRESOLVED')),
                   HUMAN_JUDGMENT_REQUIRED=sum(x['HUMAN_JUDGMENT_REQUIRED'] for x in decisions),
                   RELATIONS_PROPOSED=len(rels), TARGETS_PROPOSED=len({t for t, _ in rels}), NEW_TARGETS_WITHOUT_J=len({t for t, _ in rels} - {t for t, _ in base_cc}),
                   CC_PHYSICAL_BASELINE=f'{len(base_cc)}/{len({t for t, _ in base_cc})}', CC_PROJECTED_IF_RATIFIED=f'{len(proj)}/{len({t for t, _ in proj})}',
                   CC_PROJECTED_GREEN_ONLY=f'{len(green)}/{len({t for t, _ in green})}', CC_J1_REVALIDATION_REQUIRED=sum(
                       1 for x in decisions if (x['CC_J1_INTERACTION'] or {}).get('kind') == 'CC_J1_REVALIDATION_REQUIRED'))
    doc = dict(schema_version=1, batch='CC-J2', norm=NORM, mode='HOST_ONLY_DECISIONS_NO_MATERIALIZATION', status='AWAITING_USER_RATIFICATION',
               baseline='MULTINORM_FROZEN_CF315_198_CC29_24 (CC_J1_FROZEN_29_24 inalterado)', selection=dict(
                   rule='Unidade = precedente (todos os alvos descobertos dele juntos). Pontuação = citação oficial direta + vigência do dispositivo + '
                        'vigência do precedente + lacuna de cobertura do alvo + vários dispositivos; ordem dentro do tema por (-pontuação, canal, id); '
                        'rodízio entre os temas do CC até 30.', n=N, channels=list(CHANNELS)),
               metrics=metrics, notes=BATCH_NOTES, totals=dict(sorted(d.items())), proposed_relations=[dict(target_id=t, precedent=p) for t, p in rels],
               coverage=cover, decisions=decisions)
    return dict(backlog=backlog, doc=doc, files=files, sim=sim, decisions=decisions)


def git_sloc(commit, path, data_names):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / Path(path).name
        f.write_bytes(subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout)
        return E.sloc(f, data_names)


CCJ1_TOOLS = [('f84d267', 'JURISPRUDENCE_ENGINE/build_cc_j1.py', ('REVIEW', 'JOINT')),
              ('a927384', 'JURISPRUDENCE_ENGINE/build_cc_j1_dossier.py', ('C',)),
              ('ec3b6ff', 'JURISPRUDENCE_ENGINE/build_cc_j1_simulation.py', ())]
CCJ2_TOOLS = [('batch_engine.py', 'NEW_CORE_ENGINE', ()), ('discovery_stj_precedentes.py', 'NEW_SOURCE_ADAPTER', ()),
              ('build_cc_j2.py', 'BATCH_CONFIG', ('THEMES', 'AREAS', 'CCJ1_OPTIONS_DECLINED', 'CHANNELS', 'JOINT', 'CCJ1_TOOLS', 'CCJ2_TOOLS',
                                                  'STEP_MAP')),
              ('cc_j2_review.py', 'REVIEW_DATA', ('REVIEW', 'BATCH_NOTES'))]
# tools later extended by other missions are measured as they were when CC-J2 was frozen (the CC-J2 metric must not drift)
CCJ2_PINS = {'discovery_stj_precedentes.py': 'a8a4d7a', 'build_cc_j2.py': 'a8a4d7a'}
STEP_MAP = dict(AUTO_DISCOVERED='AUTO_DISCOVERED', AUTO_TARGET_NORMALIZED='AUTO_TARGET_NORMALIZATION', AUTO_NAMESPACE_CHECKED='AUTO_NAMESPACE_CHECK',
                AUTO_TEMPORAL_CHECKED='AUTO_TEMPORAL_CHECK', AUTO_DUPLICATE_CHECKED='AUTO_DUPLICATE_CHECK', AUTO_SOURCE_VERIFIED='OFFICIAL_SOURCE_FOUND')


def ccj1_metrics():
    dec = E.load(CCJ1_DEC)
    pilot = E.load(HERE / 'pilot_cc/PORTABILITY_PILOT_CC.json')
    pc = {c['id']: c for c in pilot['candidates']}
    sp = {(p['target'], p['precedent']): p for p in pilot['stj_channel']['pairs']}
    steps = collections.Counter()
    for x in dec['decisions']:
        st = pc[x['pilot_candidate']]['steps'] if x['pilot_candidate'] else sp[(x['discovered_target'], x['precedent'])]['steps']
        for k, v in STEP_MAP.items():
            steps[k] += bool(st.get(v))
    sim = {p['precedent'] for p in dec['simulation_relations']}
    steps['AUTO_FICHA_DRAFTED'] = sum(1 for x in dec['decisions'] if x['precedent'] in sim)
    code = {path.split('/')[-1]: dict(zip(('code', 'review_data'), git_sloc(c, path, dn))) for c, path, dn in CCJ1_TOOLS}
    m = dec['metrics']
    return dict(CANDIDATES=m['CC_J1_CANDIDATES'], CANDIDATE_UNIT='par (alvo, precedente); 28 precedentes distintos',
                **{k: steps[k] for k in E.STEPS}, HUMAN_JUDGMENT_REQUIRED=m['CC_J1_HUMAN_REVIEW_REQUIRED'],
                RELATIONS_PROPOSED=m['CC_J1_RELATIONS_PROPOSED'], TARGETS_PROPOSED=m['CC_J1_TARGETS_PROPOSED'],
                NEW_CODE_LINES_REQUIRED=sum(v['code'] for v in code.values()), REVIEW_DATA_LINES=sum(v['review_data'] for v in code.values()),
                code_by_file=code, NEW_CORE_ENGINE_CODE_LINES=sum(v['code'] for v in code.values()),
                EXISTING_TOOLS_MODIFIED=0, NEW_TOOLS_REQUIRED=len(CCJ1_TOOLS), NEW_SOURCE_ADAPTERS=0,
                SOURCE_ADAPTERS_BUILT_JUST_BEFORE=['discovery_planalto.py (piloto)', 'discovery_stj_sumulas.py (sprint de escala)'],
                SOURCE_BLOCKS=1, source_blocks_note='busca de súmulas do STJ com desafio anti-robô (não contornado); resolvido antes do lote pelo '
                                                    'PDF oficial', BATCH_SPECIFIC_LOGIC='seleção, revisão, dossiê e simulação codificados só para o CC-J1')


def scale_metrics(out):
    decs = out['decisions']
    steps = {k: sum(1 for x in decs if x['steps'].get(k)) for k in E.STEPS}
    code = {f: dict(role=role, **dict(zip(('code', 'review_data'), git_sloc(CCJ2_PINS[f], 'JURISPRUDENCE_ENGINE/' + f, dn) if f in CCJ2_PINS
                                          else E.sloc(HERE / f, dn)))) for f, role, dn in CCJ2_TOOLS}
    core = code['batch_engine.py']['code']
    j2 = dict(CANDIDATES=len(decs), CANDIDATE_UNIT='precedente (todos os seus alvos juntos); %d pares (alvo, precedente)' % sum(
                  len(x['discovered_targets']) for x in decs), **steps,
              HUMAN_JUDGMENT_REQUIRED=sum(x['HUMAN_JUDGMENT_REQUIRED'] for x in decs), RELATIONS_PROPOSED=out['doc']['metrics']['RELATIONS_PROPOSED'],
              TARGETS_PROPOSED=out['doc']['metrics']['TARGETS_PROPOSED'],
              NEW_CODE_LINES_REQUIRED=sum(v['code'] for v in code.values()), REVIEW_DATA_LINES=sum(v['review_data'] for v in code.values()),
              code_by_file=code, NEW_CORE_ENGINE_CODE_LINES=core,
              EXISTING_TOOLS_MODIFIED=1, existing_tools_modified=['JURISPRUDENCE_AUDIT/juris_types.py: +2 entradas na tabela KLASS_TO_TIPO '
                                                                  '(REPETITIVO -> repetitivo_stj, IAC -> iac; rótulos já existentes no firmware)'],
              NEW_TOOLS_REQUIRED=len(CCJ2_TOOLS), NEW_SOURCE_ADAPTERS=1, SOURCE_BLOCKS=0,
              MANUAL_TARGET_CORRECTIONS=sum(1 for x in decs if x['decision'] in E.LINKING and set(x['proposed_targets']) != set(x['discovered_targets'])),
              AUTO_EXCLUDED_AT_BACKLOG=len(out['backlog']['excluded']))
    return dict(schema_version=1, kind='FACTORY_SPEED_METRICS', batch='CC-J2', compared_with='CC-J1', CC_J1=ccj1_metrics(), CC_J2=j2,
                NEW_CORE_ENGINE_CODE=core, SCALABILITY_WARNING=dict(
                    status='YES_ONE_TIME', reason='O CC-J1 tinha a etapa de lote (seleção, revisão, dossiê, simulação) codificada só para ele; '
                    'repeti-la exigiria reescrever lógica de lote a cada lote. O CC-J2 a generalizou uma vez em batch_engine.py, sem nada '
                    'específico do CC (a norma entra por configuração). Nenhuma lógica específica do CC foi reescrita. Meta do próximo lote: '
                    'NEW_CORE_ENGINE_CODE = 0 (só configuração + tabela de revisão).', cc_specific_logic_rewritten=False),
                automation_gaps=['realocação "parágrafo único do art." (Tema 1019) e referência inexistente "943, I" (Súmula 642)',
                                 'duplicata de tese idêntica entre temas (308/309): detectável automaticamente (questão + tese iguais); hoje humana',
                                 'pertinência material, temporalidade jurídica (Leis 14.905/2024 e 15.040/2024) e interação com o CC-J1: humanas'])


def render_sim(out):
    s, m = out['sim'], out['doc']['metrics']
    cf_reg = s['OTHER_NORM_KEYS_CHANGED'] + sum(v for k, v in s['lost_by_namespace'].items() if k != NORM)
    j1_reg = s['lost_by_namespace'].get(NORM, 0) + s['BASELINE_RECORD_LINES_MISSING']
    L = ['# CC-J2 — candidato de simulação (SIMULATION_ONLY, nunca implantável)', '', '```',
         'STATUS = SIMULATION_ONLY · DEPLOYABLE = NO · SD_CHANGED = NO · FIRMWARE_CHANGED = NO',
         f"DUPLICATE_QUERY_KEYS = {s['DUPLICATE_QUERY_KEYS']} · CC_J1_BASELINE_PRESERVED = {'YES' if j1_reg == 0 else 'NO'} · CF_REGRESSION = {cf_reg} · "
         f"CC_J1_REGRESSION = {j1_reg}", '```', '',
         'Base: a camada normalizada física congelada (`CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD`, idêntica ao cartão), relida linha a linha '
         '(CF88 311 + ADCT 4 + CC2002 29 relações). Sobre ela entram as relações GREEN + YELLOW do CC-J2, empacotadas pelo `generic_packager.py` '
         'sem mudança. Pastas em `cc_j2_simulation/`.', '', '| Item | Valor |', '|---|---|']
    rows = [('Relações por norma (relações/alvos)', ', '.join(f'{k} {v[0]}/{v[1]}' for k, v in sorted(s['counts'].items()))),
            ('Relações novas do CC-J2', s['NEW_RELATIONS']), ('Visíveis no caminho multinorma do firmware (simulado)', s['NEW_VISIBLE']),
            ('Ficha abre / BACK volta à mesma lista', f"{s['NEW_FICHA_OPEN']} / {s['NEW_BACK']}"),
            ('Rótulos', ', '.join(f'{k} {v}' for k, v in s['labels'].items())), ('Rótulos OUTRO', s['OUTRO_LABELS']),
            ('Chaves do baseline preservadas (grupo antigo = prefixo do novo)', f"{s['BASELINE_KEYS'] - s['BASELINE_KEYS_NOT_PRESERVED']}/{s['BASELINE_KEYS']}"),
            ('Linhas de registro do baseline ausentes', s['BASELINE_RECORD_LINES_MISSING']), ('Chaves CF/ADCT alteradas', s['OTHER_NORM_KEYS_CHANGED']),
            ('Registros reaproveitados do cartão', ', '.join(s['records_reused_from_card'])),
            ('Fichas novas (rascunho automático)', len(s['fichas_new'])), ('Fichas compartilhadas entre normas', ', '.join(s['fichas_shared_across_norms'])),
            ('Projeção do CC se GREEN + YELLOW fossem ratificados', m['CC_PROJECTED_IF_RATIFIED']), ('Projeção só com GREEN', m['CC_PROJECTED_GREEN_ONLY'])]
    L += [f'| {a} | {b} |' for a, b in rows]
    L += ['', 'A projeção não é baseline. O baseline físico continua `CC_J1_FROZEN_29_24` (29/24), e a CF continua 315/198 (LEXV1 intocado).',
          'Os rótulos "REPETITIVO STJ n" e "IAC n" já existem no firmware multinorma, mas nunca foram validados fisicamente.']
    return '\n'.join(L) + '\n', cf_reg, j1_reg


def render_coverage(doc):
    L = ['', '## Cobertura do CC por livro (atual → projetada; a projeção não é baseline)', '',
         '| Livro | Relações | Alvos | Artigos com J | Artigos no CC | Densidade |', '|---|---:|---:|---:|---:|---:|']
    cur, pro = doc['coverage']['CURRENT'], doc['coverage']['PROJECTED']
    for k in cur:
        a, b = cur[k], pro[k]
        L.append(f"| {k} | {a['relations']} → {b['relations']} | {a['targets']} → {b['targets']} | {a['articles_with_j']} → {b['articles_with_j']} | "
                 f"{a['articles_in_norm']} | {a['density_pct']}% → {b['density_pct']}% |")
    holes = sorted(pro, key=lambda k: (pro[k]['density_pct'], k))[:3]
    L += ['', f"Menor densidade projetada: {', '.join(holes)}."]
    return L


def render_speed(sm, backlog):
    a, b = sm['CC_J1'], sm['CC_J2']
    rows = [('Candidatos', f"{a['CANDIDATES']} (pares)", f"{b['CANDIDATES']} (precedentes)"), ('Relações propostas', a['RELATIONS_PROPOSED'], b['RELATIONS_PROPOSED']),
            ('Etapas automáticas (6 checagens + ficha, por candidato)', f"{sum(a[k] for k in E.STEPS)}/{7 * a['CANDIDATES']}",
             f"{sum(b[k] for k in E.STEPS)}/{7 * b['CANDIDATES']}"),
            ('Exclusões automáticas no backlog', '—', b['AUTO_EXCLUDED_AT_BACKLOG']),
            ('Revisão humana (julgamento jurídico)', a['HUMAN_JUDGMENT_REQUIRED'], b['HUMAN_JUDGMENT_REQUIRED']),
            ('Correções manuais de alvo', '—', b['MANUAL_TARGET_CORRECTIONS']),
            ('Código novo de motor (linhas)', a['NEW_CORE_ENGINE_CODE_LINES'], b['NEW_CORE_ENGINE_CODE_LINES']),
            ('Código de configuração do lote (linhas)', '— (misturado no motor do lote)', b['code_by_file']['build_cc_j2.py']['code']),
            ('Dados de revisão humana (linhas)', a['REVIEW_DATA_LINES'], b['REVIEW_DATA_LINES']),
            ('Ferramentas existentes modificadas', a['EXISTING_TOOLS_MODIFIED'], b['EXISTING_TOOLS_MODIFIED']),
            ('Novos adapters', f"{a['NEW_SOURCE_ADAPTERS']} (2 feitos logo antes)", b['NEW_SOURCE_ADAPTERS']),
            ('Bloqueios de fonte', a['SOURCE_BLOCKS'], b['SOURCE_BLOCKS'])]
    L = ['', '## Velocidade da fábrica (CC-J1 × CC-J2)', '', '| Métrica | CC-J1 | CC-J2 |', '|---|---:|---:|'] + [f'| {r} | {x} | {y} |' for r, x, y in rows]
    L += ['', f"Por etapa (CC-J2): " + ', '.join(f'{k} {b[k]}/{b["CANDIDATES"]}' for k in E.STEPS) + '.',
          f"SCALABILITY_WARNING = {sm['SCALABILITY_WARNING']['status']}: {sm['SCALABILITY_WARNING']['reason']}",
          'Lacunas de automação: ' + '; '.join(sm['automation_gaps']) + '.', '',
          '## Fontes STJ fora das súmulas (Parte C)', '',
          'STJ_QUALIFIED_PRECEDENTS_SOURCE = AVAILABLE. O Portal de Dados Abertos do STJ publica o dataset "Precedentes qualificados" (CC-BY; '
          'Temas.csv com temas repetitivos, IAC, SIRDR, PUIL e controvérsias, tese firmada e situação). A página oficial de pesquisa de precedentes '
          'qualificados também respondeu normalmente. Nenhum desafio anti-robô foi contornado. Integração host-only pelo adaptador #4 '
          '(`discovery_stj_precedentes.py` → `stj/STJ_PRECEDENTES_INDEX.json`).',
          f"Backlog: {backlog['discovered_pairs']} pares descobertos, {len(backlog['excluded'])} excluídos automaticamente "
          f"({', '.join(f'{k} {v}' for k, v in backlog['excluded_by_code'].items())}), {backlog['CANDIDATE_PRECEDENTS']} precedentes candidatos, "
          f"{backlog['SELECTED']} selecionados; ficam para o próximo lote: {', '.join(backlog['REMAINING_FOR_NEXT_BATCH'])}."]
    return L


def outputs(out):
    doc = out['doc']
    sim_md, cf_reg, j1_reg = render_sim(out)
    doc['metrics'].update(CF_REGRESSION=cf_reg, CC_J1_REGRESSION=j1_reg, DUPLICATE_QUERY_KEYS=out['sim']['DUPLICATE_QUERY_KEYS'],
                          STJ_QUALIFIED_PRECEDENTS_SOURCE='AVAILABLE')
    sm = scale_metrics(out)
    review_md = E.render_review(doc, 'CC-J2 — segundo lote real do Código Civil (propostas aguardando ratificação)')
    review_md = review_md.replace('\nNenhuma decisão é HUMAN_APPROVED', '\n'.join(render_coverage(doc) + render_speed(sm, out['backlog'])) +
                                  '\n\nNenhuma decisão é HUMAN_APPROVED')
    man = dict(out['sim'], schema_version=1, kind='CC_J2_SIMULATION_CANDIDATE', cc_j2_human_approved=False,
               base='camada normalizada física congelada (CF/ADCT 315 + CC-J1 29)')
    j = lambda o: (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')  # noqa: E731
    files = {HERE / 'CC_J2_DECISIONS.json': j(doc), HERE / 'CC_J2_REVIEW.md': review_md.encode('utf-8'),
             HERE / 'CC_J2_RATIFICATION_DOSSIER.md': E.render_dossier(doc, 'CC-J2 — dossiê de ratificação (GREEN / YELLOW / RED)').encode('utf-8'),
             HERE / 'CC_J2_RATIFICATION_DOSSIER.json': j(E.dossier_json(doc)), HERE / 'CC_J2_SCALE_METRICS.json': j(sm),
             HERE / 'CC_J2_SIMULATION_REPORT.md': sim_md.encode('utf-8'), HERE / 'cc_j2/CC_J2_BACKLOG.json': j(out['backlog']),
             OUT_SIM / 'CC_J2_SIMULATION_MANIFEST.json': j(man)}
    files.update({OUT_SIM / 'SD' / k: v for k, v in out['files'].items()})
    return files


def main():
    out = build()
    if '--select-only' in sys.argv:
        b = out['backlog']
        print(json.dumps({k: v for k, v in b.items() if k not in ('candidates', 'excluded', 'cross_channel_corroborations')}, ensure_ascii=False, indent=1))
        return
    files = outputs(out)
    if '--check' in sys.argv:
        ok = all(p.is_file() and p.read_bytes().replace(b'\r\n', b'\n') == v for p, v in files.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for p, v in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(v)
    print(json.dumps(out['doc']['metrics'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
