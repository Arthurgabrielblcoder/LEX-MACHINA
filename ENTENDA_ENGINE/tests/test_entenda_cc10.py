import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"ENTENDA_ENGINE")); import entenda_engine as E  # noqa
from cc10_build import BASELINE,BATCH,BLOCKS,CONFIG,CORPUS  # noqa
PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"; PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class CC10Test(unittest.TestCase):
 @classmethod
 def setUpClass(c): c.rows=E.load_corpus(CORPUS); c.base=E.load_corpus(BASELINE); c.active={r["target_id"]:r for r in c.rows if r["status"]=="ACTIVE"}; c.ctx=E.NormContext("CC2002",config_path=CONFIG); c.matrix=json.loads((BATCH/"CC10_DELEGATED_REVIEW_MATRIX.json").read_text())
 def test_counts(self): self.assertEqual((len(self.rows),len(self.active)),(966,803)); self.assertEqual(sum(r["status"]=="RETIRED" for r in self.rows),163)
 def test_baseline(self):
  self.assertEqual(sha(BASELINE),"372e427d6268e38685b78dfba18ba5e87c3c7d95ca997c4356e77128e1a03eec"); by={r["explanation_id"]:r for r in self.rows}; self.assertTrue(all(by[r["explanation_id"]]==r for r in self.base))
 def test_revoked_absent(self):
  for n in range(757,803): self.assertNotIn(f"CC2002:ART.{n}",self.active); self.assertEqual(self.ctx.effective_status(f"CC2002:ART.{n}"),"REVOKED")
 def test_veto_absent(self): self.assertNotIn("CC2002:ART.819-A",self.active); self.assertEqual(self.ctx.effective_status("CC2002:ART.819-A"),"REVOKED")
 def test_new_coverage(self):
  exp={f"CC2002:ART.{n}" for n in list(range(701,757))+list(range(803,851))}; self.assertEqual({x for x in self.active if x in exp},exp)
 def test_contract(self): E.validate_corpus(self.rows,self.ctx); self.assertEqual(len({r["explanation_id"] for r in self.rows}),len(self.rows)); self.assertNotIn(b"\xef\xbf\xbd",CORPUS.read_bytes())
 def test_review(self): self.assertEqual(self.matrix["classification_counts"],{"A":104,"B":0,"C":0,"D":0}); self.assertFalse(self.matrix["human_approval_claimed"])
 def test_production(self): self.assertTrue(all(sha(PROD/"index"/n)==h for n,h in PH.items()))
if __name__=="__main__": unittest.main()
