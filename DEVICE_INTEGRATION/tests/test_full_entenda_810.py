"""FULL_CF_ENTENDA_810: SD overlay candidate with every HUMAN_APPROVED_T1 ENTENDA of the final reconciliation (Macro07 x Macro08).

Candidate: DEVICE_INTEGRATION/staging_sd_v1_full_entenda_810_candidate (tools/build_full_entenda_810_candidate.py), compared with the
physically approved BATCH04_RUN3 package (staging_sd_v1_batch04_run3_candidate). Numbers are derived from the corpora, never listed."""
import hashlib
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'ENTENDA_ENGINE'))
import build_sd_staging as S  # noqa: E402
import device_lookup_simulator as SIM  # noqa: E402
import entenda_engine as E  # noqa: E402

NEW = DI / 'staging_sd_v1_full_entenda_810_candidate/SD/99_LEX_V1'
OLD = DI / 'staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1'
FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lookup(sd):
    rows = [l.split('|') for l in (sd / '30_ENTENDA/ENTENDA_LOOKUP.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    return rows, (sd / '30_ENTENDA/ENTENDA_PAYLOAD.DAT').read_bytes()


class SelectionFromRealCorpora(unittest.TestCase):
    def test_union_of_the_approved_chain(self):
        prof = S.PROFILES['FULL_CF_ENTENDA_810']
        groups = S.approved_entenda_chain(E.NormContext('CF88'), prof['chain'])
        rows = [r for _, g in groups for r in g]
        self.assertTrue(all(r['status'] == 'ACTIVE' and r['review_status'] == 'HUMAN_APPROVED_T1' for r in rows))
        self.assertEqual(len({r['target_id'] for r in rows}), len(rows))
        self.assertEqual(len({r['explanation_key'] for r in rows}), len(rows))
        spec = json.loads((ROOT / prof['chain']['spec']).read_text(encoding='utf-8'))
        approved = lambda f: sum(1 for r in E.load_corpus(ROOT / f) if r['status'] == 'ACTIVE' and r['review_status'] == 'HUMAN_APPROVED_T1')  # noqa
        prior = [f for f in spec['prior_corpora'] if 'production_batch_07_macro' not in f]
        before_macro07 = approved('ENTENDA_ENGINE/corpus/CF88.entenda.jsonl') + sum(approved(f) for f in prior)
        macro07 = approved('ENTENDA_ENGINE/derived/production_batch_07_macro/CF88_MACRO_07.entenda.jsonl')
        macro08 = approved(prof['chain']['corpus'])
        self.assertEqual(len(rows), before_macro07 + macro07 + macro08)
        self.assertEqual((before_macro07, macro07, macro08), (382, 249, 179))      # reconciliation accounting (fa9719a)
        self.assertEqual([len(g) for _, g in groups], [before_macro07 + macro07, macro08])


@unittest.skipUnless((NEW / '00_SYS/LEXV1.VER').is_file() and (OLD / '00_SYS/LEXV1.VER').is_file(), 'staging candidates not built')
class FullEntendaPackage(unittest.TestCase):
    def test_version_file_schema_3_and_count(self):
        ver = dict(l.split('|', 1) for l in (NEW / '00_SYS/LEXV1.VER').read_text(encoding='utf-8').splitlines()[1:])
        self.assertTrue((NEW / '00_SYS/LEXV1.VER').read_text(encoding='utf-8').startswith('#LEXMACHINA|DEVICE_VERSION|3\n'))
        rows, _ = lookup(NEW)
        self.assertEqual(int(ver['ENTENDA_COUNT']), sum(1 for r in rows if r[7] == 'DIRECT'))
        self.assertEqual(ver['ENTENDA_SCOPE'], 'CF88_ADCT_FULL_HUMAN_APPROVED_T1')
        self.assertLess(int(ver['ENTENDA_COUNT']), 65536)                                    # uint16_t entendaCount in the firmware

    def test_only_the_five_expected_files_change(self):
        new = {p.relative_to(NEW).as_posix(): sha(p) for p in NEW.rglob('*') if p.is_file()}
        old = {p.relative_to(OLD).as_posix(): sha(p) for p in OLD.rglob('*') if p.is_file()}
        self.assertEqual(set(new), set(old))
        self.assertEqual(sorted(k for k in new if new[k] != old[k]),
                         ['00_SYS/LEXV1.VER', '00_SYS/LEX_DEVICE_MANIFEST.json', '10_TARGETS/CF88_TARGETS.IDX', '30_ENTENDA/ENTENDA_LOOKUP.IDX',
                          '30_ENTENDA/ENTENDA_PAYLOAD.DAT'])

    def test_lookup_payload_offsets_and_blocks(self):
        rows, pay = lookup(NEW)
        keys = [r[0] for r in rows]
        self.assertEqual(keys, sorted(keys, key=lambda k: k.encode('utf-8')))
        self.assertEqual(len(keys), len(set(keys)))
        direct = {(r[1], r[2], r[3]) for r in rows if r[7] == 'DIRECT'}
        spans = sorted((int(o), int(n)) for o, n, _ in direct)
        self.assertEqual(spans[-1][0] + spans[-1][1], len(pay))
        self.assertTrue(all(spans[i][0] + spans[i][1] == spans[i + 1][0] for i in range(len(spans) - 1)))
        for r in rows:
            self.assertEqual(r[6], 'HUMAN_APPROVED_T1', r[0])
            blob = pay[int(r[1]):int(r[1]) + int(r[2])]
            self.assertTrue(blob.startswith(f'@{r[3]}\n'.encode()) and blob.rstrip(b'\n').endswith(b'@END'), r[0])
            if r[7] == 'COVERED_BY_BLOCK':
                self.assertIn((r[1], r[2], r[3]), direct, r[0])

    def test_firmware_buffers_hold_every_block(self):
        src = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8') + (FW / 'lex_device_v1.h').read_text(encoding='utf-8')
        const = {k: int(v) for k, v in re.findall(r'#define (LEXV1_\w+) (\d+)\b', src)}
        rows, pay = lookup(NEW)
        for r in rows:
            n = int(r[2])
            self.assertLessEqual(n, const['LEXV1_BLOCO_MAX'], r[0])
            self.assertLess(len(r[0]), const['LEXV1_KEY_MAX'])
            self.assertLess(len('|'.join(r)), const['LEXV1_LINE_MAX'])
            blob = pay[int(r[1]):int(r[1]) + n]
            title = [l for l in blob.split(b'\n') if l.startswith(b'D|')]
            self.assertTrue(title and len(title[0]) - 2 < const['LEXV1_TITLE_MAX'], r[0])
        self.assertNotRegex(src, r'entendaCount\s*(==|!=|<|>|<=|>=)\s*\d{3}')            # no fixed explanation count

    def test_the_220_physical_blocks_are_unchanged(self):
        new_rows, new_pay = lookup(NEW)
        old_rows, old_pay = lookup(OLD)
        nb = {r[0]: (r[3:], new_pay[int(r[1]):int(r[1]) + int(r[2])]) for r in new_rows}
        for r in old_rows:
            self.assertEqual(nb[r[0]], (r[3:], old_pay[int(r[1]):int(r[1]) + int(r[2])]), r[0])

    def test_targets_flags_follow_the_lookup(self):
        rows, _ = lookup(NEW)
        res = {r[0]: r[7] for r in rows}
        new = [l.split('|') for l in (NEW / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
        old = {l.split('|')[0]: l.split('|') for l in (OLD / '10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')}
        self.assertEqual(len(new), len(old))
        for t in new:
            self.assertEqual(t[3][0], {'DIRECT': 'E', 'COVERED_BY_BLOCK': 'B'}.get(res.get(t[0]), '-'), t[0])
            self.assertEqual((old[t[0]][:3], old[t[0]][3][1:5]), (t[:3], t[3][1:5]), t[0])   # kind, status, C/J/W/R untouched
        self.assertTrue(set(res) <= {t[0] for t in new})

    def test_simulated_device_lookups(self):
        dev = SIM.Device(NEW)
        try:
            for q in ('CF88:ART.5', 'CF88:ART.5:INC.V', 'CF88:ART.37', 'CF88:ART.76', 'CF88:ART.100', 'CF88:ART.142', 'CF88:ART.156-A',
                      'CF88:ART.175', 'ADCT:ART.10:INC.II', 'ADCT:ART.101', 'CF88:ART.100:PAR.10'):
                self.assertTrue(dev.entenda(q, SIM.Stats()), q)
            for q in ('CF88:ART.999', 'CF88:ART.114:INC.VIII'):
                self.assertFalse(dev.entenda(q, SIM.Stats()), q)                          # fail closed / no layer 3
        finally:
            dev.close()

    def test_firmware_fixed_diag_cases_match_the_810_lookup(self):
        """Boot self-test table casos[]: every expectation must match the approved lookup (CF88:ART.127 is DIRECT since Macro07;
        the stale NONE expectation was the only one and was corrected in the diagnostic table only)."""
        rows, _ = lookup(NEW)
        res = {r[0]: r for r in rows}
        ino = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
        cases = re.findall(r'\{"([A-Z0-9:.\-]+)",(true|false),LEXV1_RES_(\w+),"([^"]*)"', ino)
        self.assertEqual(len(cases), 10)
        for tid, exists, want, anchor in cases:
            got = res.get(tid)
            self.assertEqual(want, 'NONE' if got is None else got[7], tid)
            if got is not None and got[7] == 'DIRECT':
                self.assertEqual(anchor, tid, tid)
        self.assertIn('{"CF88:ART.127",true,LEXV1_RES_DIRECT,"CF88:ART.127",1,1}', ino)

if __name__ == '__main__':
    unittest.main()
