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
    'STF_JURISPRUDENCIA': HERE / 'stf/STF_CC2002_INDEX.json',
    'PLANALTO_VIDE': PLANALTO,
}
BLOCKED_SOURCES = {
    'STJ_JURISPRUDENCIA_EM_TESES': 'https://scon.stj.jus.br/SCON/jt/ — desafio Cloudflare com resposta exigida (não contornado), 2026-10-19',
    'STJ_PESQUISA_PRONTA': 'https://scon.stj.jus.br/SCON/pesquisa_pronta/ — mesmo desafio (403), 2026-10-19',
    'STJ_PUBLICACOES_INSTITUCIONAIS': 'https://www.stj.jus.br/publicacaoinstitucional/ (Súmulas Anotadas, Jurisprudência em Teses PDF) — página de '
                                      'desafio / 404 no navegador, 2026-10-19',
    'STF_API_DIRETA_DO_HOST': 'POST direto do host recebe desafio WAF 202; captura feita pelo navegador (caminho normal da página)',
}
JOINT = {'STF:ADI:6792': 'STF:ADI:6792-7055', 'STF:ADI:7055': 'STF:ADI:6792-7055', 'STF:ADI:7047': 'STF:ADI:7047-7064', 'STF:ADI:7064': 'STF:ADI:7047-7064'}
QUALIFIED_KLASS = ('SUMULA', 'REPETITIVO', 'IAC', 'RG', 'ADI', 'ADC', 'ADPF', 'ADO', 'SIRDR')
STRONG = ('DIRECT', 'COMPONENT_FIRST', 'LIST_TAIL', 'SAME_DIPLOMA')
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


def number_in_text(t, text):
    """'art. 1.790' (any formatting of the article number) mentioned in the text and not immediately attributed to another law."""
    n = art_label(t).replace('.', r'\.?')
    for m in re.finditer(rf'\barts?\.?\s*(?:n[º°o.]\s*)?{n}(?!\d)', text or '', re.I):
        tail = text[m.end():m.end() + 45]
        if not TXT.OTHER_LAW.search(re.split(r'[;.]\s', tail)[0] or ''):
            return True
    return False


# ------------------------------------------------------------------ raw discovery (one record per evidence)
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
    # STJ espelhos
    p = SOURCES['STJ_ESPELHOS_ACORDAOS']
    if p.exists():
        x = load(p)
        for e in x['entries']:
            for t, methods in e['targets'].items():
                for m in methods:
                    field, meth = m.split(':')
                    add(source='STJ_ESPELHOS_ACORDAOS', source_url=e['source_url'], source_document_id=e['source_document_id'], tribunal='STJ',
                        classe=e['klass'], precedent_number=e['number'], precedent_id=e['id'], judgment_date=e['julgamento'], publication_date=e['publicacao'],
                        legal_reference_raw=field, candidate_target=t, citation_context=e['ementa'][:400],
                        discovery_method=('STRUCTURED_LEGISLATIVE_REFERENCE' if meth == 'STRUCTURED' else f'TEXT_{meth}'), evidence_field=field,
                        status='JULGADO', source_hash_or_capture_id=e['file_sha256'], text=e['ementa'] + ' ' + e.get('tese', ''), orgao=e['orgao'],
                        tema_links=e.get('temas', []))
        inv['STJ_ESPELHOS_ACORDAOS'] = dict(path=str(p.relative_to(HERE)), sha256=sha_file(p), records=x['stats']['ACORDAOS'], versions=x['source']['files'],
                                            citing=x['stats']['WITH_TARGETS'])
    # STF
    p = SOURCES['STF_JURISPRUDENCIA']
    f = load(p)
    for e in f['entries']:
        for t, methods in e['targets'].items():
            for m in methods:
                field, meth = m.split(':')
                pid = JOINT.get(e['id'], e['id'])
                add(source='STF_JURISPRUDENCIA', source_url=e['url'] or f['source']['api'], source_document_id=f"{e['titulo']} ({e['source_document_id']})",
                    tribunal='STF', classe=e['klass'], precedent_number=e['number'], precedent_id=pid, judgment_date=e['julgamento'],
                    publication_date=e['publicacao'], legal_reference_raw=field, candidate_target=t,
                    citation_context=(e['tese'] or e['ementa'])[:400], discovery_method=('STRUCTURED_LEGISLATIVE_REFERENCE' if meth == 'STRUCTURED' else f'TEXT_{meth}'),
                    evidence_field=field, status=e['observacao'][:80] or ('RG MÉRITO' if e['rg_merito'] else 'JULGADO'),
                    source_hash_or_capture_id=f['source']['capture_sha256'], text=e['tese'] + ' ' + e['ementa'], orgao=e['orgao'], incidente=e['incidente'],
                    titulo=e['titulo'], rg_merito=e['rg_merito'])
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
        if r['discovery_method'] == 'STRUCTURED_LEGISLATIVE_REFERENCE' and (p['paragraph'] or p['inciso'] or p['alinea']) and                 r['candidate_target'] not in text_cited[r['precedent_id']]:
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
    recs, inv = raw_records()
    groups = collections.OrderedDict()
    for r in recs:
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
        if year and year < 2003 and klass in ('SUMULA', 'REPETITIVO', 'IAC'):
            flags.append('PRECEDENTE_ANTERIOR_AO_CC2002')
        # status
        st = ' '.join(sorted({str(r.get('status') or '') for r in ev}))
        if re.search(r'CANCELAD|REVOGAD|Vinculada a Tema|Revisado', st, re.I):
            flags.append('PRECEDENTE_NAO_VIGENTE')
        if re.search(r'RE Pendente|Afetado|Pendente|Em Julgamento|Sobrestado', st, re.I):
            flags.append('PRECEDENTE_PROVISORIO')
        inc = {r.get('incidente') for r in ev if r.get('incidente')}
        if inc & {'MC', 'MC-Ref'}:
            flags.append('DECISAO_CAUTELAR')
        if inc & {'ED', 'AgR', 'ED-segundos'}:
            flags.append('INCIDENTE_RECURSAL')
        if klass == 'RG' and first['source'] == 'STF_JURISPRUDENCIA' and not any(r.get('rg_merito') for r in ev):
            flags.append('RG_SEM_MERITO_CONFIRMADO')
        # evidence strength
        txt_methods = {m.replace('TEXT_', '') for m in methods if m.startswith('TEXT_')}
        strong_fields = {r['evidence_field'] for r in ev if r['discovery_method'].replace('TEXT_', '') in STRONG}
        corroborated = number_in_text(target, text)
        if txt_methods & set(STRONG) and strong_fields & {'tese', 'enunciado', 'ementa', 'vide'}:
            strength = 'STRONG'
        elif 'OFFICIAL_ANNOTATION' in methods:
            strength = 'STRONG'
        elif txt_methods & set(STRONG) or 'NEAREST_MARKER' in txt_methods or (corroborated and 'STRUCTURED_LEGISLATIVE_REFERENCE' in methods):
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
        if not status:
            if 'TARGET_NOT_IN_INDEX' in flags:
                status = ('C', 'INVALID_TARGET', 'target inexistente no índice do CC2002, sem pai válido')
            elif 'DISPOSITIVO_REVOGADO' in flags:
                status = ('C', 'REVOKED_DISPOSITIVO', 'dispositivo revogado (Planalto)')
            elif 'PRECEDENTE_NAO_VIGENTE' in flags:
                status = ('C', 'PRECEDENT_NOT_CURRENT', st[:80])
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
                                  'DECISAO_CAUTELAR'}
            if qualified and strength == 'STRONG' and not risky:
                status = ('A', 'DIRECT_OFFICIAL_RELATION', 'fonte oficial nomeia o dispositivo na tese/enunciado/ementa de precedente qualificado')
            else:
                why = sorted(risky) + ([] if qualified else ['PRECEDENTE_NAO_QUALIFICADO']) + ([] if strength == 'STRONG' else [f'EVIDENCIA_{strength}'])
                status = ('B', 'OFFICIAL_BUT_HUMAN_REVIEW_REQUIRED', ', '.join(why))
        tier, code, reason = status
        out.append(dict(id=f'CCMD-{n:05d}', key='|'.join(key), norm=NORM, target_id=target, target_raw=t,
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
    return recs, inv, out, index_doc, phys


def area_counts(index_doc):
    return collections.Counter(E.theme_of(t['target_id'], AREAS) for t in index_doc['targets'] if t['kind'] == 'ARTIGO')


RISK_GROUPS = [('TEMPORALIDADE', ('REDACAO_ALTERADA_APOS_JULGAMENTO', 'PRECEDENTE_ANTERIOR_AO_CC2002')),
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
    files = {'CC_MASS_DISCOVERY_RAW.jsonl': jsonl([{k: v for k, v in r.items() if k not in ('text', 'tese')} for r in recs]), 'CC_MASS_DISCOVERY_QUALIFIED.jsonl': jsonl(q),
             'CC_MASS_DISCOVERY_REJECTED.jsonl': jsonl([x for x in out if x['tier'] == 'C']),
             'CC_MASS_RATIFICATION_QUEUE.json': dumpb(queue),
             'CC_MASS_SOURCE_INVENTORY.json': dumpb(dict(completed=inv, blocked=BLOCKED_SOURCES, run_date=RUN_DATE)),
             'CC_JURIS_COVERAGE_MAP.json': dumpb(cov), 'CC_MASS_DISCOVERY_METRICS.json': dumpb(metrics)}
    ck = dict(SOURCES_COMPLETED=sorted(inv), SOURCES_PENDING=sorted(k for k in SOURCES if k not in inv), SOURCES_BLOCKED=sorted(BLOCKED_SOURCES),
              RAW_COUNT=len(recs), QUALIFIED_COUNT=len(q), TIER_A_COUNT=c['A'], TIER_B_COUNT=c['B'], TIER_C_COUNT=c['C'],
              LAST_PROCESSED_SOURCE_ID=sorted(inv)[-1],
              NEXT_RESUME_STEP='python build_cc_mass_discovery.py (idempotente; uma fonte pendente entra quando o seu índice existir)',
              OUTPUT_HASHES={k: sha(v) for k, v in sorted(files.items())})
    files['CC_MASS_DISCOVERY_CHECKPOINT.json'] = dumpb(ck)
    return files, metrics, q, out, cov


def main():
    files, metrics, q, out, cov = outputs()
    if '--check' in sys.argv:
        ok = all((OUT / k).is_file() and (OUT / k).read_bytes().replace(b'\r\n', b'\n') == v for k, v in files.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.mkdir(exist_ok=True)
    for k, v in files.items():
        (OUT / k).write_bytes(v)
    print(json.dumps({k: v for k, v in metrics.items() if not isinstance(v, dict)}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
