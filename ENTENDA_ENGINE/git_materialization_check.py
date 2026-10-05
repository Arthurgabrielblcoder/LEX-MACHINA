"""Git materialization check: are the byte-critical artifacts reproduced exactly when the repository is checked out on this machine?

Materializes tracked files as a checkout would (temporary index + `git checkout-index` into a separate work tree; the main index and
working tree are never touched; core.autocrlf applies and .gitattributes come from the materialized tree itself), then verifies:
  - byte identity with the stored blob for every byte-critical path (ENTENDA derived artifacts, Lei Seca runtime, Reference Engine export);
  - logical identity (same JSON records) for normalization-safe paths (approved main corpus, read with splitlines);
  - ENTENDA index pairs: manifest sha256/bytes of LOOKUP.IDX and PAYLOAD.DAT, lookup row count, every OFFSET/BYTES block well formed;
  - Lei Seca runtime sha256 equals the value pinned in the Batch05 target plan.
Optionally (--run-tests) runs the ENTENDA and LEGAL_TARGET_ID suites inside the materialized tree, supplementing only local inputs that are
not versioned (CF text sources declared in entenda_config.json and LOCAL_UNTRACKED_INPUTS).

Usage: python git_materialization_check.py [--source HEAD|INDEX|<ref>] [--run-tests] [--keep DIR]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
# byte-critical by consumption: read by OFFSET in binary (PAYLOAD.DAT/LOOKUP.IDX) or hash-pinned (runtime, evidence copies, generated reports,
# deterministic exports compared byte by byte)
CRITICAL = ['ENTENDA_ENGINE/derived', 'DEVICE_INTEGRATION/runtime', 'LEGAL_TARGET_ID/derived']
# normalization-safe by consumption: read as text lines (splitlines) and compared only through `git diff` -> logical equality is checked
LOGICAL = ['ENTENDA_ENGINE/corpus']
FOR_TESTS = ['ENTENDA_ENGINE', 'LEGAL_TARGET_ID', 'DEVICE_INTEGRATION/runtime', 'DEVICE_INTEGRATION/tools', 'updater/catalogo_mestre_vademecum.json',
             'updater/fontes_oficiais_senado',   # base of the byte-exact CF text reconstruction (ENTENDA_ENGINE/editorial/TEXT_SOURCE_RECONSTRUCTION.json)
             'REFERENCE_REGISTRY', 'REFERENCE_COVERAGE_AUDIT', 'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1']
# local inputs that are NOT versioned (large external data); copied from the main working tree only for --run-tests
LOCAL_UNTRACKED_INPUTS = ['CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json']
# these tests run `git diff HEAD` and therefore need to be inside the repository; outside it they are reported apart, not hidden
REQUIRES_GIT_CHECKOUT = {'test_approved_batches_immutable', 'test_approved_content_immutable', 'test_protected_registry_untouched',
                         'test_batch05_untouched'}
PINNED_RUNTIME = ('DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt', 'ENTENDA_ENGINE/derived/production_batch_05/BATCH05_TARGET_PLAN.json')


def git(args, env=None, inp=None, cwd=REPO):
    return subprocess.run(['git', '-c', 'core.longpaths=true'] + args, cwd=cwd, env=env, input=inp, check=True, capture_output=True).stdout


def materialize(source, out, paths):
    """Check out `paths` of `source` (HEAD, INDEX or a ref) into `out` through a temporary index. Returns {path: blob_sha}."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    idx = Path(tempfile.mkdtemp(prefix='lexm_idx_')) / 'index'
    env = dict(os.environ, GIT_INDEX_FILE=str(idx))
    try:
        if source == 'INDEX':
            shutil.copyfile(REPO / '.git' / 'index', idx)
        else:
            git(['read-tree', source], env)
        listing = git(['ls-files', '-s', '-z', '--'] + paths, env).split(b'\0')
        blobs = {}
        for row in filter(None, listing):
            meta, path = row.split(b'\t', 1)
            blobs[path.decode('utf-8')] = meta.split()[1].decode()
        # the work tree is `out`, which has no .gitattributes on disk: git falls back to the .gitattributes recorded in the temporary index,
        # i.e. the attributes of the materialized source, never those of the main working tree
        co_env = dict(env, GIT_DIR=str(REPO / '.git'), GIT_WORK_TREE=str(out))
        names = [p for p in blobs if p != '.gitattributes']
        git(['checkout-index', '-f', '--stdin', '-z'], co_env, b'\0'.join(p.encode('utf-8') for p in names) + b'\0', cwd=out)
        return {p: blobs[p] for p in names}
    finally:
        shutil.rmtree(idx.parent, ignore_errors=True)


def blob_bytes(sha):
    return git(['cat-file', 'blob', sha])


def _records(text):
    return [json.loads(x) for x in text.splitlines() if x.strip()]


def check(out, blobs):
    out = Path(out)
    problems = []
    stats = dict(files=0, byte_identical=0, logical_equal=0, index_pairs=0, lookup_rows=0, payload_blocks=0)
    for path, sha in sorted(blobs.items()):
        if any(path.startswith(c + '/') for c in LOGICAL):
            if _records((out / path).read_bytes().decode('utf-8')) == _records(blob_bytes(sha).decode('utf-8')):
                stats['logical_equal'] += 1
            else:
                problems.append(f'LOGICAL_CONTENT_CHANGED {path}')
            continue
        if not any(path.startswith(c + '/') for c in CRITICAL):
            continue
        stats['files'] += 1
        if (out / path).read_bytes() == blob_bytes(sha):
            stats['byte_identical'] += 1
        else:
            problems.append(f'BYTES_CHANGED_ON_CHECKOUT {path}')
    for man in sorted(out.glob('ENTENDA_ENGINE/derived/**/ENTENDA_BUILD_MANIFEST.json')):
        d = man.parent
        if not (d / 'ENTENDA_LOOKUP.IDX').is_file() or not (d / 'ENTENDA_PAYLOAD.DAT').is_file():
            continue
        rel = d.relative_to(out).as_posix()
        stats['index_pairs'] += 1
        m = json.loads(man.read_text(encoding='utf-8'))
        for n in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT'):
            b = (d / n).read_bytes()
            if hashlib.sha256(b).hexdigest() != m['files'][n]['sha256'] or len(b) != m['files'][n]['bytes']:
                problems.append(f'MANIFEST_MISMATCH {rel}/{n}')
        pl = (d / 'ENTENDA_PAYLOAD.DAT').read_bytes()
        rows = [r.split('|') for r in (d / 'ENTENDA_LOOKUP.IDX').read_bytes().decode('utf-8').split('\n') if r and not r.startswith('#')]
        if len(rows) != m['lookup_rows']:
            problems.append(f'LOOKUP_ROWS {rel} {len(rows)} != {m["lookup_rows"]}')
        stats['lookup_rows'] += len(rows)
        for r in rows:
            blk = pl[int(r[1]):int(r[1]) + int(r[2])]
            if not (blk.startswith(b'@ENTENDA/') and blk.endswith(b'@END\n')) or b'\r' in blk:
                problems.append(f'BAD_BLOCK {rel} {r[0]}')
                break
            stats['payload_blocks'] += 1
    rt, plan = out / PINNED_RUNTIME[0], out / PINNED_RUNTIME[1]
    if rt.is_file() and plan.is_file():
        pinned = json.loads(plan.read_text(encoding='utf-8'))['text_base']['runtime_sha256']
        if hashlib.sha256(rt.read_bytes()).hexdigest() != pinned:
            problems.append('LEI_SECA_RUNTIME_SHA_MISMATCH')
    return problems, stats


def run_tests(out):
    """ENTENDA and LEGAL_TARGET_ID suites inside the materialized tree; untracked local inputs are copied from the main working tree."""
    out = Path(out)
    cfg = json.loads((REPO / 'ENTENDA_ENGINE/entenda_config.json').read_text(encoding='utf-8'))
    supplied = []
    for p in [src['path'] for src in cfg['norms']['CF88']['text_sources']] + LOCAL_UNTRACKED_INPUTS:
        if not (out / p).exists() and (REPO / p).is_file():
            (out / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / p, out / p)
            supplied.append(p)
    suites, rc = {}, 0
    for name in ('ENTENDA_ENGINE', 'LEGAL_TARGET_ID'):
        r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'], cwd=out / name,
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        lines = [l for l in r.stderr.splitlines() if l.startswith(('Ran ', 'OK', 'FAILED', 'FAIL:', 'ERROR:'))]
        bad = [l for l in lines if l.startswith(('FAIL:', 'ERROR:'))]
        env_only = [l for l in bad if l.split()[1] in REQUIRES_GIT_CHECKOUT]
        suites[name] = dict(summary=[l for l in lines if l.startswith(('Ran ', 'OK', 'FAILED'))],
                            failures=[l for l in bad if l not in env_only], requires_git_checkout=env_only)
        rc = rc or int(bool(suites[name]['failures']))
    return dict(returncode=rc, suites=suites, supplied_local_inputs=supplied)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default='HEAD')
    ap.add_argument('--run-tests', action='store_true')
    ap.add_argument('--keep')
    a = ap.parse_args()
    out = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix='lexm_mat_'))
    try:
        blobs = materialize(a.source, out, FOR_TESTS if a.run_tests else CRITICAL + LOGICAL)
        problems, stats = check(out, blobs)
        autocrlf = subprocess.run(['git', 'config', '--get', 'core.autocrlf'], cwd=REPO, capture_output=True, text=True).stdout.strip()
        res = dict(source=a.source, autocrlf=autocrlf, stats=stats, problems=problems[:40], problem_count=len(problems))
        if a.run_tests:
            res['tests'] = run_tests(out)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0 if not problems and (not a.run_tests or res['tests']['returncode'] == 0) else 1
    finally:
        if not a.keep:
            shutil.rmtree(out, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
