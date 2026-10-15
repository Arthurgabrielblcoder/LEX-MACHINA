"""R1A: consult the public sources of the two held works and keep RETRIEVAL METADATA ONLY (no third-party page text is stored).

Same record format as LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/03_FONTES/ENRIQUECIMENTO_V1 (consultar_fontes_enriquecimento.py):
number, url, final_url, tier, accessed_on, consulted_at, http_status, snapshot_sha256, caracteres_texto, verificacao (PAGINA_CONSULTADA |
FALHA_DE_ACESSO + erro). The editorial paraphrases live in build_r1a_identity.py and cite these records by number.
Usage: python collect_sources_r1a.py      (network; rewrites 03_FONTES/*.json)
"""
import datetime, gzip, hashlib, json, urllib.request, zlib
from html.parser import HTMLParser
from pathlib import Path

OUT = Path(__file__).resolve().parent / '03_FONTES'
# number, work, url, tier (tiers of 00_ENTRADA/INSTRUCAO_USUARIO.txt: A oficial, B institucional/acadêmica, C secundária reputável)
SOURCES = (
    (1, 'SICKO', 'https://www.festival-cannes.com/en/f/sicko/', 'B'),
    (2, 'SICKO', 'https://www.adorocinema.com/filmes/filme-54503/', 'C'),
    (3, 'PRO_DIA', 'https://mostra.org/arquivo/filme/5996', 'B'),
    (4, 'PRO_DIA', 'https://mostra.org/en/arquivo/filme/5996', 'B'),
    (5, 'PRO_DIA', 'https://sites.dartmouth.edu/plfd/?p=7666', 'B'),
    (6, 'PRO_DIA', 'https://www.ufmg.br/espacodoconhecimento/noticia/exibicao-de-documentario-pro-dia-nascer-feliz/', 'B'),
    (7, 'PRO_DIA', 'https://www.guiadasemana.com.br/cinema/sinopse/pro-dia-nascer-feliz', 'C'),
)


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'svg', 'noscript'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'svg', 'noscript') and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip and data.strip(): self.parts.append(data.strip())


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def fetch(n, work, url, tier):
    meta = dict(number=n, work=work, url=url, tier=tier, accessed_on=now()[:10], consulted_at=now())
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read()
            meta.update(final_url=r.url, http_status=r.status, snapshot_sha256=hashlib.sha256(raw).hexdigest(), verificacao='PAGINA_CONSULTADA')
            enc = r.headers.get('Content-Encoding', '')
        if enc == 'gzip' or raw[:2] == b'\x1f\x8b': raw = gzip.decompress(raw)
        elif enc == 'deflate': raw = zlib.decompress(raw)
        p = Text(); p.feed(raw.decode('utf-8', errors='replace'))
        meta['caracteres_texto'] = len(' '.join(p.parts))
    except Exception as e:
        meta.update(verificacao='FALHA_DE_ACESSO', erro=str(e))
    return meta


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for s in SOURCES:
        m = fetch(*s)
        (OUT / f"{m['number']:03}_{hashlib.sha256(m['url'].encode()).hexdigest()[:12]}.json").write_bytes(
            (json.dumps(m, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        print(json.dumps({k: m.get(k) for k in ('number', 'http_status', 'verificacao', 'caracteres_texto', 'erro')}, ensure_ascii=False))
