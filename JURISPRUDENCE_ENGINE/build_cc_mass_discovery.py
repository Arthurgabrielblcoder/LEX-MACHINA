"""CC MASS DISCOVERY — host-only, high-recall discovery of Código Civil jurisprudence from official sources, followed by deterministic
normalization, global deduplication, automatic audits and tiering (A / B / C). Nothing is ratified, materialized, deployed or flashed.

Sources (each read through an official adapter; every raw record keeps its provenance):
  STJ_SUMULAS_PDF            stj/STJ_SUMULAS_INDEX.json            (adapter #3, structured STJ legislative references + enunciado)
  STJ_PRECEDENTES_QUALIF     stj/STJ_PRECEDENTES_INDEX_V2.json     (adapter #4 v2: tese, questão, referência legislativa)
  STJ_ESPELHOS               stj/STJ_ESPELHOS_CC2002_INDEX.json    (adapter #6: espelhos de acórdãos, Segunda Seção + Corte Especial)
  STF_JURISPRUDENCIA         stf/STF_CC2002_INDEX.json             (adapter #5: RG mérito + controle concentrado)
  PLANALTO_VIDE              cc_j2/PLANALTO_CC2002_2026-10-18.json (adapter #1)
Pipeline: raw records -> unique pairs (NORM + TARGET + TRIBUNAL + CLASS + PRECEDENT, evidences aggregated) -> exclusions (physical baseline,
earlier human decisions) -> audits (target existence + fallback, namespace evidence, temporal (Planalto notes), procedural status, evidence
strength, qualified-precedent flag) -> tier. Deterministic and idempotent: same inputs, same bytes; the checkpoint records what was done.
Usage: python build_cc_mass_discovery.py [--check]
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE)]
import batch_engine as E  # noqa: E402
import discovery_stj_precedentes as TXT  # noqa: E402
sys.path.insert(0, str(HERE / 'pilot_cc'))
import cc_pilot_evidence as EV  # noqa: E402
from cc_mass_sample_review import SAMPLE_REVIEW  # noqa: E402

NORM = 'CC2002'
OUT = HERE / 'CC_MASS_DISCOVERY'
RUN_DATE = '2026-10-19'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
PLANALTO = HERE / 'cc_j2/PLANALTO_CC2002_2026-10-18.json'
PHYSICAL_SD = HERE / 'CC_J2_MATERIALIZATION_CANDIDATE/candidate/SD'      # = card after CC-J2 (CC_J2_PHYSICAL_VALIDATION 38/38)
SOURCES = {
    'STJ_SUMULAS_PDF': HERE / 'stj/STJ_SUMULAS_INDEX.json',
    'STJ_PRECEDENTES_QUALIFICADOS': HERE / 'stj/STJ_PRECEDENTES_INDEX_V2.json',
    'STJ_ESPELHOS_ACORDAOS': HERE / 'stj/STJ_ESPELHOS_CC2002_INDEX.json',
    'STJ_ESPELHOS_TURMAS': HERE / 'stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json',   # 47 MB derived index: not versioned (sha + rebuild recipe)
    'STF_JURISPRUDENCIA': HERE / 'stf/STF_CC2002_INDEX.json',
    'PLANALTO_VIDE': PLANALTO,
}
ESPELHO_SOURCES = ('STJ_ESPELHOS_ACORDAOS', 'STJ_ESPELHOS_TURMAS')
BLOCKED_SOURCES = {
    'STJ_JURISPRUDENCIA_EM_TESES': 'https://scon.stj.jus.br/SCON/jt/ — desafio Cloudflare com resposta exigida (não contornado), 2026-10-19',
    'STJ_PESQUISA_PRONTA': 'https://scon.stj.jus.br/SCON/pesquisa_pronta/ — mesmo desafio (403), 2026-10-19',
    'STJ_PUBLICACOES_INSTITUCIONAIS': 'https://www.stj.jus.br/publicacaoinstitucional/ (Súmulas Anotadas, Jurisprudência em Teses PDF) — página de '
                                      'desafio / 404 no navegador, 2026-10-19',
    'STF_API_DIRETA_DO_HOST': 'POST direto do host recebe desafio WAF 202; captura feita pelo navegador (caminho normal da página)',
}
LOCAL_RAW, LOCAL_REJ = '_local/CC_MASS_DISCOVERY_RAW_FULL.jsonl', '_local/CC_MASS_DISCOVERY_REJECTED_TURMAS.jsonl'
JOINT = {'STF:ADI:6792': 'STF:ADI:6792-7055', 'STF:ADI:7055': 'STF:ADI:6792-7055', 'STF:ADI:7047': 'STF:ADI:7047-7064', 'STF:ADI:7064': 'STF:ADI:7047-7064'}
NON_MERIT_CLASSES = ('APN', 'CC', 'MC', 'PET', 'AI', 'AR', 'RCL', 'HC', 'RHC', 'SLS', 'SS', 'SL', 'IF', 'EXSUSP', 'INQ', 'SD', 'CAUINOM')
HOMOLOGATORY = ('SEC', 'HDE')
QUALIFIED_KLASS = ('SUMULA', 'REPETITIVO', 'IAC', 'RG', 'ADI', 'ADC', 'ADPF', 'ADO', 'SIRDR')
STRONG = ('DIRECT', 'COMPONENT_FIRST', 'LIST_TAIL', 'SAME_DIPLOMA', 'ADJACENT')
AREAS = [('PARTE_GERAL', 1, 232), ('OBRIGACOES', 233, 965), ('EMPRESA', 966, 1195), ('COISAS', 1196, 1510), ('FAMILIA', 1511, 1783),
         ('SUCESSOES', 1784, 2027), ('DISPOSICOES_FINAIS_TRANSITORIAS', 2028, 2046)]
THEMES = [('PERSONALIDADE', 11, 21), ('PARTE_GERAL', 1, 10), ('PARTE_GERAL', 22, 188), ('PRESCRICAO_DECADENCIA', 189, 211), ('PARTE_GERAL', 212, 232),
          ('OBRIGACOES', 233, 420), ('CONTRATOS', 421, 853), ('OBRIGACOES', 854, 926), ('RESPONSABILIDADE_CIVIL', 927, 954), ('OBRIGACOES', 955, 965),
          ('EMPRESA', 966, 1195), ('COISAS', 1196, 1510), ('FAMILIA', 1511, 1783), ('SUCESSOES', 1784, 2027), ('TRANSICAO', 2028, 2046)]


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha(Path(p).read_bytes())


def art_label(t):
    p = E.T.parse_target_id(t)
    n = re.match(r'\d+', p['article']).group(0)
    return f'{n[:-3]}.{n[-3:]}' if len(n) > 3 else n


def iso_date(s):
    s = (s or '').strip()
    m = re.match(r'(\d{2})/(\d{2})/(\d{4})', s) or None
    if m:
        return f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
    m = re.match(r'(\d{4})-?(\d{2})-?(\d{2})', s)
    return f'{m.group(1)}-{m.group(2)}-{m.group(3)}' if m else None


def number_in_text(t, text):
    """'art. 1.790' (any formatting of the article number) mentioned in the text and not immediately attributed to another law."""
    n = art_label(t).replace('.', r'\.?')
    for m in re.finditer(rf'\barts?\.?\s*(?:n[º°o.]\s*)?{n}(?!\d)', text or '', re.I):
        tail = re.split(r'[;.]\s', text[m.end():m.end() + 45])[0] or ''
        before = (text or '')[max(0, m.start() - 45):m.start()]
        foreign = TXT.OTHER_LAW.search(tail) or re.match(r'^[^a-zA-Z]{0,12}(?:d[oa]s?|e)\s+(?!C[óo]digo Civil|CC\b|mesmo)[A-ZÁ-Ú][A-Za-zÀ-ú]', tail) or \
            re.search(r'(?:\b(?!CC\b)[A-Z]{2,}[\w/.-]*|Lei[^,;()]{0,25}|Decreto[^,;()]{0,25}|Resolu[çc][ãa]o[^,;()]{0,25})\s*,\s*$', before)
        if not foreign and not TXT.OLDER_RIGHT_AFTER.match(tail):
            return True
    return False


# ------------------------------------------------------------------ raw discovery (one record per evidence)
def ementa_key(t):
    """Ementa without the result words ('PROVIDO', 'IMPROVIDO', 'ACOLHIDOS'...) that differ between twin acórdãos of one joint judgment."""
    t = re.sub(r'\b(N[ÃA]O\s+)?(IM)?PROVID[OA]S?\b|\b(DES)?ACOLHID[OA]S?\b|\bCONHECID[OA]S?\b', '', (t or '').upper())
    return re.sub(r'\W+', '', t)[:300]


def raw_records():
    recs, inv = [], {}
    ts = RUN_DATE

    def add(**r):
        r.setdefault('candidate_norm', NORM)
        r.setdefault('discovery_timestamp', ts)
        recs.append(r)
    # STJ súmulas
    p = SOURCES['STJ_SUMULAS_PDF']
    s = load(p)
    for e in s['entries']:
        found, _, _ = TXT.cites_extended(e['enunciado'], NORM)
        for ref in e['references']:
            for t in ref['targets'] if ref['catalog_id'] == NORM else []:
                add(source='STJ_SUMULAS_PDF', source_url=s['source']['url'], source_document_id=f"SUMULA {e['number']}", tribunal='STJ', classe='SUMULA',
                    precedent_number=str(e['number']), precedent_id=f"STJ:SUMULA:{e['number']}", judgment_date=e['data_decisao'], publication_date=e['fonte'][:40],
                    legal_reference_raw=ref['law'] + ' ' + (ref['sigla'] or ''), candidate_target=t, citation_context=e['enunciado'][:400],
                    discovery_method='STRUCTURED_LEGISLATIVE_REFERENCE', evidence_field='referencias_legislativas', status=e['status'],
                    source_hash_or_capture_id=s['source']['pdf_sha256'], text=e['enunciado'], orgao=e['orgao'])
        for t, m in found.items():
            add(source='STJ_SUMULAS_PDF', source_url=s['source']['url'], source_document_id=f"SUMULA {e['number']}", tribunal='STJ', classe='SUMULA',
                precedent_number=str(e['number']), precedent_id=f"STJ:SUMULA:{e['number']}", judgment_date=e['data_decisao'], publication_date=e['fonte'][:40],
                legal_reference_raw='enunciado', candidate_target=t, citation_context=e['enunciado'][:400], discovery_method=f'TEXT_{m}',
                evidence_field='enunciado', status=e['status'], source_hash_or_capture_id=s['source']['pdf_sha256'], text=e['enunciado'], orgao=e['orgao'])
    inv['STJ_SUMULAS_PDF'] = dict(path=str(p.relative_to(HERE)), sha256=sha_file(p), records=len(s['entries']), version=s['source'].get('accessed_on'))
    # STJ qualified precedents (v2)
    p = SOURCES['STJ_PRECEDENTES_QUALIFICADOS']
    q = load(p)
    for e in q['entries']:
        if e['klass'] not in ('REPETITIVO', 'IAC', 'SIRDR'):
            continue
        txt = e['tese'] + ' ' + e['questao']
        for t, methods in e['targets'].items():
            for m in methods:
                field, meth = m.split(':')
                add(source='STJ_PRECEDENTES_QUALIFICADOS', source_url=q['source']['url'], source_document_id=f"{e['tipo']} {e['number']} (seq {e['sequencial']})",
                    tribunal='STJ', classe=e['klass'], precedent_number=e['number'], precedent_id=e['id'], judgment_date=e['data_julgamento'],
                    publication_date=e['data_publicacao'], legal_reference_raw=field, candidate_target=t,
                    citation_context=(e['tese'] if field == 'tese' else e['questao'] if field == 'questao' else e['referencia_legislativa'])[:400],
                    discovery_method=('STRUCTURED_LEGISLATIVE_REFERENCE' if meth == 'STRUCTURED_TEXT' else f'TEXT_{meth}'), evidence_field=field,
                    status=e['situacao'], source_hash_or_capture_id=q['source']['csv_sha256'], text=txt, orgao=e['orgao'], sumula_originada=e['sumula_originada'],
                    tese=e['tese'])
    inv['STJ_PRECEDENTES_QUALIFICADOS'] = dict(path=str(p.relative_to(HERE)), sha256=sha_file(p), records=q['stats']['ROWS'],
                                               version=q['source']['accessed_on'], citing=q['stats']['ENTRIES_CITING_NORM'])
    # STJ espelhos (Seções/Corte Especial; Turmas de direito privado)
    for src in ESPELHO_SOURCES:
        p = SOURCES[src]
        if p.exists():
            x = load(p)
            # joint judgments (same session, órgão and ementa apart from the dispositivo's result words): one relation, not one per process
            by_id = {e['id']: e for e in x['entries']}
            sess = collections.defaultdict(list)
            for e in x['entries']:
                if not e['temas']:
                    sess[(e['julgamento'], e['orgao'], ementa_key(e['ementa']))].append(e['id'])
            canon = {i: sorted(ids)[0] for ids in sess.values() if len(set(ids)) > 1 for i in ids}
            for e in x['entries']:
                ce = by_id[canon.get(e['id'], e['id'])]
                inc = next((i for i in ('EDcl', 'AgRg', 'AgInt', 'ProAfR', 'QO') if e['sigla'].startswith(i)), None)
                jd = e['julgamento'] or ''
                jd = f'{jd[6:8]}/{jd[4:6]}/{jd[:4]}' if re.fullmatch(r'\d{8}', jd) else jd
                for t, methods in e['targets'].items():
                    for m in methods:
                        field, meth = m.split(':')
                        common = dict(source=src, source_url=e['source_url'], source_document_id=e['source_document_id'], tribunal='STJ',
                                      judgment_date=jd, publication_date=e['publicacao'], legal_reference_raw=field, candidate_target=t,
                                      citation_context=e['ementa'][:400], evidence_field=field, source_hash_or_capture_id=e['file_sha256'],
                                      text=e['ementa'] + ' ' + e.get('tese', ''), orgao=e['orgao'], incidente=inc)
                        meth_name = 'STRUCTURED_LEGISLATIVE_REFERENCE' if meth == 'STRUCTURED' else f'TEXT_{meth}'
                        single = len(e['temas']) == 1                      # one leading case judging several themes cannot attribute a citation to one
                        if inc or not single:                              # a single-theme leading case is counted once, as its theme (no double count)
                            if ce is not e:
                                common['legal_reference_raw'] = common['evidence_field'] = field + '+JOINT'
                                common['joint_of'] = e['id']
                            add(classe=ce['sigla'].replace(' ', '_').upper(), precedent_number=ce['number'], precedent_id=ce['id'], discovery_method=meth_name,
                                status='JULGADO', **common)
                        if not inc and single:
                            for tm in e['temas']:                        # leading case of a repetitive theme: its espelho evidences the theme
                                add(classe=tm.get('kind', 'REPETITIVO'), precedent_number=tm['numero'], precedent_id=f"STJ:{tm.get('kind', 'REPETITIVO')}:{tm['numero']}",
                                    discovery_method='LEADING_CASE_' + meth_name, status=tm['situacao'] or 'TEMA', leading_case=e['id'], **common)
            inv[src] = dict(path=str(p.relative_to(HERE)), sha256=sha_file(p), records=x['stats']['ACORDAOS'], versions=x['source']['files'],
                                                citing=x['stats']['WITH_TARGETS'])
    # STF
    p = SOURCES['STF_JURISPRUDENCIA']
    f = load(p)
    # joint judgments (same date, same ementa): one precedent, the others are the same judgment
    joint = collections.defaultdict(list)
    for e in f['entries']:
        if not e['incidente']:
            joint[(e['julgamento'], e['ementa'][:400])].append(e['id'])
    joint_of = {i: sorted(ids)[0] for ids in joint.values() if len(set(ids)) > 1 for i in ids}
    for e in f['entries']:
        civil_object = bool(re.search(r'interpreta[çc][ãa]o conforme|inconstitucional|constitucionalidade|C[óo]digo Civil', e['tema'] or '', re.I)) or \
            bool(re.search(r'C[ÓO]DIGO CIVIL|DIREITO CIVIL|SUCESS|FAM[ÍI]LIA|UNI[ÃA]O EST[ÁA]VEL|CASAMENTO|RESPONSABILIDADE CIVIL', e['ementa'][:300], re.I))
        for t, methods in e['targets'].items():
            for m in methods:
                field, meth = m.split(':')
                pid = JOINT.get(e['id'], e['id'])
                if e['id'] in joint_of and joint_of[e['id']] != e['id']:
                    pid = JOINT.get(joint_of[e['id']], joint_of[e['id']])
                    field = field + '+JOINT'
                add(source='STF_JURISPRUDENCIA', source_url=e['url'] or f['source']['api'], source_document_id=f"{e['titulo']} ({e['source_document_id']})",
                    tribunal='STF', classe=(pid.split(':')[1] if pid != e['id'] else e['klass']), precedent_number=(pid.split(':')[-1] if pid != e['id'] else e['number']), precedent_id=pid, judgment_date=e['julgamento'],
                    publication_date=e['publicacao'], legal_reference_raw=field, candidate_target=t,
                    citation_context=(e['tese'] or e['ementa'])[:400], discovery_method=('STRUCTURED_LEGISLATIVE_REFERENCE' if meth == 'STRUCTURED' else f'TEXT_{meth}'),
                    evidence_field=field, status=e['observacao'][:80] or ('RG MÉRITO' if e['rg_merito'] else 'JULGADO'),
                    source_hash_or_capture_id=f['source']['capture_sha256'], text=e['tese'] + ' ' + e['ementa'], orgao=e['orgao'], incidente=e['incidente'],
                    titulo=e['titulo'], rg_merito=e['rg_merito'], civil_object=civil_object,
                    joint_with=sorted(i for i, c in joint_of.items() if c == joint_of.get(e['id'])) or None)
    inv['STF_JURISPRUDENCIA'] = dict(path=str(p.relative_to(HERE)), sha256=sha_file(p), records=f['stats']['DOCS'], version=f['source']['captured_at'],
                                     citing=f['stats']['WITH_TARGETS'])
    # Planalto
    pl = load(PLANALTO)
    for a in pl['annotations']:
        raw = f"STF:{a['klass']}:{a['number']}"
        raw = JOINT.get(raw, {al: pid for pid, fct in EV.PRECEDENTS.items() for al in fct.get('alias', [])}.get(raw, raw))
        add(source='PLANALTO_VIDE', source_url=pl['source_url'], source_document_id=a['annotation'], tribunal='STF', classe=a['klass'], precedent_number=a['number'],
            precedent_id=raw, judgment_date=None, publication_date=None, legal_reference_raw=a['annotation'], candidate_target=a['target_id'],
            citation_context=a['text_preview'], discovery_method='OFFICIAL_ANNOTATION', evidence_field='vide', status='ANOTACAO',
            source_hash_or_capture_id=pl['source_sha256'], text=a['text_preview'], orgao=None)
    inv['PLANALTO_VIDE'] = dict(path=str(PLANALTO.relative_to(HERE)), sha256=sha_file(PLANALTO), records=len(pl['annotations']), version=pl.get('accessed_on'))
    # structured references are indexed to the finest unit the documentalist chose; without a textual citation of that unit, the relation
    # is kept at article level (the precedent discussed the article, not necessarily each inciso)
    text_cited = collections.defaultdict(set)
    for r in recs:
        if r['discovery_method'].startswith('TEXT_') or r['discovery_method'] == 'OFFICIAL_ANNOTATION':
            text_cited[r['precedent_id']].add(r['candidate_target'])
    for r in recs:
        p = E.T.parse_target_id(r['candidate_target'])
        if r['discovery_method'] == 'STRUCTURED_LEGISLATIVE_REFERENCE' and r['source'] in ('STF_JURISPRUDENCIA',) + ESPELHO_SOURCES and                 (p['paragraph'] or p['inciso'] or p['alinea']) and                 r['candidate_target'] not in text_cited[r['precedent_id']]:
            r['target_collapsed_from'] = r['candidate_target']
            r['candidate_target'] = E.T.format_target_id(NORM, p['article'])
    for i, r in enumerate(recs, 1):
        r['raw_id'] = f'RAW-{i:05d}'
    return recs, inv


# ------------------------------------------------------------------ exclusions from earlier human decisions
def decided():
    pair, prec = {}, {}
    j1 = load(HERE / 'CC_J1_RATIFICATION_RECORD.json')
    d1 = {f"CCJ1-{x['rank']:02d}": x for x in load(HERE / 'CC_J1_DECISIONS.json')['decisions']}
    for it in j1['items']:
        x = d1[it['id']]
        for t in set(it['final_targets']) | {x['discovered_target']} | set(it['proposed_targets']):
            pair[(t, it['precedent'])] = f"{it['id']} {it['human_state']}"
        if not it['human_approved']:
            prec[it['precedent']] = f"{it['id']} {it['human_state']}"
    j2 = load(HERE / 'CC_J2_RATIFICATION_RECORD.json')
    d2 = {x['id']: x for x in load(HERE / 'CC_J2_DECISIONS.json')['decisions']}
    for it in j2['items']:
        x = d2[it['id']]
        for t in set(it['final_targets']) | set(x['discovered_targets']) | set(it['original_proposal']['targets']):
            pair[(t, it['precedent'])] = f"{it['id']} {it['human_state']}"
        if not it['human_approved'] and set(it['editorial_flags']) & {'REJECT_SUPERSEDED', 'REJECT_TEMPORAL_MISMATCH', 'REJECT_DUPLICATE'}:
            prec[it['precedent']] = f"{it['id']} {' '.join(it['editorial_flags'])}"
    return pair, prec


# ------------------------------------------------------------------ pairs, audits, tiers
def build():
    index_doc = load(CC_INDEX)
    index = {t['target_id']: t for t in index_doc['targets']}
    pl = load(PLANALTO)
    amend = pl['amendments']
    _, _, rows = E.physical_layer(PHYSICAL_SD)
    phys = {(r['target_id'], r['precedent_id']) for r in rows if r['target_id'].startswith(NORM + ':')}
    phys_targets = {t for t, _ in phys}
    phys_prec = {p for _, p in phys}
    dpair, dprec = decided()
    phys_or_decided = set(phys) | set(dpair)
    recs, inv = raw_records()
    groups = collections.OrderedDict()
    for r in recs:
        t = r['candidate_target']
        if t not in index:                                       # resolve the fallback BEFORE grouping: one relation per final target
            p = E.T.parse_target_id(t)
            parent = (E.T.format_target_id(NORM, p['article'], paragraph=p['paragraph']) if p['inciso'] else E.T.format_target_id(NORM, p['article'])
                      if p['paragraph'] else None)
            if parent and parent in index:
                r['target_fallback_from'], r['candidate_target'] = t, parent
        key = (NORM, r['candidate_target'], r['tribunal'], r['classe'], r['precedent_id'])
        groups.setdefault(key, []).append(r)
    out = []
    for n, (key, ev) in enumerate(groups.items(), 1):
        _, t, trib, klass, pid = key
        first = ev[0]
        methods = sorted({r['discovery_method'] for r in ev})
        fields = sorted({r['evidence_field'] for r in ev})
        sources = sorted({r['source'] for r in ev})
        text = ' '.join(sorted({r.get('text') or '' for r in ev}))
        flags, reasons = [], []
        # structure
        target = t
        if any(r.get('target_fallback_from') for r in ev):
            flags.append('TARGET_FALLBACK_TO_PARENT')
        if t not in index:
            p = E.T.parse_target_id(t)
            parent = E.T.format_target_id(NORM, p['article'], paragraph=p['paragraph']) if p['inciso'] else E.T.format_target_id(NORM, p['article']) \
                if p['paragraph'] else None
            if parent and parent in index:
                target, flags = parent, flags + ['TARGET_FALLBACK_TO_PARENT']
            else:
                flags.append('TARGET_NOT_IN_INDEX')
        # temporal
        year = re.search(r'(19|20)\d{2}', first.get('judgment_date') or '')
        year = int(year.group(0)) if year else None
        notes = amend.get(target, []) + (amend.get(E.T.format_target_id(NORM, E.T.parse_target_id(target)['article']), []) if target in index else [])
        if any(a['kind'].lower().startswith('revogad') for a in notes):
            flags.append('DISPOSITIVO_REVOGADO')
        elif year and any(a['year'] > year for a in notes):
            flags.append('REDACAO_ALTERADA_APOS_JULGAMENTO')
        jd = iso_date(first.get('judgment_date'))
        if jd and jd < '2003-01-11':                              # CC/2002 in force on 11/01/2003: before it, "Código Civil" is the CC/1916
            explicit = re.search(r'C[óo]digo Civil de 2002|CC\s*/?\s*(?:2002|02)\b|CC-02|novo C[óo]digo Civil|10\.406', text, re.I)
            flags.append('PRECEDENTE_ANTERIOR_AO_CC2002' if explicit else 'NAMESPACE_CC1916_BY_DATE')
        elif jd and jd < '2006-01-01':
            explicit = re.search(r'C[óo]digo Civil de 2002|CC\s*/?\s*(?:2002|02)\b|CC-02|novo C[óo]digo Civil|atual C[óo]digo Civil|10\.406', text, re.I)
            flags.append('POSSIVEL_REGIME_CC1916' if explicit else 'NAMESPACE_CC1916_BY_DATE')
        # status
        st = ' '.join(sorted({str(r.get('status') or '') for r in ev}))
        if re.search(r'CANCELAD|REVOGAD|Vinculada a Tema|Revisado', st, re.I):
            flags.append('PRECEDENTE_NAO_VIGENTE')
        if re.search(r'RE Pendente|Afetado|Pendente|Em Julgamento|Sobrestado', st, re.I):
            flags.append('PRECEDENTE_PROVISORIO')
        inc = {r.get('incidente') for r in ev if r.get('incidente')}
        if 'ProAfR' in inc:
            flags.append('AFETACAO_SEM_MERITO')
        if inc & {'MC', 'MC-Ref'}:
            flags.append('DECISAO_CAUTELAR')
        if inc & {'ED', 'AgR', 'ED-segundos', 'EDcl', 'AgRg', 'AgInt', 'QO'}:
            flags.append('INCIDENTE_RECURSAL')
        if klass == 'RG' and first['source'] == 'STF_JURISPRUDENCIA' and not any(r.get('rg_merito') for r in ev):
            flags.append('RG_SEM_MERITO_CONFIRMADO')
        # evidence strength
        base_methods = [m.replace('LEADING_CASE_', '') for m in methods]
        txt_methods = {m.replace('TEXT_', '') for m in base_methods if m.startswith('TEXT_')}
        strong_ev = set()
        for r in ev:
            mth, fld = r['discovery_method'].replace('LEADING_CASE_', '').replace('TEXT_', ''), r['evidence_field'].split('+')[0]
            if (mth in STRONG and fld in ('tese', 'enunciado')) or (mth in ('DIRECT', 'COMPONENT_FIRST', 'SAME_DIPLOMA', 'ADJACENT') and fld == 'ementa'):
                strong_ev.add((mth, fld))                      # a bare list tail counts as strong only inside a tese/enunciado
        corroborated = number_in_text(target, text)
        if first['source'] == 'STF_JURISPRUDENCIA' and not any(r.get('civil_object') for r in ev) and not any(
                r['evidence_field'].startswith('tese') and r['discovery_method'].startswith('TEXT_') for r in ev):
            flags.append('USO_CONTEXTUAL_POSSIVEL')               # public-law case citing the CC by analogy: needs a human reading
        if strong_ev:
            strength = 'STRONG'
        elif 'OFFICIAL_ANNOTATION' in methods:
            strength = 'STRONG'
        elif txt_methods & set(STRONG) or 'NEAREST_MARKER' in txt_methods or (corroborated and 'STRUCTURED_LEGISLATIVE_REFERENCE' in base_methods):
            strength = 'MEDIUM'
        elif 'STRUCTURED_LEGISLATIVE_REFERENCE' in methods and first['source'] in ('STJ_SUMULAS_PDF', 'STJ_PRECEDENTES_QUALIFICADOS'):
            strength = 'MEDIUM'                                  # the court itself indexed the precedent to the article
        else:
            strength = 'WEAK'
        qualified = klass in QUALIFIED_KLASS
        # duplicates / earlier decisions
        pid_al = JOINT.get(pid, pid)
        status = None
        if (target, pid_al) in phys:
            status = ('C', 'DUPLICATE_PHYSICAL_BASELINE', 'par já publicado no baseline físico 49/39')
        elif (target, pid_al) in dpair:
            status = ('C', 'PREVIOUSLY_DECIDED', dpair[(target, pid_al)])
        elif pid_al in dprec:
            status = ('C', 'PREVIOUSLY_DECIDED_PRECEDENT', dprec[pid_al])
        elif any(o.startswith(target + ':') for o, p in phys_or_decided if p == pid_al):
            status = ('C', 'SUBSUMED_BY_PUBLISHED_SPECIFIC', 'o mesmo precedente já tem vínculo publicado/decidido a um dispositivo mais específico deste')
        if not status:
            if 'NAMESPACE_CC1916_BY_DATE' in flags:
                status = ('C', 'NAMESPACE_CC1916_BY_DATE', 'julgado antes de 11/01/2003 sem menção expressa ao CC/2002: o "Código Civil" citado é o de 1916')
            elif 'TARGET_NOT_IN_INDEX' in flags:
                status = ('C', 'INVALID_TARGET', 'target inexistente no índice do CC2002, sem pai válido')
            elif 'DISPOSITIVO_REVOGADO' in flags:
                status = ('C', 'REVOKED_DISPOSITIVO', 'dispositivo revogado (Planalto)')
            elif 'PRECEDENTE_NAO_VIGENTE' in flags:
                status = ('C', 'PRECEDENT_NOT_CURRENT', st[:80])
            elif first['source'] in ESPELHO_SOURCES and klass.split('_')[-1] in NON_MERIT_CLASSES and klass != 'REPETITIVO':
                status = ('C', 'CLASS_WITHOUT_CIVIL_THESIS', f'classe processual {klass} (penal, competência, cautelar ou incidente): sem tese de direito civil')
            elif 'AFETACAO_SEM_MERITO' in flags:
                status = ('C', 'NO_MERIT_DECISION', 'proposta de afetação: não há tese de mérito')
            elif 'INCIDENTE_RECURSAL' in flags:
                status = ('C', 'INCIDENTAL_DECISION', 'embargos/agravo: o precedente é o acórdão principal')
            elif strength == 'WEAK':
                status = ('C', 'MENTION_ONLY_UNVERIFIED', 'só indexação documental da legislação citada, sem o artigo na tese/ementa')
            elif set(fields) == {'questao'} and any(TXT.OTHER_LAW.search(r.get('tese') or '') and not re.search(TXT.NORMS[NORM][0], r.get('tese') or '', re.I)
                                                     for r in ev):
                status = ('C', 'TESE_ADOTOU_OUTRA_NORMA', 'o dispositivo aparece só na questão submetida; a tese firmada aplicou outra norma')
            elif 'RG_SEM_MERITO_CONFIRMADO' in flags:
                status = ('C', 'RG_WITHOUT_MERIT', 'acórdão sem mérito de repercussão geral confirmado')
        if not status:
            risky = set(flags) & {'TARGET_FALLBACK_TO_PARENT', 'REDACAO_ALTERADA_APOS_JULGAMENTO', 'PRECEDENTE_ANTERIOR_AO_CC2002', 'PRECEDENTE_PROVISORIO',
                                  'DECISAO_CAUTELAR', 'USO_CONTEXTUAL_POSSIVEL', 'POSSIVEL_REGIME_CC1916'}
            if qualified and strength == 'STRONG' and not risky:
                status = ('A', 'DIRECT_OFFICIAL_RELATION', 'fonte oficial nomeia o dispositivo na tese/enunciado/ementa de precedente qualificado')
            else:
                why = sorted(risky) + ([] if qualified else ['PRECEDENTE_NAO_QUALIFICADO']) + ([] if strength == 'STRONG' else [f'EVIDENCIA_{strength}'])
                why += ['CLASSE_HOMOLOGATORIA'] if klass.split('_')[-1] in HOMOLOGATORY else []
                status = ('B', 'OFFICIAL_BUT_HUMAN_REVIEW_REQUIRED', ', '.join(why))
        tier, code, reason = status
        out.append(dict(id='CCMD-' + sha('|'.join(key).encode())[:10].upper(), key='|'.join(key), norm=NORM, target_id=target, target_raw=next((r['target_fallback_from'] for r in ev if r.get('target_fallback_from')), t),
                        target_collapsed_from=sorted({r['target_collapsed_from'] for r in ev if r.get('target_collapsed_from')}), tribunal=trib, classe=klass,
                        precedent_id=pid_al, precedent_number=first['precedent_number'], judgment_date=first.get('judgment_date'),
                        publication_date=first.get('publication_date'), orgao=first.get('orgao'), sources=sources, evidence_fields=fields,
                        discovery_methods=methods, evidence_count=len(ev), raw_ids=[r['raw_id'] for r in ev],
                        source_urls=sorted({r['source_url'] for r in ev if r.get('source_url')})[:3],
                        source_hashes=sorted({r['source_hash_or_capture_id'] for r in ev}),
                        citation_context=next((r['citation_context'] for r in ev if r['discovery_method'].startswith('TEXT_')), first['citation_context']),
                        status_text=st[:120], flags=sorted(set(flags)), evidence_strength=strength, number_corroborated_in_text=corroborated,
                        qualified_precedent=qualified, area=E.theme_of(target, AREAS) if target in index else None,
                        theme=E.theme_of(target, THEMES) if target in index else None, new_target=target not in phys_targets,
                        precedent_already_on_card=pid_al in phys_prec, tier=tier, tier_code=code, tier_reason=reason,
                        status='AWAITING_USER_RATIFICATION' if tier in 'AB' else 'NOT_QUALIFIED', human_approved=False))
    # a generic article-level link is dropped when the same precedent has a more specific link to that article (finest supported unit)
    spec = collections.defaultdict(set)
    for x in out:
        if x['tier'] in 'AB':
            spec[x['precedent_id']].add(x['target_id'])
    for x in out:
        if x['tier'] in 'AB' and any(o != x['target_id'] and o.startswith(x['target_id'] + ':') for o in spec[x['precedent_id']]):
            x.update(tier='C', tier_code='SUBSUMED_BY_SPECIFIC_TARGET', tier_reason='o mesmo precedente tem vínculo a um dispositivo mais específico deste artigo',
                     status='NOT_QUALIFIED')
    turma_representatives(out, phys_targets | {t for t, _ in dpair}, recs)
    return recs, inv, out, index_doc, phys


NOT_KNOWN = re.compile(r'conhecid[oa]s?\s+para\s+n[ãa]o\s+conhecer|(?:recursos?\s+especia(?:l|is)|agravos?(?:\s+interno)?|embargos(?:\s+de\s+diverg[êe]ncia)?)'
                       r'[^.;]{0,90}?\bn[ãa]o\s+conhecid[oa]s?', re.I)
MERIT_VERB = re.compile(r'(?:recursos?|agravos?|embargos)[^.;]{0,120}?\b(?:des|im)?provid[oa]s?\b|\bdesprov[êe]-l|'      # this court's dispositivo,
                        r'\b(?:negar|dar)(?:-lhes?)?\s+(?:parcial\s+)?provimento', re.I)                            # not 'a origem negou provimento'
ADMISSIBILITY = re.compile(r's[úu]mulas?\s*(?:n[º°.]*\s*)?(?:5|7|83|211|282|283|284|356|518)\b|prequestion|reexame|fundamento\s+(?:aut[ôo]nomo|inatacado)|'
                           r'intempestiv|deser[çc][ãa]o|similitude|dissenso\s+n[ãa]o|paradigmas?|incognosc', re.I)
CLAIM_ZONE = re.compile(r'\bI\.?\s*[-–]?\s*CASO EM EXAME\b(.*?)(?=\bIII\.?\s*[-–]?\s*RAZ[ÕO]ES DE DECIDIR\b)', re.I | re.S)
HOLDING_LIST = re.compile(r'Dispositivos?\s+relevantes?\s+citados?', re.I)
CORRESP = re.compile(r'correspond|atualmente\s+(?:regid|previst|disciplinad)|equivalente|reproduzid|repetid[oa]\s+(?:pelo|no)|mesma\s+reda', re.I)
CC1916 = re.compile(r'C[óo]digo\s+Civil\s+(?:de\s+)?1916|C[óo]digo\s+Civil\s+anterior|CC\s*/?\s*(?:1916|16)\b|C[óo]digo\s+Bevil', re.I)
CLAIM_CUE = re.compile(r'alegad|apontad|sustent|suscit|aduz|inadmit|[óo]bices?|prequestion|saber se|quest[ãa]o em discuss|'
                       r's[úu]mulas?\s*(?:n[º°.]*\s*)?(?:5|7|211|282|283|284|356)\b', re.I)


def merit_check(text, target):
    """Non-qualified acórdão: does the court decide on the dispositivo? None when it does; else (code, reason). (a) The appeal was not known
    for an admissibility bar (Súmula 7/5/211..., prequestionamento, paradigma) and nothing was provided/denied -> no merit decision (older
    acórdãos that 'não conhecem' after deciding the question, with no such bar, are kept). (b) Every mention of the article is in the party's
    claim or the question ('alegada violação', 'saber se', admissibility bars, the 'caso em exame / questão em discussão' sections, the latter
    only when the 'III. Razões de decidir' marker bounds them) -> mention only. The court's own 'Dispositivos relevantes citados' / 'Tese de
    julgamento'. The CNJ-format 'Dispositivos relevantes citados' list names every cited dispositivo (barred ones too): it is neutral, and keeps
    the relation only when it is the article's sole mention."""
    text = text or ''
    if NOT_KNOWN.search(text) and not MERIT_VERB.search(text) and ADMISSIBILITY.search(text):
        return ('NO_MERIT_DECISION', 'recurso não conhecido por óbice de admissibilidade: o acórdão não decide a questão de direito civil')
    art = E.T.parse_target_id(target)['article']
    m = re.match(r'(\d+)(.*)', art)
    num = f"{int(m.group(1)):,}".replace(',', '.') + m.group(2)
    zones = [(z.start(1), z.end(1)) for z in CLAIM_ZONE.finditer(text)]
    hl = HOLDING_LIST.search(text)
    hits = [h.start() for h in re.finditer(r'(?<![\d.])' + re.escape(num) + r'(?![\d])', text)]
    if not hits:
        return None
    body = [h for h in hits if not (hl and h > hl.start())]
    if not body:
        return None                                       # cited only in the court's own list: kept for human review
    for h in body:
        in_zone = any(a <= h < b for a, b in zones)
        window = re.sub(r'\b(arts?|n|fls?|inc|par|al)\.', r'\1', text[max(0, h - 160):h], flags=re.I)   # abbreviation dots are not sentence ends
        window = window[max(window.rfind('. '), window.rfind('; ')) + 1:]
        if not in_zone and not CLAIM_CUE.search(window):
            return None
    return ('MENTION_IN_CLAIM_ONLY', 'o dispositivo aparece só na alegação da parte, na questão submetida ou no óbice de admissibilidade, não nas razões de decidir')


def cc1916_correspondence(text, target):
    """'arts. 849, III, e 851 do CC/1916, correspondentes aos arts. 1.499, IV, e 1.500 do CC/2002' / 'matéria atualmente regida pelo art.
    1.641, II': the decision applied the CC/1916; the CC/2002 article is cited as its correspondent (temporal review, never TIER A)."""
    if not CC1916.search(text or ''):
        return False
    art = E.T.parse_target_id(target)['article']
    m = re.match(r'(\d+)(.*)', art)
    num = f"{int(m.group(1)):,}".replace(',', '.') + m.group(2)
    for h in re.finditer(r'(?<![\d.])' + re.escape(num) + r'(?![\d])', text):
        if CORRESP.search(text[max(0, h.start() - 90):h.start()]):
            return True
    return False


def turma_representatives(out, covered, recs):
    """Non-qualified acórdãos of the Turmas (3ª/4ª, private law) repeat the same article hundreds of times (art. 205: 384 acórdãos): counting
    each would replicate one relation to inflate the count. They only fill targets that no published, decided or higher-source A/B relation
    covers; per such target ONE representative is kept — strong text evidence in the ementa, article named in the ementa header first, then
    the most recent judgment, then the id — and the others are corroboration (TIER C, linked to it). Deterministic."""
    raw = {r['raw_id']: r for r in recs}
    for x in out:                                         # non-qualified espelho acórdãos must decide on the dispositivo (any órgão)
        txt = ' '.join(sorted({raw[i].get('text') or '' for i in x['raw_ids']}))
        if x['tier'] in 'AB' and cc1916_correspondence(txt, x['target_id']):
            x['flags'] = sorted(set(x['flags']) | {'CORRESPONDENCIA_CC1916'})
            if x['tier'] == 'A':
                x.update(tier='B', tier_code='OFFICIAL_BUT_HUMAN_REVIEW_REQUIRED', tier_reason='CORRESPONDENCIA_CC1916')
            else:
                x['tier_reason'] = ', '.join(['CORRESPONDENCIA_CC1916'] + [r for r in x['tier_reason'].split(', ') if r])
        if x['tier'] in 'AB' and not x['qualified_precedent'] and set(x['sources']) <= set(ESPELHO_SOURCES):
            why = merit_check(txt, x['target_id'])
            if why:
                x.update(tier='C', tier_code=why[0], tier_reason=why[1], status='NOT_QUALIFIED')
    higher = covered | {x['target_id'] for x in out if x['tier'] in 'AB' and x['sources'] != ['STJ_ESPELHOS_TURMAS']}
    pool = collections.defaultdict(list)
    for x in out:
        if x['tier'] not in 'AB' or x['sources'] != ['STJ_ESPELHOS_TURMAS']:
            continue
        if x['target_id'] in higher:
            x.update(tier='C', tier_code='COVERED_BY_HIGHER_SOURCE', status='NOT_QUALIFIED',
                     tier_reason='acórdão de Turma (não qualificado) para dispositivo já coberto por vínculo publicado, decidido ou de fonte superior')
        elif x['evidence_strength'] != 'STRONG' or not any(f == 'ementa' for f in x['evidence_fields']):
            x.update(tier='C', tier_code='NON_QUALIFIED_WEAK_EVIDENCE', status='NOT_QUALIFIED',
                     tier_reason='acórdão de Turma sem o dispositivo nomeado de forma direta na ementa (só indexação ou evidência indireta)')
        else:
            pool[x['target_id']].append(x)
    for t, xs in pool.items():
        art = E.T.parse_target_id(t)['article']
        m = re.match(r'(\d+)(.*)', art)
        num = f"{int(m.group(1)):,}".replace(',', '.') + m.group(2)                 # '1368-B' -> '1.368-B', as ementas write it

        def rank(x):
            head = (raw[x['raw_ids'][0]].get('citation_context') or '')[:300]
            return ('CORRESPONDENCIA_CC1916' not in x['flags'], bool(re.search(r'\bARTS?\.?\s*(?:[\d.]+\s*(?:,|E)\s*)*' + re.escape(num) + r'\b', head.upper())), iso_date(x['judgment_date']) or '', x['id'])
        xs.sort(key=rank, reverse=True)
        rep = xs[0]
        rep['corroborating_precedents'] = [o['precedent_id'] for o in xs[1:]]
        for o in xs[1:]:
            o.update(tier='C', tier_code='CORROBORATION_NON_QUALIFIED', status='NOT_QUALIFIED', representative=rep['id'],
                     tier_reason=f"corrobora {rep['precedent_id']} (representante do dispositivo entre os acórdãos de Turma)")


def area_counts(index_doc):
    return collections.Counter(E.theme_of(t['target_id'], AREAS) for t in index_doc['targets'] if t['kind'] == 'ARTIGO')


RISK_GROUPS = [('TEMPORALIDADE', ('REDACAO_ALTERADA_APOS_JULGAMENTO', 'PRECEDENTE_ANTERIOR_AO_CC2002', 'POSSIVEL_REGIME_CC1916', 'CORRESPONDENCIA_CC1916')),
               ('USO_CONTEXTUAL_STF', ('USO_CONTEXTUAL_POSSIVEL',)),
               ('CLASSE_HOMOLOGATORIA', ('CLASSE_HOMOLOGATORIA',)),
               ('PROVISORIO_OU_CAUTELAR', ('PRECEDENTE_PROVISORIO', 'DECISAO_CAUTELAR')),
               ('REALOCACAO_DE_TARGET', ('TARGET_FALLBACK_TO_PARENT',)),
               ('PRECEDENTE_NAO_QUALIFICADO', ('PRECEDENTE_NAO_QUALIFICADO',)),
               ('EVIDENCIA_INDIRETA', ('EVIDENCIA_MEDIUM',))]


def risk_group(x):
    for name, keys in RISK_GROUPS:
        if any(k in x['tier_reason'] or k in x['flags'] for k in keys):
            return name
    return 'OUTROS'


def jsonl(rows):
    return ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows).encode('utf-8')


def dumpb(o):
    return (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def outputs():
    recs, inv, out, index_doc, phys = build()
    q = [x for x in out if x['tier'] in 'AB']
    c = collections.Counter(x['tier'] for x in out)
    arts_area = area_counts(index_doc)
    phys_arts = {E.T.parse_target_id(t)['article'] for t, _ in phys}
    valid = {t['target_id'] for t in index_doc['targets']}
    cov = {}
    for name, _, _ in AREAS:
        qa = [x for x in q if x['area'] == name]
        cov[name] = dict(articles_in_cc=arts_area[name],
                         articles_with_physical_j=len({a for a in phys_arts if E.theme_of(f'{NORM}:ART.{a}', AREAS) == name}),
                         physical_relations=sum(1 for t, _ in phys if E.theme_of(t, AREAS) == name),
                         new_candidate_targets=len({x['target_id'] for x in qa if x['new_target']}),
                         new_candidate_articles=len({E.T.parse_target_id(x['target_id'])['article'] for x in qa} - phys_arts),
                         candidate_relations=len(qa), tier_a=sum(1 for x in qa if x['tier'] == 'A'), tier_b=sum(1 for x in qa if x['tier'] == 'B'),
                         sources=dict(sorted(collections.Counter(s for x in qa for s in x['sources']).items())), status='AWAITING_USER_RATIFICATION')
    holes = sorted(cov, key=lambda k: (cov[k]['candidate_relations'] / max(cov[k]['articles_in_cc'], 1), k))
    for k in cov:
        cov[k]['discovery_gap'] = 'LACUNA' if k in holes[:3] else 'OK'
    by_src = collections.Counter(s for x in q for s in x['sources'])
    new_t = {x['target_id'] for x in q if x['new_target']}
    metrics = dict(
        BASELINE_CC_PHYSICAL='49/39', BASELINE_CF_PHYSICAL='315/198', RAW_DISCOVERIES=len(recs),
        OFFICIAL_SOURCE_VERIFIED=sum(1 for r in recs if r.get('source_hash_or_capture_id')), UNIQUE_PAIRS=len(out),
        TARGET_VALIDATED=sum(1 for x in out if 'TARGET_NOT_IN_INDEX' not in x['flags']),
        NEW_UNIQUE_PAIRS=sum(1 for x in out if x['tier_code'] not in ('DUPLICATE_PHYSICAL_BASELINE', 'PREVIOUSLY_DECIDED', 'PREVIOUSLY_DECIDED_PRECEDENT')),
        TIER_A=c['A'], TIER_B=c['B'], TIER_C=c['C'], NEW_QUALIFIED_CANDIDATE_RELATIONS=len(q),
        TARGET_MINIMUM_200_REACHED='YES' if len(q) >= 200 else 'NO', TARGET_STRETCH_300_REACHED='YES' if len(q) >= 300 else 'NO',
        NEW_DISTINCT_CC_TARGETS=len(new_t), NEW_DISTINCT_CC_ARTICLES=len({E.T.parse_target_id(t)['article'] for t in new_t} - phys_arts),
        STJ_REPETITIVE_RELATIONS=sum(1 for x in q if x['classe'] in ('REPETITIVO', 'IAC', 'SIRDR')),
        STJ_SUMULA_RELATIONS=sum(1 for x in q if x['tribunal'] == 'STJ' and x['classe'] == 'SUMULA'),
        STF_RELATIONS=sum(1 for x in q if x['tribunal'] == 'STF'),
        OTHER_OFFICIAL_RELATIONS=sum(1 for x in q if x['tribunal'] == 'STJ' and x['classe'] not in ('SUMULA', 'REPETITIVO', 'IAC', 'SIRDR')),
        HUMAN_REVIEW_REQUIRED=c['B'], AUTO_REJECTED=c['C'], QUALIFIED_BY_SOURCE=dict(sorted(by_src.items())),
        TIER_C_BY_REASON=dict(sorted(collections.Counter(x['tier_code'] for x in out if x['tier'] == 'C').items())),
        INVALID_TARGETS_IN_QUALIFIED_OUTPUT=sum(1 for x in q if x['target_id'] not in valid),
        PROJECTED_CC_IF_ALL_A_AND_B_APPROVED=f"{len(phys) + len(q)}/{len({t for t, _ in phys} | {x['target_id'] for x in q})}",
        PROJECTED_CC_IF_ONLY_A_APPROVED=f"{len(phys) + c['A']}/{len({t for t, _ in phys} | {x['target_id'] for x in q if x['tier'] == 'A'})}",
        SD_CHANGED='NO', FIRMWARE_CHANGED='NO', NEW_RELATIONS_PHYSICALLY_PUBLISHED=0, RATIFICATION_PERFORMED='NO')
    items = []
    for x in q:
        items.append(dict(id=x['id'], identity=x['key'], target=x['target_id'], classe=x['classe'], tribunal=x['tribunal'], precedent=x['precedent_id'],
                          source=x['sources'], evidence=x['citation_context'], evidence_fields=x['evidence_fields'], methods=x['discovery_methods'],
                          confidence='HIGH' if x['tier'] == 'A' else ('MEDIUM' if x['evidence_strength'] == 'STRONG' else 'LOW'),
                          risk=risk_group(x) if x['tier'] == 'B' else 'BAIXO',
                          proposed_decision='PROMOTE_RECOMMENDED' if x['tier'] == 'A' else 'REVIEW_INDIVIDUALLY', reason=x['tier_reason'],
                          status='AWAITING_USER_RATIFICATION', human_approved=False,
                          linked=[y['id'] for y in q if y['precedent_id'] == x['precedent_id'] and y['id'] != x['id']],
                          human_review_required=x['tier'] == 'B', new_target=x['new_target'], area=x['area']))
    queue = dict(schema_version=1, kind='CC_MASS_RATIFICATION_QUEUE', status='AWAITING_USER_RATIFICATION', human_approved=0,
                 groups=dict(GREEN=[x['id'] for x in q if x['tier'] == 'A'],
                             YELLOW={g: [x['id'] for x in q if x['tier'] == 'B' and risk_group(x) == g] for g, _ in RISK_GROUPS + [('OUTROS', ())]},
                             RED_COUNT=c['C']), items=items)
    # large raw data of the Turmas is not versioned (project policy): the versioned RAW keeps every other source plus the Turma records behind a
    # qualified relation; the full RAW and the Turma rejections go to _local/ (git-ignored), with their sha256 in the manifest
    q_raw = {i for x in q for i in x['raw_ids']}
    slim = [{k: v for k, v in r.items() if k not in ('text', 'tese')} for r in recs]
    files = {'CC_MASS_DISCOVERY_RAW.jsonl': jsonl([r for r in slim if r['source'] != 'STJ_ESPELHOS_TURMAS' or r['raw_id'] in q_raw]),
             'CC_MASS_DISCOVERY_QUALIFIED.jsonl': jsonl(q),
             'CC_MASS_DISCOVERY_REJECTED.jsonl': jsonl([x for x in out if x['tier'] == 'C' and x['sources'] != ['STJ_ESPELHOS_TURMAS']]),
             LOCAL_RAW: jsonl(slim), LOCAL_REJ: jsonl([x for x in out if x['tier'] == 'C' and x['sources'] == ['STJ_ESPELHOS_TURMAS']]),
             'CC_MASS_RATIFICATION_QUEUE.json': dumpb(queue),
             'CC_MASS_SOURCE_INVENTORY.json': dumpb(dict(completed=inv, blocked=BLOCKED_SOURCES, run_date=RUN_DATE)),
             'CC_JURIS_COVERAGE_MAP.json': dumpb(cov), 'CC_MASS_DISCOVERY_METRICS.json': dumpb(metrics)}
    ck = dict(SOURCES_COMPLETED=sorted(inv), SOURCES_PENDING=sorted(k for k in SOURCES if k not in inv), SOURCES_BLOCKED=sorted(BLOCKED_SOURCES),
              RAW_COUNT=len(recs), QUALIFIED_COUNT=len(q), TIER_A_COUNT=c['A'], TIER_B_COUNT=c['B'], TIER_C_COUNT=c['C'],
              LAST_PROCESSED_SOURCE_ID=sorted(inv)[-1],
              NEXT_RESUME_STEP='python build_cc_mass_discovery.py (idempotente; uma fonte pendente entra quando o seu índice existir)',
              OUTPUT_HASHES={k: sha(v) for k, v in sorted(files.items())})
    sim, sim_md = simulation(q)
    files['CC_MASS_SIMULATION_REPORT.md'] = sim_md.encode('utf-8')
    metrics.update(SIMULATION_TIER_A=sim['SIMULATED'], SIMULATION_DUPLICATE_QUERY_KEYS=sim['DUPLICATE_QUERY_KEYS'], CF_REGRESSION=sim['CF_REGRESSION'],
                   CC_J1_J2_REGRESSION=sim['CC_J1_J2_REGRESSION'])
    sam = sample(q)
    aud_md, aud = audit_md(q, sam, SAMPLE_REVIEW)
    metrics.update(aud)
    files['CC_MASS_DISCOVERY_AUDIT.md'] = aud_md.encode('utf-8')
    files['CC_MASS_DISCOVERY_REPORT.md'] = report_md(metrics, cov, q, inv, aud).encode('utf-8')
    files['CC_MASS_DISCOVERY_METRICS.json'] = dumpb(metrics)
    files['CC_MASS_DISCOVERY_SHA256.json'] = dumpb({k: sha(v) for k, v in sorted(files.items())})
    ck['OUTPUT_HASHES'] = {k: sha(v) for k, v in sorted(files.items())}
    files['CC_MASS_DISCOVERY_CHECKPOINT.json'] = dumpb(ck)
    return files, metrics, q, out, cov


# ------------------------------------------------------------------ SIMULATION_ONLY (TIER A through the generic packager; never deployable)
SIM_TIPO = {'SUMULA': 'sumula', 'REPETITIVO': 'repetitivo_stj', 'IAC': 'iac', 'RG': 'repercussao_geral', 'ADI': 'adi', 'ADC': 'adc', 'ADPF': 'adpf', 'ADO': 'ado'}
PROBE = '/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'


def simulation(q):
    a = [x for x in q if x['tier'] == 'A']
    card = {k.split('/')[-1] for k in load(HERE / 'CC_J2_PHYSICAL_DEPLOY/sd_manifest_post_full.json')['entries'] if k.startswith(E.P.CONTENT + '/')}
    recs, fichas, rels, skipped = {}, {}, [], []
    for x in a:
        trib, klass, num = x['precedent_id'].split(':')[:3]
        tipo = SIM_TIPO.get(klass)
        if not tipo:
            skipped.append(dict(id=x['id'], reason=f'classe {klass} sem regra de tipo do aparelho'))
            continue
        lab = E.JT.label(tipo, trib, num.replace('-', '/'))
        recs.setdefault(x['precedent_id'], dict(tipo=tipo, tribunal=trib, numero=num.replace('-', '/'), status='simulacao', titulo=lab,
                                                fonte=(x['source_urls'] or [''])[0]))
        fichas.setdefault(E.JT.ficha(x['precedent_id']), '\n'.join([f'{lab} ({trib})', f'TRIBUNAL: {trib}', 'SIMULAÇÃO — NÃO PUBLICADO (CC MASS DISCOVERY, TIER A)', '',
                                                                     'EVIDÊNCIA OFICIAL', x['citation_context'], '', 'FONTE OFICIAL',
                                                                     (x['source_urls'] or [''])[0]]) + '\n')
        rels.append(dict(norm=NORM, target_id=x['target_id'], precedent_id=x['precedent_id'], origin='CC_MASS TIER A (SIMULATION_ONLY)'))
    files, rep = E.simulate(PHYSICAL_SD, card, rels, recs, fichas, E.P.provisional_ids(), E.P.known_targets(), PROBE, NORM)
    cf_reg = rep['OTHER_NORM_KEYS_CHANGED'] + sum(v for k, v in rep['lost_by_namespace'].items() if k != NORM)
    cc_reg = rep['lost_by_namespace'].get(NORM, 0) + rep['BASELINE_RECORD_LINES_MISSING']
    lines = ['# CC MASS DISCOVERY — simulação técnica do TIER A (SIMULATION_ONLY)', '', '```',
             f"STATUS = SIMULATION_ONLY · DEPLOYABLE = NO · SD_CHANGED = NO · FIRMWARE_CHANGED = NO · TIER_A_SIMULADOS = {len(rels)}",
             f"DUPLICATE_QUERY_KEYS = {rep['DUPLICATE_QUERY_KEYS']} · CF_REGRESSION = {cf_reg} · CC_J1_J2_REGRESSION = {cc_reg} · "
             f"VISÍVEIS = {rep['NEW_VISIBLE']} · FICHA/BACK = {rep['NEW_FICHA_OPEN']} / {rep['NEW_BACK']} · OUTRO = {rep['OUTRO_LABELS']}", '```', '',
             'Base: a camada normalizada física pós-CC-J2 (`CC_J2_MATERIALIZATION_CANDIDATE/candidate/SD`, idêntica ao cartão aprovado 38/38). Os pares '
             'TIER A entram pelo `generic_packager.py` sem mudança; fichas são rascunhos automáticos da evidência oficial. Nada aqui é aprovação jurídica.',
             '', f"Contagens por norma (relações/alvos): {', '.join(f'{k} {v[0]}/{v[1]}' for k, v in sorted(rep['counts'].items()))}.",
             f"Rótulos: {rep['labels']}. Registros reaproveitados do cartão: {', '.join(rep['records_reused_from_card']) or '—'}.",
             f"Chaves do baseline preservadas: {rep['BASELINE_KEYS'] - rep['BASELINE_KEYS_NOT_PRESERVED']}/{rep['BASELINE_KEYS']}; chaves CF/ADCT alteradas: "
             f"{rep['OTHER_NORM_KEYS_CHANGED']}.", f"Pares TIER A sem regra de tipo do aparelho (não simulados): {len(skipped)}."]
    return dict(rep, skipped=skipped, CF_REGRESSION=cf_reg, CC_J1_J2_REGRESSION=cc_reg, SIMULATED=len(rels)), '\n'.join(lines) + '\n'


# ------------------------------------------------------------------ deterministic quality sample + reports
SAMPLE_SIZE = 40


def sample(q):
    """Deterministic, stratified: first item (by sha256 of id) of every (tier, source, class) stratum, then fill by sha256 order."""
    order = sorted(q, key=lambda x: sha(x['id'].encode()))
    picked, seen = [], set()
    for x in order:
        k = (x['tier'], x['sources'][0], x['classe'] if x['classe'] in QUALIFIED_KLASS else 'ACORDAO')
        if k not in seen:
            seen.add(k)
            picked.append(x)
    for x in order:
        if len(picked) >= SAMPLE_SIZE:
            break
        if x not in picked:
            picked.append(x)
    return sorted(picked, key=lambda x: x['id'])


def audit_md(q, sam, review):
    errs = collections.Counter()
    rows = []
    for x in sam:
        r = review.get(x['id'])
        if r:
            for k in ('source_identity', 'target_mapping', 'temporal', 'material_relevance', 'duplicate'):
                errs[k] += r[k] != 'OK'
        rows.append(f"| {x['id']} | {x['tier']} | {x['precedent_id']} | {x['target_id']} | {', '.join(x['sources'])} | "
                    + (' | '.join(r[k] for k in ('source_identity', 'target_mapping', 'temporal', 'material_relevance', 'duplicate')) + f" | {r['note']} |"
                       if r else 'pendente | | | | | |'))
    m = dict(SAMPLED_RELATIONS=len(sam), REVIEWED=sum(1 for x in sam if x['id'] in review), SOURCE_IDENTITY_ERRORS=errs['source_identity'],
             TARGET_MAPPING_ERRORS=errs['target_mapping'], TEMPORAL_ERRORS=errs['temporal'], MATERIAL_RELEVANCE_ERRORS=errs['material_relevance'],
             DUPLICATE_ERRORS=errs['duplicate'])
    L = ['# CC MASS DISCOVERY — auditoria de qualidade do motor (Passagem 2)', '', '```', ' · '.join(f'{k} = {v}' for k, v in m.items()), '```', '',
         'Amostra determinística e estratificada (primeiro item de cada estrato tier × fonte × classe, completada pela ordem do sha256 do id). Cada item '
         'foi relido na fonte oficial (texto da tese/enunciado/ementa e referência estruturada já capturados com hash). Erros sistemáticos encontrados '
         'durante a operação foram corrigidos na regra e o grupo inteiro reprocessado (seção final).', '',
         '| ID | Tier | Precedente | Target | Fonte | Identidade | Target | Temporal | Pertinência | Duplicata | Nota |', '|---|---|---|---|---|---|---|---|---|---|---|']
    L += rows
    L += ['', '## Regras corrigidas durante a operação (com reprocessamento do grupo)', '',
          '- **CC/1916 confundido com CC/2002:** "art. 993 do Código Civil de 1916" e "arts. 1.062 e 1.063 do CC/1916" chegaram a virar alvos do CC/2002 '
          '(SAME_DIPLOMA e NEAREST_MARKER aceitavam "do Código Civil de 1916"). A regra passou a exigir "mesmo diploma/código" e a respeitar a lei que '
          'fecha a lista. Teste de regressão incluído.',
          '- **Granularidade herdada da indexação:** a referência estruturada aponta incisos (art. 1.790, I a IV) que o texto não discute; sem citação '
          'textual da unidade, o vínculo sobe ao artigo, e um vínculo genérico cede ao específico do mesmo precedente.',
          '- **Dupla contagem do acórdão paradigma:** o REsp paradigma de um Tema Repetitivo contava como precedente próprio e como o Tema; agora conta uma vez.',
          '- **Indexação documental sem texto:** legislação citada (STF e espelhos do STJ) sem o artigo na tese/ementa vira C (só menção); o mesmo critério '
          'para STF e STJ.',
          '- **Questão submetida contra a tese:** dispositivo só na questão, com a tese aplicando outra norma, vira C.',
          '- **Julgamentos conjuntos do STJ:** acórdãos gêmeos da mesma sessão (mesmo órgão, data e ementa salvo "provido/improvido") contavam um por '
          'processo (ex.: REsp 2082647, 2100103 e 1929926, 2ª Seção, 12/03/2025); agora uma relação, como já era no STF (ADC 29/30 + ADI 4578).',
          '- **Fallback antes da deduplicação:** "art. 723, parágrafo único" (inexistente no índice) caía no art. 723 e duplicava o par já existente; o '
          'fallback passou a ser resolvido antes do agrupamento, e a classe do julgamento conjunto vem do precedente canônico.',
          '- **Inflação por acórdãos de Turma:** a 3ª e a 4ª Turmas repetem o mesmo artigo centenas de vezes (art. 205: 384 acórdãos). Contar cada um '
          'seria replicar a relação. Acórdão de Turma (não qualificado) só preenche dispositivo sem vínculo publicado, decidido ou de fonte superior; '
          'por dispositivo, um representante (evidência textual forte na ementa; artigo na verbetação; julgamento mais recente; id), os demais '
          'viram corroboração (C, ligada ao representante).',
          '- **Recurso não conhecido:** acórdão não qualificado que não conhece do recurso por óbice de admissibilidade (Súmulas 5/7/211/282/283/284, '
          'prequestionamento, paradigma) e não dá nem nega provimento não decide o dispositivo → C. O verbo de mérito tem de ser do próprio julgado '
          '("a origem negou provimento" não conta); acórdãos antigos que "não conhecem" depois de decidir a questão, sem óbice, ficam.',
          '- **Menção só na alegação:** dispositivo citado apenas na alegação da parte, na questão em discussão ("saber se..."), no óbice de '
          'admissibilidade ou na seção "caso em exame" → C. A lista "Dispositivos relevantes citados" (formato CNJ) cita também os dispositivos barrados: '
          'é neutra, e só mantém o vínculo quando for a única menção.',
          '- **Correspondência com o CC/1916:** "arts. 849, III, e 851 do CC/1916, correspondentes aos arts. 1.499, IV, e 1.500 do CC/2002" — a decisão '
          'aplicou o código antigo; o vínculo recebe CORRESPONDENCIA_CC1916 (grupo TEMPORALIDADE, nunca TIER A) e perde prioridade como representante.',
          '- **Fonte oficial malformada:** o arquivo mensal 20240229.json da 2ª Seção é JSON inválido ("Sem lançamentos para o mês de fevereiro/2024") e '
          'um campo de referência traz "PAR:000P3": registrados (MALFORMED_FILES / GRAMMAR_REJECTS), nunca reparados nem adivinhados.']
    return '\n'.join(L) + '\n', m


def report_md(metrics, cov, q, inv, aud):
    a = [x for x in q if x['tier'] == 'A']
    by_area = sorted(cov.items(), key=lambda kv: -kv[1]['candidate_relations'])
    best_src = max(metrics['QUALIFIED_BY_SOURCE'].items(), key=lambda kv: kv[1])[0] if metrics['QUALIFIED_BY_SOURCE'] else '—'
    L = ['# CC MASS DISCOVERY — relatório executivo (host-only)', '', '```',
         f"CC_MASS_DISCOVERY_STATUS = {'SUCCESS' if metrics['NEW_QUALIFIED_CANDIDATE_RELATIONS'] >= 200 else 'PARTIAL'} · BASELINE CC 49/39 · CF 315/198",
         f"RAW {metrics['RAW_DISCOVERIES']} · PARES ÚNICOS {metrics['UNIQUE_PAIRS']} · NOVOS {metrics['NEW_UNIQUE_PAIRS']} · TIER A {metrics['TIER_A']} · "
         f"TIER B {metrics['TIER_B']} · TIER C {metrics['TIER_C']} · QUALIFICADOS {metrics['NEW_QUALIFIED_CANDIDATE_RELATIONS']}",
         f"NOVOS TARGETS {metrics['NEW_DISTINCT_CC_TARGETS']} · NOVOS ARTIGOS {metrics['NEW_DISTINCT_CC_ARTICLES']} · SD_CHANGED NO · FIRMWARE_CHANGED NO · "
         'RATIFICAÇÃO NÃO REALIZADA', '```', '',
         '## Respostas', '',
         f"1. Relações novas descobertas (pares únicos ainda não publicados nem decididos): {metrics['NEW_UNIQUE_PAIRS']} (de {metrics['RAW_DISCOVERIES']} "
         'registros brutos).',
         f"2. Com fonte oficial confirmada: todos os registros brutos ({metrics['OFFICIAL_SOURCE_VERIFIED']}) têm fonte oficial e hash de captura.",
         f"3. Passaram nos controles automáticos (TIER A + B): {metrics['NEW_QUALIFIED_CANDIDATE_RELATIONS']}.",
         f"4. TIER A: {metrics['TIER_A']}. 5. TIER B: {metrics['TIER_B']}. 6. Rejeitadas automaticamente (TIER C): {metrics['TIER_C']} "
         f"({', '.join(f'{k} {v}' for k, v in sorted(metrics['TIER_C_BY_REASON'].items(), key=lambda kv: -kv[1]))}).",
         f"7. Novos targets que podem receber jurisprudência: {metrics['NEW_DISTINCT_CC_TARGETS']}. 8. Novos artigos: {metrics['NEW_DISTINCT_CC_ARTICLES']}.",
         f"9. Livro com maior expansão: {by_area[0][0]} ({by_area[0][1]['candidate_relations']} relações candidatas).",
         f"10. Fonte com mais resultados úteis: {best_src} ({metrics['QUALIFIED_BY_SOURCE'].get(best_src, 0)} relações qualificadas).",
         f"11. Casos que exigem análise humana: {metrics['HUMAN_REVIEW_REQUIRED']} (TIER B), agrupados por risco na fila; os {metrics['TIER_A']} TIER A "
         'podem ir em bloco.',
         '12. Código novo de motor: 0 linhas em `batch_engine.py`/`generic_packager.py`. Código novo: adapters genéricos (#5 STF, #6 espelhos STJ, v2 do #4) '
         'e o construtor desta operação.',
         '13. Escala: sim — a operação processou o dataset inteiro de precedentes qualificados (2.403), as 676 súmulas, 331 acórdãos de mérito do STF e '
         f"{sum(inv.get(k, {}).get('records', 0) for k in ESPELHO_SOURCES)} espelhos de acórdãos do STJ sem triagem manual por item; o juízo humano ficou "
         'concentrado no TIER B.',
         f"14. Projeção (não é aprovação): só TIER A → CC {metrics['PROJECTED_CC_IF_ONLY_A_APPROVED']}; TIER A + B → CC "
         f"{metrics['PROJECTED_CC_IF_ALL_A_AND_B_APPROVED']}.",
         '15. Estratégia de ratificação em massa: aprovar o GREEN (TIER A) em bloco; revisar o YELLOW por grupo de risco (temporalidade, provisório, '
         'realocação, não qualificado, homologatória, evidência indireta), decidindo por regra de grupo e só os casos sinalizados individualmente; manter o '
         'RED fora.', '',
         '## Composição do qualificado (leitura honesta)', '',
         f"- Precedentes qualificados, Seções, Corte Especial e STF: {sum(1 for x in q if x['sources'] != ['STJ_ESPELHOS_TURMAS'])} relações "
         f"(TIER A {len(a)}).",
         f"- Representantes de acórdãos da 3ª/4ª Turma: {sum(1 for x in q if x['sources'] == ['STJ_ESPELHOS_TURMAS'])} relações, uma por dispositivo "
         'sem outro vínculo; todas TIER B (precedente não qualificado). '
         f"{metrics['TIER_C_BY_REASON'].get('CORROBORATION_NON_QUALIFIED', 0)} acórdãos ficaram como corroboração e "
         f"{metrics['TIER_C_BY_REASON'].get('COVERED_BY_HIGHER_SOURCE', 0)} já estavam cobertos por fonte superior (não contados).",
         '- Sem os acórdãos de Turma o total seria inferior a 200: a meta foi atingida com jurisprudência oficial real, mas em grande parte não '
         'vinculante — o ganho é cobertura (dispositivos sem nenhuma jurisprudência), não autoridade.', '',
         '## Dados não versionados (política de datasets brutos)', '',
         '- `stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json` (índice derivado, 47 MB) e `CC_MASS_DISCOVERY/_local/` (RAW completo e rejeições das '
         'Turmas) ficam fora do git; os hashes estão em CC_MASS_DISCOVERY_SHA256.json e CC_MASS_SOURCE_INVENTORY.json (arquivo a arquivo).',
         '- Reconstrução: baixar os recursos dos datasets `espelhos-de-acordaos-terceira-turma` e `espelhos-de-acordaos-quarta-turma` do portal '
         'https://dadosabertos.web.stj.jus.br (CKAN, CC-BY) e rodar `python discovery_stj_espelhos.py --dir <3ª Turma> --dir <4ª Turma> --out '
         'stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json`, depois `python build_cc_mass_discovery.py`; o `--check` confere byte a byte.', '',
         '## Cobertura por livro', '', '| Livro | Artigos no CC | Artigos com J física | Novos targets candidatos | Relações candidatas (A/B) | Lacuna |',
         '|---|---:|---:|---:|---:|---|']
    L += [f"| {k} | {v['articles_in_cc']} | {v['articles_with_physical_j']} | {v['new_candidate_targets']} | {v['candidate_relations']} "
          f"({v['tier_a']}/{v['tier_b']}) | {v['discovery_gap']} |" for k, v in cov.items()]
    L += ['', '## Fontes', '', '| Fonte | Registros processados | Com o CC | Hash |', '|---|---:|---:|---|']
    L += [f"| {k} | {v.get('records')} | {v.get('citing', '—')} | `{v['sha256'][:16]}…` |" for k, v in sorted(inv.items())]
    L += ['', 'Bloqueadas (registradas, não contornadas): ' + '; '.join(f'{k}: {v}' for k, v in BLOCKED_SOURCES.items()) + '.', '',
          '## Riscos jurídicos identificados', '',
          '- Lei 14.905/2024 (arts. 406 e 591) e Lei 15.040/2024 (seguros, arts. 757–802 revogados): pares temporais marcados ou rejeitados.',
          '- Precedentes anteriores ao CC/2002 e regras de transição (art. 2.028): marcados para revisão.',
          '- Acórdãos não qualificados (Seções, Corte Especial, Turmas, homologações) ficam no máximo em B; os de Turma, só como representante.',
          '- Recurso não conhecido por óbice de admissibilidade e dispositivo citado só na alegação da parte: rejeitados (C).',
          '- Decisões que aplicaram o CC/1916 citando o artigo correspondente do CC/2002: sinalizadas (CORRESPONDENCIA_CC1916).',
          '- Indexação documental (legislação citada) não basta: exige o artigo no texto da tese/ementa.',
          '- Temas afetados/sobrestados/"RE pendente": provisórios (B).', '',
          f"Auditoria da amostra: {aud['REVIEWED']}/{aud['SAMPLED_RELATIONS']} revisados; erros de identidade {aud['SOURCE_IDENTITY_ERRORS']}, de target "
          f"{aud['TARGET_MAPPING_ERRORS']}, temporais {aud['TEMPORAL_ERRORS']}, de pertinência {aud['MATERIAL_RELEVANCE_ERRORS']}, duplicatas "
          f"{aud['DUPLICATE_ERRORS']} (ver CC_MASS_DISCOVERY_AUDIT.md).", '',
          '## Próxima missão proposta', '', '`MASS HUMAN RATIFICATION` — aprovar o TIER A em bloco, revisar o TIER B por grupos, manter o TIER C fora. '
          'Não executada.']
    return '\n'.join(L) + '\n'


def main():
    files, metrics, q, out, cov = outputs()
    if '--check' in sys.argv:
        ok = all((OUT / k).is_file() and (OUT / k).read_bytes().replace(b'\r\n', b'\n') == v for k, v in files.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.mkdir(exist_ok=True)
    for k, v in files.items():
        (OUT / k).parent.mkdir(parents=True, exist_ok=True)
        (OUT / k).write_bytes(v)
    print(json.dumps({k: v for k, v in metrics.items() if not isinstance(v, dict)}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
