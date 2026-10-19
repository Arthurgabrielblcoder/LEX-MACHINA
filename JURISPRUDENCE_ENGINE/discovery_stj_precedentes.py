"""JURISPRUDENCE_ENGINE — discovery/verification adapter #4: STJ qualified precedents (Temas Repetitivos, IAC, SIRDR, PUIL, Controvérsias)
from the OFFICIAL STJ open-data portal (no anti-robot bypass).

Source: dataset "Precedentes qualificados" of the STJ open-data portal (CKAN, licence CC-BY), resource Temas.csv: one row per qualified
precedent with tipoPrecedente, numeroPrecedente, situacao, dataJulgamento, orgaoJulgador, questaoSubmetidaAJulgamento, teseFirmada,
referenciaLegislativa, sumulaOriginada, numeroRepercussaoGeralSTF. The citations of a norm in the tese firmada (and in the free-text
legislative reference) are mapped to target ids of the catalog norms (LEGAL_TARGET_ID grammar) — a deterministic STJ discovery channel by
norm, with no LLM in the loop. Fail closed: a citation the grammar rejects is reported, never invented; a citation of the CC/1916 is
counted apart and never becomes a CC2002 target.
Usage: python discovery_stj_precedentes.py --csv Temas.csv --norm CC2002 --out <STJ_PRECEDENTES_INDEX.json>
"""
import argparse
import collections
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'LEGAL_TARGET_ID'))
import target_id as T  # noqa: E402

DATASET_PAGE = 'https://dadosabertos.web.stj.jus.br/dataset/precedentes-qualificados'
RESOURCE_URL = ('https://dadosabertos.web.stj.jus.br/dataset/4238da2f-c07b-4c1a-b345-4402accacdcf/resource/'
                'df29da13-7d6b-41ba-ad96-cd1a5bbd191c/download/temas.csv')
SEARCH_PAGE = 'https://processo.stj.jus.br/repetitivos/temas_repetitivos/'
KLASS = {'Tema': 'REPETITIVO', 'IAC': 'IAC', 'SIRDR': 'SIRDR', 'PUIL': 'PUIL', 'Controvérsia': 'CONTROVERSIA'}
# norm markers per catalog norm: (regex for the norm named right after the article, regex for an older code of the same name)
NORMS = {'CC2002': (r'C[óo]digo\s+Civil(?:\s+(?:de|/)\s*(?:2002|1916))?|C[óo]digo\s+Civil\s+anterior|\bCC\s*/\s*(?:2002|02|1916|16)\b|\bCC-(?:02|16)\b|'
                    r'\bCC\b|Lei\s*(?:n[º°o.]\s*)?10\.406(?:/2002)?',
                    r'1916|/16\b|-16\b|anterior')}
ROM = r'[IVXLC]+'
COMP = rf'(?:\s*,\s*(?:§\s*\d+\s*[º°o]?|par[áa]grafo\s+[úu]nico|(?:inc(?:iso)?\.?\s*)?{ROM}\b|al[íi]nea\s*["“]?[a-z]["”]?))'
ART = re.compile(rf'\barts?\.\s*(?P<n>\d{{1,2}}\.\d{{3}}|\d{{1,4}})(?!\d)\s*(?:[º°o])?(?P<suf>-[A-Z])?(?P<comp>{COMP}*)', re.I)
LINK = re.compile(r'^\s*,?\s*(?:,\s*)?(?:do|da|ambos\s+do)\s+', re.I)
SAME_LIST = re.compile(r'^\s*(?:,|e|c/c(?:\s+o)?)\s*$', re.I)


def components(comp):
    par = inc = ali = None
    for c in re.findall(rf'§\s*\d+|par[áa]grafo\s+[úu]nico|(?:inc(?:iso)?\.?\s*)?\b{ROM}\b|al[íi]nea\s*["“]?[a-z]', comp, re.I):
        if c.startswith('§'):
            par, inc, ali = re.sub(r'\D', '', c), None, None
        elif c.lower().startswith('par'):
            par, inc, ali = 'UNICO', None, None
        elif c.lower().startswith('al'):
            ali = c[-1].lower()
        else:
            inc, ali = re.sub(r'(?i)^inc(?:iso)?\.?\s*', '', c).upper(), None
    return par, inc, ali


def cites(text, norm):
    """Article citations of `norm` in free text -> (targets, older_code_hits, grammar_rejects). An article counts when the norm marker follows
    it directly ("art. 206, § 3º, IX, do Código Civil") or when it opens a list closed by the marker ("arts. 1.829 e 1.839 do CC")."""
    mark, older = NORMS[norm]
    markre = re.compile(rf'^(?:{mark})', re.I)
    hits = list(ART.finditer(text or ''))
    out, old, bad = [], 0, []
    for k, h in enumerate(hits):
        chain, j = [h], k
        while j + 1 < len(hits) and SAME_LIST.match(text[hits[j].end():hits[j + 1].start()]):
            j += 1
            chain.append(hits[j])
        tail = text[chain[-1].end():chain[-1].end() + 40]
        ln = LINK.match(tail)
        if not ln:
            continue
        m = markre.match(tail[ln.end():])
        if not m:
            continue
        if re.search(older, m.group(0) + tail[ln.end() + m.end():ln.end() + m.end() + 8], re.I):
            old += 1
            continue
        par, inc, ali = components(h.group('comp'))
        art = str(int(h.group('n').replace('.', ''))) + (h.group('suf') or '').upper()
        try:
            out.append(T.format_target_id(norm, art, paragraph=par, inciso=inc, alinea=ali))
        except T.TargetIdError as e:
            bad.append(dict(citation=h.group(0), error=e.code))
    return list(dict.fromkeys(out)), old, bad


OTHER_LAW = re.compile(r'\b(CPC|CPC/\d+|C[óo]digo de Processo|CF|Constitui[çc][ãa]o|CTN|CDC|C[óo]digo (?:Tribut|Penal|de Defesa|Comercial)|CCom|Lei\s*(?:n[º°o.]\s*)?'
                       r'(?!10\.406)\d|Decreto|LEF|MP\b|Medida Provis[óo]ria|ECA|CLT|CP\b)', re.I)
SAME = re.compile(r'^\s*,?\s*(?:(?:do|da)\s+mesm[oa]|deste|desse|dess[ea]\s+[úu]ltim[oa])\s+(?:diploma(?:\s+legal)?|c[óo]digo|estatuto)\b', re.I)


def _target(norm, n, suf, comp, bad, raw):
    par, inc, ali = components(comp or '')
    try:
        return T.format_target_id(norm, str(int(n.replace('.', ''))) + (suf or '').upper(), paragraph=par, inciso=inc, alinea=ali)
    except T.TargetIdError as e:
        bad.append(dict(citation=raw, error=e.code))
        return None


def cites_extended(text, norm):
    """Higher-recall extraction (v2), every hit tagged with its method (fail closed, nothing inferred from a bare number):
    DIRECT         the existing rule (article followed by the norm marker, or a list closed by it)
    LIST_TAIL      a bare number inside an 'arts. ... e N do Código Civil' list ("arts. 219 do CPC e 405 do Código Civil")
    COMPONENT_FIRST 'parágrafo único do art. 1.238 do CC' / '§ 3º do art. 20 do CC'
    SAME_DIPLOMA   'art. 2.028 do mesmo diploma' when the last norm marker before it names this norm (not its older code)
    NEAREST_MARKER an article without any law marker whose nearest preceding marker, in the same sentence, is this norm and no other law
                   is named in between (weaker: the reviewer must confirm)"""
    text = text or ''
    mark, older = NORMS[norm]
    out, bad = {}, []
    direct, old, b0 = cites(text, norm)
    bad += b0
    for t in direct:
        out.setdefault(t, 'DIRECT')
    markre = re.compile(rf'(?:{mark})', re.I)
    for m in re.finditer(rf'(?:,|\be\b)\s*(?P<n>\d{{1,2}}\.\d{{3}}|\d{{1,4}})(?!\d)\s*(?:[º°o])?(?P<suf>-[A-Z])?(?P<comp>{COMP}*)\s*,?\s*(?:do|da)\s+(?P<mk>{mark})', text, re.I):
        if re.search(r'\barts\.', text[max(0, m.start() - 90):m.start()], re.I) and not re.search(older, m.group('mk') + text[m.end():m.end() + 8], re.I):
            t = _target(norm, m.group('n'), m.group('suf'), m.group('comp'), bad, m.group(0))
            if t:
                out.setdefault(t, 'LIST_TAIL')
    for m in re.finditer(rf'(?P<c>§\s*\d+\s*[º°o]?|par[áa]grafo\s+[úu]nico|inc(?:iso)?\.?\s*{ROM}\b)\s*,?\s*do\s+art\.\s*(?P<n>\d{{1,2}}\.\d{{3}}|\d{{1,4}})(?!\d)'
                         rf'(?P<suf>-[A-Z])?\s*,?\s*(?:do|da)\s+(?P<mk>{mark})', text, re.I):
        if not re.search(older, m.group('mk') + text[m.end():m.end() + 8], re.I):
            t = _target(norm, m.group('n'), m.group('suf'), ', ' + m.group('c'), bad, m.group(0))
            if t:
                out.setdefault(t, 'COMPONENT_FIRST')
    marks = [(mm.start(), mm.group(0) + text[mm.end():mm.end() + 8]) for mm in markre.finditer(text)]
    for h in ART.finditer(text):
        n, comp, suf = h.group('n'), h.group('comp'), h.group('suf')
        tail = text[h.end():h.end() + 60]
        prev = [mk for pos, mk in marks if pos < h.start()]
        if SAME.match(tail) and prev and not re.search(older, prev[-1], re.I):
            t = _target(norm, n, suf, comp, bad, h.group(0))
            if t:
                out.setdefault(t, 'SAME_DIPLOMA')
            continue
        if LINK.match(tail) or SAME.match(tail):
            continue                                            # names some law right after: DIRECT already decided
        if re.match(r'^\s*(?:,|e|c/c)\s*(?:o\s+)?(?:arts?\.\s*)?\d', tail) and (markre.search(tail) or OTHER_LAW.search(tail)):
            continue                                            # inside a list closed by an explicit law: the closing marker decides
        sent_start = max(text.rfind('. ', 0, h.start() - 2), text.rfind('; ', 0, h.start()), text.rfind('\n', 0, h.start()))
        window = text[sent_start + 1:h.start()]
        wm = list(markre.finditer(window))
        if not wm:
            continue
        last = wm[-1]
        between = window[last.end():]
        if re.search(older, last.group(0) + window[last.end():last.end() + 8], re.I) or OTHER_LAW.search(between):
            continue
        t = _target(norm, n, suf, comp, bad, h.group(0))
        if t:
            out.setdefault(t, 'NEAREST_MARKER')
    out = {t: m for t, m in out.items() if not any(o != t and o.startswith(t + ':') for o in out)}   # keep the most specific dispositivo
    return out, old, bad


def parse_v2(rows, norm):
    """Every qualified precedent with any citation of `norm` in the tese firmada, the questão submetida or the free-text legislative
    reference; each target carries (field, method). Older-code-only citations are counted, never mapped."""
    entries, stats = [], collections.Counter()
    for r in rows:
        stats['ROWS'] += 1
        hits, old_total, bad_all = {}, 0, []
        for field, txt in (('tese', r['teseFirmada']), ('questao', r['questaoSubmetidaAJulgamento'])):
            found, old, bad = cites_extended(txt, norm)
            old_total += old
            bad_all += bad
            for t, m in found.items():
                hits.setdefault(t, []).append(f'{field}:{m}')
        for t in reflex_cites(r['referenciaLegislativa'], norm):
            hits.setdefault(t, []).append('referencia_legislativa:STRUCTURED_TEXT')
        if not hits and not old_total:
            continue
        klass = KLASS.get(r['tipoPrecedente'], r['tipoPrecedente'].upper())
        stats['CITING_' + norm] += bool(hits)
        stats['CITING_OLDER_CODE_ONLY'] += bool(old_total and not hits)
        entries.append(dict(id=f"STJ:{klass}:{r['numeroPrecedente']}", tipo=r['tipoPrecedente'], klass=klass, number=r['numeroPrecedente'],
                            sequencial=r['sequencialPrecedente'], situacao=clean(r['situacao']), data_julgamento=clean(r['dataJulgamento']),
                            data_publicacao=clean(r['dataPublicacaoAcordao']), orgao=clean(r['orgaoJulgador']),
                            questao=clean(r['questaoSubmetidaAJulgamento']), tese=clean(r['teseFirmada']),
                            referencia_legislativa=clean(r['referenciaLegislativa']), sumula_originada=clean(r['sumulaOriginada']),
                            rg_stf=clean(r['numeroRepercussaoGeralSTF']), assuntos=clean(r.get('Assuntos')), targets=hits,
                            older_code_citations=old_total, grammar_rejects=bad_all))
    return entries, stats


def reflex_cites(text, norm):
    """Free-text legislative reference: 'CC/2002. Art. 591.' or 'Art. 206, § 3º, IX - Código Civil'."""
    mark, older = NORMS[norm]
    out = []
    for line in (text or '').splitlines():
        if not re.search(mark, line, re.I) or re.search(older, line, re.I):
            continue
        for h in ART.finditer(line):
            par, inc, ali = components(h.group('comp'))
            try:
                out.append(T.format_target_id(norm, str(int(h.group('n').replace('.', ''))) + (h.group('suf') or ''), paragraph=par, inciso=inc,
                                              alinea=ali))
            except T.TargetIdError:
                pass
    return list(dict.fromkeys(out))


def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def parse(rows, norm):
    entries, stats = [], collections.Counter()
    for r in rows:
        stats['ROWS'] += 1
        tese, refl = r['teseFirmada'], r['referenciaLegislativa']
        t1, old, bad = cites(tese, norm)
        t2 = reflex_cites(refl, norm)
        if not (t1 or t2 or old):
            continue
        klass = KLASS.get(r['tipoPrecedente'], r['tipoPrecedente'].upper())
        stats['CITING_' + norm] += bool(t1 or t2)
        stats['CITING_OLDER_CODE_ONLY'] += bool(old and not (t1 or t2))
        entries.append(dict(id=f"STJ:{klass}:{r['numeroPrecedente']}", tipo=r['tipoPrecedente'], klass=klass, number=r['numeroPrecedente'],
                            sequencial=r['sequencialPrecedente'], situacao=clean(r['situacao']), data_julgamento=clean(r['dataJulgamento']),
                            data_publicacao=clean(r['dataPublicacaoAcordao']), orgao=clean(r['orgaoJulgador']),
                            questao=clean(r['questaoSubmetidaAJulgamento']), tese=clean(tese), referencia_legislativa=clean(refl),
                            sumula_originada=clean(r['sumulaOriginada']), rg_stf=clean(r['numeroRepercussaoGeralSTF']),
                            targets_from_tese=t1, targets_from_reference=t2, older_code_citations=old, grammar_rejects=bad))
    return entries, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--norm', default='CC2002')
    ap.add_argument('--accessed-on', default='2026-10-18')
    ap.add_argument('--out', required=True)
    ap.add_argument('--v2', action='store_true', help='higher-recall extraction (tese + questão + referência; methods tagged)')
    a = ap.parse_args()
    raw = Path(a.csv).read_bytes()
    rows = list(csv.DictReader(raw.decode('utf-8-sig').splitlines(keepends=True)))
    if a.v2:
        entries, st = parse_v2(rows, a.norm)
        doc = dict(schema_version=2, adapter='discovery_stj_precedentes', mode='v2', court='STJ', norm=a.norm,
                   source=dict(url=RESOURCE_URL, dataset_page=DATASET_PAGE, search_page=SEARCH_PAGE, tier='A', org='STJ', licence='CC-BY',
                               csv_sha256=hashlib.sha256(raw).hexdigest(), csv_bytes=len(raw), accessed_on=a.accessed_on),
                   stats=dict(ROWS=st['ROWS'], BY_TYPE=dict(sorted(collections.Counter(r['tipoPrecedente'] for r in rows).items())),
                              ENTRIES_CITING_NORM=st['CITING_' + a.norm], ENTRIES_CITING_OLDER_CODE_ONLY=st['CITING_OLDER_CODE_ONLY'],
                              PAIRS=sum(len(e['targets']) for e in entries),
                              BY_METHOD=dict(sorted(collections.Counter(m.split(':')[1] for e in entries for ms in e['targets'].values() for m in ms).items()))),
                   entries=entries)
        Path(a.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + chr(10), encoding='utf-8')
        print(json.dumps(doc['stats'], ensure_ascii=False, indent=1))
        return
    entries, st = parse(rows, a.norm)
    doc = dict(schema_version=1, adapter='discovery_stj_precedentes', court='STJ', norm=a.norm,
               source=dict(url=RESOURCE_URL, dataset_page=DATASET_PAGE, search_page=SEARCH_PAGE, tier='A', org='STJ', licence='CC-BY',
                           title='Precedentes qualificados — Temas.csv (Portal de Dados Abertos do STJ)', csv_sha256=hashlib.sha256(raw).hexdigest(),
                           csv_bytes=len(raw), accessed_on=a.accessed_on,
                           method='download direto do recurso público do portal de dados abertos (CKAN); nenhum desafio anti-robô contornado'),
               stats=dict(ROWS=st['ROWS'], BY_TYPE=dict(sorted(collections.Counter(r['tipoPrecedente'] for r in rows).items())),
                          ENTRIES_CITING_NORM=st['CITING_' + a.norm], ENTRIES_CITING_OLDER_CODE_ONLY=st['CITING_OLDER_CODE_ONLY'],
                          PAIRS=sum(len(set(e['targets_from_tese']) | set(e['targets_from_reference'])) for e in entries),
                          GRAMMAR_REJECTS=sum(len(e['grammar_rejects']) for e in entries)),
               entries=entries)
    Path(a.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(doc['stats'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
