"""Byte-critical artifacts survive a git checkout on this machine (core.autocrlf + .gitattributes): ENTENDA payload offsets, manifests,
generated reports and evidence copies, Lei Seca runtime sha, Reference Engine export. Uses a temporary index and a separate work tree;
the main index and working tree are never touched. Checks the INDEX (equal to HEAD in a clean working tree)."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import git_materialization_check as G  # noqa: E402


def _in_git_repo():
    try:
        return subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=G.REPO, capture_output=True, text=True).stdout.strip() == 'true'
    except OSError:
        return False


@unittest.skipUnless(_in_git_repo(), 'not inside a git checkout')
class GitMaterializationTest(unittest.TestCase):
    def test_critical_artifacts_byte_identical_after_checkout(self):
        out = Path(tempfile.mkdtemp(prefix='lexm_test_'))
        try:
            blobs = G.materialize('INDEX', out, G.CRITICAL + G.LOGICAL)
            problems, stats = G.check(out, blobs)
        finally:
            shutil.rmtree(out, ignore_errors=True)
        self.assertEqual(problems, [])
        self.assertEqual(stats['byte_identical'], stats['files'])
        self.assertGreater(stats['files'], 150)
        self.assertEqual(stats['index_pairs'], 12)                                        # pilot + batches 01-05 (pending and final) + batch 06 + macro batches 07 and 08 candidates
        self.assertEqual(stats['payload_blocks'], stats['lookup_rows'])                   # every OFFSET/BYTES row reads a whole block
        self.assertEqual(stats['logical_equal'], 1)                                       # approved main corpus: normalization-safe

    def test_attributes_of_byte_critical_paths(self):
        def attr(path):
            out = subprocess.run(['git', 'check-attr', 'text', 'eol', '--', path], cwd=G.REPO, capture_output=True, text=True).stdout
            return {line.split(': ')[1]: line.split(': ')[2] for line in out.splitlines()}
        self.assertEqual(attr('ENTENDA_ENGINE/derived/production_batch_05/index/ENTENDA_PAYLOAD.DAT')['text'], 'unset')
        self.assertEqual(attr('ENTENDA_ENGINE/derived/production_batch_05/index/ENTENDA_LOOKUP.IDX')['text'], 'unset')
        for p in ('ENTENDA_ENGINE/derived/production_batch_05/CF88_BATCH_05.entenda.jsonl', 'DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt',
                  'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json'):
            self.assertEqual(attr(p), {'text': 'set', 'eol': 'lf'}, p)
        self.assertEqual(attr('ENTENDA_ENGINE/corpus/CF88.entenda.jsonl')['text'], 'unspecified')   # normalization-safe, no rule


if __name__ == '__main__':
    unittest.main()
