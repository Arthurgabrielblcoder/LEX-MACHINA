"""Build isolated CC-10 candidate with a historical-only block 757-802."""
from __future__ import annotations
import argparse,hashlib,importlib,json,tempfile
from collections import Counter
from pathlib import Path
import entenda_engine as E
ROOT=Path(__file__).resolve().parents[1]; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_850"; CONFIG=BATCH/"CC10_ENTENDA_CONFIG.json"; BASELINE=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_700"/"CC2002_CC09.entenda.jsonl"
CORPUS,DRAFTS,MANIFEST,COVERAGE=BATCH/"CC2002_CC10.entenda.jsonl",BATCH/"CC10_DRAFTS.json",BATCH/"CC10_MANIFEST.json",BATCH/"CC10_COVERAGE.json"; INDEX=BATCH/"candidate_index"; CHECKPOINTS=BATCH/"checkpoints"; EXPECTED="372e427d6268e38685b78dfba18ba5e87c3c7d95ca997c4356e77128e1a03eec"
BLOCKS={"701_730":[str(n) for n in range(701,731)],"731_756":[str(n) for n in range(731,757)],"757_802":[],"803_826":[str(n) for n in range(803,827)],"827_850":[str(n) for n in range(827,851)]}; MODULES=("cc10_editorial_701_756","cc10_editorial_803_826","cc10_editorial_827_850")
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def all_rows():
 rows={}
 for name in MODULES:
  mod=importlib.import_module(name); rows.update(mod.ROWS)
 expected={str(n) for n in range(701,757)}|{str(n) for n in range(803,851)}
 if set(rows)!=expected: raise SystemExit("CC10_EDITORIAL_ROWS_MISMATCH")
 return rows
def draft(rows,sel): return {"schema_version":1,"norma_id":"CC2002","template_version":"ENTENDA-T1","prompt_version":"CC10-DELEGATED-PRODUCTION-V1","review_status":"PENDING_HUMAN_REVIEW","authoring":{"method":"ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW","mission":"CC-10","generated_on":"2026-11-09","human_approval_claimed":False},"explanations":[{"target_id":f"CC2002:ART.{n}","role":"OVERVIEW","semantic_autonomy":"AUTONOMOUS","editorial_reason":"Explicação específica do dispositivo vigente, auditada quanto a requisitos, sujeitos, exceções e consequências.","content":{k:rows[n][k] for k in ("o_que_diz","o_que_significa","exemplo_pratico","atencao","palavras_dificeis")},"external_layer_notes":[],"review_status":"PENDING_HUMAN_REVIEW","editorial_version":1} for n in sel]}
def build(through=5,out=None):
 if sha(BASELINE.read_bytes())!=EXPECTED: raise SystemExit("CC10_BASELINE_MISMATCH")
 names=list(BLOCKS)[:through]; sel=[n for name in names for n in BLOCKS[name]]; ctx=E.NormContext("CC2002",config_path=CONFIG); existing=E.load_corpus(BASELINE); drafts=draft(all_rows(),sel); records=E.stamp(drafts,ctx,existing=existing); E.validate_corpus(records,ctx); root=BATCH if out is None else out; cp=root/CORPUS.name; E.write_corpus(records,cp,ctx); write(root/DRAFTS.name,drafts); im=E.build_entenda_index(ctx,records,root/"candidate_index"); active=[r for r in records if r["status"]=="ACTIVE"]; new=[r for r in active if 701<=int(r["target_id"].split("ART.",1)[1].split(":",1)[0].split("-")[0])<=850]
 man={"schema_version":1,"mission":"CC-10","candidate_only":True,"deployed":False,"through_block":through,"completed_blocks":names,"cc09_records_preserved":len(existing),"active_total":len(active),"cc10_active":len(new),"cc10_review_status_counts":dict(sorted(Counter(r["review_status"] for r in new).items())),"corpus_sha256":sha(cp.read_bytes()),"candidate_index":im,"production_index_modified":False}; cov={"schema_version":1,"scope":"CC2002 arts. 701 a 850","numbered_positions_examined":150,"article_targets_examined":151,"expected_current_explanations":104,"produced_explanations":len(new),"remaining_explanations":104-len(new),"revoked_historical_articles":[f"CC2002:ART.{n}" for n in range(757,803)],"vetoed_without_active_explanation":["CC2002:ART.819-A"],"completed_blocks":names}; write(root/MANIFEST.name,man); write(root/COVERAGE.name,cov)
 if out is None:
  name=names[-1]; ms=BLOCKS[name]; br=[r for r in new if r["target_id"].split("ART.",1)[1].split(":",1)[0] in ms]; write(CHECKPOINTS/f"CC10_{name}.json",{"schema_version":1,"block":name,"kind":"HISTORICAL_RECONCILIATION" if not ms else "ACTIVE_PRODUCTION","expected_active":len(ms),"produced":len(br),"complete":len(br)==len(ms),"target_ids":[r["target_id"] for r in br],"historical_targets":[f"CC2002:ART.{n}" for n in range(757,803)] if name=="757_802" else [],"corpus_checkpoint_sha256":man["corpus_sha256"]})
 return man
def check():
 with tempfile.TemporaryDirectory(prefix=".cc10-check-",dir=BATCH) as td:
  tmp=Path(td); r=build(5,tmp); pairs=[(tmp/CORPUS.name,CORPUS),(tmp/DRAFTS.name,DRAFTS),(tmp/MANIFEST.name,MANIFEST),(tmp/COVERAGE.name,COVERAGE)]+[(tmp/"candidate_index"/n,INDEX/n) for n in ("ENTENDA_LOOKUP.IDX","ENTENDA_PAYLOAD.DAT","ENTENDA_BUILD_MANIFEST.json")]; bad=[str(d.relative_to(ROOT)) for s,d in pairs if not d.is_file() or s.read_bytes()!=d.read_bytes()]
  if bad: raise SystemExit("CC10_NOT_REPRODUCIBLE: "+", ".join(bad))
  return r
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--through-block",type=int,default=5); p.add_argument("--check",action="store_true"); a=p.parse_args(); print(json.dumps(check() if a.check else build(a.through_block),ensure_ascii=False,indent=2))
