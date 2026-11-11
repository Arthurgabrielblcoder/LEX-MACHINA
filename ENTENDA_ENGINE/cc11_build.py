"""Build the isolated ten-checkpoint CC-11 candidate through Civil Code art. 1,380."""
from __future__ import annotations
import argparse,hashlib,importlib,json,tempfile
from collections import Counter
from pathlib import Path
import entenda_engine as E
ROOT=Path(__file__).resolve().parents[1]; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1380"; CONFIG=BATCH/"CC11_ENTENDA_CONFIG.json"
BASELINE=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1040"/"CC2002_CC10.entenda.jsonl"
CORPUS=BATCH/"CC2002_CC11.entenda.jsonl"; DRAFTS=BATCH/"CC11_DRAFTS.json"; MANIFEST=BATCH/"CC11_MANIFEST.json"; COVERAGE=BATCH/"CC11_COVERAGE.json"; INDEX=BATCH/"candidate_index"; CHECKPOINTS=BATCH/"checkpoints"
EXPECTED="7989063587a308184852e87a9489733b8b3502366e9c46a5d3a2983f39ab1802"
BLOCKS={
 "1041_1074":[str(n) for n in range(1041,1075)],
 "1075_1108":[str(n) for n in range(1075,1109)]+["1080-A"],
 "1109_1142":[str(n) for n in range(1109,1143)],
 "1143_1176":[str(n) for n in range(1143,1177)],
 "1177_1210":[str(n) for n in range(1177,1211)],
 "1211_1244":[str(n) for n in range(1211,1245)]+["1240-A"],
 "1245_1278":[str(n) for n in range(1245,1279)],
 "1279_1312":[str(n) for n in range(1279,1313)],
 "1313_1346":[str(n) for n in range(1313,1347)],
 "1347_1380":[str(n) for n in range(1347,1381)]+["1354-A"]+[f"1358-{x}" for x in "ABCDEFGHIJKLMNOPQRSTU"]+[f"1368-{x}" for x in "ABCDEF"],
}
MODULES=("cc11_editorial_1041_1162","cc11_editorial_1163_1284","cc11_editorial_1285_1380")
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def all_rows():
 rows={}
 for name in MODULES:
  mod=importlib.import_module(name); overlap=set(rows)&set(mod.ROWS)
  if overlap: raise SystemExit("CC11_EDITORIAL_DUPLICATE_ROWS: "+", ".join(sorted(overlap)))
  rows.update(mod.ROWS)
 expected={n for values in BLOCKS.values() for n in values}
 if set(rows)!=expected: raise SystemExit(f"CC11_EDITORIAL_ROWS_MISMATCH missing={sorted(expected-set(rows))} extra={sorted(set(rows)-expected)}")
 return rows
def draft(rows,selected):
 return {"schema_version":1,"norma_id":"CC2002","template_version":"ENTENDA-T1","prompt_version":"CC11-AMPLIADA-DELEGATED-PRODUCTION-V1","review_status":"PENDING_HUMAN_REVIEW","authoring":{"method":"ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW","mission":"CC-11","generated_on":"2026-11-11","human_approval_claimed":False},"explanations":[{"target_id":f"CC2002:ART.{n}","role":"OVERVIEW","semantic_autonomy":"AUTONOMOUS","editorial_reason":"Explicação específica do dispositivo vigente, auditada quanto a requisitos, sujeitos, exceções e consequências.","content":{k:rows[n][k] for k in ("o_que_diz","o_que_significa","exemplo_pratico","atencao","palavras_dificeis")},"external_layer_notes":[],"review_status":"PENDING_HUMAN_REVIEW","editorial_version":1} for n in selected]}
def build(through=10,out=None):
 if sha(BASELINE.read_bytes())!=EXPECTED: raise SystemExit("CC11_BASELINE_MISMATCH")
 names=list(BLOCKS)[:through]; selected=[n for name in names for n in BLOCKS[name]]; ctx=E.NormContext("CC2002",config_path=CONFIG); existing=E.load_corpus(BASELINE); drafts=draft(all_rows(),selected); records=E.stamp(drafts,ctx,existing=existing); E.validate_corpus(records,ctx)
 root=BATCH if out is None else out; cp=root/CORPUS.name; E.write_corpus(records,cp,ctx); write(root/DRAFTS.name,drafts); im=E.build_entenda_index(ctx,records,root/"candidate_index"); active=[r for r in records if r["status"]=="ACTIVE"]
 new=[r for r in active if 1041<=int(r["target_id"].split("ART.",1)[1].split(":",1)[0].split("-")[0])<=1380]
 man={"schema_version":1,"mission":"CC-11","candidate_only":True,"deployed":False,"through_block":through,"completed_blocks":names,"cc10_records_preserved":len(existing),"active_total":len(active),"cc11_active":len(new),"cc11_review_status_counts":dict(sorted(Counter(r["review_status"] for r in new).items())),"corpus_sha256":sha(cp.read_bytes()),"candidate_index":im,"production_index_modified":False}
 cov={"schema_version":1,"scope":"CC2002 arts. 1.041 a 1.380","numbered_positions_examined":340,"article_targets_examined":370,"expected_current_explanations":370,"produced_explanations":len(new),"remaining_explanations":370-len(new),"revoked_or_vetoed_in_scope":[],"intercalated":[f"CC2002:ART.{n}" for n in [x for values in BLOCKS.values() for x in values if "-" in x]],"completed_blocks":names}; write(root/MANIFEST.name,man); write(root/COVERAGE.name,cov)
 if out is None:
  name=names[-1]; expected=BLOCKS[name]; produced=[r for r in new if r["target_id"].split("ART.",1)[1].split(":",1)[0] in expected]
  write(CHECKPOINTS/f"CC11_{name}.json",{"schema_version":1,"block":name,"kind":"ACTIVE_PRODUCTION","expected_active":len(expected),"produced":len(produced),"complete":len(produced)==len(expected),"target_ids":[r["target_id"] for r in produced],"historical_targets":[],"corpus_checkpoint_sha256":man["corpus_sha256"]})
 return man
def check():
 with tempfile.TemporaryDirectory(prefix=".cc11-check-",dir=BATCH) as td:
  tmp=Path(td); result=build(10,tmp); pairs=[(tmp/CORPUS.name,CORPUS),(tmp/DRAFTS.name,DRAFTS),(tmp/MANIFEST.name,MANIFEST),(tmp/COVERAGE.name,COVERAGE)]+[(tmp/"candidate_index"/n,INDEX/n) for n in ("ENTENDA_LOOKUP.IDX","ENTENDA_PAYLOAD.DAT","ENTENDA_BUILD_MANIFEST.json")]; bad=[str(d.relative_to(ROOT)) for s,d in pairs if not d.is_file() or s.read_bytes()!=d.read_bytes()]
  if bad: raise SystemExit("CC11_NOT_REPRODUCIBLE: "+", ".join(bad))
  return result
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--through-block",type=int,default=10); p.add_argument("--check",action="store_true"); a=p.parse_args(); print(json.dumps(check() if a.check else build(a.through_block),ensure_ascii=False,indent=2))
