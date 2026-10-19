"""CC-J2 — MATERIALIZATION PREFLIGHT: the ratified CC-J2 relations -> an immutable host-only deploy candidate (never written to a card).

Authority: CC_J2_RATIFICATION_RECORD.json only (its pinned hashes are re-verified; the dossiers are not re-interpreted). Base = the frozen
physical normalized layer (CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD, byte-identical to the card): CF88 311 + ADCT 4 + CC2002 29 rows are
re-read and re-packaged with the 20 ratified CC-J2 relations by the generic packager. Device types come from juris_types.physical_status
(the current truth), never from the frozen device_status table. Fichas are built only from ratified evidence and notes.
Deploy shape: the multinorm firmware reads FIXED paths (06_NORMALIZADO/JUR_LOOKUP.IDX and JURISPRUDENCIA.IDX), so adding relations to an
existing layer REPLACES those index files; only the new fichas are additive. This is reported as a blocker for an additive-only deploy.
Writes CC_J2_MATERIALIZATION_CANDIDATE/ + CC_J2_MATERIALIZATION_PREFLIGHT.md.   Usage: python build_cc_j2_materialization.py [--check]
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import batch_engine as E  # noqa: E402
import juris_types as JT  # noqa: E402
from build_cc_j1_materialization import human_target, target_order, CC_FILE, CF_FILE, LOOKUP_ENTRY_BYTES, CACHE_ENTRIES_MAX  # noqa: E402

P, S, T = E.P, E.S, E.T
REC = HERE / 'CC_J2_RATIFICATION_RECORD.json'
DEC = HERE / 'CC_J2_DECISIONS.json'
STJ = HERE / 'stj/STJ_SUMULAS_INDEX.json'
PLANALTO = HERE / 'cc_j2/PLANALTO_CC2002_2026-10-18.json'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
BASE = HERE / 'CC_J1_MATERIALIZATION_CANDIDATE'
BASE_SD = BASE / 'candidate/SD'
CARD = HERE / 'CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
OUT = HERE / 'CC_J2_MATERIALIZATION_CANDIDATE'
REPORT = HERE / 'CC_J2_MATERIALIZATION_PREFLIGHT.md'
EXPECTED = dict(approved=19, not_approved=['CCJ2-03', 'CCJ2-10', 'CCJ2-12', 'CCJ2-13', 'CCJ2-15', 'CCJ2-19', 'CCJ2-24', 'CCJ2-26', 'CCJ2-27',
                                           'CCJ2-28', 'CCJ2-30'], relations=20, targets=18, new_targets=15)
SHARED_EXPECTED = {'CC2002:ART.206:PAR.5:INC.I': ['STJ:SUMULA:503', 'STJ:SUMULA:547', 'STJ:REPETITIVO:639'],
                   'CC2002:ART.206:PAR.3:INC.IV': ['STJ:SUMULA:547', 'STJ:REPETITIVO:610'],
                   'CC2002:ART.1641:INC.II': ['STF:RG:1236', 'STJ:SUMULA:655'],
                   'CC2002:ART.1829': ['STF:RG:498', 'STF:RG:809'], 'CC2002:ART.354': ['STJ:REPETITIVO:426', 'STJ:REPETITIVO:381']}
# reader-facing notes of the fichas — only from the ratified notes/evidence (CC_J2_RATIFICATION_RECORD + final dossier); no new content
FICHA_NOTES = {
    'STJ:SUMULA:619': 'A ocupação indevida de bem público é mera detenção (art. 1.208) e não gera indenização pelas acessões (art. 1.255) nem pelas '
                      'benfeitorias.',
    'STJ:IAC:1': 'HISTORICAL_BUT_RELEVANT: aplica-se às execuções regidas pelo CPC/1973; não é regra geral do CPC/2015 (ver art. 921 do CPC/2015).',
    'STJ:REPETITIVO:639': 'Contexto: crédito rural, execução fiscal; 20 anos (CC/1916) ou 5 anos (CC/2002, art. 206, § 5º, I).',
    'STJ:SUMULA:642': 'A referência legislativa oficial do STJ cita "art. 943, I", mas o art. 943 não tem incisos; o dispositivo é o art. 943 '
                      '(correção ART943_INC1 -> ART943).',
    'STJ:REPETITIVO:1019': 'Desapropriação indireta: prazo de 10 anos do parágrafo único do art. 1.238 (obras do Poder Público, utilidade pública ou '
                           'interesse social), não o prazo do caput.',
    'STJ:SUMULA:637': 'EXCEÇÃO / LIMITE INTERPRETATIVO ao art. 1.210, § 2º: a alegação de domínio não garante, por si, tutela possessória, mas o ente '
                      'público que intervém na possessória entre particulares pode deduzi-la incidentalmente.',
    'STJ:SUMULA:655': 'SUBJECT_TO_TEMA_1236_STF: após o Tema 1236/STF (2024), o regime do art. 1.641, II pode ser afastado por manifestação expressa de '
                      'vontade, mediante escritura pública; sem esse pacto, aplica-se esta súmula. Não há obrigatoriedade absoluta.',
    'STJ:REPETITIVO:381': 'Delimita o campo do art. 354; não é interpretação positiva geral do dispositivo.',
    'STJ:REPETITIVO:1130': 'Tese definitiva, não provisória: o portal do STJ ainda indica "RE pendente" (situação defasada), mas o STF negou repercussão '
                           'geral no Tema 1432 (questão infraconstitucional), com trânsito em julgado em 18/09/2026.',
    'STJ:REPETITIVO:610': 'Prazo trienal do art. 206, § 3º, IV (CC/2002) para a pretensão decorrente da nulidade de cláusula de reajuste de plano de saúde; '
                          '20 anos sob o CC/1916, observada a transição do art. 2.028.',
}
TIPO = {'SUMULA': 'sumula', 'REPETITIVO': 'repetitivo_stj', 'IAC': 'iac', 'RG': 'repercussao_geral'}
CHECKLIST = [
    ('Boot', 'Boot geral; diagnóstico LEXV1 PASS; cache juris carregado pela camada normalizada.'),
    ('IAC (rótulo nunca validado)', 'CC art. 202, p.u. → "IAC 1"; abrir a ficha (HISTORICAL_BUT_RELEVANT, CPC/1973); BACK volta à mesma lista.'),
    ('REPETITIVO STJ (rótulo nunca validado)', 'CC art. 405 → "REPETITIVO STJ 1133"; abrir; BACK.'),
    ('REPETITIVO STJ', 'CC art. 50 → "REPETITIVO STJ 1210"; abrir; BACK.'),
    ('REPETITIVO STJ + EXCLUSION_CONTEXT', 'CC art. 354 → "REPETITIVO STJ 426" e "REPETITIVO STJ 381"; a ficha do 381 começa por INAPLICABILIDADE À '
                                           'COMPENSAÇÃO TRIBUTÁRIA; BACK.'),
    ('Súmula 642', 'CC art. 943 → "Súmula 642 STJ" (ficha registra a correção ART943_INC1 → ART943); nenhum "inciso I" no art. 943.'),
    ('Tema 1130', 'CC art. 76, p.u. → "REPETITIVO STJ 1130"; a ficha NÃO diz provisório e explica STJ defasado × Tema 1432/STF.'),
    ('Target compartilhado', 'CC art. 206, § 5º, I → Súmula 503 + Súmula 547 + REPETITIVO STJ 639 (3 itens, os 2 antigos primeiro).'),
    ('Target compartilhado', 'CC art. 206, § 3º, IV → Súmula 547 + REPETITIVO STJ 610 (2 itens).'),
    ('Target compartilhado', 'CC art. 1.641, II → RG TEMA 1236 + Súmula 655 STJ; a ficha da 655 traz a qualificação do Tema 1236.'),
    ('Fichas reaproveitadas', 'CC art. 1.829 → RG TEMA 498 + RG TEMA 809 (mesmas fichas físicas do art. 1.790).'),
    ('Súmula 619', 'CC art. 1.208 e art. 1.255 → a mesma ficha "Súmula 619 STJ".'),
    ('Novos targets', 'Arts. 835, 286, 191, 206 § 3º III, 1.238 p.u., 1.210 § 2º: cada um abre a ficha e volta com BACK.'),
    ('Regressão CC-J1', 'Os 24 targets do CC-J1 (checklist 36/36) com as mesmas listas; art. 206-A sem Tema 1194; art. 422 sem Súmula 609.'),
    ('Rejeitados', 'Nenhum dos 11 não aprovados aparece (ex.: art. 1.639, § 2º sem Tema 1236; art. 1.566, I sem Tema 529; art. 368 sem Tema 587).'),
    ('Tema 932 cross-norm', 'CC art. 927, p.u. e CF art. 7º, XXVIII abrem a mesma ficha STF_RG_932.'),
    ('Regressão CF', 'CF art. 62 → RG TEMA 33 e RG TEMA 1196; CF art. 53, § 1º → HC 232627; ADCT art. 107-A → só ADI 7064.'),
    ('Camadas congeladas', 'CF art. 196 → REF. "Sicko - S.O.S. Saúde" (Referências nº 4); CF art. 127 → ENTENDA; CF art. 202, § 5º → CORR. LC 108/2001.'),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_lf(p):
    return sha(Path(p).read_bytes().replace(b'\r\n', b'\n'))


def fail(code):
    raise SystemExit(f'PREFLIGHT_STOP {code}')


def authority():
    rec = E.load(REC)
    drift = sorted(k for k, v in rec['pinned'].items() if sha_lf(HERE / k) != v)
    if drift:
        fail(f'RATIFICATION_PINS_CHANGED {drift}')
    items = rec['items']
    appr = [i for i in items if i['human_approved']]
    nota = sorted(i['id'] for i in items if not i['human_approved'])
    if (len(items), len(appr), nota, rec['counts']['PENDING']) != (30, EXPECTED['approved'], EXPECTED['not_approved'], 0):
        fail('RATIFICATION_COUNTS')
    rels = sorted({(t, i['precedent']) for i in appr for t in i['final_targets']})
    if rels != sorted((r['target_id'], r['precedent']) for r in rec['approved_relations']):
        fail('RELATIONS_DO_NOT_RECONCILE')
    return rec, appr, rels, nota


def target_checks(targets):
    idx = {t['target_id']: t for t in E.load(CC_INDEX)['targets']}
    amend = E.load(PLANALTO)['amendments']                         # complete scope: absent = current wording, no note
    out = []
    for t in sorted(targets):
        p = T.parse_target_id(t)
        rt = T.format_target_id(p['namespace'], p['article'], paragraph=p['paragraph'], inciso=p['inciso'], alinea=p['alinea'])
        out.append(dict(target=t, kind=p['kind'], exists=t in idx, granularity_ok=t in idx and idx[t]['kind'] == p['kind'], namespace=p['namespace'],
                        round_trip=rt == t, vigente=not any(a['kind'].lower().startswith('revogad') for a in amend.get(t, [])),
                        amendments=[f"{a['kind']} pela {a['by']}" for a in amend.get(t, [])]))
    return out


def ficha_and_record(it, dec, targets, stj):
    trib, klass, num = it['precedent'].split(':')
    tipo = TIPO[klass]
    tlist = '; '.join(human_target(t) for t in sorted(targets, key=target_order))
    notes = [FICHA_NOTES[it['precedent']]] if it['precedent'] in FICHA_NOTES else []
    flags = it['editorial_flags']
    if klass == 'SUMULA':
        e = stj[it['precedent']]
        rec = dict(tipo=tipo, tribunal=trib, numero=num, status='vigente', titulo=f'Súmula {num} STJ', fonte=it['source']['url'])
        body = [f'SÚMULA {num} DO STJ', 'TRIBUNAL: STJ', 'STATUS: vigente', f"ÓRGÃO JULGADOR: {e['orgao']}", '', 'ENUNCIADO', e['enunciado'], '',
                'JULGAMENTO', f"{e['data_decisao']}; {e['fonte']}.", '']
    else:
        nome = 'Tema Repetitivo' if klass == 'REPETITIVO' else 'IAC'
        rec = dict(tipo=tipo, tribunal=trib, numero=num, status='tese_firmada', titulo=f'{nome} {num} STJ', fonte=it['source'].get('page', it['source']['url']))
        if flags and flags[0] == 'EXCLUSION_CONTEXT':
            head_note = ['INAPLICABILIDADE À COMPENSAÇÃO TRIBUTÁRIA (EXCLUSION_CONTEXT)', '']
        else:
            head_note = []
        body = [f'{nome.upper()} {num} DO STJ', 'TRIBUNAL: STJ', f"STATUS: tese firmada; {dec['judgment']}", f'PROCESSO: {JT.label(tipo, trib, num)}', '']
        body += head_note + ['TESE FIRMADA', dec['evidence'], '', 'SITUAÇÃO NA FONTE OFICIAL (STJ)', dec['status_text'], '']
    body += ['CÓDIGO CIVIL', tlist, '']
    if notes:
        body += ['NOTA'] + notes + ['']
    if it.get('source_anomaly'):
        body += ['PROVENIÊNCIA', it['source_anomaly'], '']
    body += ['FONTE OFICIAL', rec['fonte']] + ([f"Dados abertos do STJ: {it['source']['url']}"] if it['source'].get('page') else [])
    return rec, '\n'.join(body) + '\n'


def build():
    rec, appr, rels, nota = authority()
    dec = {x['precedent']: x for x in E.load(DEC)['decisions']}
    stj = {f"STJ:SUMULA:{e['number']}": e for e in E.load(STJ)['entries']}
    card = {k.split('/')[-1] for k in E.load(CARD)['entries'] if k.startswith(P.CONTENT + '/')}
    card_entries = E.load(CARD)['entries']
    look0, recs0, rows = E.physical_layer(BASE_SD)
    base_rels = [dict(norm=E.namespace_of(r['target_id']), target_id=r['target_id'], precedent_id=r['precedent_id'], origin='PHYSICAL_BASELINE')
                 for r in rows]
    base_rec = {r['precedent_id']: r['record'] for r in rows}
    phys_cc = {(r['target_id'], r['precedent_id']) for r in rows if r['target_id'].startswith('CC2002:')}
    targets = sorted({t for t, _ in rels}, key=target_order)
    new_targets = sorted(set(targets) - {t for t, _ in phys_cc}, key=target_order)
    if (len(rels), len(targets), len(new_targets)) != (EXPECTED['relations'], EXPECTED['targets'], EXPECTED['new_targets']):
        fail('RELATION_TARGET_COUNTS')
    tchk = target_checks(targets)
    bad = [x['target'] for x in tchk if not (x['exists'] and x['granularity_ok'] and x['round_trip'] and x['vigente'] and x['namespace'] == 'CC2002')]
    if bad:
        fail(f'TARGET_CHECK {bad}')
    # ---- records + fichas (reuse records/fichas already on the card) ----
    by_prec = collections.defaultdict(list)
    for t, p in rels:
        by_prec[p].append(t)
    new_records, new_fichas, reused = {}, {}, []
    for it in appr:
        pid = it['precedent']
        if pid in base_rec and JT.ficha(pid) in card:
            reused.append(JT.ficha(pid))
            continue
        r, body = ficha_and_record(it, dec[pid], by_prec[pid], stj)
        new_records[pid], new_fichas[JT.ficha(pid)] = r, body
    new_rels = [dict(norm='CC2002', target_id=t, precedent_id=p, origin='CC-J2 HUMAN_APPROVED') for t, p in rels]
    prov = P.provisional_ids()
    files = P.package(base_rels + new_rels, {**new_records, **base_rec}, card, new_fichas=new_fichas, provisional_ids=prov, known_targets=P.known_targets())
    look, recs = files[P.LAYER + '/JUR_LOOKUP.IDX'], files[P.LAYER + '/JURISPRUDENCIA.IDX']
    lm = json.loads(files[P.LAYER + '/MULTINORM_MANIFEST.json'])
    build_id = sha(look + recs)[:16]
    old_ver = (BASE_SD / P.LAYER / 'LAYER.VER').read_text(encoding='utf-8')
    ver = '\n'.join(['#LEXMACHINA|JURIS_NORMALIZED_LAYER|1', f'BUILD_ID|{build_id}', f'LAYER|{P.LAYER}', 'CF_BASELINE|J2I_FROZEN_315_198',
                     [l for l in old_ver.splitlines() if l.startswith('CC_J1_RATIFICATION_SHA256|')][0], f'CC_J2_RATIFICATION_SHA256|{sha_lf(REC)}',
                     *[f'NORM|{n}|{v["relations"]}|{v["targets_with_j"]}' for n, v in sorted(lm['norms'].items())]]) + '\n'
    files[P.LAYER + '/LAYER.VER'] = ver.encode('utf-8')
    fichas_files = {k.split('/')[-1] for k in files if k.startswith(P.CONTENT)}
    pkg0 = S.Package(look0, recs0, card)
    pkg = S.Package(look, recs, card | fichas_files)

    def visit(t, probe=CC_FILE):
        _, art, par, inc, ali = P.query_key(t).split('|')
        st = S.carregar(pkg, probe, art, par, inc, ali)
        opened = all(S.open_and_back(pkg, st, i)['opened'] and S.carregar(pkg, probe, art, par, inc, ali)['relations'] == st['relations']
                     for i in range(len(st['relations'])))
        return st, opened and S.carregar(pkg, probe, art, par, inc, ali) == st
    all_cc = collections.defaultdict(list)
    for r in base_rels + new_rels:
        if r['target_id'].startswith('CC2002:'):
            all_cc[r['target_id']].append(r['precedent_id'])
    e2e, vis2, labels = [], 0, collections.Counter()
    for t in targets:
        st, ok = visit(t)
        got = [x['arquivo'] for x in st['relations']]
        ok = ok and st['branch'] == 'MULTINORMA' and got == [JT.ficha(p) for p in all_cc[t]]
        vis2 += sum(1 for p in by_prec_inv(rels, t) if JT.ficha(p) in got)
        labels.update(re.sub(r'\d+(/\d+)?', 'n', x['label']) for x in st['relations'] if x['arquivo'] in {JT.ficha(p) for p in by_prec_inv(rels, t)})
        e2e.append(dict(target=t, ok=ok, list=[x['label'] for x in st['relations']]))
    j1, vis1 = [], 0
    for t in sorted({t for t, _ in phys_cc}, key=target_order):
        st, ok = visit(t)
        got = [x['arquivo'] for x in st['relations']]
        old = [JT.ficha(p) for tt, p in [(r['target_id'], r['precedent_id']) for r in rows] if tt == t]
        ok = ok and got[:len(old)] == old
        vis1 += sum(1 for f in old if f in got)
        j1.append(dict(target=t, ok=ok, list=[x['label'] for x in st['relations']], gained=len(got) - len(old)))
    # CF/ADCT: every physical key outside CC2002 has byte-identical rows; semantic 315/198 via the CF fixture
    cf_keys = [l[:5] for l in pkg0.lookups if l[0] != 'CC2002']
    cf_changed = [k for k in cf_keys if pkg.exact(*k) is None or pkg.rows(*pkg.exact(*k)) != pkg0.rows(*pkg0.exact(*k))]
    vis_cf, _ = P.cf_fixture()
    cf_lost = []
    for r in vis_cf:
        norma, art, par, inc, ali = P.query_key(r['target_id']).split('|')
        hit = pkg.exact(norma, art, par, inc, ali)
        if not hit or JT.ficha(r['precedent_id']) not in {S.relation(l, '')['arquivo'] for l in pkg.rows(*hit)}:
            cf_lost.append(r['target_id'] + '|' + r['precedent_id'])
    art62 = [x['label'] for x in S.carregar(pkg, CF_FILE, '62')['relations']]
    t932 = ([x['caminho'] for x in S.carregar(pkg, CC_FILE, '927', par='unico')['relations'] if x['numero'] == '932'],
            [x['caminho'] for x in S.carregar(pkg, CF_FILE, '7', inc='XXVIII')['relations'] if x['numero'] == '932'])
    keys = [l[:5] for l in pkg.lookups]
    rec_lines = [l for l in recs.decode('utf-8').split('\n')[1:] if l]
    old_lines = collections.Counter(l for l in recs0.decode('utf-8').split('\n')[1:] if l)
    missing_old = sum((old_lines - collections.Counter(rec_lines)).values())
    cc_ids = {l.split('|')[6] for l in rec_lines if ':CC2002:' in l}
    rejected_ids = {i['precedent'] for i in rec['items'] if not i['human_approved']} - {p for _, p in rels}
    # 1236/529/587 rejected only on the CC-J2 target; their CC-J1 links (if any) are physical baseline, not CC-J2
    rejected_links = {(t, i['precedent']) for i in rec['items'] if not i['human_approved'] for t in i['original_proposal']['targets']}
    rejected_materialized = sum(1 for k in rejected_links if (k[0], k[1]) in {(r['target_id'], r['precedent_id']) for r in new_rels}) + sum(
        1 for p in rejected_ids if p in cc_ids and p not in {pp for _, pp in phys_cc})
    def merged(t, exp):                                        # old (physical) rows first and unchanged; the new ones after them, any order
        got = [x['arquivo'] for x in visit(t)[0]['relations']]
        old = [JT.ficha(p) for p in exp if (t, p) in phys_cc]
        return got[:len(old)] == old and sorted(got[len(old):]) == sorted(JT.ficha(p) for p in exp if (t, p) not in phys_cc)
    shared = {t: merged(t, exp) for t, exp in SHARED_EXPECTED.items()}
    # deploy shape vs the card
    cand_files = {f'candidate/SD/{k}': v for k, v in files.items()}
    add, replace, collide = [], [], []
    for k, v in files.items():
        if k not in card_entries:
            add.append(k)
        elif card_entries[k]['sha256'] == sha(v):
            collide.append(k)                                       # identical bytes already on card: nothing to write
        else:
            replace.append(k)
    unexpected = [k for k in replace if not k.startswith(P.LAYER + '/')] + [k for k in add if not k.startswith((P.CONTENT + '/', P.LAYER + '/'))]
    n = lm['norms']
    ty = collections.Counter(new_records[p]['tipo'] for p in new_records)
    psram = len(keys) * LOOKUP_ENTRY_BYTES + len(recs) + 1
    items_by = {i['precedent']: i for i in appr}
    checks = dict(
        CCJ2_RATIFICATION_VALID='PASS', APPROVED_PROPOSALS=len(appr), NOT_APPROVED=len(nota), PENDING=0, APPROVED_RELATIONS=len(rels),
        DISTINCT_TARGETS_TOUCHED=len(targets), NEW_TARGETS=len(new_targets), TARGETS_ALREADY_IN_CC_J1=len(targets) - len(new_targets),
        DISTINCT_PRECEDENTS=len(by_prec), LOGICAL_FICHAS=len({JT.ficha(p) for p in by_prec}), NEW_FICHAS=len(new_fichas), REUSED_FICHAS=len(reused),
        REUSED_FICHA_NAMES=sorted(reused), DUPLICATED_FICHA_BYTES=len(set(new_fichas) & card),
        REJECTED_MATERIALIZED=rejected_materialized, INVALID_TARGETS=len(bad), INVALID_ART943_INC1_TARGET_CREATED='NO' if all(
            'ART.943:INC' not in r['target_id'] for r in new_rels) else 'YES',
        TEMA1130_PROVISIONAL='NO' if 'STJ:REPETITIVO:1130' not in prov and not items_by['STJ:REPETITIVO:1130']['provisional'] else 'YES',
        DUPLICATE_QUERY_KEYS=len(keys) - len(set(keys)), LOOKUP_LOST_RELATIONS=len(base_rels) + len(rels) - len(rec_lines),
        BASELINE_RECORD_LINES_MISSING=missing_old,
        CC2002=f"{n['CC2002']['relations']}/{n['CC2002']['targets_with_j']}",
        CF_ADCT_NORMALIZED=f"{n['CF88']['relations'] + n['ADCT']['relations']}", CF_SEMANTIC=f'{len(vis_cf) - len(cf_lost)}/{len(vis_cf)}',
        CF_TARGETS=f"{len({r['target_id'] for r in vis_cf if r['target_id'] + '|' + r['precedent_id'] not in cf_lost})}/{len({r['target_id'] for r in vis_cf})}",
        PROJECTED_TOTAL_MULTINORM=f"{len(vis_cf) + n['CC2002']['relations']}/{len({r['target_id'] for r in vis_cf}) + n['CC2002']['targets_with_j']}",
        CCJ2_TARGETS_E2E=f"{sum(x['ok'] for x in e2e)}/{len(e2e)}", CCJ2_RELATIONS_VISIBLE=f'{vis2}/{len(rels)}',
        CCJ1_RELATIONS_PRESERVED=f'{vis1}/{len(phys_cc)}', CCJ1_TARGETS_PRESERVED=f"{sum(x['ok'] for x in j1)}/{len(j1)}",
        CCJ1_REGRESSION=len(phys_cc) - vis1 + sum(not x['ok'] for x in j1) + missing_old,
        CF_KEYS_CHANGED=len(cf_changed), CF_REGRESSION=len(cf_changed) + len(cf_lost), ART62=art62,
        TEMA932_CROSS_NORM='PASS' if t932[0] == t932[1] == ['/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT'] else 'FAIL',
        SHARED_TARGETS_MERGED={k: 'PASS' if v else 'FAIL' for k, v in shared.items()},
        LABELS_NEW=dict(sorted(labels.items())), OUTRO_LABELS=sum(v for k, v in labels.items() if k.startswith('OUTRO')),
        IAC_LABEL_SIMULATION='PASS' if labels.get('IAC n') == 1 and JT.label('iac', 'STJ', '1') == 'IAC 1' else 'FAIL',
        REPETITIVO_STJ_LABEL_SIMULATION='PASS' if labels.get('REPETITIVO STJ n', 0) == sum(1 for _, p in rels if ':REPETITIVO:' in p) else 'FAIL',
        IAC_ARCHITECTURAL_SUPPORT='YES' if JT.device_status('IAC') != 'NEW_JURIS_TYPE_REQUIRES_DESIGN' else 'NO',
        IAC_PHYSICAL_VALIDATION='YES' if JT.physical_status('IAC') == 'VALIDATED' else 'NO',
        REPETITIVO_STJ_ARCHITECTURAL_SUPPORT='YES' if JT.device_status('REPETITIVO') != 'NEW_JURIS_TYPE_REQUIRES_DESIGN' else 'NO',
        REPETITIVO_STJ_PHYSICAL_VALIDATION='YES' if JT.physical_status('REPETITIVO') == 'VALIDATED' else 'NO',
        SUMULA_STJ_PHYSICALLY_VALIDATED='YES' if JT.physical_status('SUMULA_STJ') == 'VALIDATED' else 'NO', DEVICE_STATUS_SOURCE='physical_status',
        NEW_TYPES=dict(sorted(ty.items())), TRIBUNALS=dict(sorted(collections.Counter(p.split(':')[0] for p in by_prec).items())),
        CACHE_ENTRIES_USED=len(keys), CACHE_ENTRIES_MAX=CACHE_ENTRIES_MAX, CACHE_MARGIN=CACHE_ENTRIES_MAX - len(keys), RECORDS=len(rec_lines),
        RECORDS_BYTES=len(recs), LOOKUP_BYTES=len(look), PSRAM_ESTIMATED=psram, PSRAM_PREVIOUS_LAYER=len(pkg0.lookups) * LOOKUP_ENTRY_BYTES + len(recs0) + 1,
        FILES_TO_ADD=len(add), FILES_TO_REPLACE=len(replace), FILES_IDENTICAL_ON_CARD=len(collide), UNEXPECTED_PATH_COLLISIONS=len(unexpected),
        ADDITIVE_ONLY='YES' if not replace else 'NO', SD_CHANGED='NO', FIRMWARE_CHANGED='NO', HISTORICAL_CCJ2_HASHES_CHANGED='NO')
    old_layer = {k: dict(bytes=card_entries[k]['bytes'], sha256=card_entries[k]['sha256']) for k in replace}
    deploy = dict(mode='ADDITIVE_FICHAS_PLUS_INDEX_REPLACEMENT', additive_only=not replace, files_to_add=sorted(add), files_to_replace=sorted(replace),
                  files_identical_on_card=sorted(collide), unexpected_path_collisions=unexpected, card_files_before=old_layer,
                  minimum_replacement_for_firmware=[k for k in replace if k.endswith('.IDX')],
                  why='O firmware multinorma lê caminhos FIXOS (06_NORMALIZADO/JUR_LOOKUP.IDX e JURISPRUDENCIA.IDX) e uma única camada; os índices são '
                      'agregados (uma linha por chave). Acrescentar relações a uma camada já instalada exige substituir esses índices. LAYER.VER e '
                      'MULTINORM_MANIFEST.json não são lidos pelo firmware, mas ficariam com contagens antigas se não forem trocados.',
                  options=['A — substituir os 4 arquivos da camada (2 índices + LAYER.VER + manifesto) com escrita segura e backup; rollback restaura '
                           'os bytes do CC-J1 (hashes conhecidos) e apaga as fichas novas',
                           'B — substituir só os 2 índices (mínimo para o firmware); LAYER.VER e manifesto ficam com as contagens do CC-J1',
                           'C — mudar o firmware para ler camadas aditivas (exige novo flash e nova validação física; não recomendado agora)'],
                  recommendation='A')
    rollback = dict(executed=False, scope='remover SOMENTE o CC-J2', delete=sorted(add),
                    restore={k: dict(from_=f'CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD/{k}', sha256=card_entries[k]['sha256']) for k in replace},
                    expected_after=dict(CC='29/24', CF_ADCT='315/198', card_files=E.load(CARD)['file_count']),
                    verify='conferir o cartão contra CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json (1.213 arquivos)', firmware='não muda')
    host = dict(checks=checks, targets=tchk, new_targets=new_targets, e2e_cc_j2=e2e, e2e_cc_j1=j1, cf_changed_keys=cf_changed, cf_lost=cf_lost,
                not_approved=nota, rejected_precedents=sorted(rejected_ids))
    j = lambda o: (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')  # noqa: E731
    cand = dict(cand_files)
    cand['host/PREFLIGHT_RESULT.json'] = j(host)
    cand['host/DEPLOY_PLAN.json'] = j(deploy)
    cand['host/ROLLBACK_PLAN.json'] = j(rollback)
    cand['host/PHYSICAL_CHECKLIST.json'] = j([dict(n=i, item=a, check=b) for i, (a, b) in enumerate(CHECKLIST, 1)])
    man = dict(schema_version=1, kind='CC_J2_MATERIALIZATION_CANDIDATE', build_id=build_id, status='HOST_ONLY_DEPLOY_CANDIDATE', deployed=False,
               deploy_ready=False, deploy_blocker='ADDITIVE_ONLY = NO: exige decisão do usuário sobre a substituição dos arquivos da camada',
               authority=dict(ratification_record=REC.name, sha256_lf=sha_lf(REC)), base=dict(layer='CC_J1_MATERIALIZATION_CANDIDATE (= cartão)',
                                                                                             build_id='4c0615575e3da8fc'),
               counts=dict(relations=len(rels), targets=len(targets), new_targets=len(new_targets), precedents=len(by_prec), new_fichas=len(new_fichas),
                           reused_fichas=sorted(reused), types=dict(sorted(ty.items())), tribunals=checks['TRIBUNALS'],
                           shared_fichas_across_norms=lm['fichas_shared_across_norms']),
               files={k: dict(bytes=len(v), sha256=sha(v)) for k, v in sorted(cand.items())})
    cand['SHA256_MANIFEST.json'] = j(man)
    return cand, host, deploy, rollback, man


def by_prec_inv(rels, t):
    return [p for tt, p in rels if tt == t]


def render(host, deploy, rollback, man_sha):
    c = host['checks']
    L = ['# CC-J2 — MATERIALIZATION PREFLIGHT (host-only)', '', '```',
         f"CC_J2_PREFLIGHT = {'PARTIAL' if c['ADDITIVE_ONLY'] == 'NO' else 'PASS'} · ADDITIVE_ONLY = {c['ADDITIVE_ONLY']} · SD_CHANGED = NO · FIRMWARE_CHANGED = NO",
         f"RELAÇÕES {c['APPROVED_RELATIONS']} · TARGETS {c['DISTINCT_TARGETS_TOUCHED']} ({c['NEW_TARGETS']} novos) · CC {c['CC2002']} · TOTAL {c['PROJECTED_TOTAL_MULTINORM']}",
         f"DUPLICATE_QUERY_KEYS {c['DUPLICATE_QUERY_KEYS']} · LOOKUP_LOST_RELATIONS {c['LOOKUP_LOST_RELATIONS']} · CCJ1_REGRESSION {c['CCJ1_REGRESSION']} · "
         f"CF_REGRESSION {c['CF_REGRESSION']}", '```', '',
         '## 1. Ratificação autoritativa', '',
         f"`CC_J2_RATIFICATION_RECORD.json`, com todos os hashes fixados reconferidos: {c['CCJ2_RATIFICATION_VALID']}. Aprovadas {c['APPROVED_PROPOSALS']}, "
         f"não aprovadas {c['NOT_APPROVED']}, pendentes {c['PENDING']}. REJECTED_MATERIALIZED = {c['REJECTED_MATERIALIZED']}.", '',
         '## 2–4. Relações e targets', '', '| Target | Lista no aparelho (simulada) | E2E |', '|---|---|---|']
    L += [f"| {x['target']} | {'; '.join(x['list'])} | {'PASS' if x['ok'] else 'FAIL'} |" for x in host['e2e_cc_j2']]
    L += ['', f"Targets novos ({c['NEW_TARGETS']}): {', '.join(host['new_targets'])}.",
          'Todos os 18 existem no índice do CC2002, com granularidade correta, round-trip do ID, namespace CC2002 e sem nota de revogação '
          f"(INVALID_TARGETS = {c['INVALID_TARGETS']}). A Súmula 642 está só no art. 943 (INVALID_ART943_INC1_TARGET_CREATED = "
          f"{c['INVALID_ART943_INC1_TARGET_CREATED']}).", '',
          'Targets compartilhados (listas antigas preservadas, novas acrescentadas no fim): ' +
          ', '.join(f'{k} {v}' for k, v in c['SHARED_TARGETS_MERGED'].items()) + '.', '',
          '## 5–7. Fichas e tipos', '',
          f"Fichas lógicas {c['LOGICAL_FICHAS']}: {c['NEW_FICHAS']} novas e {c['REUSED_FICHAS']} reaproveitadas do cartão "
          f"({', '.join(c['REUSED_FICHA_NAMES'])}, mesmos bytes; a nota delas já cita o art. 1.829). Bytes duplicados: {c['DUPLICATED_FICHA_BYTES']}.",
          f"Tipos novos: {c['NEW_TYPES']}. Tribunais: {c['TRIBUNALS']}. Fichas compartilhadas entre normas: STF_RG_932 (CF + CC), STF_ADI_7047-7064 (CF + ADCT).",
          'As notas ratificadas estão nas fichas: IAC 1 (HISTORICAL_BUT_RELEVANT, CPC/1973), Súmula 637 (EXCEPTION), Súmula 655 '
          '(SUBJECT_TO_TEMA_1236_STF), Tema 381 (abre com INAPLICABILIDADE À COMPENSAÇÃO TRIBUTÁRIA), Tema 1130 (STJ defasado × Tema 1432/STF), '
          'Súmula 642 (proveniência ART943_INC1 → ART943).', '',
          '## 8–9. IAC e REPETITIVO STJ', '',
          f"Rótulos derivados de `juris_types.label`. Visto na simulação: {c['LABELS_NEW']}; rótulos OUTRO: {c['OUTRO_LABELS']}. "
          f"IAC_LABEL_SIMULATION = {c['IAC_LABEL_SIMULATION']}, REPETITIVO_STJ_LABEL_SIMULATION = {c['REPETITIVO_STJ_LABEL_SIMULATION']} "
          '("REPETITIVO STJ n", distinto de "RG TEMA n" do STF).',
          f"IAC: suporte arquitetural {c['IAC_ARCHITECTURAL_SUPPORT']}, validação física {c['IAC_PHYSICAL_VALIDATION']}. REPETITIVO STJ: suporte "
          f"{c['REPETITIVO_STJ_ARCHITECTURAL_SUPPORT']}, validação física {c['REPETITIVO_STJ_PHYSICAL_VALIDATION']}. Súmula STJ: validada fisicamente "
          f"{c['SUMULA_STJ_PHYSICALLY_VALIDATED']} (fonte: `physical_status`).",
          'Dívida do motor: `batch_engine.py`, `apply_review`, linha 249, ainda chama `JT.device_status`. Trocar ali mudaria os hashes fixados do CC-J2 '
          '(métricas e decisões), por isso não foi trocado. Este preflight usa `JT.physical_status` diretamente; a troca no motor entra na refatoração '
          'antes do CC-J3. HISTORICAL_CCJ2_HASHES_CHANGED = NO.', '',
          '## 10. Simulação (firmware multinorma, modelo host)', '',
          f"CC-J2: CCJ2_TARGETS_E2E = {c['CCJ2_TARGETS_E2E']}, CCJ2_RELATIONS_VISIBLE = {c['CCJ2_RELATIONS_VISIBLE']} (abrir CC → target → JURIS → lista "
          'completa → cada ficha → BACK → mesma lista → artigo).',
          f"CC-J1: CCJ1_RELATIONS_PRESERVED = {c['CCJ1_RELATIONS_PRESERVED']}, CCJ1_TARGETS_PRESERVED = {c['CCJ1_TARGETS_PRESERVED']} (linhas antigas "
          f"byte-idênticas e na mesma ordem; ausentes {c['BASELINE_RECORD_LINES_MISSING']}); CCJ1_REGRESSION = {c['CCJ1_REGRESSION']}.",
          f"CF/ADCT: {c['CF_SEMANTIC']} relações e {c['CF_TARGETS']} targets alcançáveis; chaves CF/ADCT alteradas: {c['CF_KEYS_CHANGED']}; CF_REGRESSION = "
          f"{c['CF_REGRESSION']}. Art. 62: {', '.join(c['ART62'])}. Tema 932 entre normas: {c['TEMA932_CROSS_NORM']}.", '',
          '## 11. Cache / PSRAM', '',
          f"Chaves de lookup {c['CACHE_ENTRIES_USED']} de {c['CACHE_ENTRIES_MAX']} (margem {c['CACHE_MARGIN']}); registros {c['RECORDS']}; "
          f"JURISPRUDENCIA.IDX {c['RECORDS_BYTES']} B; JUR_LOOKUP.IDX {c['LOOKUP_BYTES']} B; PSRAM estimada {c['PSRAM_ESTIMATED']} B "
          f"(camada atual: {c['PSRAM_PREVIOUS_LAYER']} B; 68 B por entrada, medido no aparelho).", '',
          '## 12. Candidato e forma de deploy', '',
          f"`CC_J2_MATERIALIZATION_CANDIDATE/`, imutável e host-only. Arquivos a acrescentar: {c['FILES_TO_ADD']}; a substituir: {c['FILES_TO_REPLACE']}; "
          f"colisões inesperadas: {c['UNEXPECTED_PATH_COLLISIONS']}.", '',
          f"**ADDITIVE_ONLY = {c['ADDITIVE_ONLY']}.** {deploy['why']}", '', 'Arquivos que seriam substituídos (bytes atuais no cartão):', '']
    L += [f"- `{k}` ({v['bytes']} B, `{v['sha256'][:16]}…`)" for k, v in deploy['card_files_before'].items()]
    L += ['', 'Opções (decisão do usuário antes de qualquer deploy):', ''] + [f'- {o}' for o in deploy['options']]
    L += ['', f"Recomendação: {deploy['recommendation']}. O preflight fica PARTIAL até essa decisão; o candidato não está liberado para deploy.", '',
          '## 13. Hashes', '', f"`SHA256_MANIFEST.json` sha256 `{man_sha}` (lista todos os arquivos do candidato com bytes e sha256).", '',
          '## 14. Rollback (não executado)', '', f"Apagar os {len(rollback['delete'])} arquivos novos e restaurar os {len(rollback['restore'])} arquivos da "
          'camada a partir de `CC_J1_MATERIALIZATION_CANDIDATE` (hashes conferidos). Resultado: CC 29/24, CF/ADCT 315/198, 1.213 arquivos; firmware não muda.',
          '', '## 15. Checklist físico futuro (não executado)', '']
    L += [f'{i}. **{a}:** {b}' for i, (a, b) in enumerate(CHECKLIST, 1)]
    L += ['', 'Nada foi implantado, gravado ou conectado. Próximo passo: decisão do usuário sobre a forma de deploy (opção A/B/C).']
    return '\n'.join(L) + '\n'


def main():
    cand, host, deploy, rollback, man = build()
    man_sha = sha(cand['SHA256_MANIFEST.json'])
    report = render(host, deploy, rollback, man_sha).encode('utf-8')
    if '--check' in sys.argv:
        ok = all((OUT / k).is_file() and (OUT / k).read_bytes().replace(b'\r\n', b'\n') == v.replace(b'\r\n', b'\n') for k, v in cand.items()) \
            and REPORT.read_bytes().replace(b'\r\n', b'\n') == report
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for k, v in cand.items():
        (OUT / k).parent.mkdir(parents=True, exist_ok=True)
        (OUT / k).write_bytes(v)
    REPORT.write_bytes(report)
    print(json.dumps(host['checks'], ensure_ascii=False, indent=1))
    print('MANIFEST_SHA256', man_sha)


if __name__ == '__main__':
    main()
