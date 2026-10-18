"""JURISPRUDENCE_ENGINE — discovery adapter #1 (norm-agnostic): official Planalto compiled text -> jurisprudence annotations.

The CF backlog was seeded, among other sources, by the "Vide ADI ..." annotations of the Planalto compiled Constitution (J2A source P1).
This adapter generalizes that step to any Planalto compiled law: it walks the HTML paragraph by paragraph, drops struck-through
(revoked) wording, tracks the structural position (article / paragraph / inciso / alínea) and returns, for every jurisprudence
annotation, the dispositivo it is attached to plus the amendment notes ("Redação dada pela Lei ...", "Incluído pela ...") of that
same dispositivo, which feed the temporal audit. Pure function over the HTML bytes; no network (download is a separate, recorded step).

Usage: python discovery_planalto.py --html <downloaded.htm> --norm CC2002 --out <annotations.json>
"""
import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'LEGAL_TARGET_ID'))
import target_id as T  # noqa: E402

JURIS = re.compile(r'\(\s*Vide:?\s+(?P<body>[^)]{0,200}?(?:ADIN|ADI|ADC|ADPF|ADO|Recurso Extraordin[aá]rio|RE\b|Tema|S[uú]mula)[^)]{0,120})\)', re.I)
REF = re.compile(r'(?P<klass>ADIN|ADI|ADC|ADPF|ADO|Recurso Extraordin[aá]rio|RE)\s*(?:n[ºo°.]\s*)?(?P<num>\d[\d.]*)', re.I)
AMEND = re.compile(r'\((?P<kind>Reda[cç][aã]o dada|Inclu[ií]d[oa]|Revogad[oa]|Renumerad[oa])\s+pel[ao]\s+(?P<norm>[^)]*?(?:de|,)\s*(?P<year>\d{4}))\)', re.I)
ART = re.compile(r'^Art\.\s*(?P<n>\d[\d.]*)\s*(?:º|o)?\s*(?P<suf>-[A-Z])?\s*[.\-–]?')
PAR = re.compile(r'^(?:§\s*(?P<n>\d+)\s*(?:º|o)?|Par[aá]grafo\s+[úu]nico)', re.I)
INC = re.compile(r'^(?P<r>[IVXLC]+)\s*[-–—]')
ALI = re.compile(r'^(?P<a>[a-z])\)\s')
HEADING = re.compile(r'^(?:PARTE|LIVRO|T[ÍI]TULO|CAP[ÍI]TULO|Se[çc][ãa]o|Subse[çc][ãa]o)\b')
KLASS = {'ADIN': 'ADI', 'ADI': 'ADI', 'ADC': 'ADC', 'ADPF': 'ADPF', 'ADO': 'ADO', 'RE': 'RE'}


def paragraphs(raw_html):
    raw = re.sub(r'(?is)<strike>.*?</strike>|<s>.*?</s>|<del>.*?</del>', ' ', raw_html)      # revoked wording is not current text
    for chunk in re.split(r'(?i)<p\b[^>]*>', raw):
        text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', chunk))).strip()
        if text:
            yield text


def walk(raw_html, norm, anomalies=None):
    """(target_id, text) for every current paragraph inside an article, with the structural position resolved. Positions the
    target grammar cannot represent (e.g. alínea directly under a paragraph, CP art. 7º, § 2º, a) are skipped and recorded in
    `anomalies` (fail closed: never invent a target)."""
    pos = dict(article=None, paragraph=None, inciso=None, alinea=None)
    for text in paragraphs(raw_html):
        m = ART.match(text)
        if HEADING.match(text):
            pos = dict(article=None, paragraph=None, inciso=None, alinea=None)          # structural headings end the article
        elif m:
            pos = dict(article=m.group('n').replace('.', '') + (m.group('suf') or ''), paragraph=None, inciso=None, alinea=None)
        elif pos['article'] and PAR.match(text):
            p = PAR.match(text)
            pos = dict(pos, paragraph=p.group('n') or 'UNICO', inciso=None, alinea=None)
        elif pos['article'] and INC.match(text):
            pos = dict(pos, inciso=INC.match(text).group('r'), alinea=None)
        elif pos['article'] and ALI.match(text):
            pos = dict(pos, alinea=ALI.match(text).group('a'))
        if pos['article']:
            try:
                tid = T.format_target_id(norm, pos['article'], paragraph=pos['paragraph'], inciso=pos['inciso'], alinea=pos['alinea'])
            except T.TargetIdError as e:
                if anomalies is not None:
                    anomalies.append(dict(position=dict(pos), error=str(e).split(':')[0]))
                continue
            yield tid, text


def amendments(text):
    return [dict(kind=a.group('kind'), by=re.sub(r'\s+', ' ', a.group('norm')).strip(), year=int(a.group('year'))) for a in AMEND.finditer(text)]


def amendment_index(raw_html, norm, targets):
    """Amendment notes of the listed dispositivos (current wording only), for the temporal audit."""
    want, out = set(targets), {}
    for target, text in walk(raw_html, norm):
        if target in want:
            out.setdefault(target, []).extend(amendments(text))
    return {t: out.get(t, []) for t in sorted(want)}


def extract(raw_html, norm):
    out = []
    for target, text in walk(raw_html, norm):
        hits = list(JURIS.finditer(text))
        if not hits:
            continue
        amend = amendments(text)
        for h in hits:
            for r in REF.finditer(h.group('body')):
                klass = 'RE' if r.group('klass').lower().startswith('recurso') else KLASS[r.group('klass').upper()]
                out.append(dict(target_id=target, annotation=re.sub(r'\s+', ' ', h.group(0)), court='STF', klass=klass,
                                number=r.group('num').replace('.', ''), amendments_on_dispositivo=amend, text_preview=text[:160]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', required=True)
    ap.add_argument('--norm', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--url', default='')
    ap.add_argument('--amendments-for', nargs='*', default=[], help='target ids whose amendment notes are also recorded')
    a = ap.parse_args()
    raw = Path(a.html).read_bytes()
    text = raw.decode('cp1252', errors='replace')
    doc = dict(schema_version=1, adapter='discovery_planalto', norm=a.norm, source_url=a.url, source_sha256=hashlib.sha256(raw).hexdigest(),
               source_bytes=len(raw), annotations=extract(text, a.norm), amendments=amendment_index(text, a.norm, a.amendments_for))
    Path(a.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(len(doc['annotations']), doc['source_sha256'])


if __name__ == '__main__':
    main()
