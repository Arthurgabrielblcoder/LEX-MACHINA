"""Ingestão rastreável das fontes oficiais do Senado usadas pelo runtime da CF (CF88 + ADCT).

Reaproveita o pipeline oficial do updater (main.py): mesmo cliente HTTP com retry, mesma resolução da linha
"Compilação Monovigente", mesmo extrator de corpo (_extrair_corpo_senado + normalizar_texto) e a mesma validação
forte (_validar_especial_mestre / FONTES_ESPECIAIS_MESTRE). Nada é reescrito à mão.

Para cada fonte, grava em fontes_oficiais_senado/<ID>/<publicacao>_<sha8>/:
  raw.html        resposta bruta original (bytes exatos)
  normalizado.txt corpo extraído pelo pipeline (UTF-8, LF)
  metadata.json   URLs, norma, tipo de compilação, aquisição (UTC), sha256 bruto/normalizado, versão do parser
e atualiza fontes_oficiais_senado/SOURCES_LOCK.json (o exportador do runtime lê SOMENTE o que está travado ali).

Uso: python ingerir_fontes_oficiais_senado.py [CF88 ADCT]
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import main as M  # noqa: E402

INGESTOR_VERSION = 1
OUT = HERE / 'fontes_oficiais_senado'
NORMAS = {'CF88': '579494', 'ADCT': '604119'}


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _git_blob(path):
    try:
        return subprocess.run(['git', 'hash-object', str(path)], cwd=HERE, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def ingerir(ident):
    cfg = M.FONTES_ESPECIAIS_MESTRE[ident]
    publicacoes = M._resolver_publicacoes_monovigentes(cfg['norma_url'])
    tentativas = []
    for url in publicacoes:
        resp = M._requisitar_com_retry(url)
        raw = resp.content
        try:
            texto = M._extrair_corpo_senado(raw, cfg['titulo_inicio'])
        except RuntimeError as e:
            tentativas.append(dict(url=url, aceita=False, motivo=str(e), raw_sha256=_sha(raw)))
            continue
        problemas = M._validar_especial_mestre(ident, texto)
        if problemas:
            tentativas.append(dict(url=url, aceita=False, motivo=problemas, raw_sha256=_sha(raw)))
            continue
        norm = texto.encode('utf-8')
        pub = url.rstrip('/').rsplit('/', 1)[1]
        d = OUT / ident / f'{pub}_{_sha(raw)[:8]}'
        d.mkdir(parents=True, exist_ok=True)
        (d / 'raw.html').write_bytes(raw)
        (d / 'normalizado.txt').write_bytes(norm)
        meta = dict(
            schema_version=1, ingestor_version=INGESTOR_VERSION, id=ident, norma_id_senado=NORMAS[ident],
            titulo=cfg['titulo_inicio'], fonte='Senado Federal (legis.senado.leg.br)', tipo_compilacao='COMPILACAO_MONOVIGENTE',
            norma_url=cfg['norma_url'], publicacao_url=url, url_final=str(resp.url), http_status=resp.status_code,
            content_type=resp.headers.get('Content-Type'), adquirido_em_utc=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            raw_bytes=len(raw), raw_sha256=_sha(raw), normalizado_bytes=len(norm), normalizado_sha256=_sha(norm),
            parser=dict(extrator='updater/main.py::_extrair_corpo_senado + normalizar_texto', validacao='updater/main.py::_validar_especial_mestre',
                        main_py_git_blob=_git_blob(HERE / 'main.py'), ingestor_git_blob=_git_blob(Path(__file__))),
            validacao=dict(aprovada=True, artigos_cabecalho=len(M._artigos_cabecalho(texto)), linhas=len(texto.splitlines()), caracteres=len(texto)),
            outras_publicacoes_tentadas=tentativas)
        (d / 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        return d, meta
    raise RuntimeError(f'{ident}: nenhuma Compilação Monovigente passou na validação forte: {tentativas}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    alvos = sys.argv[1:] or list(NORMAS)
    lock_p = OUT / 'SOURCES_LOCK.json'
    lock = json.loads(lock_p.read_text(encoding='utf-8')) if lock_p.is_file() else dict(schema_version=1, sources={})
    for ident in alvos:
        d, meta = ingerir(ident)
        lock['sources'][ident] = dict(dir=d.relative_to(OUT).as_posix(), norma_id_senado=meta['norma_id_senado'], publicacao_url=meta['publicacao_url'],
                                      raw_sha256=meta['raw_sha256'], normalizado_sha256=meta['normalizado_sha256'], adquirido_em_utc=meta['adquirido_em_utc'])
        print(ident, d.relative_to(HERE).as_posix(), meta['raw_sha256'], meta['normalizado_sha256'], meta['validacao'])
    lock['sources'] = dict(sorted(lock['sources'].items()))
    lock_p.write_text(json.dumps(lock, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
