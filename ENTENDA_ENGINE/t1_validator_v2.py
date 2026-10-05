"""ENTENDA-T1 validator v2 (standard A6): risk routing distilled from the human decisions of the Batch05 HIGH rounds.

Layer on top of the engine (entenda_engine.validate_explanation stays the contract) and of editorial_checks (findings + resolutions).
It never rewrites content and never changes review status: it classifies.

Severities:
  HARD_FAIL                    objective error; cannot be approved as is
  REVIEW_REQUIRED              human decision needed; route QUICK (localized, objective) or FULL (legal risk / external content)
  EDITORIAL_AUTO_FIX_ELIGIBLE  only micro-adjustments of the A6 policy (registered deviation; no change of meaning)
  INFO                         resolved / justified warning, known false positive, handled catalog topic

The detector does NOT replace legal review: it routes risk. Known false negatives are listed in the regression report.
"""
import json
import re
from pathlib import Path

import entenda_engine as E

HERE = Path(__file__).resolve().parent
CATALOG = HERE / 'editorial/T1_EXTERNAL_CATALOG.json'
KNOWN = HERE / 'editorial/T1_KNOWN_RESOLUTIONS.json'
CONFIG = HERE / 'editorial/T1_PIPELINE_CONFIG.json'
VERSION = 'T1_VALIDATOR_V2 (A6, 2026-10-04)'

BODY = ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')
NEG = re.compile(r'\b(não|nem|sem|nunca)\b[^.;:]{0,90}$', re.I)          # negation earlier in the same clause
FINALITY_IN_TEXT = re.compile(r'\bpara (?:[a-zà-ú]+(?:ar|er|ir)(?:-(?:lhe|lhes|se))?)\b', re.I)
INTERNAL_ID = re.compile(r'\b[A-Z0-9]{2,}_[A-Z0-9_]{2,}\b')
EXTERNAL_FACT = re.compile(r'(\bTemas? \d{2,4}\b|\bADI (?:nº )?\d|\bLei Complementar nº \d|\bLei nº \d|'
                           r'\bart\. ?\d+º?,? da (?:EC|Emenda Constitucional)\b|\b(?:EC|Emenda Constitucional nº) ?\d+/\d{4},? art\. ?\d+)', re.I)
A6_EFFECTIVE = '2026-10-04'        # approvals reviewed on/after this date are bound by the A6 provenance rule (Batch05 HIGH rounds and later)

# (code, route, sections, regex, negation_aware, snapshot_suppression, learned_from)
#   snapshot_suppression: 'SAME_PHRASE' -> drop when the matched phrase is in the Lei Seca; 'FINALITY' -> drop when the text has a finality clause;
#   'STEM' -> drop when the matched stem is in the Lei Seca
PATTERN_RULES = [
    ('TELEOLOGY_SPECULATIVE', 'QUICK', ('o_que_significa', 'exemplo_pratico', 'atencao'),
     r'\b(o objetivo [ée]|objetivo d[oa]s?|a finalidade [ée]|serve para|para evitar|evita(?:r|ndo)?|incentiv\w*|aproveitar o|a ideia [ée]|'
     r'a regra (?:dá|busca|quer)|isso adia|reduz(?:ir)? (?:os )?custos?|protege tamb[ée]m|'
     r'porque (?:o|a|os|as) [\wÀ-ÿ]+(?: (?:de|do|da) [\wÀ-ÿ]+)? (?:exige|exigem|requer|requerem|demanda|demandam))\b', False, 'FINALITY',
     'R01 37 XVI "aproveitar o profissional"; R02 38 V "evitar fragmentacao", 39 §4 "objetivo e transparencia", 39 §9; R03B §19 "incentivo", §20 custos; '
     'R-SANITY 38 II "porque o cargo de Prefeito exige dedicacao" (justificativa causal; 0 ocorrencias no restante do acervo)'),
    ('UNIVERSAL_CLAIM', 'QUICK', ('o_que_diz', 'o_que_significa', 'exemplo_pratico'),
     r'\b(todos os|todas as|todo servidor|todo ente|cada ente tem|s[óo] pode|somente pode|sempre|nunca|em nenhuma hip[óo]tese|'
     r'os demais agentes|qualquer atividade)\b', True, 'SAME_PHRASE',
     'R02 41 "so pode perder o cargo nas hipoteses do § 1º"; R03A 40 "todos os servidores", 40 §1º I "qualquer atividade"; R03B §11, §13, §20'),
    ('AUTOMATIC_CONSEQUENCE', 'QUICK', BODY,
     r'(automaticamente|como se n[ãa]o tivesse|pode ser exonerad\w*|buscar? a diferen[çc]a|continua(?:m)? com as regras anteriores)', True, None,
     'R02 41 §2 "como se nao tivesse saido", 41 §4 "pode ser exonerado"; R03A §2 "buscar a diferenca"; R03B §9, §14'),
    ('PERMISSION_NOT_IN_TEXT', 'QUICK', BODY, r'\bpode (?:ficar|ser) (?:abaixo|inferior|menor|reduzid\w*)', True, None,
     'R03B §7 "pode ficar abaixo do salario minimo"'),
    ('QUALIFIER_NOT_IN_TEXT', 'QUICK', ('o_que_diz', 'o_que_significa', 'atencao'), r'\b(subsidi[áa]ri\w*|omiss[ao]s?|lacunas?)\b', True, 'STEM',
     'R03B §12 "aplicacao subsidiaria ... quando o art. 40 e a lei do ente nao tratam"'),
    ('INTERPRETATION_AS_RULE', 'FULL', BODY,
     r'(leitura usual|entendimento (?:usual|majorit[áa]rio|dominante|predominante)|em geral se entende|costuma-se entender)', False, None,
     'R03B §18 "a leitura usual e"'),
    ('EXAMPLE_INVENTED_REQUIREMENT', 'QUICK', ('exemplo_pratico',),
     r'\b(?:analisa\w*|avalia\w*|considera\w*)\b[^.]{0,40}?\b(\w{5,}), (\w{5,}) e (\w{5,})|\bpromovid\w+ para (?:a|essa) vaga', False, 'STEM',
     'R02 41 §4 "assiduidade, produtividade e responsabilidade"; R02 41 §2 "promovida para essa vaga"'),
    ('LAW_STATUS_CLAIM', 'FULL', BODY + ('external_layer_notes',),
     r'(lei complementar|lei espec[íi]fica|lei federal|a lei)\b[^.]{0,80}\b(j[áa] (?:foi|existe|regulament\w*)|foi editada|est[áa] na camada|'
     r'regulamentou|que fixou)', False, None, 'R03A §1º II "a lei complementar que fixou"; R03B §22 "esta na camada de leis correlatas"'),
    ('OUTDATED_CONTROVERSY', 'FULL', ('o_que_diz', 'o_que_significa', 'atencao'),
     r'(qual reda[çc][ãa]o produz efeitos|hist[óo]rico constitucional complexo|ainda (?:se )?discute|n[ãa]o est[áa] pacificad\w*)', False, None,
     'R02 39 "qual redacao produz efeitos"'),
]
_COMPILED = [(c, r, s, re.compile(x, re.I), n, sup, lf) for c, r, s, x, n, sup, lf in PATTERN_RULES]
QUICK_CODES = {c for c, r, *_ in PATTERN_RULES if r == 'QUICK'} | {'EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE', 'EXCEPTION_OR_RESSALVA_DROPPED',
                                                                   'EXHAUSTIVE_ENUMERATION_RISK'}

# micro-adjustment policy A6 (item numbers as approved in round 3A)
MICRO_POLICY = ['sigla -> nome por extenso', 'artigo/preposicao/ordem sintatica/sinonimo estritamente equivalente contra copia literal',
                'remocao de termo redundante do glossario acima de 5', 'ajuste gramatical exigido pelo validador',
                'substituicao de identificador interno por expressao para o usuario final']
FUNCTION_SWAPS = [('dos ', 'para os '), ('das ', 'nas '), (' de ', ' da '), (' de ', ' do '), (' do ', ' de '), (' da ', ' de '),
                  (' aos ', ' a '), (' e abrange', ', abrangendo'), (' integrado ', ' composto ')]
SIGLAS = {'STF': 'Supremo Tribunal Federal', 'STJ': 'Superior Tribunal de Justiça', 'TST': 'Tribunal Superior do Trabalho',
          'TSE': 'Tribunal Superior Eleitoral', 'TCU': 'Tribunal de Contas da União'}


def load_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def load_catalog(path=CATALOG):
    doc = load_json(path)
    for e in doc['entries']:
        for k in ('trigger', 'contradicts', 'open_framing', 'context'):
            e['_' + k] = re.compile(e[k], re.I) if e.get(k) else None
    return doc


def _sentences(text):
    return [s for s in re.split(r'(?<=[.;:!?])\s+|\n', text or '') if s.strip()]


def _texts(rec, sections):
    c = rec['content']
    for sec in sections:
        if sec == 'external_layer_notes':
            for n in rec.get('external_layer_notes', []):
                yield sec, n
        elif sec == 'palavras_dificeis':
            for t in c['palavras_dificeis']:
                yield sec, f"{t['termo']}: {t['explicacao']}"
        else:
            yield sec, c.get(sec) or ''


def _f(code, severity, route, section='*', match='', sentence='', detail='', rule=None):
    return dict(code=code, severity=severity, route=route, section=section, match=match, sentence=sentence[:160], detail=detail,
                **({'learned_from': rule} if rule else {}))


def _provenance(rec):
    return (rec.get('human_review') or {}).get('content_provenance') or []


def _a6_approved(rec):
    hr = rec.get('human_review') or {}
    return rec.get('review_status') == 'HUMAN_APPROVED_T1' and str(hr.get('reviewed_on', '')) >= A6_EFFECTIVE


def pattern_findings(rec):
    snap = rec['source']['source_text_snapshot'].lower()
    out = []
    for code, route, secs, rx, neg, sup, lf in _COMPILED:
        for sec, text in _texts(rec, secs):
            for s in _sentences(text):
                for m in rx.finditer(s):
                    if neg and NEG.search(s[:m.start()]):
                        continue
                    if sup == 'SAME_PHRASE' and m.group(0).lower() in snap:
                        continue
                    if sup == 'FINALITY' and FINALITY_IN_TEXT.search(snap):
                        continue
                    if sup == 'STEM':
                        words = [g for g in m.groups() if g] or [m.group(0)]
                        if any(w.lower()[:6] in snap for w in words):
                            continue
                    out.append(_f(code, 'REVIEW_REQUIRED', route, sec, m.group(0), s, rule=lf))
    return out


def catalog_findings(rec, catalog):
    tid = rec['target_id']
    covered = set(rec['granularity'].get('covered_targets', []))
    body = '\n'.join(t for _, t in _texts(rec, BODY + ('palavras_dificeis',)))
    allt = (body + '\n' + '\n'.join(rec.get('external_layer_notes', []))).lower()
    out = []
    for e in catalog['entries']:
        linked = any(r in allt for r in e['refs'])
        member = tid in e['applies_to_targets'] or bool(covered & set(e['applies_to_targets']))
        ok = lambda s: not e['_context'] or e['_context'].search(s)  # noqa: E731
        trig = next((m for s in _sentences(body) if ok(s) for m in [e['_trigger'].search(s)] if m), None) if e['_trigger'] else None
        if e['_open_framing']:
            for s in _sentences(body):
                m = e['_open_framing'].search(s)
                if m:
                    out.append(_f('RESOLVED_TREATED_AS_OPEN', 'REVIEW_REQUIRED', 'FULL', '*', m.group(0), s, e['id']))
        if e['_contradicts']:
            for sec, text in _texts(rec, BODY + ('palavras_dificeis', 'external_layer_notes')):
                for s in _sentences(text):
                    m = e['_contradicts'].search(s)
                    if m and ok(s) and not NEG.search(s[:m.start()]):
                        out.append(_f('CATALOG_CONTRADICTION', 'REVIEW_REQUIRED', 'FULL', sec, m.group(0), s, e['id']))
        if (member or trig) and not linked and e['placement'] != 'CORE_ALLOWED':
            out.append(_f('CATALOG_LINK_MISSING', 'REVIEW_REQUIRED', 'FULL', '*', trig.group(0) if trig else '', '',
                          f"{e['id']} ({'target catalogado' if member else 'tema detectado no corpo'})"))
        elif (member or trig) and linked:
            out.append(_f('CATALOG_TOPIC_HANDLED', 'INFO', None, '*', '', '', e['id']))
    return out


def provenance_findings(rec):
    out = []
    texts = list(_texts(rec, BODY + ('palavras_dificeis', 'external_layer_notes')))
    hits = [(sec, m.group(0), s) for sec, t in texts for s in _sentences(t) for m in EXTERNAL_FACT.finditer(s)]
    snap = rec['source']['source_text_snapshot'].lower()
    hits = [h for h in hits if h[1].lower() not in snap]
    if not hits:
        return out
    if _provenance(rec):
        return [_f('EXTERNAL_FACT_WITH_PROVENANCE', 'INFO', None, h[0], h[1], h[2]) for h in hits]
    for sec, m, s in hits:
        if _a6_approved(rec):
            out.append(_f('EXTERNAL_FACT_NO_PROVENANCE', 'HARD_FAIL', None, sec, m, s, 'aprovado sob A6 sem content_provenance'))
        elif rec.get('review_status') == 'HUMAN_APPROVED_T1':
            out.append(_f('LEGACY_EXTERNAL_FACT', 'INFO', None, sec, m, s, 'aprovado antes do A6 (sem campo de proveniencia)'))
        else:
            out.append(_f('EXTERNAL_FACT_NEEDS_PROVENANCE', 'REVIEW_REQUIRED', 'FULL', sec, m, s))
    return out


def hard_findings(rec, ctx):
    out = []
    try:
        E.validate_explanation(rec, ctx)
    except E.EntendaError as ex:
        out.append(_f('ENGINE_CONTRACT', 'HARD_FAIL', None, detail=str(ex)))
    s = rec['source']
    current = ctx.snapshot(rec['target_id'], rec['granularity'].get('covered_targets', []))
    if s.get('source_text_snapshot') != current:
        out.append(_f('LEI_SECA_DIVERGENCE', 'HARD_FAIL', None, detail='snapshot != runtime atual (STALE)'))
    for sec, t in _texts(rec, BODY + ('palavras_dificeis',)):
        for m in INTERNAL_ID.finditer(t):
            out.append(_f('INTERNAL_IDENTIFIER', 'HARD_FAIL', None, sec, m.group(0), t[max(0, m.start() - 60):m.end() + 40]))
    return out


def autofix_findings(rec, lint_rows):
    out = []
    for w in lint_rows:
        if w['code'] == 'NEAR_COPY_OF_OFFICIAL_TEXT':
            out.append(_f('NEAR_COPY_MICROFIX', 'EDITORIAL_AUTO_FIX_ELIGIBLE', None, w['section'], w['detail'], detail='politica A6 item 2'))
    for sec, t in _texts(rec, BODY):
        for sig in SIGLAS:
            if re.search(rf'\b{sig}\b', t):
                out.append(_f('SIGLA_EXPANSION', 'EDITORIAL_AUTO_FIX_ELIGIBLE', None, sec, sig, detail='politica A6 item 1'))
    return out


def lint_findings(lint_rows, editorial_rows):
    """Engine lint and editorial_checks: resolved/soft -> INFO; an unresolved editorial_checks finding -> REVIEW (QUICK)."""
    out = []
    for f in editorial_rows:
        if f.get('resolution'):
            out.append(_f('EDITORIAL_CHECK_RESOLVED', 'INFO', None, f['section'], f['code'], detail=f['resolution'][:120]))
        else:
            out.append(_f('EDITORIAL_CHECK_UNRESOLVED', 'REVIEW_REQUIRED', 'QUICK', f['section'], f['code'], detail=f['detail'][:120]))
    for w in lint_rows:
        if w['code'] != 'NEAR_COPY_OF_OFFICIAL_TEXT':
            out.append(_f('LINT_' + w['code'], 'INFO', None, w['section'], w['detail'][:60]))
    return out


def apply_known(rec, findings, known):
    """Known false positives / human-approved wording (explanation-scoped) -> INFO with the registered justification."""
    reg = known.get('resolutions', {}).get(rec['explanation_id'], {})
    for f in findings:
        if f['severity'] == 'REVIEW_REQUIRED':
            why = reg.get(f"{f['code']}:{f['match'].lower()}") or reg.get(f['code'])
            if why:
                f.update(severity='INFO', route=None, known_resolution=why)
    return findings


# ---------------------------------------------------------------- semantic rules (Batch05 final calibration, generalizable)

CITE = re.compile(r'\bart\. (\d+(?:-[A-Z])?)(?:, (§ \d+º?|[IVXL]+)\b)?|\binciso ([IVXL]+)\b|(?<![\w,] )§ (\d+)º?(?!\S*-)')
# a condition attributed to the subject ("deve ser compatível", "deve ter", "precisa possuir"); participles ("deve ser divulgado") are not
NORMATIVE = re.compile(r'\b(?:deve|devem|precisa|precisam) (?:ser|ter|possuir|estar) (?:uma? |o |a |os |as )?'
                       r'(?![\wÀ-ÿ]*(?:ad[oa]s?|id[oa]s?|st[oa]s?|it[oa]s?|ert[oa]s?)\b)[\wÀ-ÿ]{4,}', re.I)
EXCEPTION_IN_TEXT = re.compile(r'\b(exceto|salvo|com exceção de)\s+([^;,.:]+)', re.I)
GENERALIZING = re.compile(r'\b(não perde|todos|todas|qualquer|sempre|integralmente)\b', re.I)
CLOSED_LIST = re.compile(r'\b[\wÀ-ÿ]+s(?: [\wÀ-ÿ]+)? são (?:os|as)(?: de| do| da| dos| das)? ([A-ZÁÉÍÓÚ][\wÀ-ÿ]+(?: [A-ZÁÉÍÓÚ][\wÀ-ÿ]+)?)'
                         r'((?:, [A-ZÁÉÍÓÚ][\wÀ-ÿ]+(?: [A-ZÁÉÍÓÚ][\wÀ-ÿ]+)?)*) e (?:os |as |o |a )?(?:de |do |da )?([A-ZÁÉÍÓÚ][\wÀ-ÿ]+)')
SEMANTIC_RULES = [
    ('EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE', 'QUICK',
     'R-FINAL CF88:ART.37:INC.VIII v1 ("a deficiencia deve ser compativel com as atribuicoes do cargo": condicao fora do inciso, sem proveniencia)'),
    ('EXCEPTION_OR_RESSALVA_DROPPED', 'QUICK',
     'R-FINAL CF88:ART.38:INC.IV v1 ("nao perde tempo de carreira" apagava a ressalva da promocao por merecimento)'),
    ('EXHAUSTIVE_ENUMERATION_RISK', 'QUICK', 'R-FINAL CF88:ART.38:INC.I v1 ("Mandatos federais sao os de Deputado Federal e Senador")'),
]
SEMANTIC_LEARNED = {c: lf for c, _, lf in SEMANTIC_RULES}


def _stems(text, n=6, minlen=7):
    return {w.lower()[:n] for w in E.words(text) if len(w) >= minlen}


def cited_targets(rec, ctx):
    """Runtime devices cited in the explanation body (art. N, § N, inciso N)."""
    art = rec['target_id'].split(':')[1]
    out = []
    body = ' '.join(rec['content'][k] or '' for k in BODY)
    for m in CITE.finditer(body):
        if m.group(1):
            t = f"CF88:ART.{m.group(1)}" + (f":PAR.{re.sub(r'[^0-9]', '', m.group(2))}" if m.group(2) and m.group(2).startswith('§')
                                           else f":INC.{m.group(2)}" if m.group(2) else '')
        elif m.group(3):
            t = f'CF88:{art}:INC.{m.group(3)}'
        else:
            t = f'CF88:{art}:PAR.{m.group(4)}'
        if t != rec['target_id'] and t not in out and t in ctx.text:
            out.append(t)
    return out


def semantic_findings(rec, ctx):
    out = []
    snap = rec['source']['source_text_snapshot']
    c = rec['content']
    # A. normative condition not grounded in the target, the cited runtime context or a registered provenance
    if not _provenance(rec):
        ground = snap.lower() + ' ' + ' '.join(ctx.text[t] for t in cited_targets(rec, ctx)).lower()
        gst = {w.lower()[:6] for w in E.words(ground) if len(w) >= 6}
        for sec in ('o_que_diz', 'o_que_significa', 'atencao'):
            for s in _sentences(c.get(sec) or ''):
                m = NORMATIVE.search(s)
                if not m or NEG.search(s[:m.start()]):
                    continue
                missing = sorted(st for st in _stems(s[m.start():]) if st not in gst)
                if len(missing) >= 2:
                    out.append(_f('EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE', 'REVIEW_REQUIRED', 'QUICK', sec, m.group(0), s,
                                  'termos fora da Lei Seca/contexto citado: ' + ', '.join(missing[:4]),
                                  SEMANTIC_LEARNED['EXTERNAL_NORMATIVE_CLAIM_WITHOUT_PROVENANCE']))
    # B. express exception of the text dropped where the explanation restates the rule in general terms
    for line in snap.split('\n'):
        txt = line.split('\t', 1)[-1]
        for m in EXCEPTION_IN_TEXT.finditer(txt):
            exc = [w for w in E.words(m.group(2)) if len(w) >= 6]
            if not exc:
                continue
            key = max(exc, key=len).lower()[:5]
            rule = {w.lower()[:5] for w in E.words(txt[:m.start()]) if len(w) >= 5}
            for sec in ('o_que_significa', 'exemplo_pratico'):
                for para in (c.get(sec) or '').split('\n'):
                    pw = {w.lower()[:5] for w in E.words(para) if len(w) >= 5}
                    g = GENERALIZING.search(para)
                    if g and len(rule & pw) >= 2 and key not in pw:
                        out.append(_f('EXCEPTION_OR_RESSALVA_DROPPED', 'REVIEW_REQUIRED', 'QUICK', sec, g.group(0), para,
                                      f'ressalva do texto: "{m.group(0)[:60]}"', SEMANTIC_LEARNED['EXCEPTION_OR_RESSALVA_DROPPED']))
    # C. examples presented as a closed list without support in the text
    low = snap.lower()
    for sec in ('o_que_diz', 'o_que_significa'):
        for s in _sentences(c.get(sec) or ''):
            if re.search(r'\b(como|por exemplo|entre outr|exemplos?)\b', s, re.I):
                continue
            m = CLOSED_LIST.search(s)
            if m:
                items = [m.group(1), m.group(3)] + [x.strip() for x in (m.group(2) or '').split(',') if x.strip()]
                if not all(i.lower() in low for i in items):
                    out.append(_f('EXHAUSTIVE_ENUMERATION_RISK', 'REVIEW_REQUIRED', 'QUICK', sec, m.group(0)[:60], s,
                                  'lista apresentada como fechada sem respaldo no texto', SEMANTIC_LEARNED['EXHAUSTIVE_ENUMERATION_RISK']))
    return out


def validate(rec, ctx, catalog, known=None, lint_rows=(), editorial_rows=()):
    findings = hard_findings(rec, ctx) + pattern_findings(rec) + semantic_findings(rec, ctx) + catalog_findings(rec, catalog) + provenance_findings(rec)
    findings += autofix_findings(rec, lint_rows) + lint_findings(lint_rows, editorial_rows)
    return apply_known(rec, findings, known or {})


def route(findings, risk):
    """A CLEAN_LOW · B CLEAN_MEDIUM · C QUICK_REVIEW · D FULL_HUMAN_REVIEW · E HARD_FAIL (HIGH without findings still goes to D)."""
    if any(f['severity'] == 'HARD_FAIL' for f in findings):
        return 'E_HARD_FAIL'
    rev = [f for f in findings if f['severity'] == 'REVIEW_REQUIRED']
    if any(f['route'] == 'FULL' for f in rev) or len({f['code'] for f in rev}) > 2 or risk == 'HIGH':
        return 'D_FULL_HUMAN_REVIEW'
    if rev:
        return 'C_QUICK_REVIEW'
    return 'A_CLEAN_LOW' if risk == 'LOW' else 'B_CLEAN_MEDIUM'


# ---------------------------------------------------------------- micro-auto (suggestion only; applying is a registered deviation)

def copy_runs(text, snapshot, n=10):
    ws = [w.lower() for w in E.words(text)]
    src = E._ngrams([w.lower() for w in E.words(snapshot)], n + 1)
    return [' '.join(ws[i:i + n + 1]) for i in range(len(ws) - n) if tuple(ws[i:i + n + 1]) in src]


def suggest_copy_microfix(text, snapshot, n=10):
    """Smallest function-word swap that removes every >n-word copy run. Returns (before, after) or None; never applied here."""
    if not copy_runs(text, snapshot, n):
        return None
    for a, b in FUNCTION_SWAPS:
        start = 0
        while True:
            i = text.find(a, start)
            if i < 0:
                break
            cand = text[:i] + b + text[i + len(a):]
            if not copy_runs(cand, snapshot, n):
                lo, hi = max(0, i - 25), min(len(text), i + len(a) + 25)
                return text[lo:hi], cand[lo:hi + len(b) - len(a)]
            start = i + 1
    return None


# ---------------------------------------------------------------- version chain (immutability)

def version_chain_findings(records, previous=()):
    """Stamped versions are immutable; RETIRED points to the current version of the same key; one ACTIVE per key."""
    out = []
    prev = {r['explanation_id']: r for r in previous}
    by_id = {r['explanation_id']: r for r in records}
    active = {}
    for r in records:
        p = prev.get(r['explanation_id'])
        if p and (p['content'] != r['content'] or p['external_layer_notes'] != r['external_layer_notes']):
            out.append(_f('VERSION_MUTATION', 'HARD_FAIL', None, detail=r['explanation_id']))
        if r['status'] == 'ACTIVE':
            if r['explanation_key'] in active:
                out.append(_f('DUPLICATE_ACTIVE', 'HARD_FAIL', None, detail=r['explanation_key']))
            active[r['explanation_key']] = r
    for r in records:
        if r['status'] == 'RETIRED':
            a = active.get(r['explanation_key'])
            if not a or r.get('superseded_by') != a['explanation_id'] or r['editorial_version'] >= a['editorial_version'] \
                    or r['superseded_by'] not in by_id:
                out.append(_f('VERSION_CHAIN_BROKEN', 'HARD_FAIL', None, detail=r['explanation_id']))
    return out
