"""Prepare CC-10 source and explicit historical status."""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"LEGAL_TARGET_ID")); import build_target_index as BT  # noqa: E402
CC09=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_700"; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_850"
OLD_SOURCE,OLD_STATUS=CC09/"SOURCE_CC2002_ARTS_001_700.txt",CC09/"CC2002_TARGET_STATUS.json"
OP=ROOT/"updater"/"backup_saida"/"antes_recuperacao_monovigente_20260913_162304"/"2- C#U00d3DIGO CIVIL"/"codigo_civil_ lei10.406 2002.txt"
SOURCE,INDEX,STATUS=BATCH/"SOURCE_CC2002_ARTS_001_850.txt",BATCH/"CC2002_TARGET_INDEX.json",BATCH/"CC2002_TARGET_STATUS.json"; PROV=BATCH/"SOURCE_PROVENANCE.json"
LAW=ROOT/"ENTENDA_ENGINE"/"derived"/"CC10_LEI_15040_CAMARA.html"; OFFICIAL=ROOT/"ENTENDA_ENGINE"/"derived"/"CC07_CODIGO_CIVIL_CAMARA.html"
EXPECTED="7264b71ede9d7fffb4d7a6494556ac6593ade2419085bce1807131f23205034b"
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def main():
 raw=OP.read_bytes()
 if sha(raw)!=EXPECTED: raise SystemExit("CC10_OPERATIONAL_SOURCE_HASH_MISMATCH")
 text=raw.decode("utf-8-sig"); s,e=re.search(r"(?m)^Art\. 701\.\s",text),re.search(r"(?m)^Art\. 851\.\s",text)
 if not s or not e: raise SystemExit("CC10_BOUNDARY_NOT_FOUND")
 addition=text[s.start():e.start()].rstrip()+"\n"; combined=(OLD_SOURCE.read_text(encoding="utf-8").rstrip()+"\n\n"+addition).encode(); BATCH.mkdir(parents=True,exist_ok=True); SOURCE.write_bytes(combined)
 idx=BT.build("CC2002",SOURCE); idx["source"]["path"]=str(SOURCE.relative_to(ROOT)).replace("\\","/"); write(INDEX,idx)
 historical=dict(json.loads(OLD_STATUS.read_text(encoding="utf-8"))["targets"])
 for n in range(757,803):
  reason="Revogado pelo art. 133 da Lei 15.040/2024, em vigor desde 11/12/2025"
  historical[f"CC2002:ART.{n}"]={"status":"HISTORICAL_ONLY","revoked_marker":True,"reason":reason}; historical[f"CC2002:ART.{n}:CAPUT"]={"status":"HISTORICAL_ONLY","revoked_marker":True,"reason":reason}
 historical["CC2002:ART.819-A"]={"status":"HISTORICAL_ONLY","revoked_marker":True,"reason":"Artigo vetado na Lei 10.931/2004"}; historical["CC2002:ART.819-A:CAPUT"]={"status":"HISTORICAL_ONLY","revoked_marker":True,"reason":"Artigo vetado na Lei 10.931/2004"}
 indexed={t["target_id"] for t in idx["targets"]}; missing=sorted(set(historical)-indexed)
 if missing: raise SystemExit("CC10_HISTORICAL_NOT_INDEXED: "+", ".join(missing))
 write(STATUS,{"schema_version":1,"target_index_sha256":sha(INDEX.read_bytes()),"method":"Marcadores da fonte operacional confrontados com Código Civil consolidado e art. 133 da Lei 15.040/2024 em 09/11/2026.","counts":{"explicit_revoked_or_vetoed":len(historical)},"targets":historical})
 write(PROV,{"schema_version":1,"norma_id":"CC2002","scope":"Código Civil, arts. 1 a 850, com produção nova limitada aos arts. 701 a 850","preserved_cc09_source_sha256":sha(OLD_SOURCE.read_bytes()),"operational_source_sha256":sha(raw),"new_scope_excerpt_sha256":sha(addition.encode()),"combined_candidate_source_sha256":sha(combined),"official_confrontation":{"checked_on":"2026-11-09","codigo_civil_sha256":sha(OFFICIAL.read_bytes()),"lei_15040_sha256":sha(LAW.read_bytes()),"lei_15040_effective_date":"2025-12-11","revoking_provision":"Lei 15.040/2024, art. 133"},"device_source_modified":False})
 scoped=[t for t in idx["targets"] if t["kind"]=="ARTIGO" and 701<=int(t["article"].split("-")[0])<=850]; print(json.dumps({"article_targets_examined":len(scoped),"active_expected":104,"revoked_757_802":46,"vetoed":["819-A"],"combined_sha256":sha(combined)},indent=2))
if __name__=="__main__": main()
