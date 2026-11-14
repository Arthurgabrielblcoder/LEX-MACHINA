"""Revise only the two HIGH_B proposals rejected by independent review."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "derived/qa07_high_findings_resolution"
EDITOR = OUT / "QA07_EDITOR_HIGH_B.json"
REVIEW = OUT / "QA07_REVIEW_HIGH_B.json"
DEST = OUT / "QA07_EDITOR_HIGH_B_REVISION_2.json"
SOURCE = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build():
    editor = load(EDITOR)
    review = load(REVIEW)
    rejected = {row["target_id"]: row for row in review["records"] if row["decision"] == "REJEITADA"}
    if set(rejected) != {"CC2002:ART.1358-J", "CC2002:ART.1358-S"}:
        raise RuntimeError("unexpected rejected proposal scope")
    original = {row["target_id"]: row for row in editor["records"]}
    records = []

    row = deepcopy(original["CC2002:ART.1358-J"])
    row["revision"] = {
        "round": 2,
        "objection_code": "DAILY_FINE_SOURCE_OVERGENERALIZED",
        "resolution": (
            "A multa diária do inciso VIII foi vinculada ao instrumento pertinente, que pode ser o "
            "instrumento de instituição ou a convenção; as sanções do § 1º foram separadas e "
            "mantidas como matéria de previsão obrigatória na convenção."
        ),
    }
    row["proposed_content"] = {
        "o_que_diz": (
            "O multiproprietário deve pagar contribuições mesmo sem usar, conservar e usar o imóvel "
            "conforme sua finalidade, comunicar danos, permitir reparos urgentes e responder pelos "
            "danos causados por si ou por quem autorizar. Deve desocupar até o dia e a hora fixados no "
            "instrumento de instituição ou na convenção, sob a multa diária estipulada no instrumento "
            "pertinente. Separadamente, a convenção deve prever multa por descumprimento e, se houver "
            "reiteração, multa progressiva e perda temporária do uso da fração. Reparos por uso normal "
            "e desgaste natural são custeados por todos; os causados por uso anormal cabem apenas ao "
            "responsável, sem prejuízo de multa."
        ),
        "o_que_significa": (
            "Cada titular precisa entregar o imóvel no horário e no estado necessários ao período "
            "seguinte. A multa diária pela demora segue o instrumento que disciplina a desocupação; "
            "as demais sanções por descumprimento seguem a convenção. O custo coletivo cobre desgaste "
            "normal, enquanto dano por uso anormal recai sobre o responsável."
        ),
        "exemplo_pratico": (
            "Um titular permanece após o horário fixado e entrega o imóvel danificado por uso anormal. "
            "Pode sofrer a multa diária prevista no instrumento pertinente e arcar sozinho com o "
            "reparo. Se reiterar descumprimentos, poderá sofrer a multa progressiva e a perda temporária "
            "de uso previstas na convenção."
        ),
        "atencao": (
            "A multa diária do atraso deve estar convencionada no instrumento pertinente, que pode ser "
            "o instrumento de instituição ou a convenção. Já a multa por descumprimento, a multa "
            "progressiva e a perda temporária do uso dependem de previsão na convenção; estas duas "
            "últimas exigem descumprimento reiterado. Desgaste natural não pode ser imputado somente a "
            "um titular."
        ),
        "palavras_dificeis": [
            {"termo": "Instrumento pertinente", "explicacao": "instrumento de instituição ou convenção que disciplina a obrigação e a multa diária no caso concreto"},
            {"termo": "Multa progressiva", "explicacao": "sanção cujo valor aumenta diante da repetição do descumprimento"},
            {"termo": "Uso anormal", "explicacao": "utilização incompatível com a finalidade ou os cuidados ordinários do imóvel"},
        ],
    }
    records.append(row)

    row = deepcopy(original["CC2002:ART.1358-S"])
    row["revision"] = {
        "round": 2,
        "objection_code": "SPECIAL_RENTAL_SYSTEM_GATE_INCOMPLETE",
        "resolution": (
            "O âmbito do parágrafo único foi explicitado cumulativamente: locação das frações "
            "exclusivamente por administração única e repartição das receitas independentemente da "
            "ocupação efetiva."
        ),
    }
    row["proposed_content"] = {
        "o_que_diz": (
            "O inadimplemento de despesas ordinárias ou extraordinárias pode levar, pelo procedimento "
            "civil, à adjudicação da fração de tempo ao condomínio edilício. Há medidas adicionais "
            "somente quando o imóvel integra empreendimento em que os titulares podem ou devem locar "
            "suas frações exclusivamente por uma administração única e repartem as receitas das "
            "locações independentemente da ocupação efetiva de cada unidade. Nesse regime específico, "
            "a convenção pode proibir o uso até a quitação, incluir a fração no conjunto administrado "
            "e obrigar a administradora a aplicar integralmente os valores líquidos do inadimplente nas "
            "dívidas dos condomínios edilício e de multipropriedade, repassando imediatamente eventual saldo."
        ),
        "o_que_significa": (
            "A fração pode satisfazer judicialmente a dívida. As medidas sobre uso e receitas não valem "
            "para qualquer locação centralizada: exigem, ao mesmo tempo, exclusividade da administração "
            "das locações e partilha das receitas sem depender de qual unidade foi efetivamente ocupada, "
            "além de previsão na convenção."
        ),
        "exemplo_pratico": (
            "Em empreendimento no qual todas as frações são locadas exclusivamente por uma única "
            "administradora e a receita comum é repartida mesmo quando certa unidade não foi ocupada, a "
            "convenção pode colocar a fração do inadimplente no conjunto administrado. A administradora "
            "usa os valores líquidos dele para quitar os débitos condominiais e repassa imediatamente o saldo."
        ),
        "atencao": (
            "Proibição de uso, inclusão da fração no conjunto administrado e aplicação das receitas não "
            "são automáticas nem alcançam toda multipropriedade com locação. Dependem cumulativamente do "
            "sistema exclusivo de administração única, da partilha de receitas independentemente da "
            "ocupação efetiva e de disciplina na convenção."
        ),
        "palavras_dificeis": [
            {"termo": "Adjudicação", "explicacao": "transferência da fração ao credor, pelo procedimento legal, para satisfação da dívida"},
            {"termo": "Administração única", "explicacao": "gestão exclusiva das locações das frações por uma só administradora"},
            {"termo": "Valores líquidos", "explicacao": "receitas restantes após as deduções legítimas do sistema de locação"},
        ],
    }
    records.append(row)

    doc = {
        "schema_version": 1,
        "mission": "QA-07",
        "role": "EDITOR_REVISION_AFTER_INDEPENDENT_REJECTION",
        "as_of": "2026-11-14",
        "status": "REVISION_2_PENDING_NEW_INDEPENDENT_REVALIDATION",
        "original_editorial_file": EDITOR.name,
        "original_editorial_sha256": sha(EDITOR),
        "negative_review_file": REVIEW.name,
        "negative_review_sha256": sha(REVIEW),
        "source": {"url": SOURCE, "cutoff": "2026-11-14", "authority": "Câmara dos Deputados"},
        "target_total": 2,
        "finding_total": sum(len(row["finding_ids"]) for row in records),
        "records": records,
        "corpus_modified": False,
        "original_proposal_modified": False,
        "human_approval_claimed": False,
    }
    DEST.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"targets": 2, "findings": doc["finding_total"], "sha256": sha(DEST)}, ensure_ascii=False))


if __name__ == "__main__":
    build()
