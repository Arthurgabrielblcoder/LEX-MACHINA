import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"ENTENDA_ENGINE"))
import entenda_engine as E  # noqa: E402
from cc09_build import BASELINE,BATCH,BLOCKS,CONFIG,CORPUS  # noqa: E402
PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"; PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class CC09Test(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.rows=E.load_corpus(CORPUS); c.base=E.load_corpus(BASELINE); c.active={r["target_id"]:r for r in c.rows if r["status"]=="ACTIVE"}; c.matrix=json.loads((BATCH/"CC09_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8")); c.ctx=E.NormContext("CC2002",config_path=CONFIG)
 def test_counts_coverage(self):
  exp={f"CC2002:ART.{n}" for n in range(551,701)}; self.assertEqual({x for x in self.active if x in exp},exp); self.assertEqual((len(self.rows),len(self.active)),(862,699)); self.assertEqual(sum(r["status"]=="RETIRED" for r in self.rows),163)
 def test_baseline_exact(self):
  self.assertEqual(sha(BASELINE),"c1951fe3af7f514c17376864fa8b3692564c6621249804afc6dc177f37dcb8bc"); by={r["explanation_id"]:r for r in self.rows}; self.assertTrue(all(by[r["explanation_id"]]==r for r in self.base)); self.assertEqual((len(self.base),sum(r["status"]=="ACTIVE" for r in self.base)),(712,549))
 def test_blocks_audits(self):
  for name,ms in BLOCKS.items():
   cp=json.loads((BATCH/"checkpoints"/f"CC09_{name}.json").read_text(encoding="utf-8")); au=json.loads((BATCH/"audit_blocks"/f"CC09_AUDIT_{name}.json").read_text(encoding="utf-8")); self.assertEqual((cp["produced"],cp["complete"]),(len(ms),True)); self.assertEqual((au["reviewed"],au["complete"]),(len(ms),True))
 def test_review(self):
  self.assertEqual(self.matrix["classification_counts"],{"A":150,"B":0,"C":0,"D":0}); self.assertEqual(len(self.matrix["records"]),150); self.assertFalse(self.matrix["human_approval_claimed"]); self.assertTrue(all(r["formal_review_status"]=="PENDING_HUMAN_REVIEW" for r in self.matrix["records"]))
 def test_contract_utf8_unique(self):
  E.validate_corpus(self.rows,self.ctx); self.assertEqual(len({r["explanation_id"] for r in self.rows}),len(self.rows)); self.assertNotIn(b"\xef\xbf\xbd",CORPUS.read_bytes()); self.assertTrue(all(self.active[f"CC2002:ART.{n}"]["content"]["palavras_dificeis"] for n in range(551,701)))
 def test_sensitive_changes(self):
  a591=str(self.active["CC2002:ART.591"]["content"]).lower(); self.assertIn("taxa legal",a591); a693=str(self.active["CC2002:ART.693"]["content"]).lower(); self.assertIn("crédito",a693); a698=str(self.active["CC2002:ART.698"]["content"]).lower(); self.assertIn("parcial",a698)
 def test_deposit_caution(self):
  a=str(self.active["CC2002:ART.652"]["content"]).lower(); self.assertIn("não deve ser apresentada como automática",a); self.assertIn("constitucional",a)
 def test_production_immutable(self):
  rel=json.loads((BATCH/"CC09_RELEASE_MANIFEST.json").read_text(encoding="utf-8")); self.assertFalse(rel["deployed"]); self.assertTrue(all(sha(PROD/"index"/n)==h for n,h in PH.items()))
if __name__=="__main__": unittest.main()
