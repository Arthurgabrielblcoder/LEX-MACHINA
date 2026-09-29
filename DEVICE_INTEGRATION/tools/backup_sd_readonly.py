"""Read-only full backup of the LEX MACHINA microSD (DEVICE INTEGRATION V1-A2B).

The source volume is only ever opened with mode 'rb' and os.stat/os.scandir. Nothing is created, renamed, deleted or touched on it.
Refuses to run unless the strong signature is present on exactly the given root.
Usage: python backup_sd_readonly.py <SOURCE_ROOT e.g. D:\\> <DEST_DIR under DEVICE_INTEGRATION/backups>
       python backup_sd_readonly.py --verify <SOURCE_ROOT> <DEST_DIR>
"""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKUPS = (HERE.parent / 'backups').resolve()
SIGNATURE = ('99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX', '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX')
CHUNK = 1 << 20


def signature_ok(root):
    root = Path(root)
    return all((root / p).is_file() for p in SIGNATURE) and any(d.is_dir() and d.name.startswith('1- CONSTITUI') for d in root.iterdir())


def walk(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for f in sorted(filenames):
            p = Path(dirpath) / f
            out.append(p)
    return out


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(CHUNK), b''):
            h.update(b)
    return h.hexdigest()


def backup(src, dest):
    src, dest = Path(src), Path(dest).resolve()
    if BACKUPS not in dest.parents:
        raise SystemExit(f'DEST_OUTSIDE_BACKUPS: {dest}')
    if dest.exists():
        raise SystemExit(f'DEST_EXISTS: {dest}')
    if not signature_ok(src):
        raise SystemExit('SIGNATURE_NOT_FOUND')
    files, errors = [], []
    data = dest / 'data'
    for p in walk(src):
        rel = p.relative_to(src).as_posix()
        target = data / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256()
        try:
            st = os.stat(p)
            with open(p, 'rb') as fi, open(target, 'wb') as fo:
                for b in iter(lambda: fi.read(CHUNK), b''):
                    h.update(b)
                    fo.write(b)
            os.utime(target, (st.st_atime, st.st_mtime))       # timestamps preserved on the copy only
            files.append(dict(relative_path=rel, size=st.st_size, sha256=h.hexdigest(), mtime=int(st.st_mtime)))
        except OSError as e:
            errors.append(dict(relative_path=rel, error=str(e)))
    agg = hashlib.sha256(''.join(f"{f['relative_path']}\t{f['size']}\t{f['sha256']}\n" for f in files).encode('utf-8')).hexdigest()
    return files, errors, agg


def verify(src, dest, manifest):
    src, data = Path(src), Path(dest) / 'data'
    bad = []
    listed = {f['relative_path'] for f in manifest['files']}
    now = {p.relative_to(src).as_posix() for p in walk(src)}
    if listed != now:
        bad.append(dict(kind='FILE_SET_CHANGED', missing=sorted(now - listed)[:20], extra=sorted(listed - now)[:20]))
    for f in manifest['files']:
        s, c = src / f['relative_path'], data / f['relative_path']
        if not c.is_file() or c.stat().st_size != f['size'] or os.stat(s).st_size != f['size']:
            bad.append(dict(kind='SIZE', path=f['relative_path']))
            continue
        if sha_file(c) != f['sha256'] or sha_file(s) != f['sha256']:
            bad.append(dict(kind='SHA256', path=f['relative_path']))
    return bad


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == '--verify':
        src, dest = sys.argv[2], Path(sys.argv[3])
        m = json.loads((dest / 'manifest.json').read_text(encoding='utf-8'))
        bad = verify(src, dest, m)
        res = 'BACKUP_VERIFIED' if not bad and not m['errors'] else 'BACKUP_VERIFICATION_FAILED'
        (dest / 'VERIFICATION.json').write_text(json.dumps(dict(result=res, checked_files=len(m['files']), problems=bad), indent=1) + '\n', encoding='utf-8')
        print(res, len(m['files']), len(bad))
    else:
        src, dest = sys.argv[1], Path(sys.argv[2])
        info = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        files, errors, agg = backup(src, dest)
        m = dict(schema_version=1, backup_timestamp=info.pop('timestamp', None), source_volume=info, signature=list(SIGNATURE),
                 total_files=len(files), total_bytes=sum(f['size'] for f in files), aggregate_manifest_sha256=agg,
                 aggregate_rule='sha256 das linhas "relative_path\\tsize\\tsha256\\n" em ordem de percurso', errors=errors, files=files)
        (dest / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(len(files), m['total_bytes'], agg, 'errors', len(errors))
