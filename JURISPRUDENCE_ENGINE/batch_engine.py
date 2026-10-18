"""JURISPRUDENCE_ENGINE — generic review-batch engine (norm-agnostic; host-only; never writes to a card, never ratifies).

CC-J1 had its batch stage hard-coded in three scripts (build_cc_j1.py selection + review, build_cc_j1_dossier.py, build_cc_j1_simulation.py).
This module is that stage once, for any norm of the catalog: a batch is a CONFIG (norm, channels, exclusions from earlier ratifications,
themes of the norm) + a REVIEW table (the human reading of the official evidence) — data, not code. Stages:
  physical_layer   frozen normalized layer (06_NORMALIZADO) -> baseline relations + precedent records (the authority, byte-for-byte)
  backlog          discovered pairs -> automatic checks (target grammar, namespace/index, temporal, duplicates, source) -> exclusions
  score / select   deterministic risk/coverage score + round-robin over the norm's themes (diversity, not only easy cases)
  apply_review     validates every human decision against fail-closed rules (categories, targets, GREEN/YELLOW/RED invariants)
  coverage         current vs projected relations/targets per area of the norm (projection is never a baseline)
  simulate         generic packager over baseline + proposals; CF / earlier-batch regression and device-path reachability
  sloc             code vs review-data lines of a builder (factory-speed metric)
"""
import ast
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'firmware_multinorm'), str(ROOT / 'LEGAL_TARGET_ID'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import generic_packager as P  # noqa: E402
import juris_types as JT  # noqa: E402
import multinorm_sim as S  # noqa: E402
import target_id as T  # noqa: E402

LINKING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED', 'MULTI_TARGET_RECOMMENDED', 'CONTEXTUAL_RECOMMENDED')
REJECTS = ('REJECT_FALSE_POSITIVE_RECOMMENDED', 'REJECT_TEMPORAL_MISMATCH_RECOMMENDED', 'REJECT_SUPERSEDED_RECOMMENDED', 'REJECT_NOT_MATERIAL_RECOMMENDED')
NON_LINKING = REJECTS + ('ALREADY_COVERED', 'DUPLICATE_RECOMMENDATION', 'UNRESOLVED_EXTERNAL', 'UNRESOLVED_IDENTIFICATION')
DECISIONS = LINKING + NON_LINKING
TEMPORAL = ('CURRENT', 'HISTORICAL_BUT_RELEVANT', 'SUPERSEDED', 'NEEDS_REVIEW', 'WRONG_CODE_VERSION')
GROUPS = ('GREEN', 'YELLOW', 'RED')
STEPS = ('AUTO_DISCOVERED', 'AUTO_TARGET_NORMALIZED', 'AUTO_NAMESPACE_CHECKED', 'AUTO_TEMPORAL_CHECKED', 'AUTO_DUPLICATE_CHECKED',
         'AUTO_SOURCE_VERIFIED', 'AUTO_FICHA_DRAFTED')


class BatchError(ValueError):
    pass


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


# ---------------- physical baseline ----------------
def tail_to_target(tail):
    norm, art, par, inc, ali = tail.split(':')
    return T.format_target_id(norm, art, paragraph=None if par == '-' else par, inciso=None if inc == '-' else inc, alinea=None if ali == '-' else ali)


def physical_layer(sd_root):
    """(lookup bytes, records bytes, rows) of the frozen normalized layer; each row = one physical relation with its record."""
    layer = Path(sd_root) / P.LAYER
    look, recs = (layer / 'JUR_LOOKUP.IDX').read_bytes(), (layer / 'JURISPRUDENCIA.IDX').read_bytes()
    rows, meta = [], {}
    for line in recs.decode('utf-8').split('\n')[1:]:
        if not line:
            continue
        f = line.split('|')
        ident = f[6]
        rec = dict(tipo=f[1], tribunal=f[2], numero=f[3], status=f[4], titulo=f[5], fonte=f[7])
        if meta.setdefault(ident, rec) != rec:
            raise BatchError(f'INCONSISTENT_PHYSICAL_RECORD {ident}')
        rows.append(dict(line=line, target_id=tail_to_target(f[0][len(ident) + 1:]), precedent_id=ident, record=rec))
    return look, recs, rows


def namespace_of(target_id):
    return T.parse_target_id(target_id)['namespace']


def article_number(target_id):
    return int(re.match(r'\d+', T.parse_target_id(target_id)['article']).group(0))


# ---------------- channel readers (official adapters' outputs -> discovery pairs, any norm) ----------------
def _year(s):
    m = re.search(r'(19|20)\d{2}', s or '')
    return int(m.group(0)) if m else None


def pairs_from_stj_sumulas(idx, norm):
    src = dict(id='STJ_PDF', url=idx['source']['url'], sha256=idx['source']['pdf_sha256'], tier='A')
    out = []
    for e in idx['entries']:
        for r in e['references']:
            if r['catalog_id'] != norm:
                continue
            for t in r['targets']:
                out.append(dict(channel='STJ_SUMULAS_PDF', precedent=f"STJ:SUMULA:{e['number']}", target=t, tribunal='STJ', klass='SUMULA_STJ',
                                number=str(e['number']), device_label=JT.label('sumula', 'STJ', e['number']), judgment_year=_year(e['data_decisao']),
                                current=e['status'] == 'VIGENTE', final=True, merit=True, status_text=e['status'],
                                judgment=f"{e['orgao']}, {e['data_decisao']}", evidence=e['enunciado'], source=src,
                                text_names_article=bool(re.search(r'\bart', e['enunciado'], re.I)), ficha_kind='SUMULA'))
    return out


STJ_FINAL = ('Trânsito em Julgado', 'Mérito Julgado')
STJ_PUBLISHED = ('Acórdão Publicado', 'Acórdão Publicado - RE Pendente')
STJ_TIPO = {'REPETITIVO': 'repetitivo_stj', 'IAC': 'iac'}


def pairs_from_stj_precedentes(idx, norm):
    src = dict(id='STJ_DADOS_ABERTOS_TEMAS', url=idx['source']['url'], sha256=idx['source']['csv_sha256'], tier='A')
    out = []
    for e in idx['entries']:
        if e['klass'] not in STJ_TIPO:
            continue
        for t, from_tese in [(t, True) for t in e['targets_from_tese']] + [(t, False) for t in e['targets_from_reference'] if t not in e['targets_from_tese']]:
            if namespace_of(t) != norm:
                continue
            out.append(dict(channel='STJ_PRECEDENTES_DADOS_ABERTOS', precedent=e['id'], target=t, tribunal='STJ', klass=e['klass'], number=e['number'],
                            device_label=JT.label(STJ_TIPO[e['klass']], 'STJ', e['number']), judgment_year=_year(e['data_julgamento']),
                            current=e['situacao'] in STJ_FINAL + STJ_PUBLISHED, final=e['situacao'] in STJ_FINAL, merit=True,
                            status_text=e['situacao'], judgment=f"{e['orgao']}, j. {e['data_julgamento']}", evidence=e['tese'],
                            questao=e['questao'], sumula_originada=e['sumula_originada'], rg_stf=e['rg_stf'], source=dict(src, page=idx['source']['search_page']),
                            text_names_article=from_tese, ficha_kind='TESE'))
    return out


# ---------------- backlog ----------------
def temporal_auto(target, amendments, judgment_year):
    """Planalto amendment notes of the dispositivo vs the judgment year (fail closed: unknown -> not checked)."""
    if target not in amendments:
        return dict(checked=False, result='UNKNOWN', notes=[])
    notes = amendments[target]
    if any(a['kind'].lower().startswith('revogad') for a in notes):
        res = 'REVOKED'
    elif judgment_year and any(a['year'] > judgment_year for a in notes):
        res = 'AMENDED_AFTER_JUDGMENT'
    else:
        res = 'CURRENT'
    return dict(checked=True, result=res, notes=[f"{a['kind']} pela {a['by']}" for a in notes])


def backlog(pairs, norm, index, amendments, baseline, precedent_exclusions, pair_exclusions):
    """pairs: discovery output, one dict per (target, precedent) with channel, judgment_year, current (bool), source{url,sha256,tier},
    text_names_article. Exclusions are explicit (code, note). Returns (candidates grouped by precedent, excluded, cross-channel corroborations)."""
    excluded, corrob, seen, cands = [], [], {}, collections.OrderedDict()
    for p in pairs:
        key = (p['target'], p['precedent'])
        if key in seen:
            corrob.append(dict(target=p['target'], precedent=p['precedent'], channel=p['channel'], kept=seen[key]))
            continue
        seen[key] = p['channel']
        try:
            t = T.parse_target_id(p['target'])
            normalized = True
        except T.TargetIdError:
            t, normalized = None, False
        why = precedent_exclusions.get(p['precedent']) or pair_exclusions.get(key)
        if key in baseline:
            why = ('IN_PHYSICAL_BASELINE', 'relação já publicada no baseline físico congelado')
        if not why and not p.get('current', True):
            why = ('PRECEDENT_NOT_CURRENT', p.get('status_text', ''))
        if not why and normalized and t['namespace'] != norm:
            why = ('OTHER_NORM', t['namespace'])
        if why:
            excluded.append(dict(target=p['target'], precedent=p['precedent'], channel=p['channel'], code=why[0], note=why[1]))
            continue
        tmp = temporal_auto(p['target'], amendments, p.get('judgment_year'))
        src = p.get('source') or {}
        pair = dict(target=p['target'], in_index=p['target'] in index, temporal_auto=tmp,
                    steps=dict(AUTO_DISCOVERED=True, AUTO_TARGET_NORMALIZED=normalized, AUTO_NAMESPACE_CHECKED=normalized,
                               AUTO_TEMPORAL_CHECKED=tmp['checked'], AUTO_DUPLICATE_CHECKED=True,
                               AUTO_SOURCE_VERIFIED=bool(src.get('url') and src.get('sha256') and src.get('tier') == 'A')))
        c = cands.setdefault(p['precedent'], dict({k: v for k, v in p.items() if k not in ('target',)}, discovered_targets=[], pairs=[]))
        c['discovered_targets'].append(p['target'])
        c['pairs'].append(pair)
    return list(cands.values()), excluded, corrob


# ---------------- scoring / selection ----------------
def theme_of(target_id, themes):
    n = article_number(target_id)
    for name, lo, hi in themes:
        if lo <= n <= hi:
            return name
    return 'OUTROS'


def score(c, cov):
    """Risk/coverage score (documented in the batch report): direct official citation, current dispositivo, current precedent, coverage gap,
    several dispositivos. Never rewards targets that already have jurisprudence."""
    tmp = [x['temporal_auto']['result'] for x in c['pairs']]
    validity = -4 if all(r == 'REVOKED' for r in tmp) else -2 if 'REVOKED' in tmp else 1 if 'AMENDED_AFTER_JUDGMENT' in tmp else 2 if all(
        r == 'CURRENT' for r in tmp) else 0
    prec = 2 if c.get('current', True) and c.get('final', True) and c.get('merit', True) else -2 if not c.get('merit', True) else 1
    gap = max(2 if cov.get(t, 0) == 0 else 1 if cov.get(t, 0) == 1 else 0 for t in c['discovered_targets'])
    parts = dict(direct=3 if c.get('text_names_article') else 2, target_validity=validity, precedent=prec, coverage_gap=gap,
                 multi_dispositivo=1 if len(set(c['discovered_targets'])) > 1 else 0, in_index=0 if all(x['in_index'] for x in c['pairs']) else -1)
    return sum(parts.values()), parts


def select(cands, n, themes, cov, channel_order):
    """Deterministic: order inside each theme by (-score, channel order, precedent id); then round-robin over the themes (themes ordered by
    their best score, then name) until n. Returns (selected, remaining)."""
    for c in cands:
        c['score'], c['score_parts'] = score(c, cov)
        c['theme'] = theme_of(c['discovered_targets'][0], themes)
    by = collections.defaultdict(list)
    for c in sorted(cands, key=lambda c: (-c['score'], channel_order.index(c['channel']), c['precedent'])):
        by[c['theme']].append(c)
    order = sorted(by, key=lambda th: (-by[th][0]['score'], th))
    sel, i = [], 0
    while len(sel) < n and any(i < len(by[th]) for th in order):
        for th in order:
            if i < len(by[th]) and len(sel) < n:
                sel.append(by[th][i])
        i += 1
    ids = {c['precedent'] for c in sel}
    return sel, [c for c in cands if c['precedent'] not in ids]


# ---------------- human review (validated, never ratified) ----------------
def apply_review(selected, review, norm, index, prefix):
    if sorted(review) != sorted(c['precedent'] for c in selected):
        raise BatchError('REVIEW_DOES_NOT_MATCH_SELECTION ' + str(sorted(set(review) ^ {c['precedent'] for c in selected})))
    out = []
    for rank, c in enumerate(selected, 1):
        r = review[c['precedent']]
        d, targets, tmp, grp = r['decision'], r['targets'], r['temporal'], r['group']
        if d not in DECISIONS or tmp not in TEMPORAL or grp not in GROUPS:
            raise BatchError(f'BAD_CATEGORY {c["precedent"]}')
        for t in targets:
            if namespace_of(t) != norm or t not in index:
                raise BatchError(f'TARGET_NOT_IN_INDEX {c["precedent"]} {t}')
        auto = {x['target']: x['temporal_auto']['result'] for x in c['pairs']}
        if d in LINKING:
            if not targets or (d == 'MULTI_TARGET_RECOMMENDED' and len(targets) < 2):
                raise BatchError(f'LINKING_WITHOUT_TARGETS {c["precedent"]}')
            if d == 'REALLOCATE_RECOMMENDED' and set(targets) == set(c['discovered_targets']):
                raise BatchError(f'REALLOCATE_TO_SAME {c["precedent"]}')
            if any(auto.get(t) == 'REVOKED' for t in targets):
                raise BatchError(f'LINK_TO_REVOKED {c["precedent"]}')
        elif targets:
            raise BatchError(f'NON_LINKING_WITH_TARGETS {c["precedent"]}')
        green_ok = (d == 'PROMOTE_RECOMMENDED' and tmp == 'CURRENT' and c['source'].get('tier') == 'A' and not r.get('human')
                    and all(auto.get(t, 'CURRENT') == 'CURRENT' for t in targets) and c.get('final', True))
        if (grp == 'GREEN' and not green_ok) or (grp == 'YELLOW' and d not in LINKING) or (grp == 'RED' and d in LINKING):
            raise BatchError(f'GROUP_RULE_VIOLATION {c["precedent"]} {grp} {d}')
        out.append(dict(id=f'{prefix}-{rank:02d}', rank=rank, precedent=c['precedent'], channel=c['channel'], theme=c['theme'],
                        score=c['score'], score_parts=c['score_parts'], discovered_targets=c['discovered_targets'],
                        temporal_auto={x['target']: x['temporal_auto'] for x in c['pairs']}, in_index={x['target']: x['in_index'] for x in c['pairs']},
                        steps={k: all(x['steps'][k] for x in c['pairs']) for k in STEPS if k != 'AUTO_FICHA_DRAFTED'},
                        tribunal=c['tribunal'], klass=c['klass'], number=c['number'], device_label=c['device_label'],
                        device_type=JT.device_status(c['klass']), status_text=c.get('status_text', ''), judgment=c.get('judgment', ''),
                        evidence=c.get('evidence', ''), source=c['source'], decision=d, proposed_targets=targets, temporal=tmp,
                        confidence=r['confidence'], group=grp, risk=r['risk'], motive=r['motive'], yellow=r.get('yellow'), red_reopen=r.get('reopen'),
                        CC_J1_INTERACTION=r.get('ccj1'), HUMAN_JUDGMENT_REQUIRED=grp == 'YELLOW' or bool(r.get('human')) or r['confidence'] != 'HIGH',
                        status='AWAITING_USER_RATIFICATION', human_approved=False))
    return out


def relations(decisions, groups=('GREEN', 'YELLOW')):
    return sorted({(t, x['precedent']) for x in decisions if x['decision'] in LINKING and x['group'] in groups for t in x['proposed_targets']})


# ---------------- coverage ----------------
def coverage(rels, index_targets, themes, areas):
    """rels: (target, precedent). Per area: relations, distinct targets, articles with J, articles of the area in the index (density)."""
    arts = collections.Counter(theme_of(t['target_id'], areas) for t in index_targets if t['kind'] == 'ARTIGO')
    out = {}
    for name, _, _ in areas:
        rs = [(t, p) for t, p in rels if theme_of(t, areas) == name]
        with_j = {T.parse_target_id(t)['article'] for t, _ in rs}
        out[name] = dict(relations=len(rs), targets=len({t for t, _ in rs}), articles_with_j=len(with_j), articles_in_norm=arts[name],
                         density_pct=round(100 * len(with_j) / arts[name], 2) if arts[name] else 0.0,
                         themes=dict(sorted(collections.Counter(theme_of(t, themes) for t, _ in rs).items())))
    return out


# ---------------- simulation (never deployable) ----------------
def simulate(sd_root, card_fichas, new_rels, new_records, new_fichas, provisional_ids, known_targets, probe_path, norm):
    look0, recs0, rows = physical_layer(sd_root)
    base_rels = [dict(norm=namespace_of(r['target_id']), target_id=r['target_id'], precedent_id=r['precedent_id'], origin='PHYSICAL_BASELINE')
                 for r in rows]
    base_rec = {r['precedent_id']: r['record'] for r in rows}
    reused = sorted(k for k in new_records if k in base_rec)
    prec = {**{k: v for k, v in new_records.items() if k not in base_rec}, **base_rec}       # a precedent already on the card keeps its record
    fichas = {k: v for k, v in new_fichas.items() if k not in card_fichas}
    files = P.package(base_rels + new_rels, prec, card_fichas, new_fichas=fichas, provisional_ids=provisional_ids, known_targets=known_targets)
    look1, recs1 = files[P.LAYER + '/JUR_LOOKUP.IDX'], files[P.LAYER + '/JURISPRUDENCIA.IDX']
    man = json.loads(files[P.LAYER + '/MULTINORM_MANIFEST.json'])
    pkg0, pkg1 = S.Package(look0, recs0, card_fichas), S.Package(look1, recs1, set(card_fichas) | {k.split('/')[-1] for k in files})
    keys0 = [l[:5] for l in pkg0.lookups]
    lost, changed_cf, lost_by_ns = [], [], collections.Counter()
    for k in keys0:
        old = pkg0.rows(*pkg0.exact(*k))
        hit = pkg1.exact(*k)
        new = pkg1.rows(*hit) if hit else []
        if new[:len(old)] != old:
            lost.append('|'.join(k))
            lost_by_ns[k[0]] += 1
        if k[0] != norm and new != old:
            changed_cf.append('|'.join(k))
    old_lines = collections.Counter(l for l in recs0.decode('utf-8').split('\n')[1:] if l)
    new_lines = collections.Counter(l for l in recs1.decode('utf-8').split('\n')[1:] if l)
    missing_lines = sum((old_lines - new_lines).values())
    vis = opened = back = 0
    labels = collections.Counter()
    for r in new_rels:
        _, art, par, inc, ali = P.query_key(r['target_id']).split('|')
        st = S.carregar(pkg1, probe_path, art, par, inc, ali)
        hit = [x for x in st['relations'] if x['arquivo'] == JT.ficha(r['precedent_id'])]
        vis += bool(hit) and st['branch'] == 'MULTINORMA'
        if hit:
            labels[hit[0]['label'].split(' ')[0]] += 1
            o = S.open_and_back(pkg1, st, st['relations'].index(hit[0]))
            opened += o['opened']
            back += S.carregar(pkg1, probe_path, art, par, inc, ali)['relations'] == st['relations']
    rep = dict(status='SIMULATION_ONLY', deployable=False, counts={n: (v['relations'], v['targets_with_j']) for n, v in man['norms'].items()},
               DUPLICATE_QUERY_KEYS=man['totals']['DUPLICATE_QUERY_KEYS'], BASELINE_RECORD_LINES_MISSING=missing_lines,
               BASELINE_KEYS=len(keys0), BASELINE_KEYS_NOT_PRESERVED=len(lost), lost_keys=lost[:10], lost_by_namespace=dict(lost_by_ns),
               OTHER_NORM_KEYS_CHANGED=len(changed_cf), other_norm_changed=changed_cf[:10], NEW_RELATIONS=len(new_rels),
               NEW_VISIBLE=f'{vis}/{len(new_rels)}', NEW_FICHA_OPEN=f'{opened}/{len(new_rels)}', NEW_BACK=f'{back}/{len(new_rels)}',
               labels=dict(sorted(labels.items())), OUTRO_LABELS=labels.get('OUTRO', 0), records_reused_from_card=reused,
               fichas_new=sorted(k.split('/')[-1] for k in files if k.startswith(P.CONTENT)), fichas_shared_across_norms=man['fichas_shared_across_norms'])
    return files, rep


# ---------------- factory-speed metric ----------------
def sloc(path, data_names=()):
    """(code lines, review-data lines) of a Python file: non-blank, non-comment, docstrings excluded; data = lines spanned by top-level
    assignments to the named tables (human review / dossier text), which are judgment, not engine code."""
    src = Path(path).read_text(encoding='utf-8')
    tree = ast.parse(src)
    skip, data = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body and isinstance(node.body[0], ast.Expr) and \
                isinstance(getattr(node.body[0], 'value', None), ast.Constant) and isinstance(node.body[0].value.value, str):
            skip.update(range(node.body[0].lineno, node.body[0].end_lineno + 1))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in data_names for t in node.targets):
            data.update(range(node.lineno, node.end_lineno + 1))
    lines = [i for i, l in enumerate(src.splitlines(), 1) if l.strip() and not l.strip().startswith('#') and i not in skip]
    return sum(1 for i in lines if i not in data), sum(1 for i in lines if i in data)


# ---------------- earlier ratification -> exclusions ----------------
def exclusions_from_ratification(rec, decisions, prefix, declined=None, stj_prec=None):
    """From a frozen ratification record (+ its decisions file): pending precedents, rejected precedents (the rejection reason is about the
    precedent), discovered targets the ratification moved away from, dossier options the user declined, and STJ themes whose súmula was
    decided on the same target. Returns (precedent exclusions, pair exclusions), each value = (code, note)."""
    dec = {f"{prefix}-{x['rank']:02d}": x for x in decisions}
    pexc, qexc, decided = {}, {}, collections.defaultdict(set)
    for it in rec['items']:
        x = dec[it['id']]
        decided[it['precedent']] |= set(it['final_targets']) | {x['discovered_target']}
        if it['human_state'].startswith('PENDING'):
            pexc[it['precedent']] = (f'{prefix}_PENDING', f"{it['id']} {it['human_state']} (reavaliar só com evidência oficial nova)")
        elif it['human_state'] == 'HUMAN_REJECTED_OR_NOT_APPROVED':
            pexc.setdefault(it['precedent'], (f'{prefix}_REJECTED_PRECEDENT', f"{it['id']} não aprovado; decisão equivalente vale para os demais alvos"))
        elif x['discovered_target'] not in it['final_targets']:
            qexc[(x['discovered_target'], it['precedent'])] = (f'{prefix}_DECIDED_TARGET_SET', f"{it['id']}: alvo descoberto realocado na ratificação")
    for k, v in (declined or {}).items():
        qexc[k] = (f'{prefix}_DECIDED_TARGET_SET', v)
    for e in (stj_prec or {}).get('entries', []):
        for n in re.findall(r'\d+', e['sumula_originada'] or ''):
            for t in e['targets_from_tese'] + e['targets_from_reference']:
                if t in decided.get(f'STJ:SUMULA:{n}', ()):
                    qexc[(t, e['id'])] = ('EQUIVALENT_SUMULA_DECIDED', f"{e['id']} originou a Súmula {n}/STJ, já decidida em {prefix} neste alvo")
    return pexc, qexc


# ---------------- automatic precedent record + ficha draft (simulation only) ----------------
def draft_record_and_ficha(x, batch):
    trib, klass, num = x['precedent'].split(':')[:3]
    head = f'SIMULAÇÃO — NÃO PUBLICADO ({batch}, aguardando ratificação)'
    if klass == 'SUMULA':
        rec = dict(tipo='sumula', tribunal=trib, numero=num, status='vigente', titulo=f'Súmula {num} {trib}', fonte=x['source']['url'])
        body = [f'SÚMULA {num} DO {trib}', f'TRIBUNAL: {trib}', head, f"ÓRGÃO JULGADOR / DECISÃO: {x['judgment']}", '', 'ENUNCIADO', x['evidence']]
    elif klass in STJ_TIPO:
        nome = 'Tema Repetitivo' if klass == 'REPETITIVO' else klass
        rec = dict(tipo=STJ_TIPO[klass], tribunal=trib, numero=num, status='tese_firmada_re_pendente' if 'RE Pendente' in x['status_text'] else
                   'tese_firmada', titulo=f'{nome} {num} {trib}', fonte=x['source'].get('page', x['source']['url']))
        body = [f'{nome.upper()} {num} DO {trib}', f'TRIBUNAL: {trib}', head, f"ÓRGÃO JULGADOR / JULGAMENTO: {x['judgment']}",
                f"SITUAÇÃO: {x['status_text']}", '', 'TESE FIRMADA', x['evidence']]
    elif klass == 'RG':
        rec = dict(tipo='repercussao_geral', tribunal=trib, numero=num, status='tese_fixada', titulo=f'Tema de Repercussão Geral {num}',
                   fonte=f'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={num}')
        body = [f'TEMA DE REPERCUSSÃO GERAL {num}', f'TRIBUNAL: {trib}', head, f"SITUAÇÃO: {x['status_text']}", '', 'TRECHO OFICIAL', x['evidence']]
    else:
        raise BatchError(f'NO_RECORD_RULE {x["precedent"]}')
    body += ['', 'FONTE OFICIAL'] + ([x['source']['page'], 'Dados abertos: ' + x['source']['url']] if x['source'].get('page') else [x['source']['url']])
    return rec, '\n'.join(body) + '\n'


# ---------------- renderers (same formats for every batch) ----------------
def _short(d):
    return d.replace('_RECOMMENDED', '')


def render_review(doc, title):
    m = doc['metrics']
    L = [f'# {title}', '', '```', f"LOTE = {doc['batch']} · NORMA = {doc['norm']} · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION "
         f"(human_approved = false)", ' · '.join(f'{k} = {v}' for k, v in m.items()), '```', '', '## Seleção', '', doc['selection']['rule'], '',
         '## Decisões', '', '| # | Canal | Tema | Precedente | Alvos descobertos | Temporalidade | Proposta | Alvos propostos | Grupo | Motivo |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for x in doc['decisions']:
        L.append(f"| {x['rank']} | {x['channel']} | {x['theme']} | {x['device_label']} | {', '.join(x['discovered_targets'])} | {x['temporal']} | "
                 f"**{_short(x['decision'])}** | {', '.join(x['proposed_targets']) or '—'} | {x['group']} | {x['motive']} |")
    L += ['', '## Interações com o CC-J1 (congelado; nada alterado)', '']
    L += [f"- {x['device_label']}: {x['CC_J1_INTERACTION']['kind']} — {x['CC_J1_INTERACTION']['note']}" for x in doc['decisions'] if x['CC_J1_INTERACTION']]
    L += ['', '## Notas do lote', ''] + [f'- **{k}**: {v}' for k, v in doc['notes'].items()]
    L += ['', 'Nenhuma decisão é HUMAN_APPROVED. A ratificação é do usuário.']
    return '\n'.join(L) + '\n'


def render_dossier(doc, title):
    by = collections.defaultdict(list)
    for x in doc['decisions']:
        by[x['group']].append(x)
    L = [f'# {title}', '', '```', f"GREEN = {len(by['GREEN'])} (SAFE_FOR_BLOCK_RATIFICATION, não ratificado) · YELLOW = {len(by['YELLOW'])} "
         f"(REVIEW_INDIVIDUALLY) · RED = {len(by['RED'])} (DO_NOT_RATIFY_NOW) · human_approved = 0", '```', '',
         'Critérios: GREEN = relação direta, atual, oficial, sem alerta; YELLOW = realocação, vários alvos, temporalidade, relação contextual, '
         'provisório ou dúvida jurídica; RED = falso positivo, superado, código errado, não material, duplicata ou não resolvido.', '',
         f"## GREEN ({len(by['GREEN'])})", '', '| ID | Precedente | Alvo | Risco | Motivo |', '|---|---|---|---|---|']
    L += [f"| {x['id']} | {x['device_label']} | {', '.join(x['proposed_targets'])} | {x['risk']} | {x['motive']} |" for x in by['GREEN']]
    L += ['', f"## YELLOW ({len(by['YELLOW'])})", '']
    for x in by['YELLOW']:
        pb, fav, risk, alt, rec = x['yellow']
        L += [f"### {x['id']} — {x['device_label']} ({_short(x['decision'])})", '', f"- **Alvo descoberto → proposto:** {', '.join(x['discovered_targets'])} → "
              f"{', '.join(x['proposed_targets'])}", f"- **Problema:** {pb}", f'- **A favor:** {fav}', f'- **Risco:** {risk}',
              f"- **Opções:** A — aprovar a proposta; B — {alt}; C — rejeitar; D — manter pendente.", f'- **Recomendação:** {rec}']
        if x['CC_J1_INTERACTION']:
            L.append(f"- **CC-J1:** {x['CC_J1_INTERACTION']['note']}")
        L.append('')
    L += [f"## RED ({len(by['RED'])})", '', '| ID | Precedente | Alvo descoberto | Proposta | Motivo | Reabrir se |', '|---|---|---|---|---|---|']
    L += [f"| {x['id']} | {x['device_label']} | {', '.join(x['discovered_targets'])} | {_short(x['decision'])} | {x['motive']} | {x['red_reopen']} |"
          for x in by['RED']]
    L += ['', 'Nada foi ratificado. A ratificação (em bloco do GREEN, individual do YELLOW) é do usuário.']
    return '\n'.join(L) + '\n'


def dossier_json(doc):
    return dict(schema_version=1, kind='RATIFICATION_DOSSIER', batch=doc['batch'], status='AWAITING_USER_RATIFICATION', human_approved=0,
                groups=dict(collections.Counter(x['group'] for x in doc['decisions'])),
                items=[{k: x[k] for k in ('id', 'precedent', 'device_label', 'device_type', 'group', 'risk', 'decision', 'discovered_targets',
                                          'proposed_targets', 'temporal', 'motive', 'yellow', 'red_reopen', 'CC_J1_INTERACTION', 'source')}
                       for x in doc['decisions']])
