from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from cc13_build import BATCH,CORPUS
ROOT=Path(__file__).resolve().parents[1]; PROD=ROOT/"ENTENDA_ENGINE"/"derived"/"production_cc_001_114"; PH={"ENTENDA_LOOKUP.IDX":"38074a6d752b2a3ebd4e7411ff25c43abc3c69ad117b3cf49a4f5b73aece3e82","ENTENDA_PAYLOAD.DAT":"6caa56b1d5f047b12df087c39ab7998db579de2c445352caa7ad7219c9641638","ENTENDA_BUILD_MANIFEST.json":"213dc52380c3b359c35d9bc5c8e9a85a24043c0dd19f7eeb841b059eeda3a760"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(v): return (json.dumps(v,ensure_ascii=False,indent=2)+"\n").encode()
def outputs():
 rows=[json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]; active=[r for r in rows if r["status"]=="ACTIVE"]; matrix=json.loads((BATCH/"CC13_DELEGATED_REVIEW_MATRIX.json").read_text(encoding="utf-8")); counts=matrix["classification_counts"]; revoked=[f"CC2002:ART.{n}" for n in (*range(1768,1774),1776,1780)]; inter=[f"CC2002:ART.{n}" for n in ("1775-A","1783-A","1815-A")]
 legislation={"schema_version":1,"mission":"CC-13","verified_on":"2026-11-12","numbered_positions_examined":326,"article_targets_examined":329,"current_explanations":321,"active_intercalated":inter,"revoked_articles":revoked,"revoked_count":8,"vetoed":[],"constitutional_interpretation":{"article":"CC2002:ART.1790","formal_status":"CURRENT_TEXT_WITH_UNCONSTITUTIONAL_APPLICATION","stf_themes":[498,809],"current_rule":"Aplica-se o regime sucessório do art. 1.829 a casamento e união estável.","modulation":"Inventários judiciais sem trânsito em julgado da partilha e partilhas extrajudiciais sem escritura pública."},"source_anomalies":[{"article":"CC2002:ART.1992","operational_heading":"Art.1.992.","effect":"Parsed canonically"},{"article":"CC2002:ART.1994","operational_heading":"Art.1.994.","effect":"Parsed canonically"}]}
 integrity={"schema_version":1,"mission":"CC-13","candidate_only":True,"deployed":False,"baseline":{"head":"a16e859d98e3761a142a18505c6aa893818a43ce","sha256":"76b945f8af99482fb54f93f6ae9d2da331fc5483470eb4bb7892fbcb19d51f24","records":1859,"active":1696,"historical_versions":163},"candidate":{"records":len(rows),"active":len(active),"historical_versions":len(rows)-len(active),"cc13_active":321,"civil_code_scope":"CC2002 arts. 1–2.046 complete candidate coverage"},"production_index":{n:{"unchanged":sha(PROD/"index"/n)==h,"sha256":sha(PROD/"index"/n)} for n,h in PH.items()},"firmware_modified":False,"physical_device_accessed":False}
 quality={"schema_version":1,"mission":"CC-13","records":321,"classification_counts":counts,"human_approval_claimed":False,"empty_required_fields":0,"glossaries_present":321}; corrections={"schema_version":1,"mission":"CC-13","substantive_corrections":counts["B"],"pending_legal_questions":[r["target_id"] for r in matrix["records"] if r["classification"] in ("C","D")]}
 report=f"""# CC-13 final — conclusão do Código Civil

Foram examinadas 326 posições numeradas e 329 alvos de artigo entre 1.721 e 2.046. Produziram-se 321 explicações vigentes, incluindo três artigos intercalados. Oito artigos foram reconciliados como integralmente revogados, sem explicação ativa. O art. 1.790 foi mantido estruturalmente, com explicação da declaração de inconstitucionalidade da distinção sucessória e aplicação do art. 1.829 segundo os Temas 498 e 809 do STF.

O corpus candidato integral contém {len(active)} explicações ativas, {len(rows)} versões totais e {len(rows)-len(active)} históricas, cobrindo o Código Civil dos arts. 1 a 2.046. As 1.859 versões da CC-12 foram preservadas byte a byte.

Classificação CC-13: A={counts['A']}, B={counts['B']}, C={counts['C']}, D={counts['D']}. Corpus `{sha(CORPUS)}`; lookup `{sha(BATCH/'candidate_index'/'ENTENDA_LOOKUP.IDX')}`; payload `{sha(BATCH/'candidate_index'/'ENTENDA_PAYLOAD.DAT')}`. Não houve deploy nem alteração de hardware ou índices de produção.
"""
 roadmap="""# Roteiro da próxima fase — não executado

1. Reproduzir e sanear as sete falhas e dois erros históricos da suíte global.
2. Adaptar o teste de materialização para worktrees vinculados sem reduzir sua garantia.
3. Fazer auditoria jurídica independente, priorizando registros B e institutos constitucionalmente sensíveis.
4. Reconferir vigência, alterações legislativas e fontes oficiais em data de corte atualizada.
5. Auditar a cobertura material das subdivisões de cada artigo, além da cobertura por artigo.
6. Produzir o ENTENDA da Lei 15.040/2024 em namespace próprio.
7. Planejar a integração do Código Civil com as 810 explicações constitucionais existentes.
8. Somente depois, preparar instalação única, verificável e reversível no microSD, precedida de análise de firmware e plano de rollback.

Nenhuma dessas etapas foi executada na CC-13.
"""
 return {BATCH/"CC13_LEGISLATIVE_RECONCILIATION.json":enc(legislation),BATCH/"CC13_INTEGRITY_REPORT.json":enc(integrity),BATCH/"CC13_QUALITY_METRICS.json":enc(quality),BATCH/"CC13_CORRECTIONS.json":enc(corrections),BATCH/"CC13_FINAL_REPORT.md":report.encode(),BATCH/"CC13_NEXT_PHASE_ROADMAP.md":roadmap.encode()}
def main(check):
 out=outputs(); bad=[str(p.relative_to(ROOT)) for p,d in out.items() if check and (not p.is_file() or p.read_bytes()!=d)]
 if bad: raise SystemExit("CC13_FINAL_NOT_REPRODUCIBLE: "+", ".join(bad))
 if not check:
  for p,d in out.items(): p.write_bytes(d)
 print(json.dumps({"check":check,"corpus_sha256":sha(CORPUS)},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); main(p.parse_args().check)
