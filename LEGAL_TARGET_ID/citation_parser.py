"""Deterministic, fail-closed parser of literal legal citations -> device components (norm-agnostic).

Given the citation text and the article number a record was attached to, it returns what the text literally says
about THAT article: which subdivisions are cited and which norm the citation belongs to. It never expands an article
into its children and never guesses; anything outside the small grammar below is UNPARSEABLE.

Supported (examples):
  'incisos V e X do artigo 5º da Constituição'        -> INC V, INC X            (subdivisions before the article)
  '§§ 9º e 10 do art. 100 da Constituição'           -> PAR 9, PAR 10
  'art. 40, parágrafo 1º, inciso II, da CF'          -> PAR 1 + INC II (nested)  (subdivisions after the article)
  'arts. 5º, incs. II e XIII, 84, ...'               -> INC II, INC XIII
  '(CF, §3º, art. 73 e art. 75)'                      -> art 73: PAR 3 ; art 75: whole article
  'art. 5º, caput e I'                                -> CAPUT + INC I
  'art. 3º da EC nº 113/2021'                         -> norm = other ('EC nº 113/2021')
Norm context: first norm marker in the rest of the clause (parenthetical asides removed); a preceding '(CF,' opens a
CF context; 'seu art.' refers to a previously named norm (other). Multiple paragraphs combined with incisos are ambiguous.
"""
import re

ORD = r'\d{1,4}(?![\d.]\d)(?:\s*[º°o])?(?:-[A-Z])?'
ROMAN = r'[IVXLC]{1,7}(?:-[A-Z])?'
LIST_ORD = ORD + r'(?:\s*(?:,|e)\s*' + ORD + r')*'
LIST_ROM = ROMAN + r'(?:\s*(?:,|e)\s*' + ROMAN + r')*'
PAR_UNICO = r'par[áa]grafo\s+[úu]nico'
SUB = (r'(?:(?P<par>(?:§§?|par[áa]grafos?)\s*' + LIST_ORD + r')|(?P<unico>' + PAR_UNICO + r')|(?P<inc>(?:incisos?|incs?\.)\s*' + LIST_ROM + r')'
       r'|(?P<caput>caput(?:\s*e\s*(?P<caput_inc>' + LIST_ROM + r'))?))')
CF_MARK = re.compile(r'^(?:\s*(?:,|;)?\s*)(?:da|do)\s+(?:Constitui[çc][ãa]o|CF\b|CF/|Carta)', re.I)
CF_ANY = re.compile(r'(?:da|do)\s+(?:Constitui[çc][ãa]o|CF\b|CF/|Carta\s+(?:Magna|da\s+Rep))', re.I)
OTHER_MARK = re.compile(r'(?:da|do)\s+(?P<label>(?:EC|Emenda Constitucional)\s*(?:n[ºo°.]\s*)?\d+[/.]?\d*|Lei Complementar\s*(?:n[ºo°.]\s*)?[\d.]+(?:/\d+)?'
                        r'|LC\s*(?:n[ºo°.]\s*)?[\d.]+(?:/\d+)?|Lei\s*(?:n[ºo°.]\s*)?[\d.]+(?:/\d+)?|C[óo]digo(?:\s+(?:(?:de|do|da)\s+)?(?-i:[A-ZÁ-Ú])[a-zá-ú]+){1,3}|Decreto(?:-Lei)?\s*(?:n[ºo°.]\s*)?[\d.]+(?:/\d+)?'
                        r'|ADCT)', re.I)


BARE_INC_RE = re.compile(r'\s*,\s*(?P<bare>' + LIST_ROM + r')(?=\s*(?:,|\)|;|$|\s+(?:da|do)\b))')
ALINEA_AFTER_RE = re.compile(r'\s*,\s*(?:al[íi]neas?\s+)?["“\'‘]?[a-z]["”\'’]?\s*(?:,|\)|$|\s+(?:da|do)\b)')
ALINEA_BEFORE_RE = re.compile(r'al[íi]neas?\s+["“\'‘]?[a-z]["”\'’]?(?:\s*(?:,|e)\s*["“\'‘]?[a-z]["”\'’]?)*\s*,?\s*(?:do|da)\s+(?:incisos?|incs?\.|§)?[^;]*$', re.I)


def _nums(s):
    return [re.sub(r'\s*[º°o]$', '', x.strip()).replace(' ', '') for x in re.split(r'\s*(?:,|\be\b)\s*', s) if x.strip()]


def _strip_parens(s):
    prev = None
    while prev != s:
        prev, s = s, re.sub(r'\([^()]*\)', ' ', s)
    return s


def _norm_after(text, end):
    rest = _strip_parens(text[end:])
    # sentence boundary: ';' or '. X' not preceded by a legal abbreviation (art., arts., inc., incs., n.)
    rest = re.split(r';|(?<!\binc)(?<!\bincs)(?<!\bart)(?<!\barts)(?<!\bn)\.\s+(?=[A-Z0-9])', rest, maxsplit=1)[0]
    cf, other = CF_ANY.search(rest), OTHER_MARK.search(rest)
    if other and (not cf or other.start() < cf.start()):
        lab = re.sub(r'\s+(?:e|do|da|de|dos|das)$', '', other.group('label').strip(), flags=re.I)
        return ('ADCT' if lab.upper() == 'ADCT' else 'OTHER'), lab
    if cf:
        return 'CF', None
    return None, None


def parse_for_article(text, article):
    """Return dict(status, norm, norm_label, components, unit_text) for the given article number."""
    art = str(article)
    art_re = re.compile(r'(?:(?P<pre>' + SUB + r')\s*,?\s*(?:do|da)?\s*)?(?P<seu>seu\s+)?art(?:igo)?s?\.?\s*(?P<arts>' + LIST_ORD + r')', re.I)
    hits = []
    for m in art_re.finditer(text):
        nums = _nums(m.group('arts'))
        if art not in nums:
            continue
        first = nums[0] == art
        pre = m.group('pre') if first else None
        post, pos = [], m.end()
        if nums[-1] == art:
            while True:
                pm = re.compile(r'\s*,\s*' + SUB, re.I).match(text, pos)
                if not pm:
                    # bare roman list right after the article ('art. 7º, VIII') = incisos
                    pm = BARE_INC_RE.match(text, pos)
                if not pm:
                    break
                post.append(pm)
                pos = pm.end()
        hits.append((m, pre, post, pos))
    if not hits:
        return dict(status='UNPARSEABLE', reason='ARTICLE_NOT_FOUND_IN_CITATION')
    results = []
    for m, pre, post, end in hits:
        comps = []
        for g in ([re.compile(SUB, re.I).fullmatch(pre)] if pre else []) + post:
            if g is None:
                continue
            if 'bare' in g.groupdict() and g.group('bare'):
                comps += [('INC', n.upper()) for n in _nums(g.group('bare'))]
                continue
            if g.group('par'):
                comps += [('PAR', n) for n in _nums(re.sub(r'^(?:§§?|par[áa]grafos?)\s*', '', g.group('par'), flags=re.I))]
            elif g.group('unico'):
                comps.append(('PAR', 'UNICO'))
            elif g.group('inc'):
                comps += [('INC', n.upper()) for n in _nums(re.sub(r'^(?:incisos?|incs?\.)\s*', '', g.group('inc'), flags=re.I))]
            elif g.group('caput'):
                comps.append(('CAPUT', None))
                if g.group('caput_inc'):
                    comps += [('INC', n.upper()) for n in _nums(g.group('caput_inc'))]
        if m.group('seu'):
            norm, label = 'OTHER', 'norma referida por "seu art."'
        else:
            norm, label = _norm_after(text, end)
            before = text[max(0, m.start() - 40):m.start()]
            if norm is None and re.search(r'\(\s*CF\s*,[^()]*$', before):
                norm = 'CF'
        results.append(dict(norm=norm, norm_label=label, components=comps, unit_text=text[m.start():end].strip()))
    for (m, pre, post, end), r in zip(hits, results):
        # vague / range expressions right after the unit ('caput e seguintes', 'incisos I a IV')
        if re.match(r'\s*(?:,\s*)?(?:e\s+seguintes|e\s+ss\b|a\s+[IVXLC]+\b|a\s+\d)', text[end:], re.I):
            return dict(status='AMBIGUOUS', reason='VAGUE_OR_RANGE_EXPRESSION', **r)
        # a subdivision keyword right before the article that the grammar did not capture (e.g. 'incisos I a IV do art. 144')
        # alíneas are outside this grammar (before or after the unit): fail closed instead of dropping them
        if ALINEA_AFTER_RE.match(text, end) or ALINEA_BEFORE_RE.search(text[max(0, m.start() - 40):m.start()]):
            return dict(status='AMBIGUOUS', reason='ALINEA_NOT_SUPPORTED_BY_CITATION_GRAMMAR', **r)
        before = text[max(0, m.start() - 60):m.start()]
        kw = list(re.finditer(r'§|incisos?|incs?\.|par[áa]grafos?|al[íi]neas?|caput', before, re.I))
        if pre is None and kw and not re.search(r'\bart', before[kw[-1].end():], re.I):
            return dict(status='AMBIGUOUS', reason='UNCAPTURED_PRECEDING_SUBDIVISION', **r)
    uniq = {(r['norm'], tuple(r['components'])) for r in results}
    norms = {r['norm'] for r in results}
    if len(norms) > 1:
        return dict(status='AMBIGUOUS', reason='ARTICLE_CITED_UNDER_DIFFERENT_NORMS', hits=results)
    for r in results:
        pars = [c for c in r['components'] if c[0] == 'PAR']
        if len(pars) > 1 and any(c[0] == 'INC' for c in r['components']):
            return dict(status='AMBIGUOUS', reason='MULTIPLE_PARAGRAPHS_WITH_INCISOS', **r)
    r = results[0]
    if r['norm'] is None:
        return dict(status='UNPARSEABLE', reason='NORM_CONTEXT_NOT_IDENTIFIED', **r)
    # same article cited more than once under the same norm ('art. 7º, VIII ... art. 7º, XVII'): union of the literal hits
    return dict(status='OK', norm=r['norm'], norm_label=r['norm_label'], components=[c for x in results for c in x['components']],
                component_groups=[x['components'] for x in results], unit_text=' | '.join(x['unit_text'] for x in results))


def _targets_of_group(namespace, article, comps, fmt):
    pars = [c[1] for c in comps if c[0] == 'PAR']
    incs = [c[1] for c in comps if c[0] == 'INC']
    out = []
    if not comps:
        return [fmt(namespace, article)]
    if any(c[0] == 'CAPUT' for c in comps):
        out.append(fmt(namespace, article, caput=True))
    if pars and incs:
        out += [fmt(namespace, article, paragraph=pars[0], inciso=i) for i in incs]
    else:
        out += [fmt(namespace, article, paragraph=p) for p in pars]
        out += [fmt(namespace, article, inciso=i) for i in incs]
    return out


def to_targets(namespace, article, parsed, fmt):
    """Components -> canonical target ids via the grammar's formatter `fmt` (target_id.format_target_id); ordered, unique."""
    out = []
    for comps in parsed.get('component_groups') or [parsed['components']]:
        for t in _targets_of_group(namespace, article, comps, fmt):
            if t not in out:
                out.append(t)
    return out
