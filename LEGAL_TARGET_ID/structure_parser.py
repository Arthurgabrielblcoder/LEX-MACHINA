"""Generic structural parser: legal text lines -> canonical targets (target_id from target_id.py).

Only structure is extracted (article, caput, paragraph, inciso, alinea, namespace). The official text is never
modified. Norm-specific behaviour comes from configuration (namespace markers from namespaces.json, optional
end markers), not from code branches per norm.

Repeated labels: some compiled sources keep superseded wordings right before the current one (same label twice).
They are the SAME target; every occurrence is recorded and the last one is treated as current. Any repetition is
reported so it can be reviewed; distinct labels that would collapse into the same id (the V2 '§ 4º-A' defect) cannot
happen because suffixes are part of the grammar.
"""
import hashlib
import re

import target_id as T

# A letter suffix ('103-A', '4º-A') must be glued to the number: '§ 4º - Será' is a dash, not suffix 'S'.
SUFFIX = r'(?:-([A-Z])(?![A-Za-zÀ-ÿ]))?'
# THOUSANDS_PARSER_FIX: 'Art. 2.000.' is article 2000 (Codigo Civil, CPC, CLT...). A '.' belongs to the number only when a
# 1-3 digit block is followed by '.' + EXACTLY 3 digits; 'Art. 2. Texto' is still article 2. Dots are removed before
# normalize_number_label (whose grammar still fails closed above 4 digits).
ART_NUM = r'(\d{1,3}(?:\.\d{3})+(?!\d)|\d{1,4})'
ART_RE = re.compile(r'^Art\.?\s*' + ART_NUM + r'(?:º|°|o)?' + SUFFIX + r'(?:\s*\.\s*|\s+|$)(.*)$', re.I)
ART_ALONE_RE = re.compile(r'^Art\.?$', re.I)
# Opt-in (article_case_sensitive=True): only 'Art' with capital A opens an article and a namespace title must match
# exactly. Needed for sources whose hyperlinked cross-references become their own lines ('art. 2º da Lei nº 12.858...',
# 'Ato das Disposições Constitucionais Transitórias' in the middle of a sentence). Default off: approved indexes built
# before this option are unchanged.
ART_RE_CS = re.compile(ART_RE.pattern)
ART_ALONE_RE_CS = re.compile(ART_ALONE_RE.pattern)
PAR_RE = re.compile(r'^§\s*(\d{1,3})(?:º|°|o)?' + SUFFIX + r'\s*\.?\s*(.*)$')
PAR_UNICO_RE = re.compile(r'^Par[aá]grafo\s+[uú]nico\s*[.:\-–—]?\s*(.*)$', re.I)
# The separator dash must be followed by whitespace: 'I-A o Conselho' is inciso I-A, never inciso I with text 'A o...'.
INC_RE = re.compile(r'^([IVXLCDM]+(?:-[A-Z])?)\s*[-–—](?:\s+|$)(.*)$')
ALI_RE = re.compile(r'^([a-z])\)\s*(.*)$')
UNMARKED_INC_RE = re.compile(r'^([IVXLC]{1,6}(?:-[A-Z])?)\s+[a-zà-ú]')
HEADER_RE = re.compile(r'^(TÍTULO|CAPÍTULO|SEÇÃO|SUBSEÇÃO|LIVRO|PARTE)\b', re.I)
NAMED_HEADER_RE = re.compile(r'^(DO|DA|DOS|DAS)\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9][A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9 ,\-–—]+$')


def _clean(s):
    return re.sub(r'\s+', ' ', s).strip()


def parse_structure(text, norma_id, reg=None, end_markers=(), preview_len=100, article_case_sensitive=False):
    reg = reg or T.registry()
    if not reg.known(norma_id) or reg.parent(norma_id):
        raise T.TargetIdError('UNKNOWN_NORM', norma_id)
    markers = {cfg['source_marker'].upper(): ns for ns, cfg in reg.sub.items() if cfg['parent'] == norma_id}
    lines = text.splitlines()
    targets, order, anomalies = {}, [], []
    ns, art, par, inc = norma_id, None, None, None
    open_tid = None
    after_marker = False
    pending_art = None
    anchor = {'tid': None}  # last device opened (context for anomalies even after open_tid is closed)
    art_re, art_alone_re = (ART_RE_CS, ART_ALONE_RE_CS) if article_case_sensitive else (ART_RE, ART_ALONE_RE)

    def add(tid, kind_line, text_line, lineno, structural_only=False):
        rec = targets.get(tid)
        if rec is None:
            t = T.parse_target_id(tid, reg)
            rec = dict(target_id=tid, parent_id=T.parent_target_id(tid, reg), kind=t['kind'], namespace=t['namespace'],
                       norma_id=t['norma_id'], article=t['article'], paragraph=t['paragraph'], inciso=t['inciso'],
                       alinea=t['alinea'], occurrences=[], _text=[])
            targets[tid] = rec
            order.append(tid)
        rec['occurrences'].append(lineno)
        if not structural_only:
            rec['_text'] = [text_line] if text_line else []
            anchor['tid'] = tid
        return tid

    ended = False
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        if any(line.startswith(m) for m in end_markers):
            # closing formula (signatures follow): close the open device; parsing resumes at the next namespace marker
            ended = True
            anomalies.append(dict(line=i, code='CLOSING_MARKER', text=line[:80]))
            art, par, inc, open_tid = None, None, None, None
            continue
        # strict mode: the namespace title must match exactly (a hyperlink fragment 'Ato das Disposições Constitucionais
        # Transitórias' in the middle of a sentence is not the ADCT title)
        if (line in markers) if article_case_sensitive else (line.upper() in markers):
            ns, art, par, inc, open_tid = markers[line.upper()], None, None, None, None
            add(ns, None, None, i, structural_only=True)
            continue
        if pending_art is not None:
            line = 'Art. ' + line
            pending_art = None
        if art_alone_re.match(line):
            pending_art = i
            continue
        m = art_re.match(line)
        if m:
            art = T.normalize_number_label(m.group(1).replace('.', '') + ('-' + m.group(2) if m.group(2) else ''))
            par = inc = None
            after_marker = False
            add(ns, None, None, i, structural_only=True) if ns not in targets else None
            add(T.format_target_id(ns, art, reg=reg), None, None, i, structural_only=True)
            open_tid = add(T.format_target_id(ns, art, caput=True, reg=reg), None, m.group(3) or '', i)
            continue
        if HEADER_RE.match(line):
            after_marker = True
            continue
        if after_marker and not (PAR_RE.match(line) or PAR_UNICO_RE.match(line) or INC_RE.match(line) or ALI_RE.match(line)):
            after_marker = False
            continue
        if NAMED_HEADER_RE.match(line) and not re.search(r'[.;:!?]', line):
            continue
        if art is None:
            continue
        m = PAR_RE.match(line)
        mu = None if m else PAR_UNICO_RE.match(line)
        if m or mu:
            par = 'UNICO' if mu else T.normalize_number_label(m.group(1) + ('-' + m.group(2) if m.group(2) else ''))
            inc = None
            open_tid = add(T.format_target_id(ns, art, paragraph=par, reg=reg), None, (mu or m).groups()[-1], i)
            continue
        m = INC_RE.match(line)
        if m and T.INC_RE.fullmatch(m.group(1)):
            inc = m.group(1)
            open_tid = add(T.format_target_id(ns, art, paragraph=par, inciso=inc, reg=reg), None, m.group(2), i)
            continue
        if m:
            anomalies.append(dict(line=i, code='NON_CANONICAL_ROMAN_LINE', text=line[:80]))
        mu2 = UNMARKED_INC_RE.match(line)
        if mu2 and T.INC_RE.fullmatch(mu2.group(1)):
            # Some compiled sources omit the dash ('I as ações oriundas...'). Accepted as inciso ONLY when it continues
            # the enumeration of the same parent: next number after the previous inciso, the same label again
            # (re-worded version), or 'I' right after a caput/paragraph ending with ':'. Otherwise fail closed.
            label = mu2.group(1)
            parent_tid = T.format_target_id(ns, art, paragraph=par, reg=reg) if par else T.format_target_id(ns, art, caput=True, reg=reg)
            prev = inc  # last inciso of the current parent (reset on each new article/paragraph)
            parent_text = _clean(' '.join(targets[parent_tid]['_text'])) if parent_tid in targets else ''
            while True:  # strip every trailing editorial note: '(Redação dada ...) (Vide ADIN 3392) ...'
                stripped = re.sub(r'\s*\((?:Reda|Inclu|Vide|Revog|Acrescid|Renumer)[^)]*\)\s*$', '', parent_text)
                if stripped == parent_text:
                    break
                parent_text = stripped
            ok = False
            if prev:
                ok = T.roman_to_int(label) in (T.roman_to_int(prev) + 1, T.roman_to_int(prev))
            elif label == 'I':
                ok = parent_text.endswith(':')
            if ok:
                inc = label
                open_tid = add(T.format_target_id(ns, art, paragraph=par, inciso=inc, reg=reg), None, line[len(label):].strip(), i)
                anomalies.append(dict(line=i, code='INCISO_WITHOUT_SEPARATOR_ACCEPTED_BY_SEQUENCE', target=open_tid, text=line[:80]))
                continue
            anomalies.append(dict(line=i, code='POSSIBLE_INCISO_WITHOUT_SEPARATOR', context=anchor['tid'], label=label, text=line[:80]))
            open_tid = None  # not attributed to the previous device
            continue
        m = ALI_RE.match(line)
        if m:
            if inc is None:
                anomalies.append(dict(line=i, code='ALINEA_WITHOUT_INCISO', context=open_tid, text=line[:80]))
                if open_tid:
                    targets[open_tid]['_text'].append(line)
                continue
            open_tid = add(T.format_target_id(ns, art, paragraph=par, inciso=inc, alinea=m.group(1), reg=reg), None, m.group(2), i)
            continue
        if open_tid:
            targets[open_tid]['_text'].append(line)
    # finalize
    out = []
    for tid in order:
        r = targets[tid]
        body = _clean(' '.join(r.pop('_text')))
        r['line_start'] = r['occurrences'][-1]
        r['repeated_label_occurrences'] = len(r['occurrences']) if r['kind'] not in ('ARTIGO', 'NORMA', 'NAMESPACE') else None
        r['preview'] = body[:preview_len] if body else None
        r['text_sha256_current'] = hashlib.sha256(body.encode('utf-8')).hexdigest() if body else None
        out.append(r)
    root = norma_id
    if root not in targets:
        raise T.TargetIdError('NO_STRUCTURE_FOUND', norma_id)
    return out, anomalies, ended
