"""Build the final isolated ten-checkpoint CC-13 candidate through Civil Code art. 2,046."""
from __future__ import annotations
import argparse,hashlib,importlib,json,tempfile
from collections import Counter
from pathlib import Path
import entenda_engine as E
ROOT=Path(__file__).resolve().parents[1]; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_2046"; CONFIG=BATCH/"CC13_ENTENDA_CONFIG.json"; BASELINE=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1720"/"CC2002_CC12.entenda.jsonl"
CORPUS=BATCH/"CC2002_CC13.entenda.jsonl"; DRAFTS=BATCH/"CC13_DRAFTS.json"; MANIFEST=BATCH/"CC13_MANIFEST.json"; COVERAGE=BATCH/"CC13_COVERAGE.json"; INDEX=BATCH/"candidate_index"; CHECKPOINTS=BATCH/"checkpoints"; EXPECTED="76b945f8af99482fb54f93f6ae9d2da331fc5483470eb4bb7892fbcb19d51f24"
BLOCKS={
 "1721_1753":[str(n) for n in range(1721,1754)],
 "1754_1786":[str(n) for n in range(1754,1787) if n not in (*range(1768,1774),1776,1780)]+["1775-A","1783-A"],
 "1787_1819":[str(n) for n in range(1787,1820)]+["1815-A"],
 "1820_1852":[str(n) for n in range(1820,1853)],
 "1853_1885":[str(n) for n in range(1853,1886)],
 "1886_1918":[str(n) for n in range(1886,1919)],
 "1919_1951":[str(n) for n in range(1919,1952)],
 "1952_1984":[str(n) for n in range(1952,1985)],
 "1985_2017":[str(n) for n in range(1985,2018)],
 "2018_2046":[str(n) for n in range(2018,2047)],
}
HISTORICAL={"1754_1786":[str(n) for n in (*range(1768,1774),1776,1780)]}; MODULES=("cc13_editorial_1721_1828","cc13_editorial_1829_1937","cc13_editorial_1938_2046")
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def all_rows():
 rows={}
 for name in MODULES:
  mod=importlib.import_module(name); overlap=set(rows)&set(mod.ROWS)
  if overlap: raise SystemExit("CC13_EDITORIAL_DUPLICATE_ROWS: "+", ".join(sorted(overlap)))
  rows.update(mod.ROWS)
 expected={n for values in BLOCKS.values() for n in values}
 if set(rows)!=expected: raise SystemExit(f"CC13_EDITORIAL_ROWS_MISMATCH missing={sorted(expected-set(rows))} extra={sorted(set(rows)-expected)}")
 return rows
def draft(rows,selected):
 return {"schema_version":1,"norma_id":"CC2002","template_version":"ENTENDA-T1","prompt_version":"CC13-FINAL-DELEGATED-PRODUCTION-V1","review_status":"PENDING_HUMAN_REVIEW","authoring":{"method":"ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW","mission":"CC-13","generated_on":"2026-11-12","human_approval_claimed":False},"explanations":[{"target_id":f"CC2002:ART.{n}","role":"OVERVIEW","semantic_autonomy":"AUTONOMOUS","editorial_reason":"Explicação específica do dispositivo vigente, auditada quanto a requisitos, exceções, consequências, interpretação constitucional e direito intertemporal aplicáveis.","content":{k:rows[n][k] for k in ("o_que_diz","o_que_significa","exemplo_pratico","atencao","palavras_dificeis")},"external_layer_notes":[],"review_status":"PENDING_HUMAN_REVIEW","editorial_version":1} for n in selected]}
def build(through=10,out=None):
 if sha(BASELINE.read_bytes())!=EXPECTED: raise SystemExit("CC13_BASELINE_MISMATCH")
 names=list(BLOCKS)[:through]; selected=[n for name in names for n in BLOCKS[name]]; ctx=E.NormContext("CC2002",config_path=CONFIG); existing=E.load_corpus(BASELINE); drafts=draft(all_rows(),selected); records=E.stamp(drafts,ctx,existing=existing); E.validate_corpus(records,ctx); root=BATCH if out is None else out; cp=root/CORPUS.name; E.write_corpus(records,cp,ctx); write(root/DRAFTS.name,drafts); im=E.build_entenda_index(ctx,records,root/"candidate_index"); active=[r for r in records if r["status"]=="ACTIVE"]
 new=[r for r in active if 1721<=int(r["target_id"].split("ART.",1)[1].split(":",1)[0].split("-")[0])<=2046]; man={"schema_version":1,"mission":"CC-13","candidate_only":True,"deployed":False,"through_block":through,"completed_blocks":names,"cc12_records_preserved":len(existing),"active_total":len(active),"cc13_active":len(new),"cc13_review_status_counts":dict(sorted(Counter(r["review_status"] for r in new).items())),"corpus_sha256":sha(cp.read_bytes()),"candidate_index":im,"production_index_modified":False}
 hist=[f"CC2002:ART.{n}" for n in (*range(1768,1774),1776,1780)]; inter=[f"CC2002:ART.{n}" for n in ("1775-A","1783-A","1815-A")]; cov={"schema_version":1,"scope":"CC2002 arts. 1.721 a 2.046; conclusão do Código Civil","numbered_positions_examined":326,"article_targets_examined":329,"expected_current_explanations":321,"produced_explanations":len(new),"remaining_explanations":321-len(new),"revoked_historical_articles":hist,"vetoed_without_active_explanation":[],"active_intercalated":inter,"constitutional_application_notes":{"CC2002:ART.1790":"Distinção sucessória declarada inconstitucional pelo STF; aplica-se o regime do art. 1.829."},"completed_blocks":names}; write(root/MANIFEST.name,man); write(root/COVERAGE.name,cov)
 if out is None:
  name=names[-1]; expected=BLOCKS[name]; produced=[r for r in new if r["target_id"].split("ART.",1)[1].split(":",1)[0] in expected]; hist_block=[f"CC2002:ART.{n}" for n in HISTORICAL.get(name,[])]; write(CHECKPOINTS/f"CC13_{name}.json",{"schema_version":1,"block":name,"kind":"MIXED" if hist_block else "ACTIVE_PRODUCTION","expected_active":len(expected),"produced":len(produced),"complete":len(produced)==len(expected),"target_ids":[r["target_id"] for r in produced],"historical_targets":hist_block,"corpus_checkpoint_sha256":man["corpus_sha256"]})
 return man
def check():
 with tempfile.TemporaryDirectory(prefix=".cc13-check-",dir=BATCH) as td:
  tmp=Path(td); result=build(10,tmp); pairs=[(tmp/CORPUS.name,CORPUS),(tmp/DRAFTS.name,DRAFTS),(tmp/MANIFEST.name,MANIFEST),(tmp/COVERAGE.name,COVERAGE)]+[(tmp/"candidate_index"/n,INDEX/n) for n in ("ENTENDA_LOOKUP.IDX","ENTENDA_PAYLOAD.DAT","ENTENDA_BUILD_MANIFEST.json")]; bad=[str(d.relative_to(ROOT)) for s,d in pairs if not d.is_file() or s.read_bytes()!=d.read_bytes()]
  if bad: raise SystemExit("CC13_NOT_REPRODUCIBLE: "+", ".join(bad))
  return result
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--through-block",type=int,default=10); p.add_argument("--check",action="store_true"); a=p.parse_args(); print(json.dumps(check() if a.check else build(a.through_block),ensure_ascii=False,indent=2))
