"""Build the isolated ten-checkpoint CC-12 candidate through Civil Code art. 1,720."""
from __future__ import annotations
import argparse,hashlib,importlib,json,tempfile
from collections import Counter
from pathlib import Path
import entenda_engine as E
ROOT=Path(__file__).resolve().parents[1]; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1720"; CONFIG=BATCH/"CC12_ENTENDA_CONFIG.json"; BASELINE=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1380"/"CC2002_CC11.entenda.jsonl"
CORPUS=BATCH/"CC2002_CC12.entenda.jsonl"; DRAFTS=BATCH/"CC12_DRAFTS.json"; MANIFEST=BATCH/"CC12_MANIFEST.json"; COVERAGE=BATCH/"CC12_COVERAGE.json"; INDEX=BATCH/"candidate_index"; CHECKPOINTS=BATCH/"checkpoints"; EXPECTED="e676be4c042cdf81dd05374cd7fe28431407e4e2fe59ff74922670c298ab969a"
BLOCKS={
 "1381_1414":[str(n) for n in range(1381,1415)],
 "1415_1448":[str(n) for n in range(1415,1449)],
 "1449_1482":[str(n) for n in range(1449,1483) if n not in (1463,1482)],
 "1483_1516":[str(n) for n in range(1483,1517) if n not in (1483,1494)]+["1487-A"]+[f"1510-{x}" for x in "ABCDE"],
 "1517_1550":[str(n) for n in range(1517,1551)],
 "1551_1584":[str(n) for n in range(1551,1585)],
 "1585_1618":[str(n) for n in range(1585,1619)],
 "1619_1652":[str(n) for n in range(1619,1653) if n not in range(1620,1630)],
 "1653_1686":[str(n) for n in range(1653,1687)],
 "1687_1720":[str(n) for n in range(1687,1721)],
}
HISTORICAL={"1449_1482":["1463","1482"],"1483_1516":["1483","1494"],"1619_1652":[str(n) for n in range(1620,1630)]}
MODULES=("cc12_editorial_1381_1494","cc12_editorial_1495_1605","cc12_editorial_1606_1720")
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def all_rows():
 rows={}
 for name in MODULES:
  mod=importlib.import_module(name); overlap=set(rows)&set(mod.ROWS)
  if overlap: raise SystemExit("CC12_EDITORIAL_DUPLICATE_ROWS: "+", ".join(sorted(overlap)))
  rows.update(mod.ROWS)
 expected={n for values in BLOCKS.values() for n in values}
 if set(rows)!=expected: raise SystemExit(f"CC12_EDITORIAL_ROWS_MISMATCH missing={sorted(expected-set(rows))} extra={sorted(set(rows)-expected)}")
 return rows
def draft(rows,selected):
 return {"schema_version":1,"norma_id":"CC2002","template_version":"ENTENDA-T1","prompt_version":"CC12-AMPLIADA-DELEGATED-PRODUCTION-V1","review_status":"PENDING_HUMAN_REVIEW","authoring":{"method":"ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW","mission":"CC-12","generated_on":"2026-11-11","human_approval_claimed":False},"explanations":[{"target_id":f"CC2002:ART.{n}","role":"OVERVIEW","semantic_autonomy":"AUTONOMOUS","editorial_reason":"Explicação específica do dispositivo vigente, auditada quanto a requisitos, sujeitos, exceções, consequências e interpretação contemporânea aplicável.","content":{k:rows[n][k] for k in ("o_que_diz","o_que_significa","exemplo_pratico","atencao","palavras_dificeis")},"external_layer_notes":[],"review_status":"PENDING_HUMAN_REVIEW","editorial_version":1} for n in selected]}
def build(through=10,out=None):
 if sha(BASELINE.read_bytes())!=EXPECTED: raise SystemExit("CC12_BASELINE_MISMATCH")
 names=list(BLOCKS)[:through]; selected=[n for name in names for n in BLOCKS[name]]; ctx=E.NormContext("CC2002",config_path=CONFIG); existing=E.load_corpus(BASELINE); drafts=draft(all_rows(),selected); records=E.stamp(drafts,ctx,existing=existing); E.validate_corpus(records,ctx); root=BATCH if out is None else out; cp=root/CORPUS.name; E.write_corpus(records,cp,ctx); write(root/DRAFTS.name,drafts); im=E.build_entenda_index(ctx,records,root/"candidate_index"); active=[r for r in records if r["status"]=="ACTIVE"]
 new=[r for r in active if 1381<=int(r["target_id"].split("ART.",1)[1].split(":",1)[0].split("-")[0])<=1720]
 man={"schema_version":1,"mission":"CC-12","candidate_only":True,"deployed":False,"through_block":through,"completed_blocks":names,"cc11_records_preserved":len(existing),"active_total":len(active),"cc12_active":len(new),"cc12_review_status_counts":dict(sorted(Counter(r["review_status"] for r in new).items())),"corpus_sha256":sha(cp.read_bytes()),"candidate_index":im,"production_index_modified":False}
 hist=[f"CC2002:ART.{n}" for n in (1463,1482,1483,1494,*range(1620,1630))]; inter=[f"CC2002:ART.{n}" for n in ("1487-A","1510-A","1510-B","1510-C","1510-D","1510-E")]
 cov={"schema_version":1,"scope":"CC2002 arts. 1.381 a 1.720","numbered_positions_examined":340,"indexed_article_targets_examined":337,"expected_current_explanations":332,"produced_explanations":len(new),"remaining_explanations":332-len(new),"revoked_historical_articles":hist,"vetoed_without_active_explanation":[],"active_intercalated":inter,"grouped_revocation_note":"A fonte consolida os arts. 1.620 a 1.629 em um único cabeçalho revogatório.","completed_blocks":names}; write(root/MANIFEST.name,man); write(root/COVERAGE.name,cov)
 if out is None:
  name=names[-1]; expected=BLOCKS[name]; produced=[r for r in new if r["target_id"].split("ART.",1)[1].split(":",1)[0] in expected]; hist_block=[f"CC2002:ART.{n}" for n in HISTORICAL.get(name,[])]
  write(CHECKPOINTS/f"CC12_{name}.json",{"schema_version":1,"block":name,"kind":"MIXED" if hist_block else "ACTIVE_PRODUCTION","expected_active":len(expected),"produced":len(produced),"complete":len(produced)==len(expected),"target_ids":[r["target_id"] for r in produced],"historical_targets":hist_block,"corpus_checkpoint_sha256":man["corpus_sha256"]})
 return man
def check():
 with tempfile.TemporaryDirectory(prefix=".cc12-check-",dir=BATCH) as td:
  tmp=Path(td); result=build(10,tmp); pairs=[(tmp/CORPUS.name,CORPUS),(tmp/DRAFTS.name,DRAFTS),(tmp/MANIFEST.name,MANIFEST),(tmp/COVERAGE.name,COVERAGE)]+[(tmp/"candidate_index"/n,INDEX/n) for n in ("ENTENDA_LOOKUP.IDX","ENTENDA_PAYLOAD.DAT","ENTENDA_BUILD_MANIFEST.json")]; bad=[str(d.relative_to(ROOT)) for s,d in pairs if not d.is_file() or s.read_bytes()!=d.read_bytes()]
  if bad: raise SystemExit("CC12_NOT_REPRODUCIBLE: "+", ".join(bad))
  return result
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--through-block",type=int,default=10); p.add_argument("--check",action="store_true"); a=p.parse_args(); print(json.dumps(check() if a.check else build(a.through_block),ensure_ascii=False,indent=2))
