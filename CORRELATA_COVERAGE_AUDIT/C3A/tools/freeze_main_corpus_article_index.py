"""Freeze article indexes (numbers only, no text) used by C3A to check destination articles against the NORM TEXT:
  main_corpus_article_index.json   main-corpus norms (MAIN_CORPUS route), from the main checkout's SD backup
  ext_text_article_index.json      external norms already on the card, from their card text (the card's own EXT_ARTIGOS.IDX has gaps;
                                   the device view uses that card index, the legal check uses the text)
  ext_index_audit.json             C3A.1: for every article a DEVICE_READY link of RUN4 jumps to, is it in the card EXT_ARTIGOS.IDX and does
                                   its offset start the article heading? (only those articles, not whole norms)
  ext_texts/<NORM>/<file>          card texts of the norms whose referenced articles are missing from the card index (needed to repair it)
Each file is checked against the sha256 of the C0 evidence pin (fail closed on mismatch).
Usage (needs the main checkout): python freeze_main_corpus_article_index.py --legacy-root C:/GitHub/LEX-MACHINA
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[2]
PIN = AUDIT / 'inputs/CORRELATA_EVIDENCE_PIN.json'
OUT = AUDIT / 'C3A/inputs/main_corpus_article_index.json'
OUT_EXT = AUDIT / 'C3A/inputs/ext_text_article_index.json'
OUT_AUDIT = AUDIT / 'C3A/inputs/ext_index_audit.json'
TEXTS = AUDIT / 'C3A/inputs/ext_texts'
ROOT = AUDIT.parent
BACKUP = 'DEVICE_INTEGRATION/backups/sd_20260929T163407Z/data'
EXT_PKG = 'LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/SD_PRONTO'
ART = re.compile(r'^\s*Art\.\s*(\d+)(?:º|°|o)?(?:\s*-\s*([A-Z])\b)?', re.M)
ART_INLINE = re.compile(r'\bArt\.\s*(\d+)(?:º|°|o)?(?:\s*-\s*([A-Z])\b)?')


def arts(rx, text):
    return sorted({x.group(1) + ('-' + x.group(2) if x.group(2) else '') for x in rx.finditer(text)}, key=lambda s: (int(s.split('-')[0]), s))


def read(path, expected, label):
    b = Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest() != expected:
        raise SystemExit(f'PIN_MISMATCH {label}')
    return b.decode('utf-8', 'replace')


def dump(path, doc):
    path.write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--legacy-root', required=True)
    a = ap.parse_args()
    pin = json.loads(PIN.read_text(encoding='utf-8'))
    cands = json.loads((AUDIT / 'CF88_CORRELATA_CANDIDATES.json').read_text(encoding='utf-8'))['candidates']
    needed = sorted({c['acervo_id'] for c in cands if c['acervo_status'] == 'IN_MAIN_CORPUS'})
    main_pin = {m['id']: m for m in pin['main_corpus']}
    out = {}
    for nid in needed:
        m = main_pin[nid]
        t = read(Path(a.legacy_root) / BACKUP / m['rel'], m['sha256'], nid)
        out[nid] = dict(norm_name=m['nome'], source_path=m['rel'], sha256=m['sha256'], bytes=m['bytes'], articles=arts(ART, t))
    dump(OUT, dict(schema_version=1, artifact='C3A_MAIN_CORPUS_ARTICLE_INDEX', source=BACKUP,
                   policy='Somente números de artigo; o texto não é copiado. Índice para validar destination_articles da rota MAIN_CORPUS.', norms=out))
    ext = {}
    for path, f in sorted(pin['relations_v2_package']['files'].items()):
        parts = path.split('/')
        if len(parts) == 4 and parts[1] == '03_NORMAS_EXTERNAS':
            t = read(Path(a.legacy_root) / EXT_PKG / path, f['sha256'], path)
            ext[parts[2]] = dict(source_path=path, sha256=f['sha256'], articles=arts(ART_INLINE, t))
    dump(OUT_EXT, dict(schema_version=1, artifact='C3A_EXT_TEXT_ARTICLE_INDEX', source=EXT_PKG,
                       policy='Artigos citados como "Art. N" no texto da norma no cartão (superconjunto para a checagem jurídica).', norms=ext))
    print({k: len(v['articles']) for k, v in out.items()}, {k: len(v['articles']) for k, v in ext.items()})
    audit_device_ready_articles(Path(a.legacy_root), pin)


def referenced_articles():
    """(norm, article) pairs that DEVICE_READY links of the current RUN4 candidate intend to open (intended, before any card fallback)."""
    view = json.loads((ROOT / 'LEGAL_TARGET_ID/derived/export_test/run4_candidate/legal_view/CF88_CORRELATA_LEGAL_VIEW.json').read_text(encoding='utf-8'))
    card = {(r[5], r[0] + '|' + r[1] + '|' + r[2] + '|' + r[3] + '|' + r[4]): r for r in
            (l.split('|') for l in (AUDIT / 'C3A/inputs/card_relations_v2/RELACOES.IDX').read_text(encoding='utf-8').splitlines() if l and l[0] != '#')}
    out = set()
    for e in view['entries']:
        if e['device_state'] != 'DEVICE_READY':
            continue
        if e['kind'] == 'ADDITION':
            arts = e['destination_articles']
        elif e.get('route_fix'):
            arts = e['route_fix']['articles']
        else:
            arts = [r[9] for (rel, _), r in card.items() if rel == e['relation_id'] and r[6] == e['destination_norm_id']]
            arts = sorted({x for a in arts for x in a.split(',') if x})
        out |= {(e['destination_norm_id'], x) for x in arts}
    return sorted(out)


def audit_device_ready_articles(root, pin):
    import sys
    sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
    import correlata_overlay as O
    files = pin['relations_v2_package']['files']
    idx = {}
    for l in (AUDIT / 'C3A/inputs/card_relations_v2/EXT_ARTIGOS.IDX').read_text(encoding='utf-8').splitlines():
        if l and l[0] != '#':
            n, art, off, size = l.split('|')
            idx[(n, art)] = (int(off), int(size))
    rows, need_text = [], set()
    for nid, art in referenced_articles():
        path = next(k for k in files if k.split('/')[1:3] == ['03_NORMAS_EXTERNAS', nid])
        t = read(root / EXT_PKG / path, files[path]['sha256'], path).encode('utf-8')
        heads = O.article_heading_offsets(t, art)
        hit = idx.get((nid, art))
        status = 'MISSING_FROM_CARD_INDEX' if not hit else ('OK' if hit[0] in heads else 'OFFSET_NOT_AT_HEADING')
        if status != 'OK':
            need_text.add((nid, path))
        rows.append(dict(norm_id=nid, article=art, status=status, card_offset=hit[0] if hit else None, heading_offsets_in_text=heads))
    for nid, path in sorted(need_text):
        dst = TEXTS / nid / Path(path).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((root / EXT_PKG / path).read_bytes())
    dump(OUT_AUDIT, dict(schema_version=1, artifact='C3A1_EXT_INDEX_AUDIT', scope='somente artigos abertos por vínculos DEVICE_READY do RUN4',
                         counts={k: sum(r['status'] == k for r in rows) for k in ('OK', 'MISSING_FROM_CARD_INDEX', 'OFFSET_NOT_AT_HEADING')},
                         texts_frozen=sorted(f'{n}/{Path(p).name}' for n, p in need_text), articles=rows))
    print('audit', len(rows), sorted(need_text))


if __name__ == '__main__':
    main()
