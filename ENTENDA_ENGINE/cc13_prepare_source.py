"""Prepare the isolated final CC-13 source through Civil Code art. 2,046."""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"LEGAL_TARGET_ID")); import build_target_index as BT  # noqa: E402
CC12=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_1720"; BATCH=ROOT/"ENTENDA_ENGINE"/"derived"/"candidate_cc_001_2046"
OLD_SOURCE,OLD_STATUS=CC12/"SOURCE_CC2002_ARTS_001_1720.txt",CC12/"CC2002_TARGET_STATUS.json"; OP=ROOT/"updater"/"backup_saida"/"antes_recuperacao_monovigente_20260913_162304"/"2- C#U00d3DIGO CIVIL"/"codigo_civil_ lei10.406 2002.txt"
SOURCE,INDEX,STATUS=BATCH/"SOURCE_CC2002_ARTS_001_2046.txt",BATCH/"CC2002_TARGET_INDEX.json",BATCH/"CC2002_TARGET_STATUS.json"; PROV=BATCH/"SOURCE_PROVENANCE.json"; OFFICIAL=ROOT/"ENTENDA_ENGINE"/"derived"/"CC07_CODIGO_CIVIL_CAMARA.html"
EXPECTED="7264b71ede9d7fffb4d7a6494556ac6593ade2419085bce1807131f23205034b"; INTERCALATED=("1775-A","1783-A","1815-A"); REVOKED=(*range(1768,1774),1776,1780)
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode())
def main():
 raw=OP.read_bytes()
 if sha(raw)!=EXPECTED: raise SystemExit("CC13_OPERATIONAL_SOURCE_HASH_MISMATCH")
 text=raw.decode("utf-8-sig"); start=re.search(r"(?m)^Art\. 1\.721\.\s",text); end=re.search(r"(?m)^Brasília, 10 de janeiro de 2002",text)
 if not start or not end: raise SystemExit("CC13_BOUNDARY_NOT_FOUND")
 addition=text[start.start():end.start()].rstrip()+"\n"; combined=(OLD_SOURCE.read_text(encoding="utf-8").rstrip()+"\n\n"+addition).encode(); BATCH.mkdir(parents=True,exist_ok=True); SOURCE.write_bytes(combined)
 idx=BT.build("CC2002",SOURCE); idx["source"]["path"]=str(SOURCE.relative_to(ROOT)).replace("\\","/"); write(INDEX,idx)
 historical=dict(json.loads(OLD_STATUS.read_text(encoding="utf-8"))["targets"])
 for n in REVOKED:
  reason="Revogado pela Lei 13.105/2015" if n in range(1768,1774) else "Revogado pela Lei 13.146/2015"
  for suffix in ("",":CAPUT"): historical[f"CC2002:ART.{n}{suffix}"]={"status":"HISTORICAL_ONLY","revoked_marker":True,"reason":reason}
 indexed={t["target_id"] for t in idx["targets"]}; missing=sorted(set(historical)-indexed)
 if missing: raise SystemExit("CC13_HISTORICAL_NOT_INDEXED: "+", ".join(missing))
 article_ids={t["article"] for t in idx["targets"] if t["kind"]=="ARTIGO" and 1721<=int(t["article"].split("-")[0])<=2046}; expected={str(n) for n in range(1721,2047)}|set(INTERCALATED)
 if article_ids!=expected: raise SystemExit(f"CC13_ARTICLE_RECONCILIATION_MISMATCH missing={sorted(expected-article_ids)} extra={sorted(article_ids-expected)}")
 write(STATUS,{"schema_version":1,"target_index_sha256":sha(INDEX.read_bytes()),"method":"Status histórico herdado da CC-12 e revogações CC-13 confrontadas com a fonte consolidada em 12/11/2026; art. 1.790 permanece estruturalmente vigente, com aplicação constitucional registrada editorialmente.","counts":{"explicit_revoked_or_vetoed":len(historical)},"targets":historical})
 write(PROV,{"schema_version":1,"norma_id":"CC2002","scope":"Código Civil integral, arts. 1 a 2.046; produção nova limitada aos arts. 1.721 a 2.046","preserved_cc12_source_sha256":sha(OLD_SOURCE.read_bytes()),"preserved_cc12_corpus_sha256":sha((CC12/"CC2002_CC12.entenda.jsonl").read_bytes()),"operational_source_sha256":sha(raw),"new_scope_excerpt_sha256":sha(addition.encode()),"combined_candidate_source_sha256":sha(combined),"official_confrontation":{"checked_on":"2026-11-12","codigo_civil_sha256":sha(OFFICIAL.read_bytes()),"stf_tema_809":"https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=809","stf_re_878694":"https://portal.stf.jus.br/processos/listarProcessos.asp?classe=RE&numeroProcesso=878694","art_1790_effect":"Distinção sucessória inconstitucional; aplica-se o art. 1.829 a casamento e união estável, observada a modulação do STF."},"protected_files":["CC-12 corpus (1,859 versions)","production indexes","firmware","physical microSD"],"device_source_modified":False})
 print(json.dumps({"numbered_positions_examined":326,"article_targets_examined":len(article_ids),"active_expected":321,"revoked_positions":list(REVOKED),"intercalated":list(INTERCALATED),"constitutional_interpretation":["1790"],"combined_sha256":sha(combined)},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
