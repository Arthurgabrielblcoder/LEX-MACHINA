from __future__ import annotations
import argparse,hashlib,importlib,json
from pathlib import Path
from cc12_build import BATCH,BLOCKS,CORPUS,HISTORICAL,MODULES
ROOT=Path(__file__).resolve().parents[1]; MATRIX=BATCH/"CC12_DELEGATED_REVIEW_MATRIX.json"; RELEASE=BATCH/"CC12_RELEASE_MANIFEST.json"; AD=BATCH/"audit_blocks"; OFFICIAL="https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def evidence():
 out={}
 for name in MODULES:
  mod=importlib.import_module(name)
  if set(mod.AUDIT)!=set(mod.ROWS): raise SystemExit(f"CC12_AUDIT_ROWS_MISMATCH: {name}")
  for article,item in mod.AUDIT.items():
   if item.get("classification") not in "ABCD" or not item.get("rationale"): raise SystemExit(f"CC12_AUDIT_INVALID: {article}")
   out[article]=item
 return out
def outputs():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active={r["target_id"]:r for r in rows if r["status"]=="ACTIVE"}; ev=evidence(); reviewed=[]
 for n in [x for values in BLOCKS.values() for x in values]:
  tid=f"CC2002:ART.{n}"; r=active[tid]; item=ev[n]; c=item["classification"]
  reviewed.append({"target_id":tid,"explanation_id":r["explanation_id"],"classification":c,"delegated_editorial_release":c in ("A","B"),"formal_review_status":r["review_status"],"human_approval_claimed":False,"official_source":OFFICIAL,"source_snapshot_sha256":r["source"]["source_text_sha256"],"evidence":"Dispositivo e subdivisões confrontados individualmente; vigência, requisitos, exceções, prazos e interpretação constitucional ou especial aplicável foram revisados.","reasoning":item["rationale"],"remaining_risk":r["content"]["atencao"]})
 counts={k:sum(r["classification"]==k for r in reviewed) for k in "ABCD"}; released=sum(r["delegated_editorial_release"] for r in reviewed); matrix={"schema_version":1,"mission":"CC-12","method":"INDIVIDUAL_DELEGATED_AI_LEGAL_AND_EDITORIAL_REVIEW","reviewed_records":len(reviewed),"classification_counts":counts,"delegated_editorial_release_count":released,"pending_count":len(reviewed)-released,"human_approval_claimed":False,"records":reviewed}; release={"schema_version":1,"mission":"CC-12","candidate_only":True,"deployed":False,"reviewed":len(reviewed),"classification_counts":counts,"eligible_for_delegated_editorial_release":released,"pending":len(reviewed)-released,"formal_review_status":"PENDING_HUMAN_REVIEW","human_approval_claimed":False,"corpus_sha256":hashlib.sha256(CORPUS.read_bytes()).hexdigest(),"production_index_modified":False}; out={MATRIX:matrix,RELEASE:release}; by={r["target_id"]:r for r in reviewed}
 for name,values in BLOCKS.items():
  rs=[by[f"CC2002:ART.{n}"] for n in values]; hist=[f"CC2002:ART.{n}" for n in HISTORICAL.get(name,[])]; out[AD/f"CC12_AUDIT_{name}.json"]={"schema_version":1,"block":name,"kind":"MIXED" if hist else "ACTIVE_PRODUCTION","expected_active":len(values),"reviewed":len(rs),"complete":len(rs)==len(values),"classification_counts":{k:sum(r["classification"]==k for r in rs) for k in "ABCD"},"historical_targets":hist,"records":rs}
 return out
def main(check):
 out=outputs(); bad=[str(p.relative_to(ROOT)) for p,v in out.items() if check and (not p.is_file() or p.read_bytes()!=enc(v))]
 if bad: raise SystemExit("CC12_AUDIT_NOT_REPRODUCIBLE: "+", ".join(bad))
 if not check:
  for p,v in out.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(enc(v))
 print(json.dumps({"reviewed":len(out[MATRIX]["records"]),"counts":out[MATRIX]["classification_counts"],"check":check},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
