"""ONDA 0 — local safety snapshot of the critical state (read-only on the project).

Selects, from CLEANUP_AUDIT/INVENTARIO_REPOSITORIO.json, every PROTECTED file that is not
safely in Git (untracked, ignored or modified) plus CLEANUP_AUDIT/, verifies each file's current
SHA-256 against the audit inventory, writes a ZIP with relative paths, SAFETY_MANIFEST.json,
then re-opens the ZIP and re-hashes every member. Never deletes or moves project files.
Usage: python CLEANUP_AUDIT/_onda0_snapshot.py <snapshot_dir>
"""
import datetime, hashlib, json, sys, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXCL = ('/.venv/', '/__pycache__/', '/.pytest_cache/')


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main(dest):
    dest = Path(dest)
    assert not dest.exists(), f'{dest} já existe: não sobrescrever'
    dest.mkdir(parents=True)
    inv = json.loads((REPO / 'CLEANUP_AUDIT/INVENTARIO_REPOSITORIO.json').read_text(encoding='utf-8'))['arquivos']
    sel, changed = [], []
    for f in inv:
        p = f['path']
        if f['protecao'] != 'PROTEGIDO' or any(x in '/' + p for x in EXCL):
            continue
        if f['tracked'] and not f['modified']:
            continue  # already preserved by the Git history (bundle)
        cur = sha(REPO / p)
        if cur != f['sha256']:
            changed.append(p)
        sel.append(dict(arquivo_original=str(REPO / p), path_relativo=p, tamanho=f['tamanho_bytes'], sha256=cur,
                        categoria=f['categoria_preliminar'], motivo_de_protecao=f['justificativa'],
                        git=('modified' if f['modified'] else 'ignored' if f['ignored'] else 'untracked')))
    for p in sorted((REPO / 'CLEANUP_AUDIT').iterdir()):
        if p.is_file():
            rel = p.relative_to(REPO).as_posix()
            sel.append(dict(arquivo_original=str(p), path_relativo=rel, tamanho=p.stat().st_size, sha256=sha(p),
                            categoria='AUDITORIA_LIMPEZA', motivo_de_protecao='Relatórios, inventário e scripts da auditoria e da ONDA 0.', git='untracked'))
    zp = dest / 'LEX_MACHINA_CRITICAL_UNTRACKED_PRE_CLEANUP.zip'
    with zipfile.ZipFile(zp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for e in sel:
            z.write(REPO / e['path_relativo'], arcname=e['path_relativo'])
    # ---- validation: re-open, CRC test, re-hash every member, compare with manifest
    with zipfile.ZipFile(zp) as z:
        bad_crc = z.testzip()
        names = z.namelist()
        mism = [e['path_relativo'] for e in sel if sha_bytes(z.read(e['path_relativo'])) != e['sha256']]
    abs_or_up = [n for n in names if n.startswith('/') or ':' in n or '..' in n.split('/')]
    val = dict(zip_crc_ok=bad_crc is None, membros=len(names), esperados=len(sel), unicos=len(set(names)) == len(names),
               hashes_membros_conferem=not mism, divergencias_hash=mism[:20], paths_relativos_ok=not abs_or_up,
               arquivos_alterados_desde_auditoria=changed, bytes_originais=sum(e['tamanho'] for e in sel), bytes_zip=zp.stat().st_size)
    val['valido'] = val['zip_crc_ok'] and val['membros'] == val['esperados'] and val['unicos'] and val['hashes_membros_conferem'] and val['paths_relativos_ok']
    cats = {}
    for e in sel:
        cats.setdefault(e['categoria'], [0, 0])
        cats[e['categoria']][0] += 1
        cats[e['categoria']][1] += e['tamanho']
    manifest = dict(tipo='SNAPSHOT_LOCAL_DE_SEGURANCA', nao_e='BACKUP_FRIO_EXTERNO',
                    aviso='Mesmo disco que o repositório. Antes de exclusões definitivas, copiar este snapshot para outro meio (disco externo, outro computador, NAS ou nuvem).',
                    criado_em=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(), repositorio=str(REPO),
                    criterio='Arquivos PROTEGIDOS da auditoria que não estão preservados no Git (untracked/ignored/modified) + CLEANUP_AUDIT/. Excluídos: .venv, __pycache__, .pytest_cache. Arquivos tracked não modificados estão no Git bundle.',
                    total_arquivos=len(sel), total_bytes=val['bytes_originais'], por_categoria=cats, validacao=val, arquivos=sel)
    (dest / 'SAFETY_MANIFEST.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in val.items() if k != 'divergencias_hash'}, ensure_ascii=False), json.dumps(cats))


if __name__ == '__main__':
    main(sys.argv[1])
