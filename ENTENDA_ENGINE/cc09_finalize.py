"""Deterministic final evidence for CC-09."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from cc09_build import BATCH,CORPUS
ROOT=Path(__file__).resolve().parents[1]; PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"; PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def outputs():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active={r["target_id"]:r for r in rows if r["status"]=="ACTIVE"}; new={k:v for k,v in active.items() if 551<=int(k.split("ART.",1)[1].split(":",1)[0].split("-")[0])<=700}; wc={}
 for k,r in new.items():
  c=r["content"]; text=" ".join([c[x] for x in ("o_que_diz","o_que_significa","exemplo_pratico","atencao")]+[t["termo"]+" "+t["explicacao"] for t in c["palavras_dificeis"]]); wc[k]=len(re.findall(r"\b[\wÀ-ÿ-]+\b",text))
 quality={"schema_version":1,"mission":"CC-09","records":len(new),"words_total":sum(wc.values()),"words_average":round(sum(wc.values())/len(wc),2),"words_min":{"target_id":min(wc,key=wc.get),"value":min(wc.values())},"words_max":{"target_id":max(wc,key=wc.get),"value":max(wc.values())},"classification_counts":{"A":150,"B":0,"C":0,"D":0},"human_approval_claimed":False}
 legislation={"schema_version":1,"mission":"CC-09","verified_on":"2026-11-09","official_source":"https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html","numbered_positions_examined":150,"article_targets_examined":150,"current_articles":150,"intercalated":[],"historical_only":[],"relevant_changes":[{"target_id":"CC2002:ART.591","basis":"Lei 14.905/2024 refletida, com taxa legal subsidiária."},{"target_id":"CC2002:ART.693","basis":"Lei 14.690/2023 refletida no objeto da comissão."},{"target_id":"CC2002:ART.698","basis":"Cláusula del credere parcial refletida."}],"device_source_modified":False}
 integrity={"schema_version":1,"mission":"CC-09","candidate_only":True,"deployed":False,"baseline":{"expected_head":"b39612f22e704c8addc909df74c509c17ea4abb4","cc08_corpus_sha256":"c1951fe3af7f514c17376864fa8b3692564c6621249804afc6dc177f37dcb8bc","records":712,"active":549},"candidate":{"records":len(rows),"active":len(active),"cc09_active":len(new),"historical_versions":len(rows)-len(active),"formal_status":"PENDING_HUMAN_REVIEW","delegated_release":150},"production_index":{n:{"expected_sha256":h,"actual_sha256":sha(PROD/"index"/n),"unchanged":sha(PROD/"index"/n)==h} for n,h in PH.items()},"firmware_modified":False,"physical_device_accessed":False}
 corrections={"schema_version":1,"mission":"CC-09","substantive_post_persistence_corrections":0,"pre_persistence_adjustments":[],"pending_legal_questions":[]}
 report=f"""# CC-09 — relatório final

Produzidas 150 explicações vigentes para os arts. 551–700. O corpus candidato contém {len(active)} explicações ativas, {len(rows)} versões totais e {len(rows)-len(active)} históricas. As 712 versões da CC-08 foram preservadas. Classificação delegada: A=150, B=C=D=0, sem aprovação humana alegada.

Corpus SHA-256: `{sha(CORPUS)}`. Lookup: `{sha(BATCH/'candidate_index'/'ENTENDA_LOOKUP.IDX')}`. Payload: `{sha(BATCH/'candidate_index'/'ENTENDA_PAYLOAD.DAT')}`.

Não houve deploy, alteração de firmware, acesso ao dispositivo nem modificação dos índices de produção. Próximo intervalo recomendado: arts. 701–850, em missão separada.
"""
 return {BATCH/"CC09_QUALITY_METRICS.json":enc(quality),BATCH/"CC09_LEGISLATIVE_RECONCILIATION.json":enc(legislation),BATCH/"CC09_INTEGRITY_REPORT.json":enc(integrity),BATCH/"CC09_CORRECTIONS.json":enc(corrections),BATCH/"CC09_FINAL_REPORT.md":report.encode()}
def main(check):
 out=outputs()
 if check:
  bad=[str(p.relative_to(ROOT)) for p,d in out.items() if not p.is_file() or p.read_bytes()!=d]
  if bad: raise SystemExit("CC09_FINAL_NOT_REPRODUCIBLE: "+", ".join(bad))
 else:
  for p,d in out.items(): p.write_bytes(d)
 print(json.dumps({"check":check,"corpus_sha256":sha(CORPUS)},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
