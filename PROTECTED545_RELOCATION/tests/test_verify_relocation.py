"""Unit tests for the derived protected545 relocation verifier (synthetic proof in a temp dir; never touches the repo)."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import relocation_ledger as rl  # noqa: E402
import verify_relocation as vr  # noqa: E402

PROOF = 'V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json'


class RelocationVerifierTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='p545_test_'))
        self.repo = self.tmp / 'repo'
        self.arch = self.tmp / 'archive'
        self.arch.mkdir()
        files = {'OLD_A/data/x.json': b'{"a":1}\n', 'OLD_A/data/y.json': b'{"b":2}\n', 'OLD_B/z.IDX': b'#IDX\n1|2\n'}
        entries = []
        for rel, data in files.items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            entries.append(dict(path=rel, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
        pf = self.repo / PROOF
        pf.parent.mkdir(parents=True)
        pf.write_bytes(json.dumps(dict(files=entries)).encode())
        self.entries = {e['path']: e for e in entries}
        self.proof_sha = vr.file_sha256(pf)
        self.bind = {'REPO_ROOT': str(self.repo), 'ARCH': str(self.arch)}

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ledger(self):
        return rl.new_ledger('test', PROOF, self.proof_sha, ['ARCH'])

    def move(self, rel, dest_rel, led, event_type='RELOCATE', src_root='REPO_ROOT', dst_root='ARCH'):
        src = Path(self.bind[src_root]) / rel
        dst = Path(self.bind[dst_root]) / dest_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        rl.append_event(led, event_type, self.entries[rel],
                        dict(root_id=src_root, relative_path=rel), dict(root_id=dst_root, relative_path=dest_rel), 'test', 'test-manifest')

    def run_v(self, led=None, head=None):
        return vr.verify(PROOF, self.bind, led, self.proof_sha, head)

    def status(self, res, path):
        return next(r['status'] for r in res['occurrences'] if r['original_path'] == path)

    # ---------- positive ----------
    def test_original_present_without_ledger(self):
        res = self.run_v()
        self.assertEqual(res['result'], 'PASS')
        self.assertEqual(res['counts'], {'ORIGINAL_PATH_PRESENT': 3})

    def test_valid_relocation(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/OLD_A/data/x.json', led)
        res = self.run_v(led, led['head']['event_hash'])
        self.assertEqual(res['result'], 'PASS')
        self.assertEqual(self.status(res, 'OLD_A/data/x.json'), 'VALID_RELOCATION')

    def test_two_generations_keep_lineage(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W1/x.json', led)
        e = self.entries['OLD_A/data/x.json']
        (self.arch / 'W2').mkdir()
        (self.arch / 'W1/x.json').rename(self.arch / 'W2/x.json')
        rl.append_event(led, 'RELOCATE', e, dict(root_id='ARCH', relative_path='W1/x.json'), dict(root_id='ARCH', relative_path='W2/x.json'), 'gen2', 'm')
        res = self.run_v(led)
        rec = next(r for r in res['occurrences'] if r['original_path'] == 'OLD_A/data/x.json')
        self.assertEqual(res['result'], 'PASS')
        self.assertEqual([x['to_location']['relative_path'] for x in rec['lineage']], ['W1/x.json', 'W2/x.json'])

    def test_rollback_event_restores_original(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        e = self.entries['OLD_A/data/x.json']
        (self.arch / 'W/x.json').rename(self.repo / 'OLD_A/data/x.json')
        rl.append_event(led, 'ROLLBACK', e, dict(root_id='ARCH', relative_path='W/x.json'), dict(root_id='REPO_ROOT', relative_path='OLD_A/data/x.json'), 'rb', 'm')
        res = self.run_v(led)
        self.assertEqual(res['result'], 'PASS')
        self.assertEqual(self.status(res, 'OLD_A/data/x.json'), 'ORIGINAL_PATH_PRESENT')
        self.assertEqual(len(led['events']), 2)

    # ---------- negative ----------
    def test_original_missing_without_ledger(self):
        (self.repo / 'OLD_B/z.IDX').unlink()
        res = self.run_v()
        self.assertEqual(res['result'], 'FAIL')
        self.assertEqual(self.status(res, 'OLD_B/z.IDX'), 'MISSING')

    def test_destination_missing(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        (self.arch / 'W/x.json').unlink()
        self.assertEqual(self.status(self.run_v(led), 'OLD_A/data/x.json'), 'MISSING')

    def test_hash_altered(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        (self.arch / 'W/x.json').write_bytes(b'{"a":9}\n')
        res = self.run_v(led)
        self.assertEqual(res['result'], 'FAIL')
        self.assertEqual(self.status(res, 'OLD_A/data/x.json'), 'HASH_MISMATCH')

    def test_size_altered(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        (self.arch / 'W/x.json').write_bytes(b'{"a":1}\n\n')
        res = self.run_v(led)
        rec = next(r for r in res['occurrences'] if r['original_path'] == 'OLD_A/data/x.json')
        self.assertEqual((res['result'], rec['status'], rec['problems']), ('FAIL', 'HASH_MISMATCH', ['SIZE_MISMATCH']))

    def test_ledger_without_occurrence(self):
        led = self.ledger()
        (self.arch / 'W').mkdir()
        (self.repo / 'OLD_A/data/x.json').rename(self.arch / 'W/x.json')
        self.assertEqual(self.status(self.run_v(led), 'OLD_A/data/x.json'), 'MISSING')

    def test_two_destinations(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W1/x.json', led)
        e = self.entries['OLD_A/data/x.json']
        (self.arch / 'W2').mkdir()
        shutil.copy2(self.arch / 'W1/x.json', self.arch / 'W2/x.json')
        rl.append_event(led, 'RELOCATE', e, dict(root_id='REPO_ROOT', relative_path='OLD_A/data/x.json'), dict(root_id='ARCH', relative_path='W2/x.json'), 'dup', 'm')
        res = self.run_v(led)
        self.assertEqual(res['result'], 'FAIL')
        self.assertEqual(self.status(res, 'OLD_A/data/x.json'), 'AMBIGUOUS_RELOCATION')

    def test_stale_copy_left_at_original(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        shutil.copy2(self.arch / 'W/x.json', self.repo / 'OLD_A/data/x.json')
        self.assertEqual(self.status(self.run_v(led), 'OLD_A/data/x.json'), 'AMBIGUOUS_RELOCATION')

    def test_cycle(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        e = self.entries['OLD_A/data/x.json']
        (self.arch / 'W/x.json').rename(self.repo / 'OLD_A/data/x.json')
        rl.append_event(led, 'RELOCATE', e, dict(root_id='ARCH', relative_path='W/x.json'), dict(root_id='REPO_ROOT', relative_path='OLD_A/data/x.json'), 'cycle', 'm')
        res = self.run_v(led)
        rec = next(r for r in res['occurrences'] if r['original_path'] == 'OLD_A/data/x.json')
        self.assertEqual((res['result'], rec['status']), ('FAIL', 'INVALID_LINEAGE'))
        self.assertIn('CYCLE', rec['problems'])

    def test_wrong_from_path(self):
        led = self.ledger()
        (self.arch / 'W').mkdir()
        (self.repo / 'OLD_A/data/x.json').rename(self.arch / 'W/x.json')
        rl.append_event(led, 'RELOCATE', self.entries['OLD_A/data/x.json'], dict(root_id='REPO_ROOT', relative_path='OLD_A/other/x.json'),
                        dict(root_id='ARCH', relative_path='W/x.json'), 'bad', 'm')
        res = self.run_v(led)
        rec = next(r for r in res['occurrences'] if r['original_path'] == 'OLD_A/data/x.json')
        self.assertEqual((res['result'], rec['status'], rec['problems']), ('FAIL', 'INVALID_LINEAGE', ['BROKEN_LINEAGE']))

    def test_wrong_occurrence(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        ev = led['events'][0]
        ev['original']['sha256'] = self.entries['OLD_A/data/y.json']['sha256']
        ev['event_hash'] = rl.event_hash(ev)
        led['head']['event_hash'] = ev['event_hash']
        res = self.run_v(led)
        self.assertEqual(res['result'], 'FAIL')
        self.assertIn('WRONG_OCCURRENCE', next(r for r in res['occurrences'] if r['original_path'] == 'OLD_A/data/x.json')['problems'])

    def test_destination_holds_other_occurrence(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        shutil.copy2(self.repo / 'OLD_A/data/y.json', self.arch / 'W/x.json')
        self.assertEqual(self.status(self.run_v(led), 'OLD_A/data/x.json'), 'HASH_MISMATCH')

    def test_unknown_occurrence(self):
        led = self.ledger()
        fake = dict(path='NOT/IN/PROOF.json', sha256='0' * 64, bytes=1)
        rl.append_event(led, 'RELOCATE', fake, dict(root_id='REPO_ROOT', relative_path='NOT/IN/PROOF.json'), dict(root_id='ARCH', relative_path='W/p.json'), 'x', 'm')
        res = self.run_v(led)
        self.assertEqual(res['result'], 'FAIL')
        self.assertTrue(any(e.startswith('UNKNOWN_OCCURRENCE') for e in res['ledger_errors']))

    def test_casefold_collision(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/Data.json', led)
        (self.arch / 'W2').mkdir()
        (self.repo / 'OLD_A/data/y.json').rename(self.arch / 'W2/y.json')
        rl.append_event(led, 'RELOCATE', self.entries['OLD_A/data/y.json'], dict(root_id='REPO_ROOT', relative_path='OLD_A/data/y.json'),
                        dict(root_id='ARCH', relative_path='w/data.JSON'), 'collide', 'm')
        res = self.run_v(led)
        self.assertEqual(res['result'], 'FAIL')
        self.assertIn('LOCATION_COLLISION_CASEFOLD_NFC', next(r for r in res['occurrences'] if r['original_path'] == 'OLD_A/data/x.json')['problems'])

    def test_nfc_collision_and_non_nfc_path(self):
        led = self.ledger()
        (self.arch / 'W').mkdir()
        (self.repo / 'OLD_A/data/x.json').rename(self.arch / 'W/x.json')
        rl.append_event(led, 'RELOCATE', self.entries['OLD_A/data/x.json'], dict(root_id='REPO_ROOT', relative_path='OLD_A/data/x.json'),
                        dict(root_id='ARCH', relative_path='W/Cá.json'), 'nfd', 'm')
        rec = next(r for r in self.run_v(led)['occurrences'] if r['original_path'] == 'OLD_A/data/x.json')
        self.assertEqual(rec['status'], 'INVALID_LINEAGE')
        self.assertIn('UNSAFE_PATH:NON_NFC_PATH', rec['problems'])

    def test_path_traversal(self):
        led = self.ledger()
        rl.append_event(led, 'RELOCATE', self.entries['OLD_B/z.IDX'], dict(root_id='REPO_ROOT', relative_path='OLD_B/z.IDX'),
                        dict(root_id='ARCH', relative_path='../escape/z.IDX'), 'trav', 'm')
        rec = next(r for r in self.run_v(led)['occurrences'] if r['original_path'] == 'OLD_B/z.IDX')
        self.assertIn('UNSAFE_PATH:PATH_TRAVERSAL', rec['problems'])

    def test_ledger_tampered(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        led['events'][0]['reason'] = 'edited later'
        res = self.run_v(led)
        self.assertEqual(res['result'], 'FAIL')
        self.assertTrue(any('event_hash' in e for e in res['ledger_errors']))

    def test_ledger_truncated(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        self.move('OLD_A/data/y.json', 'W/y.json', led)
        anchor = led['head']['event_hash']
        led['events'].pop()
        res = self.run_v(led, anchor)
        self.assertEqual(res['result'], 'FAIL')
        self.assertTrue(any(e.startswith('LEDGER_TRUNCATED') for e in res['ledger_errors']))

    def test_ledger_truncated_with_rewritten_head_caught_by_anchor(self):
        led = self.ledger()
        self.move('OLD_A/data/x.json', 'W/x.json', led)
        self.move('OLD_A/data/y.json', 'W/y.json', led)
        anchor = led['head']['event_hash']
        led['events'].pop()
        led['head'] = dict(count=1, event_hash=led['events'][0]['event_hash'])
        (self.arch / 'W/y.json').rename(self.repo / 'OLD_A/data/y.json')
        res = self.run_v(led, anchor)
        self.assertIn('LEDGER_TRUNCATED_OR_CORRUPT:anchor_mismatch', res['ledger_errors'])

    def test_original_proof_changed(self):
        pf = self.repo / PROOF
        pf.write_bytes(pf.read_bytes() + b' ')
        self.assertIn('ORIGINAL_PROOF_HASH_MISMATCH', self.run_v()['ledger_errors'])


if __name__ == '__main__':
    unittest.main()
