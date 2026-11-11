import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"ENTENDA_ENGINE")); import entenda_engine as E  # noqa
from cc11_build import BASELINE,BATCH,BLOCKS,CONFIG,CORPUS  # noqa
PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"; PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class CC11Test(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.rows=E.load_corpus(CORPUS); c.base=E.load_corpus(BASELINE); c.active={r["target_id"]:r for r in c.rows if r["status"]=="ACTIVE"}; c.ctx=E.NormContext("CC2002",config_path=CONFIG); c.matrix=json.loads((BATCH/"CC11_DELEGATED_REVIEW_MATRIX.json").read_text())
 def test_counts(self): self.assertEqual((len(self.rows),len(self.active)),(1527,1364)); self.assertEqual(sum(r["status"]=="RETIRED" for r in self.rows),163)
 def test_baseline(self):
  self.assertEqual(sha(BASELINE),"7989063587a308184852e87a9489733b8b3502366e9c46a5d3a2983f39ab1802"); by={r["explanation_id"]:r for r in self.rows}; self.assertEqual(len(self.base),1157); self.assertTrue(all(by[r["explanation_id"]]==r for r in self.base))
 def test_new_coverage(self):
  expected={f"CC2002:ART.{n}" for values in BLOCKS.values() for n in values}; actual={x for x in self.active if x.startswith("CC2002:ART.") and 1041<=int(x.split("ART.",1)[1].split(":",1)[0].split("-")[0])<=1380}; self.assertEqual(actual,expected); self.assertEqual(len(expected),370)
 def test_intercalated(self): self.assertEqual(sum("-" in x.split("ART.",1)[1] for x in {f"CC2002:ART.{n}" for values in BLOCKS.values() for n in values}),30)
 def test_article_1337(self): self.assertIn("CC2002:ART.1337",self.active); self.assertEqual(self.ctx.effective_status("CC2002:ART.1337"),"CURRENT")
 def test_contract(self): E.validate_corpus(self.rows,self.ctx); self.assertEqual(len({r["explanation_id"] for r in self.rows}),len(self.rows)); self.assertNotIn(b"\xef\xbf\xbd",CORPUS.read_bytes())
 def test_review(self): self.assertEqual(self.matrix["reviewed_records"],370); self.assertEqual(self.matrix["classification_counts"]["C"]+self.matrix["classification_counts"]["D"],0); self.assertFalse(self.matrix["human_approval_claimed"])
 def test_checkpoints(self):
  self.assertEqual(len(BLOCKS),10)
  for name in BLOCKS: self.assertTrue((BATCH/"checkpoints"/f"CC11_{name}.json").is_file()); self.assertTrue((BATCH/"audit_blocks"/f"CC11_AUDIT_{name}.json").is_file())
 def test_production(self): self.assertTrue(all(sha(PROD/"index"/n)==h for n,h in PH.items()))
if __name__=="__main__": unittest.main()
