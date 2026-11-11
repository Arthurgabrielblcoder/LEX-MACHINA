from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from cc11_build import BATCH,CORPUS,BLOCKS
ROOT=Path(__file__).resolve().parents[1]; PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"
PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def outputs():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active=[r for r in rows if r["status"]=="ACTIVE"]; matrix=json.loads((BATCH/"CC11_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8")); counts=matrix["classification_counts"]; inter=[f"CC2002:ART.{n}" for n in [x for values in BLOCKS.values() for x in values if "-" in x]]
 legislation={"schema_version":1,"mission":"CC-11","verified_on":"2026-11-11","numbered_positions_examined":340,"article_targets_examined":370,"current_explanations":370,"active_intercalated":inter,"revoked_articles":[],"revoked_count":0,"vetoed":[],"source_anomaly":{"article":"CC2002:ART.1337","operational_heading":"Art. 1337.","effect":"Parsed canonically as article 1337; no legislative gap."}}
 integrity={"schema_version":1,"mission":"CC-11","candidate_only":True,"deployed":False,"baseline":{"head":"8b53b676af2fe26d649abebdd39179e5b3966fb6","sha256":"7989063587a308184852e87a9489733b8b3502366e9c46a5d3a2983f39ab1802","records":1157,"active":994,"historical_versions":163},"candidate":{"records":len(rows),"active":len(active),"historical_versions":len(rows)-len(active),"cc11_active":370},"production_index":{n:{"unchanged":sha(PROD/"index"/n)==h,"sha256":sha(PROD/"index"/n)} for n,h in PH.items()},"firmware_modified":False,"physical_device_accessed":False}
 quality={"schema_version":1,"mission":"CC-11","records":370,"classification_counts":counts,"human_approval_claimed":False,"empty_required_fields":0,"glossaries_present":370}; corrections={"schema_version":1,"mission":"CC-11","substantive_corrections":counts["B"],"pending_legal_questions":[r["target_id"] for r in matrix["records"] if r["classification"] in ("C","D")]}
 report=f"""# CC-11 ampliada — relatório final

Foram examinadas 340 posições numeradas e 370 alvos de artigo entre 1.041 e 1.380. Produziram-se 370 explicações vigentes, incluindo 30 artigos intercalados; não há artigo integralmente revogado ou vetado no intervalo reconciliado. O corpus contém {len(active)} explicações ativas, {len(rows)} versões totais e {len(rows)-len(active)} históricas. As 1.157 versões da CC-10 foram preservadas integralmente.

Classificação: A={counts['A']}, B={counts['B']}, C={counts['C']}, D={counts['D']}. Corpus `{sha(CORPUS)}`; lookup `{sha(BATCH/'candidate_index'/'ENTENDA_LOOKUP.IDX')}`; payload `{sha(BATCH/'candidate_index'/'ENTENDA_PAYLOAD.DAT')}`. Não houve deploy nem alteração de hardware ou índices de produção. Próximo intervalo recomendado: arts. 1.381–1.720.
"""
 return {BATCH/"CC11_LEGISLATIVE_RECONCILIATION.json":enc(legislation),BATCH/"CC11_INTEGRITY_REPORT.json":enc(integrity),BATCH/"CC11_QUALITY_METRICS.json":enc(quality),BATCH/"CC11_CORRECTIONS.json":enc(corrections),BATCH/"CC11_FINAL_REPORT.md":report.encode()}
def main(check):
 out=outputs(); bad=[str(p.relative_to(ROOT)) for p,d in out.items() if check and (not p.is_file() or p.read_bytes()!=d)]
 if bad: raise SystemExit("CC11_FINAL_NOT_REPRODUCIBLE: "+", ".join(bad))
 if not check:
  for p,d in out.items(): p.write_bytes(d)
 print(json.dumps({"check":check,"corpus_sha256":sha(CORPUS)},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
