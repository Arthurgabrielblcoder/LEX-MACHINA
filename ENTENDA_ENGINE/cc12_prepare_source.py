"""Prepare the isolated CC-12 source through Civil Code art. 1,720."""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"LEGAL_TARGET_ID")); import build_target_index as BT  # noqa: E402
CC11=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1380"; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1720"
OLD_SOURCE,OLD_STATUS=CC11/"SOURCE_CC2002_ARTS_001_1380.txt",CC11/"CC2002_TARGET_STATUS.json"
OP=ROOT/"updater"/"backup_saida"/"antes_recuperacao_monovigente_20260913_162304"/"2- C#U00d3DIGO CIVIL"/"codigo_civil_ lei10.406 2002.txt"
SOURCE,INDEX,STATUS=BATCH/"SOURCE_CC2002_ARTS_001_1720.txt",BATCH/"CC2002_TARGET_INDEX.json",BATCH/"CC2002_TARGET_STATUS.json"; PROV=BATCH/"SOURCE_PROVENANCE.json"; OFFICIAL=ROOT/"ENTENDA_ENGINE"/"derived"/"CC07_CODIGO_CIVIL_CAMARA.html"
EXPECTED="7264b71ede9d7fffb4d7a6494556ac6593ade2419085bce1807131f23205034b"; INTERCALATED=("1487-A","1510-A","1510-B","1510-C","1510-D","1510-E"); REVOKED=(1463,1482,1483,1494,*range(1620,1630)); INDEXED_REVOKED=(1463,1482,1483,1494,1620)
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def main():
 raw=OP.read_bytes()
 if sha(raw)!=EXPECTED: raise SystemExit("CC12_OPERATIONAL_SOURCE_HASH_MISMATCH")
 text=raw.decode("utf-8-sig"); start=re.search(r"(?m)^Art\. 1\.381\.\s",text); end=re.search(r"(?m)^Art\. 1\.721\.\s",text)
 if not start or not end: raise SystemExit("CC12_BOUNDARY_NOT_FOUND")
 addition=text[start.start():end.start()].rstrip()+"\n"; combined=(OLD_SOURCE.read_text(encoding="utf-8").rstrip()+"\n\n"+addition).encode(); BATCH.mkdir(parents=True,exist_ok=True); SOURCE.write_bytes(combined)
 idx=BT.build("CC2002",SOURCE); idx["source"]["path"]=str(SOURCE.relative_to(ROOT)).replace("\\","/"); write(INDEX,idx)
 historical=dict(json.loads(OLD_STATUS.read_text(encoding="utf-8"))["targets"])
 reasons={1463:"Revogado pela Lei 14.179/2021",1482:"Revogado pela Lei 13.105/2015",1483:"Revogado pela Lei 13.105/2015",1494:"Revogado pela Lei 14.382/2022",1620:"Arts. 1.620 a 1.629 revogados pela Lei 12.010/2009"}
 for n in INDEXED_REVOKED:
  for suffix in ("",":CAPUT"): historical[f"CC2002:ART.{n}{suffix}"]={"status":"HISTORICAL_ONLY","revoked_marker":True,"reason":reasons[n]}
 indexed={t["target_id"] for t in idx["targets"]}; missing=sorted(set(historical)-indexed)
 if missing: raise SystemExit("CC12_HISTORICAL_NOT_INDEXED: "+", ".join(missing))
 article_ids={t["article"] for t in idx["targets"] if t["kind"]=="ARTIGO" and 1381<=int(t["article"].split("-")[0])<=1720}; expected={str(n) for n in range(1381,1721) if n not in range(1621,1630)}|set(INTERCALATED)
 if article_ids!=expected: raise SystemExit(f"CC12_ARTICLE_RECONCILIATION_MISMATCH missing={sorted(expected-article_ids)} extra={sorted(article_ids-expected)}")
 write(STATUS,{"schema_version":1,"target_index_sha256":sha(INDEX.read_bytes()),"method":"Status histórico herdado da CC-11 e revogações do intervalo CC-12 confrontadas com a fonte consolidada em 11/11/2026.","counts":{"explicit_revoked_or_vetoed":len(historical)},"targets":historical})
 write(PROV,{"schema_version":1,"norma_id":"CC2002","scope":"Código Civil, arts. 1 a 1.720, com produção nova limitada aos arts. 1.381 a 1.720","preserved_cc11_source_sha256":sha(OLD_SOURCE.read_bytes()),"preserved_cc11_corpus_sha256":sha((CC11/"CC2002_CC11.entenda.jsonl").read_bytes()),"operational_source_sha256":sha(raw),"new_scope_excerpt_sha256":sha(addition.encode()),"combined_candidate_source_sha256":sha(combined),"official_confrontation":{"checked_on":"2026-11-11","codigo_civil_sha256":sha(OFFICIAL.read_bytes())},"grouped_revocation":{"source_heading":"Art. 1.620. a 1.629.","historical_positions":[f"CC2002:ART.{n}" for n in range(1620,1630)],"indexed_heading":"CC2002:ART.1620"},"protected_files":["CC-11 corpus (1,527 versions)","production indexes","firmware","physical microSD"],"device_source_modified":False})
 print(json.dumps({"numbered_positions_examined":340,"indexed_article_targets_examined":len(article_ids),"active_expected":332,"revoked_positions":list(REVOKED),"intercalated":list(INTERCALATED),"combined_sha256":sha(combined)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
