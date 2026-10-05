"""Deterministic vigency map (amendment / "Vide" annotations per target) from the versioned canonical structural source of a norm.

The canonical source (e.g. updater/backup_catalogos/.../cf.txt for CF88) is multi-version: each device appears with its wordings and the
annotation of each one ("Redacao dada pela Emenda Constitucional n. X, de Y", "Incluido pela ...", "Vide ..."). The CURRENT wording of a
target is the runtime text (NormContext.text). This module pairs each runtime text with the canonical line whose text, without label
and annotations, is identical (normalized: case, accents of the diaeresis, spaces, punctuation), and returns that line's annotations.
No annotation is ever inferred: a target without an identical canonical line gets no entry (counted as unmatched).
"""
import re
import unicodedata
from pathlib import Path

ANNOT_RE = re.compile(r'\((?:\s*)((?:Reda[çc][ãa]o dada|Inclu[íi]d[oa]|Vide|Acrescentad[oa]|Renumerad[oa]|Revogad[oa])[^()]*(?:\([^()]*\)[^()]*)*)\)',
                      re.I)
LABEL_RE = re.compile(r'^\s*(?:Art\.\s*\d+[º°o]?(?:-[A-Z])?\.?|§\s*\d+[º°o]?(?:-[A-Z])?\.?|Parágrafo único\.?|[IVXLC]+\s*[-–]|[a-z]\)|\d+\))\s*', re.I)


ART_RE = re.compile(r'^Art\.\s*(\d+(?:-[A-Z])?)', re.I)


def _fold(s):
    s = unicodedata.normalize('NFKD', s.replace('ü', 'u').replace('Ü', 'U'))
    s = ''.join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return ' '.join(s.split())


def _ascii(s):
    s = s.replace('nº', 'n.').replace('n°', 'n.')
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return ' '.join(s.replace('º', '.').replace('°', '.').replace('nº', 'n.').split())


def canonical_annotations(path):
    """{(article label, folded text without label/annotations): [annotation, ...]} from the canonical multi-version source."""
    out, art = {}, None
    for raw in Path(path).read_text(encoding='utf-8-sig').splitlines():
        line = raw.strip()
        if not line:
            continue
        m = ART_RE.match(line)
        if m:
            art = m.group(1).upper()
        ann = [' '.join(a.split()) for a in ANNOT_RE.findall(line)]
        text = ANNOT_RE.sub(' ', line)
        text = LABEL_RE.sub('', text)
        key = (art, _fold(text))
        if key[1] and ann:
            out.setdefault(key, [])
            for a in ann:
                if a not in out[key]:
                    out[key].append(a)
    return out


def vigency_map(ctx, targets, canonical_path):
    """Returns (vigency_by_target, stats). Annotations ASCII-folded like the Batch06 plan ("Redacao dada pela Emenda Constitucional n. 18")."""
    ann = canonical_annotations(canonical_path)
    out, matched, unmatched = {}, 0, 0
    for t in targets:
        txt = ctx.text.get(t)
        if not txt:
            continue
        art = t.split(':')[1].split('.', 1)[1]
        hits = ann.get((art, _fold(LABEL_RE.sub('', txt))))
        if hits is None:
            unmatched += 1
            continue
        matched += 1
        out[t] = [_ascii(a).rstrip(':').rstrip() for a in hits]
    return dict(sorted(out.items(), key=lambda kv: ctx.order[kv[0]])), dict(targets_with_text=matched + unmatched, annotated=matched,
                                                                           without_identical_annotated_line=unmatched)
