"""JURISPRUDENCE_ENGINE — discovery adapter #5: STF jurisprudence search (official), any catalog norm.

Input: a capture of the official STF jurisprudence search API (https://jurisprudencia.stf.jus.br/api/search/search, the same POST the official
search page issues; captured through the browser because a direct host POST receives a WAF challenge, which is never bypassed). Each acórdão
carries the STF's own documentation fields: documental_legislacao_citada_texto (structured: "LEG-FED LEI-010406 ANO-2002 ART-01790 INC-00001"),
tema/tese of repercussão geral, ementa, observação ("REPERCUSSÃO GERAL - MÉRITO JULGADO"), dates, inteiro teor URL.
Output per acórdão: precedent identity (RG merit -> STF:RG:<tema>; ADI/ADC/ADPF/ADO -> STF:<classe>:<n>, incidents flagged), the targets of the
requested norm found (a) in the structured legislation field and (b) in the tese/ementa text (adapter #4 citation rules), each tagged with
where it was found. Fail closed: a reference the target grammar rejects is reported, never invented.
Usage: python discovery_stf_jurisprudencia.py --capture stf_capture.json --norm CC2002 --out STF_CC2002_INDEX.json
"""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'LEGAL_TARGET_ID')]
import discovery_stj_precedentes as TXT  # noqa: E402
import discovery_stj_sumulas as SUM  # noqa: E402
import target_id as T  # noqa: E402

LEGREF = re.compile(r'LEG-(\w+)\s+(\w+)-([0-9*]+)\s+ANO-(\d{4})(.*)', re.S)
TOK = re.compile(r'\b(ART|PAR|INC|LET)-([0-9A-Z]+)|"CAPUT"')
CONCENTRATED = ('ADI', 'ADC', 'ADPF', 'ADO')


def legis_targets(blocks, norm, laws):
    """Structured legislation blocks -> targets of `norm` (most specific of each ART/PAR/INC/LET chain), grammar rejects."""
    out, bad = [], []
    for b in blocks:
        m = LEGREF.match(b.strip())
        if not m or laws.get((m.group(2), 0 if '*' in m.group(3) else int(m.group(3)), int(m.group(4)))) != norm:
            continue
        cur, chain = None, []
        for k, v in TOK.findall(m.group(5)):
            if k == 'ART' and v.isdigit():
                cur = dict(article=str(int(v)), paragraph=None, inciso=None, alinea=None)
            elif cur is None or not k:
                continue
            elif k == 'PAR':
                cur = dict(cur, paragraph='UNICO' if v == 'UNICO' else str(int(v)), inciso=None, alinea=None)
            elif k == 'INC' and v.isdigit():
                cur = dict(cur, inciso=SUM.roman(int(v)), alinea=None)
            elif k == 'LET':
                cur = dict(cur, alinea=v.lower())
            else:
                continue
            try:
                chain.append(T.format_target_id(norm, cur['article'], paragraph=cur['paragraph'], inciso=cur['inciso'], alinea=cur['alinea']))
            except T.TargetIdError as e:
                bad.append(dict(position=dict(cur), error=e.code))
        out += [t for t in chain if not any(o != t and o.startswith(t + ':') for o in chain)]
    return list(dict.fromkeys(out)), bad


def identity(d):
    classe, inc = d['classe'], d.get('incidente')
    tema = re.match(r'\s*(\d+)\s*-', d.get('tema') or '')
    if d.get('rg_merito') and tema:
        return f'STF:RG:{tema.group(1)}', 'RG', tema.group(1), inc
    if classe in CONCENTRATED:
        return f"STF:{classe}:{d['numero']}", classe, str(d['numero']), inc
    return f"STF:{classe}:{d['numero']}", classe, str(d['numero']), inc


def parse(cap, norm):
    laws = SUM.catalog_laws()
    entries, st = [], collections.Counter()
    for d in cap['docs']:
        st['DOCS'] += 1
        lt, bad = legis_targets(d.get('legislacao') or [], norm, laws)
        hits = {t: ['legislacao_citada:STRUCTURED'] for t in lt}
        for field in ('tese', 'ementa'):
            found, _, b2 = TXT.cites_extended(d.get(field) or '', norm)
            bad += b2
            for t, m in found.items():
                hits.setdefault(t, []).append(f'{field}:{m}')
        if not hits:
            continue
        pid, klass, number, inc = identity(d)
        st['WITH_TARGETS'] += 1
        entries.append(dict(id=pid, klass=klass, number=number, incidente=inc, titulo=d['titulo'], set=d['set'], orgao=d.get('orgao'),
                            julgamento=d.get('julgamento'), publicacao=d.get('publicacao'), rg_merito=bool(d.get('rg_merito')),
                            tema=re.sub(r'\s+', ' ', d.get('tema') or '').strip(), tese=re.sub(r'\s+', ' ', d.get('tese') or '').strip(),
                            ementa=re.sub(r'\s+', ' ', d.get('ementa') or '').strip(), observacao=re.sub(r'\s+', ' ', d.get('observacao') or '').strip(),
                            source_document_id=d['id'], url=d.get('inteiro_teor_url'), targets=hits, grammar_rejects=bad))
    return entries, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--capture', required=True)
    ap.add_argument('--norm', default='CC2002')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    raw = Path(a.capture).read_bytes()
    cap = json.loads(raw)
    entries, st = parse(cap, a.norm)
    doc = dict(schema_version=1, adapter='discovery_stf_jurisprudencia', court='STF', norm=a.norm,
               source=dict(api=cap['api'], query=cap['query'], captured_at=cap['captured_at'], method=cap.get('method'), tier='A', org='STF',
                           capture_sha256=hashlib.sha256(raw).hexdigest(), capture_bytes=len(raw)),
               stats=dict(DOCS=st['DOCS'], WITH_TARGETS=st['WITH_TARGETS'], PAIRS=sum(len(e['targets']) for e in entries),
                          BY_EVIDENCE=dict(sorted(collections.Counter(m.split(':')[0] for e in entries for ms in e['targets'].values() for m in ms).items())),
                          GRAMMAR_REJECTS=sum(len(e['grammar_rejects']) for e in entries)),
               entries=entries)
    Path(a.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(doc['stats'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
