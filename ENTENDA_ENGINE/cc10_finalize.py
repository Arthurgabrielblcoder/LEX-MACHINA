from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from cc10_build import BATCH, CORPUS
ROOT=Path(__file__).resolve().parents[1]; PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"
PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def outputs():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active=[r for r in rows if r["status"]=="ACTIVE"]
 matrix=json.loads((BATCH/"CC10_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8")); counts=matrix["classification_counts"]
 legislation={"schema_version":1,"mission":"CC-10","verified_on":"2026-11-11","numbered_positions_examined":340,"article_targets_examined":343,"current_explanations":295,"active_intercalated":["CC2002:ART.853-A"],"revoked_articles":[f"CC2002:ART.{n}" for n in range(757,803)]+["CC2002:ART.980-A"],"revoked_count":47,"revoking_norm":"Lei 15.040/2024, art. 133 (arts. 757–802); Lei 14.382/2022 (art. 980-A)","lei_15040_effective_date":"2025-12-11","intertemporal_note":"A revogação impede tratar os artigos como direito vigente, sem excluir análise histórica de contratos e fatos anteriores conforme as regras aplicáveis.","vetoed":["CC2002:ART.819-A"],"new_insurance_law_not_ingested_into_cc2002":True,"future_special_law_mission_recommended":"Lei 15.040/2024"}
 integrity={"schema_version":1,"mission":"CC-10","candidate_only":True,"deployed":False,"baseline":{"head":"461c01fbcb8eb703b6fe3110033e432366e79b95","sha256":"372e427d6268e38685b78dfba18ba5e87c3c7d95ca997c4356e77128e1a03eec","records":862,"active":699},"candidate":{"records":len(rows),"active":len(active),"historical_versions":len(rows)-len(active),"cc10_active":295},"production_index":{n:{"unchanged":sha(PROD/"index"/n)==h,"sha256":sha(PROD/"index"/n)} for n,h in PH.items()},"firmware_modified":False,"physical_device_accessed":False}
 quality={"schema_version":1,"mission":"CC-10","records":295,"classification_counts":counts,"human_approval_claimed":False,"empty_required_fields":0,"glossaries_present":295}
 corrections={"schema_version":1,"mission":"CC-10","substantive_corrections":counts["B"],"pending_legal_questions":[r["target_id"] for r in matrix["records"] if r["classification"] in ("C","D")]}
 report=f"""# CC-10 ampliada — relatório final

Foram examinadas 340 posições numeradas e 343 alvos de artigo entre 701 e 1.040. Produziram-se 295 explicações vigentes, incluindo o art. 853-A. Os 46 arts. 757–802 foram registrados como revogados pela Lei 15.040/2024 desde 11/12/2025, o art. 980-A como revogado e o art. 819-A como vetado. O corpus contém {len(active)} explicações ativas, {len(rows)} versões totais e {len(rows)-len(active)} históricas. As 862 versões da CC-09 foram preservadas integralmente.

Classificação: A={counts['A']}, B={counts['B']}, C={counts['C']}, D={counts['D']}. Corpus `{sha(CORPUS)}`; lookup `{sha(BATCH/'candidate_index'/'ENTENDA_LOOKUP.IDX')}`; payload `{sha(BATCH/'candidate_index'/'ENTENDA_PAYLOAD.DAT')}`. Não houve deploy nem alteração de hardware ou índices de produção. Recomenda-se futuramente produzir o ENTENDA próprio da Lei 15.040/2024. Próximo intervalo recomendado: arts. 1.041–1.380.
"""
 return {BATCH/"CC10_LEGISLATIVE_RECONCILIATION.json":enc(legislation),BATCH/"CC10_INTEGRITY_REPORT.json":enc(integrity),BATCH/"CC10_QUALITY_METRICS.json":enc(quality),BATCH/"CC10_CORRECTIONS.json":enc(corrections),BATCH/"CC10_FINAL_REPORT.md":report.encode()}
def main(check):
 out=outputs(); bad=[str(p.relative_to(ROOT)) for p,d in out.items() if check and (not p.is_file() or p.read_bytes()!=d)]
 if bad: raise SystemExit("CC10_FINAL_NOT_REPRODUCIBLE: "+", ".join(bad))
 if not check:
  for p,d in out.items(): p.write_bytes(d)
 print(json.dumps({"check":check,"corpus_sha256":sha(CORPUS)},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
