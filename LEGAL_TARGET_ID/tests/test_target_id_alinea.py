"""Target grammar — alínea without inciso (codes such as CP, CPP, CTN, CLT). CF88/ADCT stay strict; every committed target id keeps
exactly the same parse and serialization (EXISTING_TARGET_IDS_CHANGED = 0)."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import target_id as T  # noqa: E402

EXAMPLES = HERE / 'derived' / 'ALINEA_WITHOUT_INCISO_EXAMPLES.json'


def roundtrip(tid):
    p = T.parse_target_id(tid)
    s = T.format_target_id(p['namespace'], p['article'], caput=p['caput'], paragraph=p['paragraph'], inciso=p['inciso'], alinea=p['alinea'])
    q = T.parse_target_id(s)
    return s, p, q


def committed_target_ids():
    files = subprocess.run(['git', 'ls-files', '*TARGET_INDEX.json', '*_TARGETS.IDX'], capture_output=True, text=True, cwd=REPO).stdout.split()
    ids = set()
    for f in files:
        path = REPO / f
        if f.endswith('.json'):
            ids |= {t['target_id'] for t in json.loads(path.read_text(encoding='utf-8'))['targets']}
        else:
            ids |= {l.split('|', 1)[0] for l in path.read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')}
    return files, ids


class AlineaWithoutInciso(unittest.TestCase):
    def test_real_examples_roundtrip(self):
        norms = json.loads(EXAMPLES.read_text(encoding='utf-8'))['norms']
        self.assertEqual(sorted(norms), ['CLT1943', 'CP1940', 'CPP1941', 'CTN1966'])
        for n, d in norms.items():
            self.assertTrue(d['all_target_ids'], n)
            self.assertEqual(d['grammar_anomalies_after'], 0)
            for tid in d['all_target_ids']:
                s, p, q = roundtrip(tid)
                self.assertEqual((s, p), (tid, q), tid)
                self.assertEqual((p['kind'], p['inciso']), ('ALINEA', None))
                parent = T.parent_target_id(tid)
                self.assertEqual(parent, T.format_target_id(n, p['article'], paragraph=p['paragraph']) if p['paragraph']
                                 else T.format_target_id(n, p['article'], caput=True))
        self.assertIn('CP1940:ART.7:PAR.2:AL.a', norms['CP1940']['all_target_ids'])       # CP art. 7º, § 2º, a

    def test_cf_and_adct_stay_strict(self):
        for tid in ('CF88:ART.37:AL.a', 'CF88:ART.37:PAR.6:AL.a', 'ADCT:ART.5:AL.a'):
            self.assertEqual(T.validate_target_id(tid), (False, 'ALINEA_WITHOUT_INCISO'))
        self.assertEqual(T.validate_target_id('CP1940:ART.7:CAPUT:AL.a'), (False, 'NON_CANONICAL'))
        self.assertTrue(T.registry().alinea_requires_inciso('CF88') and not T.registry().alinea_requires_inciso('CC2002'))

    def test_existing_target_ids_unchanged(self):
        files, ids = committed_target_ids()
        self.assertGreaterEqual(len(files), 30)
        changed = []
        for tid in ids:
            s, p, q = roundtrip(tid)
            if s != tid or p != q:
                changed.append(tid)
        self.assertEqual(changed, [])                                        # EXISTING_TARGET_IDS_CHANGED = 0
        self.assertFalse([t for t in ids if t.startswith(('CF88:', 'ADCT:', 'CC2002:')) and ':AL.' in t and ':INC.' not in t])


if __name__ == '__main__':
    unittest.main()
