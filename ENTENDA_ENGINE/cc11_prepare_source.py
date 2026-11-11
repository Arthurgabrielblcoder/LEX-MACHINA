"""Prepare the isolated CC-11 source through Civil Code art. 1,380."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"LEGAL_TARGET_ID")); import build_target_index as BT  # noqa: E402
CC10=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1040"; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1380"
OLD_SOURCE,OLD_STATUS=CC10/"SOURCE_CC2002_ARTS_001_1040.txt",CC10/"CC2002_TARGET_STATUS.json"
OP=ROOT/"updater"/"backup_saida"/"antes_recuperacao_monovigente_20260913_162304"/"2- C#U00d3DIGO CIVIL"/"codigo_civil_ lei10.406 2002.txt"
SOURCE,INDEX,STATUS=BATCH/"SOURCE_CC2002_ARTS_001_1380.txt",BATCH/"CC2002_TARGET_INDEX.json",BATCH/"CC2002_TARGET_STATUS.json"; PROV=BATCH/"SOURCE_PROVENANCE.json"
OFFICIAL=ROOT/"ENTENDA_ENGINE"/"derived"/"CC07_CODIGO_CIVIL_CAMARA.html"; EXPECTED="7264b71ede9d7fffb4d7a6494556ac6593ade2419085bce1807131f23205034b"
INTERCALATED=("1080-A","1240-A","1354-A")+tuple(f"1358-{x}" for x in "ABCDEFGHIJKLMNOPQRSTU")+tuple(f"1368-{x}" for x in "ABCDEF")
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def main():
 raw=OP.read_bytes()
 if sha(raw)!=EXPECTED: raise SystemExit("CC11_OPERATIONAL_SOURCE_HASH_MISMATCH")
 text=raw.decode("utf-8-sig"); start=re.search(r"(?m)^Art\. 1\.041\.\s",text); end=re.search(r"(?m)^Art\. 1\.381\.\s",text)
 if not start or not end: raise SystemExit("CC11_BOUNDARY_NOT_FOUND")
 addition=text[start.start():end.start()].rstrip()+"\n"; combined=(OLD_SOURCE.read_text(encoding="utf-8").rstrip()+"\n\n"+addition).encode()
 BATCH.mkdir(parents=True,exist_ok=True); SOURCE.write_bytes(combined)
 idx=BT.build("CC2002",SOURCE); idx["source"]["path"]=str(SOURCE.relative_to(ROOT)).replace("\\","/"); write(INDEX,idx)
 historical=dict(json.loads(OLD_STATUS.read_text(encoding="utf-8"))["targets"])
 indexed={t["target_id"] for t in idx["targets"]}; missing=sorted(set(historical)-indexed)
 if missing: raise SystemExit("CC11_HISTORICAL_NOT_INDEXED: "+", ".join(missing))
 article_ids={t["article"] for t in idx["targets"] if t["kind"]=="ARTIGO" and 1041<=int(t["article"].split("-")[0])<=1380}
 expected={str(n) for n in range(1041,1381)}|set(INTERCALATED)
 if article_ids!=expected: raise SystemExit(f"CC11_ARTICLE_RECONCILIATION_MISMATCH missing={sorted(expected-article_ids)} extra={sorted(article_ids-expected)}")
 write(STATUS,{"schema_version":1,"target_index_sha256":sha(INDEX.read_bytes()),"method":"Status histórico herdado integralmente da CC-10; arts. 1.041–1.380 e intercalados confrontados com a fonte consolidada em 11/11/2026.","counts":{"explicit_revoked_or_vetoed":len(historical)},"targets":historical})
 write(PROV,{"schema_version":1,"norma_id":"CC2002","scope":"Código Civil, arts. 1 a 1.380, com produção nova limitada aos arts. 1.041 a 1.380","preserved_cc10_source_sha256":sha(OLD_SOURCE.read_bytes()),"preserved_cc10_corpus_sha256":sha((CC10/"CC2002_CC10.entenda.jsonl").read_bytes()),"operational_source_sha256":sha(raw),"new_scope_excerpt_sha256":sha(addition.encode()),"combined_candidate_source_sha256":sha(combined),"official_confrontation":{"checked_on":"2026-11-11","codigo_civil_sha256":sha(OFFICIAL.read_bytes())},"protected_files":["CC-10 corpus (1,157 versions)","production indexes","firmware","physical microSD"],"device_source_modified":False})
 print(json.dumps({"numbered_positions_examined":340,"article_targets_examined":len(article_ids),"active_expected":370,"intercalated":list(INTERCALATED),"revoked_or_vetoed_in_scope":0,"combined_sha256":sha(combined)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
