"""Freeze article indexes (numbers only, no text) used by C3A to check destination articles against the NORM TEXT:
  main_corpus_article_index.json   main-corpus norms (MAIN_CORPUS route), from the main checkout's SD backup
  ext_text_article_index.json      external norms already on the card, from their card text (the card's own EXT_ARTIGOS.IDX has gaps;
                                   the device view uses that card index, the legal check uses the text)
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


if __name__ == '__main__':
    main()
