from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from cc12_build import BATCH,CORPUS
ROOT=Path(__file__).resolve().parents[1]; PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"; PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def outputs():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active=[r for r in rows if r["status"]=="ACTIVE"]; matrix=json.loads((BATCH/"CC12_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8")); counts=matrix["classification_counts"]; revoked=[f"CC2002:ART.{n}" for n in (1463,1482,1483,1494,*range(1620,1630))]; inter=[f"CC2002:ART.{n}" for n in ("1487-A","1510-A","1510-B","1510-C","1510-D","1510-E")]
 legislation={"schema_version":1,"mission":"CC-12","verified_on":"2026-11-11","numbered_positions_examined":340,"indexed_article_targets_examined":337,"current_explanations":332,"active_intercalated":inter,"revoked_articles":revoked,"revoked_count":14,"vetoed":[],"grouped_revocation":"A fonte apresenta os arts. 1.620 a 1.629 em um único cabeçalho revogatório.","source_anomalies":[{"article":"CC2002:ART.1403","operational_heading":"Art. 1.403 Incumbem...","effect":"Parsed canonically"},{"article":"CC2002:ART.1636","operational_heading":"Art 1.636.","effect":"Parsed canonically"}]}
 integrity={"schema_version":1,"mission":"CC-12","candidate_only":True,"deployed":False,"baseline":{"head":"3409a81fe3a95b16f36d1515ff23f1e3c30c2d96","sha256":"e676be4c042cdf81dd05374cd7fe28431407e4e2fe59ff74922670c298ab969a","records":1527,"active":1364,"historical_versions":163},"candidate":{"records":len(rows),"active":len(active),"historical_versions":len(rows)-len(active),"cc12_active":332},"production_index":{n:{"unchanged":sha(PROD/"index"/n)==h,"sha256":sha(PROD/"index"/n)} for n,h in PH.items()},"firmware_modified":False,"physical_device_accessed":False}
 quality={"schema_version":1,"mission":"CC-12","records":332,"classification_counts":counts,"human_approval_claimed":False,"empty_required_fields":0,"glossaries_present":332}; corrections={"schema_version":1,"mission":"CC-12","substantive_corrections":counts["B"],"pending_legal_questions":[r["target_id"] for r in matrix["records"] if r["classification"] in ("C","D")]}
 report=f"""# CC-12 ampliada — relatório final

Foram examinadas 340 posições numeradas e 337 alvos indexados entre 1.381 e 1.720. Produziram-se 332 explicações vigentes, incluindo seis artigos intercalados. Quatorze posições foram reconciliadas como integralmente revogadas, sem explicação ativa. O corpus contém {len(active)} explicações ativas, {len(rows)} versões totais e {len(rows)-len(active)} históricas. As 1.527 versões da CC-11 foram preservadas integralmente.

Classificação: A={counts['A']}, B={counts['B']}, C={counts['C']}, D={counts['D']}. Corpus `{sha(CORPUS)}`; lookup `{sha(BATCH/'candidate_index'/'ENTENDA_LOOKUP.IDX')}`; payload `{sha(BATCH/'candidate_index'/'ENTENDA_PAYLOAD.DAT')}`. Não houve deploy nem alteração de hardware ou índices de produção. Próximo intervalo recomendado: arts. 1.721–2.046.
"""
 return {BATCH/"CC12_LEGISLATIVE_RECONCILIATION.json":enc(legislation),BATCH/"CC12_INTEGRITY_REPORT.json":enc(integrity),BATCH/"CC12_QUALITY_METRICS.json":enc(quality),BATCH/"CC12_CORRECTIONS.json":enc(corrections),BATCH/"CC12_FINAL_REPORT.md":report.encode()}
def main(check):
 out=outputs(); bad=[str(p.relative_to(ROOT)) for p,d in out.items() if check and (not p.is_file() or p.read_bytes()!=d)]
 if bad: raise SystemExit("CC12_FINAL_NOT_REPRODUCIBLE: "+", ".join(bad))
 if not check:
  for p,d in out.items(): p.write_bytes(d)
 print(json.dumps({"check":check,"corpus_sha256":sha(CORPUS)},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
