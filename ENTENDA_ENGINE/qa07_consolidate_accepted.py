"""Consolidate independently accepted QA-07 content, merging overlapping targets once."""
import hashlib
import json
from pathlib import Path

import qa07_prepare as prep


OUT = prep.OUT
FIVE = {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


MERGED = {
    "CC2002:ART.1301": {
        "o_que_diz": "Janelas, eirados, terraços e varandas com vista direta para o terreno vizinho devem ficar a pelo menos um metro e meio da divisa. Para janela com visão oblíqua ou perpendicular à linha divisória, o mínimo é de setenta e cinco centímetros. Essas restrições não alcançam pequenas aberturas exclusivamente para luz ou ventilação quando tiverem, no máximo, dez centímetros de largura por vinte de comprimento e estiverem a mais de dois metros de altura em cada piso.",
        "o_que_significa": "A lei protege a privacidade do vizinho com afastamentos diferentes conforme a direção da vista. Também admite abertura reduzida e elevada apenas para iluminação ou ventilação, desde que todas as dimensões legais sejam respeitadas.",
        "exemplo_pratico": "Uma janela perpendicular à divisa pode observar o mínimo de setenta e cinco centímetros; uma janela com vista direta exige um metro e meio. Já uma abertura de dez por vinte centímetros instalada acima de dois metros do piso pode servir apenas à ventilação sem seguir esses afastamentos.",
        "atencao": "Não confunda os três regimes: um metro e meio para vista direta; setenta e cinco centímetros para visão oblíqua ou perpendicular; e a exceção das pequenas aberturas, cujos limites de largura, comprimento e altura são cumulativos.",
        "palavras_dificeis": [{"termo": "Visão oblíqua", "explicacao": "vista lateral ou indireta em relação à linha divisória"}, {"termo": "Eirado", "explicacao": "terraço ou área descoberta elevada de uma edificação"}],
    },
    "CC2002:ART.1358-P": {
        "o_que_diz": "A convenção do condomínio edilício com multipropriedade deve identificar unidades e períodos e disciplinar despesas, administração, sanções, quóruns e o rateio entre titulares da mesma unidade. Sem critério diferente no instrumento de instituição ou na convenção de multipropriedade, o rateio é proporcional à fração de tempo de cada titular. Se houver sistema de intercâmbio de período ou local de uso, a convenção deve indicá-lo; a responsabilidade e as obrigações da companhia de intercâmbio ficam limitadas à documentação de sua contratação.",
        "o_que_significa": "A convenção precisa organizar tanto os custos de cada período quanto eventual troca de tempo ou local de uso. Na falta de regra válida diferente, quem possui período maior arca com parcela proporcionalmente maior; e a companhia de intercâmbio responde apenas pelo que assumiu contratualmente.",
        "exemplo_pratico": "Dois titulares têm uma e três semanas na mesma unidade. Sem outro critério válido, o segundo participa do rateio em proporção três vezes maior. Se o empreendimento permitir trocar semanas por estadias em outro local, a convenção identifica o sistema e o contrato delimita as obrigações da companhia.",
        "atencao": "A proporcionalidade à fração de tempo é regra supletiva. A existência de intercâmbio não é presumida: se oferecido, deve constar da convenção, e a companhia não assume obrigações além das previstas na contratação.",
        "palavras_dificeis": [{"termo": "Regra supletiva", "explicacao": "regra aplicada quando os instrumentos permitidos não estabelecem solução diferente"}, {"termo": "Sistema de intercâmbio", "explicacao": "mecanismo contratual de troca do período ou do local de fruição da multipropriedade"}],
    },
}


def ids_high(row, group):
    if group == "A":
        return [f["finding_id"] for f in row["findings"]], [f["subdivision_id"] for f in row["findings"]]
    return row["finding_ids"], row["subdivision_ids"]


def build():
    prep.build()
    a, b = load("QA07_EDITOR_HIGH_A.json"), load("QA07_EDITOR_HIGH_B.json")
    b2, ind = load("QA07_EDITOR_HIGH_B_REVISION_2.json"), load("QA07_INDETERMINATE_DECISIONS.json")
    ra, rb = load("QA07_REVIEW_HIGH_A.json"), load("QA07_REVIEW_HIGH_B.json")
    rb2, ri = load("QA07_REVIEW_HIGH_B_REVISION_2.json"), load("QA07_REVIEW_INDETERMINATE.json")
    if any(r["decision"] != "ACEITA" for r in ra["records"]):
        raise RuntimeError("HIGH_A contains unaccepted proposal")
    rejected = {r["target_id"] for r in rb["records"] if r["decision"] == "REJEITADA"}
    if rejected != {"CC2002:ART.1358-J", "CC2002:ART.1358-S"}:
        raise RuntimeError("unexpected HIGH_B rejection set")
    if any(r["decision"] != "ACEITA" for r in rb2["records"]):
        raise RuntimeError("revised HIGH_B contains unaccepted proposal")
    if any(r["review_decision"] != "ACEITA" for r in ri["records"]):
        raise RuntimeError("indeterminate decision not independently accepted")
    rows = {}
    for group, doc in (("A", a), ("B", b)):
        for row in doc["records"]:
            if row["target_id"] in rejected:
                continue
            fids, sids = ids_high(row, group)
            rows[row["target_id"]] = {
                "target_id": row["target_id"], "finding_ids": fids, "subdivision_ids": sids,
                "previous_content": row["previous_content"], "proposed_content": row["proposed_content"],
                "origins": [f"HIGH_{group}"], "integration_kind": "DIRECT_ACCEPTED_PROPOSAL",
            }
    for row in b2["records"]:
        rows[row["target_id"]] = {
            "target_id": row["target_id"], "finding_ids": row["finding_ids"],
            "subdivision_ids": row["subdivision_ids"], "previous_content": row["previous_content"],
            "proposed_content": row["proposed_content"], "origins": ["HIGH_B_REVISION_2"],
            "integration_kind": "REVISED_AFTER_REJECTION_AND_ACCEPTED",
        }
    for row in ind["records"]:
        if row["decision"] != "CONFIRMADO_PARA_CORRECAO":
            continue
        tid = row["target_id"]
        if tid in rows:
            rows[tid]["finding_ids"].append(row["finding_id"])
            rows[tid]["subdivision_ids"].append(row["subdivision_id"])
            rows[tid]["origins"].append("INDETERMINATE_CONFIRMED")
            rows[tid]["proposed_content"] = MERGED[tid]
            rows[tid]["integration_kind"] = "INTEGRATED_OVERLAPPING_ACCEPTED_PROPOSALS"
        else:
            rows[tid] = {
                "target_id": tid, "finding_ids": [row["finding_id"]],
                "subdivision_ids": [row["subdivision_id"]], "previous_content": row["previous_content"],
                "proposed_content": row["proposed_content"], "origins": ["INDETERMINATE_CONFIRMED"],
                "integration_kind": "DIRECT_ACCEPTED_PROPOSAL",
            }
    records = sorted(rows.values(), key=lambda r: (int(r["target_id"].split(".")[1].split("-")[0]), r["target_id"]))
    if len(records) != 31 or len({r["target_id"] for r in records}) != 31:
        raise RuntimeError("accepted target cardinality mismatch")
    ids = [fid for row in records for fid in row["finding_ids"]]
    if len(ids) != 49 or len(set(ids)) != 49:
        raise RuntimeError("accepted correction finding coverage mismatch")
    for row in records:
        if set(row["previous_content"]) != FIVE or set(row["proposed_content"]) != FIVE:
            raise RuntimeError(f"five-field mismatch: {row['target_id']}")
    source_hashes = {name: sha(OUT / name) for name in (
        "QA07_EDITOR_HIGH_A.json", "QA07_EDITOR_HIGH_B.json", "QA07_EDITOR_HIGH_B_REVISION_2.json",
        "QA07_INDETERMINATE_DECISIONS.json", "QA07_REVIEW_HIGH_A.json", "QA07_REVIEW_HIGH_B.json",
        "QA07_REVIEW_HIGH_B_REVISION_2.json", "QA07_REVIEW_INDETERMINATE.json")}
    doc = {
        "schema_version": 1, "mission": "QA-07", "as_of": prep.AS_OF,
        "status": "ACCEPTED_CONTENT_CONSOLIDATED_PENDING_OVERLAP_REVIEW",
        "target_total": 31, "resolved_finding_total": 49,
        "high_findings": 41, "indeterminate_confirmed_for_correction": 8,
        "indeterminate_materially_sufficient": 2,
        "overlapping_targets_integrated": sorted(MERGED), "source_sha256": source_hashes,
        "records": records, "corpus_modified": False, "human_approval_claimed": False,
    }
    path = OUT / "QA07_ACCEPTED_CONTENT_DRAFT.json"
    prep.write(path, doc)
    print(json.dumps({"targets": 31, "findings": 49, "overlaps": sorted(MERGED),
                      "sha256": sha(path)}, ensure_ascii=False))


if __name__ == "__main__":
    build()
