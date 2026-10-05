"""ENTENDA-T1 validator v3: generalizable checks added during the Batch06 scale recalibration, layered on validator v2.

v2 (t1_validator_v2.py) stays frozen for the approved batches (Batch05 regression and calibration keep their results). v3 = v2 findings
+ general false-positive refinements + new deterministic detectors. It never rewrites content and never changes review status.

Refinements of v2 pattern rules (general, never per target):
  TELEOLOGY_SPECULATIVE "incentiv*"   dropped when the stem is a noun of the article's own Lei Seca, or designates subject matter
                                       ("de incentivos", "sobre incentivos"); kept when it characterizes the function of the rule
  UNIVERSAL_CLAIM                      dropped when the sentence reproduces an explicit quorum/condition of the text: fraction or majority
                                       of the text in the sentence, "cada <noun>" of the text for "todos os <noun>", "somente/so" in the
                                       text for "so pode", a 3-word run of the text after the quantifier, or the same phrase in the article
  AUTOMATIC_CONSEQUENCE                dropped when the article text itself states the automatic consequence ("automaticamente",
                                       "ad nutum"/"demissiveis" for exoneration)
  EXTERNAL_FACT_*                      match widened to the full identification ("Lei Complementar nº 78, de 1993"); a fact only in the
                                       external layer notes is routed QUICK (the T1 core does not depend on it)

New detectors (REVIEW_REQUIRED unless stated):
  NUMBER_NOT_IN_TEXT               a quantity (digits, words, fractions, percentages) in O QUE DIZ / O QUE SIGNIFICA / ATENCAO that the Lei
                                   Seca of the record, its article or the cited runtime devices do not contain (example: "54 dos 81")
  EXAMPLE_NUMBER_NOT_IN_TEXT       same inside EXEMPLO PRATICO: INFO (hypothetical figures are allowed; shown in the packet warnings)
  RESSALVA_OMITTED_IN_SUMMARY      a covered device (own text, OVERVIEW subtree, BLOCK siblings) has "salvo/exceto/ressalvado/sem
                                   prejuizo de/com excecao de"; the draft restates that device but no sentence carries the exception
  LIST_ITEM_POSSIBLY_DROPPED       the draft paraphrases a constitutional list (>= 60% of the items or elements recognized) and one item
                                   or coordinated element has no trace; skipped when the draft says the list is selective ("entre elas")
  EXTERNAL_NORMATIVE_CONTENT_CLAIM a law/regimento/foreign article "preve/estabelece/determina/dispoe/fixa/define..." something, and the
                                   content is not in the snapshot, the T1 catalog, the relations pin or registered provenance
  HISTORICAL_CLAIM_UNVERIFIED      a statement about previous wording/regime ("antes da Emenda", "materiais anteriores") not supported by
                                   the vigency annotations of the target plan
  CONDITION_NOT_IN_TEXT            "desde que / contanto que / so se" introduces a condition whose terms are not in the Lei Seca
  SEMANTIC_AMBIGUITY_REVIEW_REQUIRED a registered ambiguous phrase (editorial/T1_SEMANTIC_AMBIGUITY_REGISTRY.json) is paraphrased instead
                                   of being quoted, i.e. the draft resolves the ambiguity by itself (FULL)
Interpretive signals (input of t1_risk.assess, not findings): jurisprudence REQUIRED_FOR_CORRECTNESS vs CONTEXT_ONLY, controversy, ambiguity.
Known limits: listed in LIMITS (copied into the batch reports).
"""
import json
import re
from pathlib import Path

import entenda_engine as E
import t1_validator_v2 as V

VERSION = 'T1_VALIDATOR_V3 (A6 + recalibracao Batch06, 2026-10-05)'
HERE = Path(__file__).resolve().parent
AMBIGUITY_REGISTRY = HERE / 'editorial/T1_SEMANTIC_AMBIGUITY_REGISTRY.json'
QUICK_V3 = {'NUMBER_NOT_IN_TEXT', 'RESSALVA_OMITTED_IN_SUMMARY', 'LIST_ITEM_POSSIBLY_DROPPED', 'HISTORICAL_CLAIM_UNVERIFIED', 'CONDITION_NOT_IN_TEXT'}
LIMITS = [
    'NUMBER_NOT_IN_TEXT compara quantidades, nao o sentido: um numero correto do texto usado no lugar errado passa; numeros por extenso '
    'so sao lidos em formas cardinais (um..mil) e fracoes (terco, quinto, quarto, metade, decimo); ordinais e datas ficam fora.',
    'RESSALVA_OMITTED_IN_SUMMARY reconhece que a explicacao "fala" de um dispositivo por radicais compartilhados (>= 2); parafrase com '
    'vocabulario totalmente diferente nao e reconhecida (falso negativo), e dispositivo com explicacao propria no lote nao e cobrado.',
    'LIST_ITEM_POSSIBLY_DROPPED usa radicais distintivos de cada item; sinonimos escapam (falso positivo) e omissao em lista curta (< 3 '
    'itens) nao e verificada. Listas declaradas seletivas ("entre elas", "por exemplo") nao sao cobradas.',
    'EXTERNAL_NORMATIVE_CONTENT_CLAIM depende de verbo de afirmacao normativa perto da referencia; afirmacao implicita sobre lei externa '
    'sem esse verbo nao e detectada. Remissao a artigo da propria CF presente no runtime e tratada como ancorada (o pacote D lista o texto).',
    'A distincao JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS x CONTEXT_ONLY le os marcadores de dependencia interpretativa que o proprio draft '
    'escreve; jurisprudencia necessaria e nao sinalizada pelo draft so e pega quando ha nota da camada e condicao sem base no texto.',
    'Nenhum check interpreta juridicamente o dispositivo: eles roteiam risco para revisao humana.',
]

NUM_UNITS = {'um': 1, 'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 'tres': 3, 'quatro': 4, 'cinco': 5, 'seis': 6, 'sete': 7, 'oito': 8,
             'nove': 9, 'dez': 10, 'onze': 11, 'doze': 12, 'treze': 13, 'quatorze': 14, 'catorze': 14, 'quinze': 15, 'dezesseis': 16,
             'dezessete': 17, 'dezoito': 18, 'dezenove': 19, 'vinte': 20, 'trinta': 30, 'quarenta': 40, 'cinquenta': 50, 'cinqüenta': 50,
             'sessenta': 60, 'setenta': 70, 'oitenta': 80, 'noventa': 90, 'cem': 100, 'cento': 100, 'duzentos': 200, 'duzentas': 200,
             'trezentos': 300, 'trezentas': 300, 'quatrocentos': 400, 'quinhentos': 500, 'seiscentos': 600, 'setecentos': 700,
             'oitocentos': 800, 'novecentos': 900}
FRACTIONS = {'terço': 3, 'terços': 3, 'quinto': 5, 'quintos': 5, 'quarto': 4, 'quartos': 4, 'décimo': 10, 'décimos': 10, 'sexto': 6, 'sextos': 6}
WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]+|\d+(?:[.,]\d+)*|%|§|º")
REF_WORDS = {'art', 'arts', 'artigo', 'artigos', '§', '§§', 'inciso', 'incisos', 'alínea', 'nº', 'n', 'lei', 'emenda', 'ec', 'parágrafo'}
MONTHS = ('janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro')
EXCEPTION_MARK = re.compile(r'\b(salvo|exceto|ressalvad[oa]s?|ressalva|sem preju[íi]zo d[aeo]s?|com exce[çc][ãa]o d[aeo]s?|excetuad[oa]s?)\b', re.I)
EXCEPTION_IN_DRAFT = re.compile(r'\b(salvo|exceto|ressalv\w*|exce[çc][ãa]o|exce[çc][õo]es|sem preju[íi]zo|desde que|n[ãa]o se aplica|'
                                r'n[ãa]o alcan[çc]a|fora (?:dess|dest)\w+|menos)\b', re.I)
SELECTIVE = re.compile(r'\b(entre (?:elas|eles|outr\w+)|por exemplo|como,|destacam-se|principais|algumas|alguns)\b', re.I)
STOP_STEMS = {'consti', 'nacion', 'congre', 'federa', 'repúbl', 'presid', 'dispos', 'previs', 'respec', 'termos', 'estado', 'estados',
              'membro', 'membros', 'artigo', 'inciso', 'parágr', 'caput', 'quando', 'sobre', 'também', 'qualqu', 'demais', 'outras',
              'outros', 'seguin', 'mesmo', 'mesma', 'deverá', 'poderá', 'serão', 'nenhum', 'compet', 'matéri'}
EXT_REF = (r'(Lei Complementar nº [\d.]+(?:, de \d{4})?|Lei nº [\d.]+(?:, de \d{4})?|[Rr]egimentos? [Ii]ntern\w+|[Rr]egimento|'
           r'Código [A-ZÁÉÍÓÚ]\w+(?: [A-ZÁÉÍÓÚ]\w+)?|Decreto(?:-Lei)? nº [\d.]+|Resolução nº [\d.]+|lei (?:especial|própria|federal|ordinária) '
           r'(?:que|sobre)[^,.;]{0,40}|art\. \d+[º°]?(?:-[A-Z])?(?:, [^,.;]{1,12})? d[ao] (?:Lei|ADCT|Ato das Disposições|Código|Regimento)[^,.;]*)')
CLAIM_VERB = (r'(prevê|preveem|estabelece|estabelecem|determina|determinam|dispõe|dispõem|fixa|fixam|define|definem|regula|regulam|'
              r'disciplina|disciplinam|exige|exigem|garante|asseguram?|proíbe|proíbem|autoriza|autorizam)')
EXT_CLAIM = re.compile(EXT_REF + r'[^.;]{0,40}?\b' + CLAIM_VERB + r'\b|\b(?:segundo|conforme|nos termos d[ao]) ' + EXT_REF)
HISTORICAL = re.compile(r'(antes da (?:Emenda Constitucional|EC)\b[^.;]*|materiais (?:antigos|anteriores)[^.;]*|reda[çc][ãa]o anterior[^.;]*|'
                        r'texto original da Constitui[^.;]*|reda[çc][ãa]o original[^.;]*|regime anterior[^.;]*|vem, em grande parte, da Emenda[^.;]*|'
                        r'(?:foi|foram) (?:incluíd|alterad|acrescentad)\w* pela (?:Emenda Constitucional|EC)[^.;]*|'
                        r'(?:incluíd|alterad)\w* (?:em|no ano de) \d{4}[^.;]*)', re.I)
EC_NUM = re.compile(r'(?:Emenda Constitucional|EC)\s*(?:n[º.o]*\s*)?(\d+)', re.I)
CONDITION = re.compile(r'\b(desde que|contanto que|s[óo] se|somente se|apenas se)\b([^.;:]+)', re.I)
JURIS_NOTE = re.compile(r'JURISPRUD', re.I)
JURIS_REQUIRED = re.compile(r'(n[ãa]o deve(?:m)? ser deduzid\w*|n[ãa]o se deve concluir apenas|delimitad[oa]s? pela interpreta[çc][ãa]o|'
                            r'(?:é|são|foi|foram) definid[oa]s? pela interpreta[çc][ãa]o|leitura isolada)', re.I)
CONTROVERSY = re.compile(r'(objeto de debate|controv[ée]rs\w*|gera(?:m)? d[úu]vidas|n[ãa]o est[áa] pacificad\w*|ainda (?:se )?discute)', re.I)
AMBIGUITY = re.compile(r'(n[ãa]o (?:é|est[áa]) definid[oa] nesta explica[çc][ãa]o|depende de verifica[çc][ãa]o|exige(?:m)? verifica[çc][ãa]o|'
                       r'exige(?:m)? revis[ãa]o humana|ambiguidade|n[ãa]o explicita a quais)', re.I)
INTERPRETIVE_QUESTION = re.compile(r'(?:tema|temas|quest[ãa]o|quest[õo]es) (?:tratad\w+ pela |de )interpreta[çc][ãa]o constitucional', re.I)


def _f(code, severity, route, section='*', match='', sentence='', detail=''):
    return V._f(code, severity, route, section, match, sentence, detail)


def _fold(w):
    return w.lower().replace('ü', 'u')


def _stems(text, n=6, minlen=6):
    return {_fold(w)[:n] for w in E.words(text) if len(w) >= minlen} - STOP_STEMS


_ABBREV = re.compile(r'(?:\b(?:arts?|inc|incs|al|n|p|ss?)\.|§|nº)$', re.I)


def sentences(text):
    """Sentence split that does not cut after "art.", "§", "nº" (so device references stay with their numbers)."""
    out = []
    for part in re.split(r'(?<=[.;:!?])\s+|\n', text or ''):
        if out and _ABBREV.search(out[-1]):
            out[-1] += ' ' + part
        elif part.strip():
            out.append(part)
    return out


_sentences = sentences


# ---------------------------------------------------------------- quantities

UNITS = re.compile(r'^(dias?|horas?|meses|m[êe]s|anos?|sess[õo]es|sess[ãa]o|turnos?|votos?|membros?|deputad\w*|senador\w*|vereador\w*|'
                   r'conselheir\w*|ministr\w*|cadeiras?|representantes?|legislaturas?|vezes|presentes|hectares?|cidad[ãa]os|eleitores|'
                   r'estados|munic[íi]pios|partidos|assinaturas|subscritores)$', re.I)
CONNECT = {'e', 'a', 'ou', 'º', '§', '§§'}


def _tokens(text):
    return [m.group(0) for m in re.finditer(r"[A-Za-zÀ-ÖØ-öø-ÿ]+|\d+(?:[.,]\d+)*|%|§|º|[,;:.()]", text or '')]


def quantities(text, units=False):
    """Quantities in text: ('n', '45'), ('frac', '2/3'), ('pct', '5'). Digits always; number words only with a legal unit after them
    (dias, sessoes, turnos, anos, votos, membros ...), a fraction or a percentage. Device references (art./arts./§/inciso/nº/EC and
    their chains "arts. 45 e 46", "§§ 2º e 3º"), years and dates are skipped. units=True returns (kind, value, unit)."""
    toks = _tokens(text)
    low = [t.lower() for t in toks]
    out, i, chain = set(), 0, False
    while i < len(low):
        t = low[i]
        prev = low[i - 1] if i else ''
        prev2 = low[i - 2] if i > 1 else ''
        if re.fullmatch(r'\d+(?:[.,]\d+)*', t):
            nxt = low[i + 1] if i + 1 < len(low) else ''
            unit = nxt if UNITS.match(nxt) else (low[i + 2] if i + 2 < len(low) and UNITS.match(low[i + 2]) and nxt in ('de',) else '')
            val = t.replace('.', '').replace(',', '.')
            is_ref = (prev in REF_WORDS or prev2 in REF_WORDS and prev in ('º', '.', ',')) and not unit
            is_ref = is_ref or (chain and prev in CONNECT | {','}) and not unit
            is_date = (nxt == 'de' and i + 2 < len(low) and low[i + 2] in MONTHS) or (nxt == 'º' and i + 2 < len(low) and low[i + 2] == 'de'
                                                                                    and i + 3 < len(low) and low[i + 3] in MONTHS)
            is_year = len(val) == 4 and val.isdigit() and 1800 <= int(val) <= 2100
            chain = is_ref
            if not (is_ref or is_date or is_year):
                kind = 'pct' if nxt == '%' or (nxt == 'por' and low[i + 2:i + 3] == ['cento']) else 'n'
                out.add((kind, val, unit) if units else (kind, val))
            i += 1
            continue
        if t not in ('º', ',', '.') and not re.fullmatch(r'[ivxlc]+|[a-z]', t):
            chain = chain and t in CONNECT
        if t in NUM_UNITS or t == 'mil':
            total, cur, j = 0, 0, i
            while j < len(low) and (low[j] in NUM_UNITS or low[j] == 'mil' or (low[j] == 'e' and j + 1 < len(low) and low[j + 1] in NUM_UNITS)):
                w = low[j]
                if w == 'mil':
                    total += (cur or 1) * 1000
                    cur = 0
                elif w != 'e':
                    cur += NUM_UNITS[w]
                j += 1
            value = total + cur
            nxt = low[j] if j < len(low) else ''
            nxt2 = low[j + 1] if j + 1 < len(low) else ''
            unit = nxt if UNITS.match(nxt) else (nxt2 if UNITS.match(nxt2) and nxt in ('de', 'dos', 'das') else '')
            if nxt in FRACTIONS:
                out.add(('frac', f'{value}/{FRACTIONS[nxt]}', '') if units else ('frac', f'{value}/{FRACTIONS[nxt]}'))
                j += 1
            elif nxt == 'por' and nxt2 == 'cento':
                out.add(('pct', str(value), '') if units else ('pct', str(value)))
            elif unit and not (value == 1 and j == i + 1):
                out.add(('n', str(value), unit) if units else ('n', str(value)))
            i = j
            continue
        if t == 'metade':
            out.add(('frac', '1/2', '') if units else ('frac', '1/2'))
        i += 1
    return out


def _qlabel(q):
    return {'n': '{}', 'frac': 'fracao {}', 'pct': '{}%'}[q[0]].format(q[1])


def number_findings(rec, ground, scope_text=''):
    gq = quantities(ground)
    if re.search(r'maioria (?:absoluta|dos votos|de seus membros|dos (?:seus )?membros)', ground, re.I):
        gq.add(('frac', '1/2'))   # "mais da metade" explains a majority written in the text
    scope_q = {(k, v, u[:5]) for k, v, u in quantities(scope_text, units=True)}
    out = []
    for sec in V.BODY:
        text = rec['content'].get(sec) or ''
        for s in sentences(text):
            qs = quantities(s, units=True)
            miss = sorted(_qlabel(q[:2]) for q in qs if q[:2] not in gq and (q[0], q[1], q[2][:5]) not in scope_q)
            elsewhere = sorted(_qlabel(q[:2]) + f' {q[2]}' for q in qs if q[:2] not in gq and (q[0], q[1], q[2][:5]) in scope_q)
            if elsewhere:
                out.append(_f('NUMBER_FROM_OTHER_DEVICE', 'INFO', None, sec, ', '.join(elsewhere), s,
                              'quantidade com a mesma unidade em outro dispositivo do escopo do lote (nao no dispositivo explicado)'))
            if miss:
                if sec == 'exemplo_pratico':
                    out.append(_f('EXAMPLE_NUMBER_NOT_IN_TEXT', 'INFO', None, sec, ', '.join(miss), s, 'numero do exemplo nao esta no texto'))
                else:
                    out.append(_f('NUMBER_NOT_IN_TEXT', 'REVIEW_REQUIRED', 'QUICK', sec, ', '.join(miss), s,
                                  'quantidade ausente da Lei Seca do registro, do artigo, dos dispositivos citados e do escopo do lote'))
    return out


# ---------------------------------------------------------------- exceptions and lists over covered devices

def scope_devices(rec, ctx):
    g, tid = rec['granularity'], rec['target_id']
    if g['role'] == 'OVERVIEW':
        return [t for t in ctx.subtree(tid) if ctx.effective_status(t) == 'CURRENT']
    out = [tid] + list(g.get('covered_targets', []))
    out += [s for t in list(out) for s in ctx.subtree(t) if s != t and ctx.effective_status(s) == 'CURRENT']
    return sorted(set(out), key=lambda t: ctx.order[t])


def ressalva_findings(rec, ctx, owned_elsewhere):
    body = [(sec, s) for sec in ('o_que_diz', 'o_que_significa', 'atencao') for s in _sentences(rec['content'].get(sec) or '')]
    out = []
    for t in scope_devices(rec, ctx):
        if t != rec['target_id'] and t in owned_elsewhere:
            continue  # the device (or its parent) has its own explanation in the batch; the summary may stay general
        txt = ctx.text.get(t) or ''
        m = EXCEPTION_MARK.search(txt)
        if not m:
            continue
        rule, exc = _stems(txt[:m.start()]), _stems(re.split(r'[;.]', txt[m.end():])[0])
        exc -= rule
        mentions = [(sec, s) for sec, s in body if len(rule & _stems(s)) >= 2]
        if not mentions:
            continue
        if any(EXCEPTION_IN_DRAFT.search(s) or (exc & _stems(s)) for _, s in mentions):
            continue
        sec, s = mentions[0]
        out.append(_f('RESSALVA_OMITTED_IN_SUMMARY', 'REVIEW_REQUIRED', 'QUICK', sec, m.group(0), s,
                      f'{t.split(":", 1)[1]}: "{txt[m.start():m.start() + 70]}" nao aparece na explicacao que resume o dispositivo'))
    return out


MODIFIER = re.compile(r'^(?:que|por|pelo|pela|pelos|pelas|em caso|inclusive|quando|nas?|nos?|ser)\b|^[\wÀ-ÿ]+(?:ad|id)[oa]s?\b', re.I)


def _elements(item):
    """Coordinated members of a list item; relative/participial/prepositional modifiers are not members."""
    parts = [p.strip() for p in re.split(r',\s*|\s+e\s+|\s+ou\s+|;', item) if p.strip()]
    out = []
    for p in parts:
        if MODIFIER.search(p):
            continue
        ws = [w for w in E.words(p) if len(w) >= 6 and _fold(w)[:6] not in STOP_STEMS]
        if ws:
            out.append((p, _fold(max(ws, key=len))[:6]))
    return out


def list_findings(rec, ctx):
    c = rec['content']
    body = ' '.join(c.get(k) or '' for k in ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')).lower()
    bstems = {_fold(w)[:6] for w in E.words(body) if len(w) >= 6}
    if SELECTIVE.search(c.get('o_que_diz') or ''):
        return []
    out = []
    for parent in scope_devices(rec, ctx):
        kids = [k for k in ctx.children.get(parent, []) if ctx.effective_status(k) == 'CURRENT' and ctx.kind(k) in ('INCISO', 'ALINEA')
                and not (ctx.text.get(k) or '').rstrip().endswith(':')]   # a header item ("relativa a:") is judged by its own children
        kids = sorted(kids, key=lambda t: ctx.order[t])
        if len(kids) < 2:
            continue
        head = _stems(ctx.text.get(parent) or '')
        per = {k: _stems(ctx.text.get(k) or '') - head for k in kids}
        common = {s for s in set().union(*per.values()) if sum(s in v for v in per.values()) > len(kids) / 2}
        dist = {k: v - common for k, v in per.items()}
        covered = [k for k in kids if dist[k] & bstems]
        if len(kids) >= 3 and len(covered) >= 0.6 * len(kids) and len(covered) < len(kids):
            miss = [k for k in kids if k not in covered and dist[k]]
            if miss:
                out.append(_f('LIST_ITEM_POSSIBLY_DROPPED', 'REVIEW_REQUIRED', 'QUICK', 'o_que_diz', ', '.join(m.split(':', 1)[1] for m in miss),
                              '', f'{len(covered)}/{len(kids)} itens de {parent.split(":", 1)[1]} reconhecidos; sem traco: '
                              + '; '.join(f'{m.split(":", 1)[1]} "{(ctx.text.get(m) or "")[:50]}"' for m in miss)))
        for k in covered:
            if ctx.children.get(k):
                continue
            els = _elements(ctx.text.get(k) or '')
            if len(els) < 3:
                continue
            got = [e for e in els if e[1] in bstems]
            lost = [e for e in els if e[1] not in bstems]
            if lost and len(els) >= 3 and len(got) >= 0.75 * len(els):
                out.append(_f('LIST_ITEM_POSSIBLY_DROPPED', 'REVIEW_REQUIRED', 'QUICK', 'o_que_diz', '; '.join(e[0] for e in lost)[:60], '',
                              f'{k.split(":", 1)[1]}: {len(got)}/{len(els)} elementos reconhecidos; sem traco: ' + '; '.join(f'"{e[0]}"' for e in lost)))
    return out


# ---------------------------------------------------------------- external, historical and conditional claims

def external_claim_findings(rec, catalog, pinned_targets):
    if V._provenance(rec):
        return []
    refs = [r for e in catalog.get('entries', []) for r in e['refs']]
    out = []
    for sec in V.BODY:
        for s in _sentences(rec['content'].get(sec) or ''):
            for m in EXT_CLAIM.finditer(s):
                ref = next(g for g in m.groups() if g)
                if any(r in s.lower() for r in refs):
                    continue
                core = sec in ('o_que_diz', 'o_que_significa')
                out.append(_f('EXTERNAL_NORMATIVE_CONTENT_CLAIM', 'REVIEW_REQUIRED', 'FULL' if core else 'QUICK', sec, ref[:60], s,
                              'conteudo de norma externa afirmado sem snapshot, catalogo, relacao fixada ou proveniencia'
                              + (' (relacao fixada existe so como evidencia pendente)' if rec['target_id'] in pinned_targets else '')))
    return out


def historical_findings(rec, vigency_ecs):
    out = []
    for sec in V.BODY + ('external_layer_notes',):
        for _, text in V._texts(rec, (sec,)):
            for s in _sentences(text):
                m = HISTORICAL.search(s)
                if not m:
                    continue
                ecs = set(EC_NUM.findall(s))
                previous_wording = re.search(r'antes da|anterior|antigos|original|exigia|trazem outra', s, re.I)
                if ecs and ecs <= vigency_ecs and not previous_wording:
                    out.append(_f('HISTORICAL_CLAIM_SUPPORTED', 'INFO', None, sec, m.group(0)[:60], s,
                                  'emenda registrada nas anotacoes de vigencia do plano do lote'))
                    continue
                out.append(_f('HISTORICAL_CLAIM_UNVERIFIED', 'REVIEW_REQUIRED', 'QUICK', sec, m.group(0)[:60], s,
                              'afirmacao sobre redacao/regime anterior sem evidencia no plano de vigencia (conferir na fonte historica)'))
    return out


def condition_findings(rec, ground):
    gst = {w.lower()[:6] for w in E.words(ground) if len(w) >= 6}
    out = []
    for sec in ('o_que_diz', 'o_que_significa', 'atencao'):
        for s in _sentences(rec['content'].get(sec) or ''):
            for m in CONDITION.finditer(s):
                miss = sorted(st for st in _stems(m.group(2)) if st not in gst)
                if len(miss) >= 2:
                    out.append(_f('CONDITION_NOT_IN_TEXT', 'REVIEW_REQUIRED', 'QUICK', sec, m.group(0)[:60], s,
                                  'termos da condicao fora da Lei Seca/contexto citado: ' + ', '.join(miss[:4])))
    return out


def ambiguity_findings(rec, registry):
    out = []
    snap = rec['source']['source_text_snapshot']
    for e in registry.get('entries', []):
        if e['phrase'] not in snap:
            continue
        keys = e['paraphrase_stems']
        for sec, text in V._texts(rec, V.BODY):
            for s in _sentences(text):
                hit = sum(1 for k in keys if k in s.lower())
                if hit >= 2 and not any(q in s for q in e['accepted_quotes']) and not AMBIGUITY.search(s):
                    out.append(_f('SEMANTIC_AMBIGUITY_REVIEW_REQUIRED', 'REVIEW_REQUIRED', 'FULL', sec, e['phrase'], s,
                                  f"{e['id']}: a explicacao parafraseia a expressao ambigua em vez de cita-la ({e['ambiguity']})"))
        out.append(_f('SEMANTIC_AMBIGUITY_REGISTERED', 'INFO', None, '*', e['phrase'], '', f"{e['id']}: {e['ambiguity']}"))
    return out


# ---------------------------------------------------------------- refinements of v2

def _article_text(rec, ctx):
    art = ':'.join(rec['target_id'].split(':')[:2])
    return ' '.join(ctx.text.get(t, '') for t in ctx.subtree(art))


def refine_v2(rec, findings, ctx):
    snap = rec['source']['source_text_snapshot'].lower()
    art = _article_text(rec, ctx).lower()
    heads = [rec['target_id'], ':'.join(rec['target_id'].split(':')[:2]) + ':CAPUT'] + list(rec['granularity'].get('covered_targets', []))
    own = [(ctx.text.get(t) or '').lower() for t in heads]   # the device itself (and its caput/covered siblings), not the whole subtree
    keep = []
    for f in findings:
        code, m, s = f['code'], (f['match'] or '').lower(), f['sentence'] or ''
        why = None
        if code == 'TELEOLOGY_SPECULATIVE' and m.startswith('incentiv'):
            if 'incentiv' in art:
                why = 'substantivo da propria Lei Seca do artigo'
            elif re.search(r'\b(?:de|sobre|dos|aos) incentiv', s, re.I):
                why = 'designa a materia (objeto da lei/medida), nao finalidade'
        elif code == 'UNIVERSAL_CLAIM':
            noun = re.search(re.escape(m) + r'\s+([\wÀ-ÿ]+)', s, re.I)
            fr = quantities(s) & quantities(snap + ' ' + art)
            quorum_text = re.search(r'\bmaioria\b|\bter[çc]os?\b|\bquintos?\b', snap + ' ' + art)
            if fr or quorum_text and re.search(r'\bmaioria\b|\bmetade\b|\bpresentes\b|\bvotos\b', s, re.I):
                why = 'reproduz quorum/condicao explicita do texto'
            elif noun and m in ('todos os', 'todas as') and re.search(r'\bcada ' + re.escape(noun.group(1).lower()[:5]), snap + ' ' + art):
                why = 'quantificador distributivo do texto ("cada")'
            elif m in ('só pode', 'somente pode') and any(len(_stems(ln) & _stems(s)) >= 2 for ln in own
                                                          if re.search(r'\b(?:somente|só|apenas)\b', ln)):
                why = 'restricao "somente/so" do mesmo dispositivo do texto'
            elif m == 'sempre' and 'sempre' in art:
                why = 'mesma expressao no artigo'
            elif m in ('todos os', 'todas as', 'sempre'):
                tail = [w.lower() for w in E.words(s[s.lower().find(m) + len(m):])][:8]
                if any(' '.join(tail[i:i + 3]) in snap for i in range(max(0, len(tail) - 2))):
                    why = 'o predicado quantificado reproduz trecho literal do texto'
        elif code == 'AUTOMATIC_CONSEQUENCE':
            if m.startswith('automatic') and 'automatic' in art:
                why = 'consequencia automatica expressa no artigo'
            elif 'exonerad' in m and re.search(r'ad nutum|demiss[íi]v|exonera', art):
                why = 'demissibilidade ad nutum expressa no texto'
        elif code in ('EXTERNAL_FACT_NEEDS_PROVENANCE', 'EXTERNAL_FACT_NO_PROVENANCE'):
            full = re.search(re.escape(f['match']) + r'[\d.]*(?:, de \d{4})?', s)
            if full:
                f['match'] = full.group(0)
            if f['section'] == 'external_layer_notes' and f['severity'] == 'REVIEW_REQUIRED':
                f['route'] = 'QUICK'
                f['detail'] = (f['detail'] + '; ' if f['detail'] else '') + 'so na camada externa: o nucleo T1 nao depende do fato'
        if why:
            keep.append(dict(f, severity='INFO', route=None, refined_v3=why))
        else:
            keep.append(f)
    return keep


def interpretive_signals(rec):
    c = rec['content']
    body = ' '.join(c.get(k) or '' for k in V.BODY)
    notes = ' '.join(rec.get('external_layer_notes') or [])
    sig = {}
    for name, rx in (('JURIS_REQUIRED_MARKER', JURIS_REQUIRED), ('CONTROVERSY', CONTROVERSY), ('AMBIGUITY', AMBIGUITY),
                     ('INTERPRETIVE_QUESTION', INTERPRETIVE_QUESTION)):
        m = rx.search(body) or rx.search(notes)
        if m:
            sig[name] = m.group(0)
    if JURIS_NOTE.search(notes):
        sig['JURIS_NOTE'] = next(n for n in rec['external_layer_notes'] if JURIS_NOTE.search(n))[:140]
    return sig


def grounding(rec, ctx):
    return rec['source']['source_text_snapshot'] + '\n' + _article_text(rec, ctx) + '\n' + \
        '\n'.join(ctx.text[t] for t in V.cited_targets(rec, ctx))


def load_registry(path=AMBIGUITY_REGISTRY):
    return json.loads(Path(path).read_text(encoding='utf-8')) if Path(path).is_file() else {'entries': []}


def validate(rec, ctx, catalog, known=None, lint_rows=(), editorial_rows=(), owned_elsewhere=(), vigency_ecs=frozenset(), pinned_targets=(),
             registry=None, scope_text=''):
    findings = refine_v2(rec, V.validate(rec, ctx, catalog, known, lint_rows, editorial_rows), ctx)
    ground = grounding(rec, ctx)
    findings += number_findings(rec, ground, scope_text) + ressalva_findings(rec, ctx, set(owned_elsewhere)) + list_findings(rec, ctx)
    findings += external_claim_findings(rec, catalog, set(pinned_targets)) + historical_findings(rec, set(vigency_ecs))
    findings += condition_findings(rec, ground) + ambiguity_findings(rec, registry or load_registry())
    return V.apply_known(rec, findings, known or {})


def route(findings, legal_risk):
    """A CLEAN_LOW · B CLEAN_MEDIUM · C QUICK_REVIEW · D FULL_HUMAN_REVIEW · E HARD_FAIL.
    D = legal risk HIGH or a FULL-route finding (legal content). The number of distinct editorial codes no longer escalates (v2 rule
    '> 2 codes -> D' dropped: volume of quick findings is not legal risk)."""
    if any(f['severity'] == 'HARD_FAIL' for f in findings):
        return 'E_HARD_FAIL'
    rev = [f for f in findings if f['severity'] == 'REVIEW_REQUIRED']
    if legal_risk == 'HIGH' or any(f['route'] == 'FULL' for f in rev):
        return 'D_FULL_HUMAN_REVIEW'
    if rev:
        return 'C_QUICK_REVIEW'
    return 'A_CLEAN_LOW' if legal_risk == 'LOW' else 'B_CLEAN_MEDIUM'
