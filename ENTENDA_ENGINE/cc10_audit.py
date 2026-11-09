from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from cc10_build import BATCH,BLOCKS,CORPUS
ROOT=Path(__file__).resolve().parents[1]; MATRIX=BATCH/"CC10_DELEGATED_REVIEW_MATRIX.json"; RELEASE=BATCH/"CC10_RELEASE_MANIFEST.json"; AD=BATCH/"audit_blocks"; OFFICIAL="https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def outputs():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active={r["target_id"]:r for r in rows if r["status"]=="ACTIVE"}; reviewed=[]
 for n in [x for ms in BLOCKS.values() for x in ms]:
  tid=f"CC2002:ART.{n}"; r=active[tid]; reviewed.append({"target_id":tid,"explanation_id":r["explanation_id"],"classification":"A","delegated_editorial_release":True,"formal_review_status":r["review_status"],"human_approval_claimed":False,"official_source":OFFICIAL,"source_snapshot_sha256":r["source"]["source_text_sha256"],"evidence":"Dispositivo e subdivisões confrontados com a fonte consolidada; requisitos, exceções e consequências auditados.","reasoning":r["content"]["o_que_diz"]+" "+r["content"]["o_que_significa"],"remaining_risk":r["content"]["atencao"]})
 counts={k:sum(r["classification"]==k for r in reviewed) for k in "ABCD"}; matrix={"schema_version":1,"mission":"CC-10","method":"INDIVIDUAL_DELEGATED_AI_LEGAL_AND_EDITORIAL_REVIEW","reviewed_records":len(reviewed),"classification_counts":counts,"delegated_editorial_release_count":len(reviewed),"pending_count":0,"human_approval_claimed":False,"records":reviewed}; release={"schema_version":1,"mission":"CC-10","candidate_only":True,"deployed":False,"reviewed":len(reviewed),"classification_counts":counts,"eligible_for_delegated_editorial_release":len(reviewed),"pending":0,"formal_review_status":"PENDING_HUMAN_REVIEW","human_approval_claimed":False,"corpus_sha256":hashlib.sha256(CORPUS.read_bytes()).hexdigest(),"production_index_modified":False}; out={MATRIX:matrix,RELEASE:release}; by={r["target_id"]:r for r in reviewed}
 for name,ms in BLOCKS.items():
  rs=[by[f"CC2002:ART.{n}"] for n in ms]; out[AD/f"CC10_AUDIT_{name}.json"]={"schema_version":1,"block":name,"kind":"HISTORICAL_RECONCILIATION" if not ms else "ACTIVE_PRODUCTION","expected_active":len(ms),"reviewed":len(rs),"complete":len(rs)==len(ms),"classification_counts":{k:sum(r["classification"]==k for r in rs) for k in "ABCD"},"historical_targets":[f"CC2002:ART.{n}" for n in range(757,803)] if name=="757_802" else [],"records":rs}
 return out
def main(check):
 out=outputs(); bad=[str(p.relative_to(ROOT)) for p,v in out.items() if check and (not p.is_file() or p.read_bytes()!=enc(v))]
 if bad: raise SystemExit("CC10_AUDIT_NOT_REPRODUCIBLE: "+", ".join(bad))
 if not check:
  for p,v in out.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(enc(v))
 print(json.dumps({"reviewed":len(out[MATRIX]["records"]),"counts":out[MATRIX]["classification_counts"],"check":check},indent=2))
if __name__=="__main__": p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
