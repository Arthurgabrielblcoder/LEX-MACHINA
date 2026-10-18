"""JURISPRUDENCE_ENGINE — discovery/verification adapter #3: STJ súmulas from the OFFICIAL STJ download (no anti-robot bypass).

Source: the "Súmulas do STJ" page of the STJ publishes a complete PDF ("Inteiro teor das súmulas", link /SCON/getFile?url=/docs_internet/
jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf). Each súmula carries: number, status (alterada/cancelada/revogada), branch,
enunciado, órgão julgador, data da decisão, fonte (DJ/DJe, RSSTJ, RSTJ) and the STJ's own structured legislative references
("LEG:FED LEI:010406 ANO:2002 ***** CC-02 ... ART:00186 ART:00927"). References are mapped to target ids of the catalog norms
(LEGAL_TARGET_ID grammar) — a deterministic STJ discovery channel by norm, with no LLM in the loop.
Input = text of the PDF produced by `pdftotext -enc UTF-8` (raw mode), plus the PDF sha256 for provenance.
Usage: python discovery_stj_sumulas.py --text SumulasSTJ.txt --pdf-sha256 <sha> --out <STJ_SUMULAS_INDEX.json>
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import target_id as T  # noqa: E402

SOURCE_URL = 'https://processo.stj.jus.br/SCON/getFile?url=/docs_internet/jurisprudencia/tematica/download/SU/Sumulas/SumulasSTJ.pdf'
INDEX_PAGE = 'https://processo.stj.jus.br/SCON/sumstj/'
HEAD = re.compile(r'^SÚMULA (\d+)(?: \((SÚMULA [A-ZÇÃ]+)\))?$')
LEG = re.compile(r'LEG:(\w+) (\w+):([0-9*]+) ANO:(\d{4})(?: \*{5} (\S+))?')
TOK = re.compile(r'\b(ART|PAR|INC|LET|ITEM|NUM):([0-9A-Z]*)')
KIND = {'Lei Complementar': 'LCP', 'Decreto-Lei': 'DEL', 'Lei': 'LEI', 'Decreto': 'DEC'}


def catalog_laws():
    items = json.loads((ROOT / 'updater/catalogo_mestre_vademecum.json').read_text(encoding='utf-8'))['itens']
    out = {('CFB', 0, 1988): 'CF88', ('CFD', 0, 1988): 'CF88'}
    for c in items:
        m = re.match(r'^(Lei Complementar|Decreto-Lei|Lei|Decreto)\s+([\d.]+)/(\d{4})', c['nome'])
        if m:
            out[(KIND[m.group(1)], int(m.group(2).replace('.', '')), int(m.group(3)))] = c['id']
    return out


def roman(n):
    vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    r = ''
    for v, s in vals:
        while n >= v:
            r, n = r + s, n - v
    return r


def ref_targets(norm, body):
    """Tokens after a LEG header -> target ids (fail closed: anything the grammar rejects is reported, never invented)."""
    out, bad, cur = [], [], None
    for k, v in TOK.findall(body):
        if k == 'ART' and v.isdigit():
            cur = dict(article=str(int(v)), paragraph=None, inciso=None, alinea=None)
        elif cur is None:
            continue
        elif k == 'PAR' and v:
            cur = dict(cur, paragraph='UNICO' if v == 'UNICO' else str(int(v)), inciso=None, alinea=None)
        elif k == 'INC' and v.isdigit():
            cur = dict(cur, inciso=roman(int(v)), alinea=None)
        elif k == 'LET' and v:
            cur = dict(cur, alinea=v.lower())
        else:
            continue
        try:
            out.append(T.format_target_id(norm, cur['article'], paragraph=cur['paragraph'], inciso=cur['inciso'], alinea=cur['alinea']))
        except T.TargetIdError as e:
            bad.append(dict(position=dict(cur), error=e.code))
    # a token sequence ART PAR INC yields art, art:par, art:par:inc -> keep the most specific of each chain
    keep = [t for t in out if not any(o != t and o.startswith(t + ':') for o in out)]
    return list(dict.fromkeys(keep)), bad


def parse(text, laws):
    lines = text.split('\n')
    starts = [(i, HEAD.match(l.strip())) for i, l in enumerate(lines) if HEAD.match(l.strip())]
    entries = {}
    for k, (i, m) in enumerate(starts):
        block = lines[i + 1:(starts[k + 1][0] if k + 1 < len(starts) else len(lines))]
        joined = '\n'.join(block).split('Excerto dos Precedentes')[0]

        def field(name, nxt):
            mm = re.search(rf'{name}:\n(.*?)\n(?:{nxt})', joined, re.S)
            return re.sub(r'\s+', ' ', mm.group(1)).strip() if mm else ''
        num = int(m.group(1))
        enun = field('Enunciado', 'Referências Legislativas:|Órgão Julgador:')
        refs_txt = field('Referências Legislativas', '\n|Órgão Julgador:')
        refs = []
        hits = list(LEG.finditer(refs_txt))
        for j, h in enumerate(hits):
            body = refs_txt[h.end():hits[j + 1].start() if j + 1 < len(hits) else len(refs_txt)]
            key = (h.group(2), 0 if '*' in h.group(3) else int(h.group(3)), int(h.group(4)))
            norm = laws.get(key)
            targets, bad = ref_targets(norm, body) if norm else ([], [])
            refs.append(dict(law=f'{h.group(2)}:{h.group(3)}/{h.group(4)}', sigla=h.group(5), catalog_id=norm, targets=targets, grammar_rejects=bad))
        e = dict(number=num, status=(m.group(2) or 'VIGENTE').replace('SÚMULA ', ''), branch=next((l.strip() for l in block if l.strip()), ''),
                 enunciado=enun, orgao=field('Órgão Julgador', 'Data da decisão:'), data_decisao=field('Data da decisão', 'Fonte:'),
                 fonte=field('Fonte', '\n'), references=refs)
        if num not in entries or (not entries[num]['enunciado'] and enun):
            entries[num] = e
    return [entries[n] for n in sorted(entries)]


def stats(entries):
    pairs = collections.defaultdict(set)
    for e in entries:
        if e['status'] in ('CANCELADA', 'REVOGADA'):
            continue
        for r in e['references']:
            for t in r['targets']:
                pairs[r['catalog_id']].add((t, f"STJ:SUMULA:{e['number']}"))
    hist = collections.Counter(r['sigla'] for e in entries for r in e['references'] if r['sigla'] in ('CPC-73', 'CC-16', 'CF-67', 'CF-69'))
    return dict(SUMULAS=len(entries), BY_STATUS=dict(sorted(collections.Counter(e['status'] for e in entries).items())),
                WITH_CATALOG_TARGETS=sum(1 for e in entries if any(r['targets'] for r in e['references'])),
                PAIRS_BY_NORM={k: len(v) for k, v in sorted(pairs.items(), key=lambda kv: -len(kv[1]))},
                HISTORICAL_LAW_REFERENCES=dict(sorted(hist.items())),
                GRAMMAR_REJECTS=sum(len(r['grammar_rejects']) for e in entries for r in e['references']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--pdf-sha256', required=True)
    ap.add_argument('--accessed-on', default='2026-10-18')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    entries = parse(Path(a.text).read_text(encoding='utf-8'), catalog_laws())
    doc = dict(schema_version=1, adapter='discovery_stj_sumulas', court='STJ', source=dict(url=SOURCE_URL, index_page=INDEX_PAGE, tier='A',
               org='STJ', title='Súmulas do STJ — inteiro teor (PDF oficial)', pdf_sha256=a.pdf_sha256, accessed_on=a.accessed_on,
               method='download direto do arquivo oficial publicado na página "Súmulas do STJ"; texto via pdftotext; nenhum desafio anti-robô contornado'),
               stats=stats(entries), entries=entries)
    Path(a.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(doc['stats'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
