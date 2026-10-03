"""Implantação física do SD BATCH04+RUN3 (fases B/C/D do plano físico).

  python tools/deploy_batch04_run3_sd.py pre  D:   # somente leitura no SD + backup local
  python tools/deploy_batch04_run3_sd.py copy D:   # copia os 7 REPLACED, readback, manifesto pós

Só escreve dentro de <drive>/99_LEX_V1 e só nos 7 arquivos do diff plan.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DI = os.path.dirname(HERE)
STAGING = os.path.join(DI, 'staging_sd_v1_batch04_run3_candidate', 'SD', '99_LEX_V1')
KNOWN = os.path.join(DI, 'backups', 'cc_index', 'sd_manifest_post.json')
OUT = os.path.join(DI, 'backups', 'batch04_run3')
SD_PRE_BACKUP = os.path.join(OUT, 'sd_pre', '99_LEX_V1')
PREFIX = '99_LEX_V1/'
IGNORED = ('System Volume Information/',)

REPLACED = [
    '00_SYS/LEXV1.VER',
    '00_SYS/LEX_DEVICE_MANIFEST.json',
    '10_TARGETS/CF88_TARGETS.IDX',
    '20_REFERENCES/REF_LOOKUP.IDX',
    '20_REFERENCES/REF_PAYLOAD.IDX',
    '30_ENTENDA/ENTENDA_LOOKUP.IDX',
    '30_ENTENDA/ENTENDA_PAYLOAD.DAT',
]
UNCHANGED = [
    '05_TEXT/CF88_RUNTIME.txt',
    '10_TARGETS/CC2002_ARTICLE_SEARCH.IDX',
    '10_TARGETS/CF88_ARTICLE_SEARCH.IDX',
    '10_TARGETS/CF88_TEXT_MAP.IDX',
]
EXPECTED_LEGACY = 1060


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def manifest(root):
    entries = {}
    for d, dirs, files in os.walk(root):
        dirs.sort()
        for fn in sorted(files):
            p = os.path.join(d, fn)
            rel = os.path.relpath(p, root).replace(os.sep, '/')
            if rel.startswith(IGNORED):
                continue
            entries[rel] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
    return dict(sorted(entries.items()))


def diff(a, b):
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return added, removed, changed


def dump(name, obj):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')


def stop(msg):
    print('PARAR:', msg)
    sys.exit(2)


def staging_manifest():
    return {rel: v for rel, v in manifest(STAGING).items()}


def pre(drive):
    root = drive + os.sep
    if not os.path.isdir(os.path.join(root, '99_LEX_V1')):
        stop('99_LEX_V1 ausente em ' + root)
    known = json.load(open(KNOWN, encoding='utf-8'))['entries']
    t = time.time()
    cur = manifest(root)
    dump('sd_manifest_pre.json', {'drive': drive, 'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                                  'file_count': len(cur), 'entries': cur})
    a, r, c = diff(known, cur)
    lex = {k: v for k, v in cur.items() if k.startswith(PREFIX)}
    legacy = {k: v for k, v in cur.items() if not k.startswith(PREFIX)}
    print(f'manifesto: {len(cur)} arquivos ({time.time() - t:.1f}s); 99_LEX_V1={len(lex)} legacy={len(legacy)}')
    print('vs estado físico conhecido: added', a, 'removed', r, 'changed', c)
    if a or r or c:
        stop('estado físico diverge do conhecido')
    if len(lex) != 11 or len(legacy) != EXPECTED_LEGACY:
        stop('contagem inesperada')
    # o plano: 4 UNCHANGED já iguais ao staging; 7 REPLACED diferentes
    stg = staging_manifest()
    if sorted(stg) != sorted(REPLACED + UNCHANGED) or sorted(k[len(PREFIX):] for k in lex) != sorted(stg):
        stop('conjunto de arquivos de 99_LEX_V1 difere do plano')
    for rel in UNCHANGED:
        if lex[PREFIX + rel] != stg[rel]:
            stop('UNCHANGED diverge: ' + rel)
    for rel in REPLACED:
        if lex[PREFIX + rel] == stg[rel]:
            stop('REPLACED já igual ao candidato: ' + rel)
    # backup verificável do /99_LEX_V1 inteiro (11 arquivos)
    bk = []
    for k, v in lex.items():
        rel = k[len(PREFIX):]
        dst = os.path.join(SD_PRE_BACKUP, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(root, *k.split('/')), dst)
        got = {'bytes': os.path.getsize(dst), 'sha256': sha(dst)}
        if got != v:
            stop('backup não confere: ' + rel)
        bk.append({'path': '/' + k, 'bytes': v['bytes'], 'sha256': v['sha256'],
                   'action': 'REPLACED' if rel in REPLACED else 'UNCHANGED'})
    dump('sd_pre_backup_manifest.json', {'backup_dir': 'backups/batch04_run3/sd_pre/99_LEX_V1', 'files': bk})
    print('backup 11/11 verificado em', SD_PRE_BACKUP)
    print('PRE_OK')


def copy(drive):
    root = drive + os.sep
    pre_m = json.load(open(os.path.join(OUT, 'sd_manifest_pre.json'), encoding='utf-8'))['entries']
    if manifest(os.path.join(root, '99_LEX_V1')) != {k[len(PREFIX):]: v for k, v in pre_m.items() if k.startswith(PREFIX)}:
        stop('99_LEX_V1 mudou desde o manifesto pré')
    stg = staging_manifest()
    for rel in REPLACED:
        src = os.path.join(STAGING, *rel.split('/'))
        dst = os.path.join(root, '99_LEX_V1', *rel.split('/'))
        with open(src, 'rb') as fi, open(dst, 'wb') as fo:
            fo.write(fi.read())
            fo.flush()
            os.fsync(fo.fileno())
        print('copiado', rel)
    print('COPY_DONE')


def verify(drive):
    root = drive + os.sep
    pre_m = json.load(open(os.path.join(OUT, 'sd_manifest_pre.json'), encoding='utf-8'))['entries']
    stg = staging_manifest()
    post = manifest(root)
    dump('sd_manifest_post.json', {'drive': drive, 'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                                   'file_count': len(post), 'entries': post})
    rows = []
    for rel in sorted(stg):
        got = post.get(PREFIX + rel)
        rows.append({'path': '/' + PREFIX + rel, 'staging': stg[rel], 'sd': got, 'match': got == stg[rel],
                     'action': 'REPLACED' if rel in REPLACED else 'UNCHANGED'})
    a, r, c = diff(pre_m, post)
    legacy_pre = {k: v for k, v in pre_m.items() if not k.startswith(PREFIX)}
    legacy_post = {k: v for k, v in post.items() if not k.startswith(PREFIX)}
    res = {
        'match': sum(x['match'] for x in rows), 'total': len(rows), 'files': rows,
        'diff_vs_pre': {'added': a, 'removed': r, 'changed': c},
        'replaced': len(c), 'identical_in_lex': 11 - len(c),
        'legacy_untouched': legacy_pre == legacy_post, 'legacy_count': len(legacy_post),
        'total_files': len(post),
    }
    dump('sd_manifest_diff.json', res)
    print(f"readback {res['match']}/{res['total']} MATCH")
    print('diff vs pré: added', a, 'removed', r)
    print('changed', c)
    print('legacy intocados:', res['legacy_untouched'], len(legacy_post), '| total', len(post))
    ok = (res['match'] == 11 and not a and not r and sorted(c) == sorted(PREFIX + x for x in REPLACED)
          and res['legacy_untouched'] and len(legacy_post) == EXPECTED_LEGACY)
    print('SD_VALIDATED' if ok else 'SD_NOT_VALIDATED')
    sys.exit(0 if ok else 3)


if __name__ == '__main__':
    {'pre': pre, 'copy': copy, 'verify': verify}[sys.argv[1]](sys.argv[2].rstrip('\\/'))
