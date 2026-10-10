"""Exhaustive accounting of a unittest suite: every test method is put in exactly one category, so the categories add up to the total.

Categories:
  PASS                                     ran and passed
  FAIL                                     ran and failed/errored for a reason NOT matched by the local-dependency rules
  SKIPPED                                  skipped by the test itself (reason kept; a skip is never counted as PASS)
  NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY   failed/errored, or never ran because setUpClass/setUpModule failed, and the traceback shows a
                                           dependency that only exists on the local machine (rules in LOCAL_RULES)
  NOT_COLLECTED                            module could not be imported; its test methods are counted statically (def test_*)
Total = collected test methods + statically counted methods of modules that failed to import.
Usage: python cloud_test_accounting.py <tests_dir> [--json out.json]
"""
import ast
import io
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

LOCAL_RULES = [
    ('LOCAL_SD_STAGING', re.compile(r'staging_sd_v1|staging_article_indexes|_host/|SD/99_LEX_V1')),
    ('LOCAL_GIT_TAG', re.compile(r'lex-device-v1-physical-approved|unknown revision|bad revision|fatal: invalid object name')),
    ('LOCAL_DATA_FILE', re.compile(r'FileNotFoundError|No such file or directory')),
    ('LOCAL_CF_SEGMENTADA', re.compile(r'CF_SEGMENTADA_V2')),
]


def static_tests(path):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            out += [f'{Path(path).stem}.{node.name}.{f.name}' for f in node.body if isinstance(f, ast.FunctionDef) and f.name.startswith('test')]
    return out


def leaf_tests(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from leaf_tests(t)
        else:
            yield t


def classify_trace(tb):
    for name, rx in LOCAL_RULES:
        if rx.search(tb):
            return name
    return None


class Recorder(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.outcome = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcome[test.id()] = ('PASS', '')

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcome[test.id()] = ('SKIPPED', reason)


TAG_RE = re.compile(r"['\"](lex-[A-Za-z0-9._-]+?-20\d\d-\d\d-\d\d)(?=['\":])")


def missing_tags(tests_dir):
    """{module: [tags it reads with git that do not exist in this clone]} (local-only tags never pushed to the remote)."""
    import subprocess
    out = {}
    for f in sorted(Path(tests_dir).glob('test_*.py')):
        tags = sorted(set(TAG_RE.findall(f.read_text(encoding='utf-8'))))
        miss = [t for t in tags if subprocess.run(['git', 'rev-parse', '--verify', '-q', t + '^{commit}'], cwd=tests_dir,
                                                  capture_output=True).returncode != 0]
        if miss:
            out[f.stem] = miss
    return out


def run(tests_dir):
    tests_dir = Path(tests_dir).resolve()
    sys.path.insert(0, str(tests_dir))
    loader = unittest.TestLoader()
    suite = loader.discover(str(tests_dir), pattern='test_*.py', top_level_dir=str(tests_dir))
    leaves = list(leaf_tests(suite))
    import_failed = [t for t in leaves if type(t).__name__ == '_FailedTest']
    collected = [t for t in leaves if type(t).__name__ != '_FailedTest']
    res = Recorder(io.StringIO(), True, 0)
    suite.run(res)
    rows = {}
    for t in collected:
        rows[t.id()] = res.outcome.get(t.id())
    errs = {}
    for test, tb in res.failures + res.errors:
        errs[test.id() if hasattr(test, 'id') else str(test)] = tb
    tags = missing_tags(tests_dir)
    for test, tb in res.failures + res.errors:
        tid = test.id() if hasattr(test, 'id') else str(test)
        if tid in rows:
            local = classify_trace(tb) or (f"LOCAL_GIT_TAG ({', '.join(tags[tid.split('.')[0]])} ausente no clone)" if tid.split('.')[0] in tags else None)
            rows[tid] = ('NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY', local) if local else ('FAIL', tb.strip().splitlines()[-1][:200])
    # tests that never ran because setUpClass/setUpModule failed (unittest reports one _ErrorHolder for the class/module)
    for desc, tb in errs.items():
        m = re.match(r'(setUpClass|setUpModule) \(([\w.]+)\)', desc)
        if not m:
            continue
        prefix = m.group(2)
        local = classify_trace(tb)
        for tid, v in rows.items():
            if v is None and (tid.startswith(prefix + '.') or tid.rsplit('.', 1)[0] == prefix):
                rows[tid] = ('NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY', f'{m.group(1)}: {local}') if local else \
                    ('FAIL', f'{m.group(1)}: ' + tb.strip().splitlines()[-1][:180])
    not_collected = {}
    for t in import_failed:
        mod = t.id().split('.')[-1]
        exc = getattr(t, '_exception', None)
        names = static_tests(tests_dir / f'{mod}.py') if (tests_dir / f'{mod}.py').is_file() else []
        for n in names or [f'{mod}.<module>']:
            not_collected[n] = ('NOT_COLLECTED', f'import falhou: {type(exc).__name__ if exc else "?"}: {str(exc)[:160]}')
    for tid, v in rows.items():
        if v is None:
            rows[tid] = ('FAIL', 'sem resultado registrado')
    allrows = dict(sorted({**rows, **not_collected}.items()))
    counts = Counter(v[0] for v in allrows.values())
    return dict(tests_dir=str(tests_dir.relative_to(Path(__file__).resolve().parent.parent)), python=sys.version.split()[0], missing_git_tags=tags,
                total=len(allrows), collected=len(collected), not_collected_methods=len(not_collected),
                counts={k: counts.get(k, 0) for k in ('PASS', 'FAIL', 'SKIPPED', 'NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY', 'NOT_COLLECTED')},
                unittest_summary=dict(ran=res.testsRun, failures=len(res.failures), errors=len(res.errors), skipped=len(res.skipped)),
                local_dependency_reasons=dict(Counter(re.sub(r' \(.*', '', v[1].split(': ')[-1]) for v in allrows.values()
                                                      if v[0] == 'NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY')),
                skip_reasons=dict(Counter(v[1] for v in allrows.values() if v[0] == 'SKIPPED')),
                tests={k: dict(category=v[0], detail=v[1]) for k, v in allrows.items()})


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    out = run(sys.argv[1])
    assert sum(out['counts'].values()) == out['total']
    if '--json' in sys.argv:
        Path(sys.argv[sys.argv.index('--json') + 1]).write_bytes((json.dumps(out, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in out.items() if k != 'tests'}, ensure_ascii=False, indent=1))
