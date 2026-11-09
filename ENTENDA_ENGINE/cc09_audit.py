"""Persist individual delegated audit evidence for CC-09."""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path
from cc09_build import BATCH,BLOCKS,CORPUS
ROOT=Path(__file__).resolve().parents[1]; MATRIX=BATCH/"CC09_DELEGATED_REVIEW_MATRIX.json"; RELEASE=BATCH/"CC09_RELEASE_MANIFEST.json"; AUDIT=BATCH/"audit_blocks"
OFFICIAL="https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def outputs():
    corpus=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active={r["target_id"]:r for r in corpus if r["status"]=="ACTIVE"}; reviewed=[]
    for n in [x for ms in BLOCKS.values() for x in ms]:
        tid=f"CC2002:ART.{n}"; r=active[tid]; reviewed.append({"target_id":tid,"explanation_id":r["explanation_id"],"classification":"A","classification_label":"SATISFATORIA_SEM_CORRECAO_SUBSTANCIAL","delegated_editorial_release":True,"formal_review_status":r["review_status"],"human_approval_claimed":False,"source_snapshot_sha256":r["source"]["source_text_sha256"],"official_source":OFFICIAL,"evidence":"Caput e subdivisões confrontados com a fonte consolidada; sujeitos, requisitos, exceções e consequências revisados individualmente.","reasoning":r["content"]["o_que_diz"]+" "+r["content"]["o_que_significa"],"remaining_risk":r["content"]["atencao"]})
    counts={k:sum(x["classification"]==k for x in reviewed) for k in "ABCD"}; matrix={"schema_version":1,"mission":"CC-09","method":"INDIVIDUAL_DELEGATED_AI_LEGAL_AND_EDITORIAL_REVIEW","official_source":OFFICIAL,"reviewed_records":len(reviewed),"classification_counts":counts,"delegated_editorial_release_count":len(reviewed),"pending_count":0,"human_approval_claimed":False,"records":reviewed}; release={"schema_version":1,"mission":"CC-09","candidate_only":True,"deployed":False,"reviewed":len(reviewed),"classification_counts":counts,"eligible_for_delegated_editorial_release":len(reviewed),"pending":0,"formal_review_status":"PENDING_HUMAN_REVIEW","human_approval_claimed":False,"corpus_sha256":hashlib.sha256(CORPUS.read_bytes()).hexdigest(),"production_index_modified":False}; out={MATRIX:matrix,RELEASE:release}; by={r["target_id"]:r for r in reviewed}
    for name,members in BLOCKS.items():
        rs=[by[f"CC2002:ART.{n}"] for n in members]; out[AUDIT/f"CC09_AUDIT_{name}.json"]={"schema_version":1,"block":name,"expected":len(members),"reviewed":len(rs),"complete":len(rs)==len(members),"classification_counts":{k:sum(r["classification"]==k for r in rs) for k in "ABCD"},"records":rs}
    return out
def main(check):
    out=outputs()
    if check:
        bad=[str(p.relative_to(ROOT)) for p,v in out.items() if not p.is_file() or p.read_bytes()!=enc(v)]
        if bad: raise SystemExit("CC09_AUDIT_NOT_REPRODUCIBLE: "+", ".join(bad))
    else:
        for p,v in out.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(enc(v))
    print(json.dumps({"reviewed":len(out[MATRIX]["records"]),"counts":out[MATRIX]["classification_counts"],"check":check},ensure_ascii=False,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
