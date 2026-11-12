import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"ENTENDA_ENGINE")); import entenda_engine as E  # noqa
from cc12_build import BASELINE,BATCH,BLOCKS,CONFIG,CORPUS  # noqa
PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"; PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class CC12Test(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.rows=E.load_corpus(CORPUS); c.base=E.load_corpus(BASELINE); c.active={r["target_id"]:r for r in c.rows if r["status"]=="ACTIVE"}; c.ctx=E.NormContext("CC2002",config_path=CONFIG); c.matrix=json.loads((BATCH/"CC12_DELEGATED_REVIEW_MATRIX.json").read_text())
 def test_counts(self): self.assertEqual((len(self.rows),len(self.active)),(1859,1696)); self.assertEqual(sum(r["status"]=="RETIRED" for r in self.rows),163)
 def test_baseline(self):
  self.assertEqual(sha(BASELINE),"e676be4c042cdf81dd05374cd7fe28431407e4e2fe59ff74922670c298ab969a"); by={r["explanation_id"]:r for r in self.rows}; self.assertEqual(len(self.base),1527); self.assertTrue(all(by[r["explanation_id"]]==r for r in self.base))
 def test_new_coverage(self):
  expected={f"CC2002:ART.{n}" for values in BLOCKS.values() for n in values}; actual={x for x in self.active if x.startswith("CC2002:ART.") and 1381<=int(x.split("ART.",1)[1].split(":",1)[0].split("-")[0])<=1720}; self.assertEqual(actual,expected); self.assertEqual(len(expected),332)
 def test_revoked_absent(self):
  for n in (1463,1482,1483,1494,*range(1620,1630)): self.assertNotIn(f"CC2002:ART.{n}",self.active)
  for n in (1463,1482,1483,1494,1620): self.assertEqual(self.ctx.effective_status(f"CC2002:ART.{n}"),"REVOKED")
 def test_intercalated_and_anomalies(self):
  expected={f"CC2002:ART.{n}" for n in ("1487-A","1510-A","1510-B","1510-C","1510-D","1510-E")}; self.assertTrue(expected<=set(self.active)); self.assertIn("CC2002:ART.1403",self.active); self.assertIn("CC2002:ART.1636",self.active)
 def test_contract(self): E.validate_corpus(self.rows,self.ctx); self.assertEqual(len({r["explanation_id"] for r in self.rows}),len(self.rows)); self.assertNotIn(b"\xef\xbf\xbd",CORPUS.read_bytes())
 def test_review(self): self.assertEqual(self.matrix["reviewed_records"],332); self.assertFalse(self.matrix["human_approval_claimed"])
 def test_checkpoints(self):
  self.assertEqual(len(BLOCKS),10)
  for name in BLOCKS: self.assertTrue((BATCH/"checkpoints"/f"CC12_{name}.json").is_file()); self.assertTrue((BATCH/"audit_blocks"/f"CC12_AUDIT_{name}.json").is_file())
 def test_production(self): self.assertTrue(all(sha(PROD/"index"/n)==h for n,h in PH.items()))
if __name__=="__main__": unittest.main()
