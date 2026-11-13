"""Prepare the sole QA-06 editorial correction (Civil Code art. 1,104)."""
import json
from pathlib import Path

import qa06_prepare as prep


HERE = Path(__file__).resolve().parent
OUT = prep.OUT
BASELINE = prep.CORPUS
FINDING = prep.FINDING
TARGET = "CC2002:ART.1104"
NEIGHBORS = ["CC2002:ART.1102", "CC2002:ART.1103", TARGET, "CC2002:ART.1105"]
OFFICIAL_URL = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline mismatch")
    rows = [json.loads(line) for line in BASELINE.read_text(encoding="utf-8").splitlines() if line]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    finding_document = json.loads(FINDING.read_text(encoding="utf-8"))
    if finding_document["total"] != 1 or finding_document["findings"][0]["target_id"] != TARGET:
        raise RuntimeError("unexpected QA-05 pending finding")
    baseline = active[TARGET]
    proposed = {
        "o_que_diz": baseline["content"]["o_que_diz"],
        "o_que_significa": (
            "Quanto às obrigações do cargo e à responsabilidade por sua atuação, "
            "o liquidante fica sujeito às mesmas regras jurídicas próprias dos administradores "
            "da sociedade que está sendo liquidada."
        ),
        "exemplo_pratico": (
            "Se o liquidante descumpre um dever do cargo e causa prejuízo à sociedade, a análise "
            "de sua responsabilidade segue o regime aplicável aos administradores daquela sociedade."
        ),
        "atencao": (
            "Este artigo trata do regime das obrigações e da responsabilidade do liquidante. "
            "A lista de deveres operacionais está no art. 1.103, e os poderes e limites de atuação "
            "estão no art. 1.105; o art. 1.104 não cria periodicidade própria para balanços."
        ),
        "palavras_dificeis": [{
            "termo": "Sociedade liquidanda",
            "explicacao": "sociedade que está em processo de liquidação",
        }],
    }
    changed = [field for field in prep.FIELDS if proposed[field] != baseline["content"][field]]
    if changed != ["o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"]:
        raise RuntimeError(f"unexpected changed fields: {changed}")
    record = {
        "target_id": TARGET,
        "baseline_explanation_id": baseline["explanation_id"],
        "baseline_editorial_version": baseline["editorial_version"],
        "source_finding": str(FINDING.relative_to(HERE)).replace("\\", "/"),
        "source_finding_sha256": prep.sha256(FINDING),
        "severity": "ALTO",
        "nature": "DESLOCAMENTO_DE_CONTEUDO_DO_ARTIGO_VIZINHO_E_PERIODICIDADE_INCORRETA",
        "official_source_url": OFFICIAL_URL,
        "official_source_checked_on": prep.AS_OF,
        "official_neighbor_snapshots": {target: active[target]["source"]["source_text_snapshot"] for target in NEIGHBORS},
        "baseline_content": baseline["content"],
        "proposed_content": proposed,
        "changed_fields": changed,
        "editorial_rationale": (
            "Remove tarefas do art. 1.103 e a periodicidade de balanço que não consta do art. 1.104; "
            "restaura a regra de submissão das obrigações e da responsabilidade do liquidante ao "
            "regime próprio dos administradores, sem importar poderes do art. 1.105."
        ),
        "neighbor_boundary_verification": {
            "art_1102": "liquidação e investidura do liquidante",
            "art_1103": "deveres operacionais do liquidante",
            "art_1104": "obrigações e responsabilidade regidas pelas regras dos administradores",
            "art_1105": "representação, poderes e limites do liquidante",
        },
        "editorial_status": "PROPOSED_PENDING_INDEPENDENT_REVALIDATION",
        "human_approval_claimed": False,
    }
    document = {
        "schema_version": 1, "mission": "QA-06-FRONT-A", "as_of": prep.AS_OF,
        "status": "EDITORIAL_PROPOSAL_PENDING_INDEPENDENT_REVALIDATION",
        "total": 1, "records": [record],
    }
    proposal = OUT / "QA06_A_EDITORIAL_PROPOSAL_1104.json"
    prep.write_json(proposal, document)
    checkpoint = {
        "schema_version": 1, "mission": "QA-06-FRONT-A", "checkpoint": "A-CP01",
        "as_of": prep.AS_OF, "status": "COMPLETE_PENDING_INDEPENDENT_REVALIDATION",
        "target_id": TARGET, "changed_fields": changed,
        "baseline_corpus_sha256": prep.sha256(BASELINE),
        "finding_sha256": prep.sha256(FINDING), "proposal_sha256": prep.sha256(proposal),
        "human_approval_claimed": False,
    }
    prep.write_json(OUT / "QA06_A_CP01.json", checkpoint)
    print(json.dumps({"target_id": TARGET, "changed_fields": changed,
                      "proposal_sha256": prep.sha256(proposal)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
