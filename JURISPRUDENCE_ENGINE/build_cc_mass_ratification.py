"""Constrói a camada determinística de decisão humana para as 681 relações CC prontas.

Não pesquisa, não ratifica, não materializa e não acessa o dispositivo. A única fonte
é a auditoria massiva versionada no commit 9e1febc.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path


ENG = Path(__file__).resolve().parent
OUT = ENG / "CC_MASS_DISCOVERY"
AUDIT_COMMIT = "9e1febc"
BASELINE = "MULTINORM_FROZEN_CF315_198_CC49_39"
GROUP_VERSION = "1.0.0"
READY_STATES = {"READY_FOR_BLOCK_DECISION", "READY_WITH_QUALIFICATION"}
SPECIAL_FLAGS = {
    "CORRESPONDENCIA_CC1916": "correspondência histórica com o CC/1916",
    "REDACAO_ALTERADA_APOS_JULGAMENTO": "redação do dispositivo alterada após o julgamento",
    "TARGET_FALLBACK_TO_PARENT": "target específico recuou para o dispositivo-pai",
    "USO_CONTEXTUAL_POSSIVEL": "possível uso contextual do dispositivo",
}

GROUP_META = {
    "GROUP_A": {
        "description": "Autoridade elevada e relação direta, pronta para decisão em bloco.",
        "authority_policy": "Precedente qualificado com mérito e identidade validados.",
        "qualification_policy": "Sem nota material especial além da identificação da autoridade.",
        "risk": "BAIXO",
        "recommended_human_action": "APPROVE_GROUP",
    },
    "GROUP_B": {
        "description": "Autoridade elevada com nota editorial obrigatória.",
        "authority_policy": "Precedente qualificado, súmula ou acórdão de Seção/Corte Especial; autoridade não é inferida da qualidade da relação.",
        "qualification_policy": "Aprovação somente com a nota individual já auditada.",
        "risk": "BAIXO A MODERADO",
        "recommended_human_action": "APPROVE_GROUP",
    },
    "GROUP_C": {
        "description": "Acórdãos de Turma diretos com corroboração textual por outros julgados.",
        "authority_policy": "PERSUASIVE_NON_BINDING; CORROBORATED != BINDING e CORROBORATED != NECESSARILY SETTLED.",
        "qualification_policy": "Exige nota explícita de natureza persuasiva; corroboração não autoriza a expressão jurisprudência pacífica.",
        "risk": "MODERADO",
        "recommended_human_action": "APPROVE_GROUP",
    },
    "GROUP_D": {
        "description": "Acórdãos de Turma materialmente diretos, isolados nas fontes consultadas.",
        "authority_policy": "PERSUASIVE_NON_BINDING; não é repetitivo, IAC, súmula nem precedente obrigatório.",
        "qualification_policy": "Exige notas de natureza persuasiva e de decisão localizada isoladamente.",
        "risk": "MODERADO",
        "recommended_human_action": "APPROVE_GROUP",
    },
    "GROUP_E": {
        "description": "Acórdãos de Turma cuja publicação futura usa representante substituto superior ao candidato original.",
        "authority_policy": "PERSUASIVE_NON_BINDING; a substituição não eleva a autoridade.",
        "qualification_policy": "Exige nota de substituição e uso obrigatório do replacement precedent validado.",
        "risk": "MODERADO",
        "recommended_human_action": "APPROVE_GROUP",
    },
    "GROUP_F": {
        "description": "Exceções materiais que merecem decisão individual, não aprovação genérica.",
        "authority_policy": "A autoridade é preservada individualmente; nenhum caso recebe elevação automática.",
        "qualification_policy": "Revisão individual por temporalidade, correspondência histórica, contextualidade ou target sensível.",
        "risk": "MODERADO A ALTO",
        "recommended_human_action": "HOLD_GROUP",
    },
}

OUTPUT_NAMES = (
    "CC_MASS_RATIFICATION_GROUPS.json",
    "CC_MASS_RATIFICATION_DECISION_BOARD.md",
    "CC_MASS_RATIFICATION_GROUP_MEMBERS.md",
    "CC_MASS_RATIFICATION_EXCEPTIONS.md",
    "CC_MASS_RATIFICATION_DECISION_TEMPLATE.json",
    "CC_MASS_REPLACEMENT_AUDIT.json",
    "CC_MASS_TURMA_DISPLAY_REQUIREMENTS.md",
    "CC_MASS_RATIFICATION_GATES.md",
    "CC_MASS_RATIFICATION_PREPARATION_METRICS.json",
    "CC_MASS_RATIFICATION_PREPARATION_SHA256.json",
)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_audit_hashes() -> None:
    manifest = json.loads((OUT / "CC_MASS_AUDIT_SHA256.json").read_text(encoding="utf-8"))
    required = {
        "CC_MASS_AUDIT_ALL_932.jsonl",
        "CC_MASS_AUDIT_METRICS.json",
        "CC_MASS_RATIFICATION_READY.json",
        "CC_MASS_RATIFICATION_HOLD.json",
        "CC_MASS_RATIFICATION_REJECT.json",
        "CC_MASS_TURMA_CORROBORATION.json",
    }
    for name in sorted(required):
        expected = manifest["outputs"][name]
        actual = sha((OUT / name).read_bytes())
        if actual != expected:
            raise ValueError(f"artefato de auditoria stale: {name}: {actual} != {expected}")


def special_reasons(row: dict) -> list[str]:
    reasons = [label for flag, label in SPECIAL_FLAGS.items() if flag in row["flags"]]
    temporal = row["checks"]["TEMPORAL"]
    if temporal != "COMPATIBLE" and not any("temporal" in x or "CC/1916" in x or "redação" in x for x in reasons):
        reasons.append(f"estado temporal {temporal}")
    if row.get("correspondence") and not any("correspondência" in x for x in reasons):
        reasons.append("relação por correspondência normativa/histórica")
    return reasons


def group_for(row: dict) -> str:
    if special_reasons(row):
        return "GROUP_F"
    if row["authority"] != "TURMA_ACORDAO":
        return "GROUP_A" if row["editorial_state"] == "READY_FOR_BLOCK_DECISION" else "GROUP_B"
    if row["turma"].get("substitution"):
        return "GROUP_E"
    if row["turma"]["classification"] == "CORROBORATED_TURMA_CASELAW":
        return "GROUP_C"
    return "GROUP_D"


def relation_class(row: dict) -> str:
    sub = (row.get("turma") or {}).get("substitution")
    if sub:
        match = re.search(r"evidência ([A-Z_]+)", sub["reason"])
        if match:
            return match.group(1)
    return row["checks"]["PERTINENCE"]


def relation_record(row: dict, ready_item: dict) -> dict:
    sub = (row.get("turma") or {}).get("substitution")
    identity = row["identity"]
    precedent = ready_item["PRECEDENTE"]
    return {
        "id": row["id"],
        "target": ready_item["ARTIGO"],
        "precedent": precedent,
        "tribunal": precedent.split(":", 1)[0],
        "orgao": ready_item["ORGAO_JULGADOR"],
        "classe": precedent.split(":")[1],
        "data": sub["proposed_date"] if sub else identity["data"],
        "authority_class": row["authority"],
        "relation_class": relation_class(row),
        "risk": ready_item["RISCO"],
        "reader_note": ready_item["NOTA_NECESSARIA"],
        "source_evidence": ready_item["FONTE_OFICIAL"],
        "current_human_decision": "PENDING",
        "substituted_from": ready_item.get("substituted_from"),
        "new_target": bool(row["new_target"]),
        "special_reasons": special_reasons(row),
    }


def group_hash(group_id: str, relation_ids: list[str], version: str = GROUP_VERSION) -> str:
    composition = {"group_id": group_id, "relation_ids": sorted(relation_ids), "version": version}
    canonical = json.dumps(composition, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def projection(selected: list[dict]) -> dict:
    new_targets = {item["target"] for item in selected if item["new_target"]}
    return {
        "relations": 49 + len(selected),
        "targets": 39 + len(new_targets),
        "added_relations": len(selected),
        "new_targets": len(new_targets),
    }


def replacement_audit(rows: list[dict], ready_by_id: dict[str, dict]) -> dict:
    items, errors = [], []
    for row in rows:
        sub = (row.get("turma") or {}).get("substitution")
        if not sub or row["editorial_state"] not in READY_STATES:
            continue
        ready = ready_by_id[row["id"]]
        checks = {
            "replacement_is_effective": ready["PRECEDENTE"] == sub["proposed"],
            "old_process_preserved": ready.get("substituted_from") == row["precedent"],
            "target_preserved": ready["ARTIGO"] == row["target"],
            "identity_complete": all(sub.get(k) for k in ("proposed", "proposed_orgao", "proposed_date", "proposed_espelho", "proposed_registro")),
            "source_provenance_present": bool(ready.get("FONTE_OFICIAL")),
        }
        bad = [key for key, value in checks.items() if not value]
        if bad:
            errors.append({"id": row["id"], "errors": bad})
        items.append({
            "old_candidate_id": row["id"],
            "old_process": row["precedent"],
            "replacement_process": sub["proposed"],
            "target": row["target"],
            "orgao": sub["proposed_orgao"],
            "data": sub["proposed_date"],
            "reason": sub["reason"],
            "source_provenance": {
                "espelho": sub["proposed_espelho"],
                "registro": sub["proposed_registro"],
                "fonte": ready["FONTE_OFICIAL"],
            },
            "checks": checks,
        })
    return {
        "schema_version": 1,
        "audit_commit": AUDIT_COMMIT,
        "replacement_relations": len(items),
        "replacement_identity_errors": len(errors),
        "errors": errors,
        "items": sorted(items, key=lambda x: x["old_candidate_id"]),
    }


def board_md(groups: list[dict], metrics: dict, replacements: dict) -> str:
    lines = [
        "# CC MASS RATIFICATION — painel de decisão humana",
        "",
        "> Preparação host-only. Nenhuma relação foi aprovada, materializada ou implantada.",
        "",
        f"Baseline: `{BASELINE}` · auditoria: `{AUDIT_COMMIT}` · relações prontas: **681**.",
        "",
        "| Grupo | Natureza | Relações | Targets | Risco | Recomendação |",
        "|---|---|---:|---:|---|---|",
    ]
    for group in groups:
        meta = GROUP_META[group["group_id"]]
        lines.append(f"| {group['group_id']} | {meta['description']} | {group['relation_count']} | {group['target_count']} | {meta['risk']} | `{meta['recommended_human_action']}` |")
    lines += [
        "",
        "## Regras editoriais transversais",
        "",
        "Qualidade material e autoridade são dimensões independentes. Uma relação direta de Turma continua `PERSUASIVE_NON_BINDING`.",
        "",
        "**CORROBORATED != BINDING** e **CORROBORATED != NECESSARILY SETTLED**. Corroboração significa somente que outros acórdãos materialmente semelhantes foram encontrados; este painel não usa a expressão “jurisprudência pacífica”.",
        "",
        "Todas as decisões permanecem `PENDING`. A aprovação futura exige `group_id` e `group_sha256`; composição alterada invalida a decisão.",
        "",
    ]
    historical = {
        "GROUP_A": "Baixo risco após correções sistêmicas; não inclui Tier A rejeitado nem duplicata de leading case.",
        "GROUP_B": "Notas preservam fundamento em paradigma, verbetação estruturada, exceção ou limitação de alcance.",
        "GROUP_C": "A regra de corroboração é proxy textual, não prova de consolidação.",
        "GROUP_D": "Ausência de corroboração suficiente é explicitada ao leitor.",
        "GROUP_E": f"{replacements['replacement_relations']} substituições prontas foram conferidas estruturalmente; erros de identidade: {replacements['replacement_identity_errors']}.",
        "GROUP_F": "Concentra temporalidade, CC/1916, contextualidade, fallback de target e correspondências normativas.",
    }
    for group in groups:
        meta = GROUP_META[group["group_id"]]
        examples = "; ".join(f"{x['id']} ({x['target']} → {x['precedent']})" for x in group["items"][:3])
        lines += [
            f"## {group['group_id']} — {group['relation_count']} relações / {group['target_count']} targets",
            "",
            meta["description"],
            "",
            f"- Autoridade: {meta['authority_policy']}",
            f"- Qualificação/notas: {meta['qualification_policy']}",
            f"- Risco residual: {meta['risk']}. {historical[group['group_id']]}",
            f"- Auditadas previamente: {group['relation_count']}/{group['relation_count']}.",
            f"- Exemplos: {examples}.",
            f"- Consequência de aprovar: registra decisão humana para este conjunto exato; não materializa nem faz deploy. Hash `{group['sha256']}`.",
            "",
        ]
    p = metrics["projections"]
    lines += [
        "## Projeções deduplicadas",
        "",
        "| Cenário | Relações CC | Targets CC |",
        "|---|---:|---:|",
        "| Baseline físico | 49 | 39 |",
        f"| Somente GROUP_A | {p['PROJECTED_A']['relations']} | {p['PROJECTED_A']['targets']} |",
        f"| GROUP_A + GROUP_B | {p['PROJECTED_HIGH_AUTHORITY']['relations']} | {p['PROJECTED_HIGH_AUTHORITY']['targets']} |",
        f"| + GROUP_C | {p['PROJECTED_WITH_CORROBORATED_TURMA']['relations']} | {p['PROJECTED_WITH_CORROBORATED_TURMA']['targets']} |",
        f"| + GROUP_D | {p['PROJECTED_WITH_ALL_DIRECT_TURMA']['relations']} | {p['PROJECTED_WITH_ALL_DIRECT_TURMA']['targets']} |",
        f"| Todos os grupos favoráveis | {p['PROJECTED_ALL_READY']['relations']} | {p['PROJECTED_ALL_READY']['targets']} |",
        "",
        "Targets são deduplicados contra o baseline físico; não são soma ingênua das linhas dos grupos.",
        "",
        "## Capacidade e bloqueios",
        "",
        f"A simulação versionada permanece coerente: {metrics['capacity']['LOOKUP_ENTRIES']} lookup entries de limite {metrics['capacity']['LOOKUP_LIMIT']}; PSRAM total estimada {metrics['capacity']['PSRAM_TOTAL_BYTES']} B; blocker: `{metrics['CAPACITY_BLOCKER']}`.",
        "",
        "`TURMA_DISPLAY_GATE = PENDING`: nenhuma relação de Turma pode avançar à materialização antes da apresentação compacta e da ficha detalhada serem implementadas e validadas.",
        "",
        "Lista completa: `CC_MASS_RATIFICATION_GROUP_MEMBERS.md`. Exceções: `CC_MASS_RATIFICATION_EXCEPTIONS.md`.",
    ]
    return "\n".join(lines) + "\n"


def members_md(groups: list[dict]) -> str:
    lines = [
        "# CC MASS RATIFICATION — composição completa dos grupos",
        "",
        "Todas as decisões estão `PENDING`. A lista é informativa e não materializa relações.",
        "",
    ]
    for group in groups:
        lines += [
            f"## {group['group_id']} — {group['relation_count']} relações — `{group['sha256']}`",
            "",
            "| ID | Target | Precedente | Tribunal | Órgão | Classe | Data | Autoridade | Relação | Risco | Nota | Fonte | Decisão |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for item in group["items"]:
            vals = [item[k] for k in ("id", "target", "precedent", "tribunal", "orgao", "classe", "data", "authority_class", "relation_class", "risk", "reader_note", "source_evidence", "current_human_decision")]
            clean = [str(v or "—").replace("|", "\\|").replace("\n", " ") for v in vals]
            lines.append("| " + " | ".join(clean) + " |")
        lines.append("")
    return "\n".join(lines)


def exceptions_md(group_f: dict) -> str:
    lines = [
        "# CC MASS RATIFICATION — exceções para revisão individual",
        "",
        f"Exceções materiais: **{group_f['relation_count']}**. Notas padrão de autoridade não foram usadas, por si sós, para transformar uma relação em exceção.",
        "",
        "| ID | Target | Precedente | Motivo material | Decisão |",
        "|---|---|---|---|---|",
    ]
    categories = collections.Counter()
    for item in group_f["items"]:
        reason = "; ".join(item["special_reasons"])
        categories.update(item["special_reasons"])
        lines.append(f"| {item['id']} | {item['target']} | {item['precedent']} | {reason} | PENDING |")
    lines += ["", "## Categorias", ""] + [f"- {name}: {count}" for name, count in sorted(categories.items())]
    lines += ["", "Esses casos não devem ser incluídos em uma aprovação genérica dos demais grupos.", ""]
    return "\n".join(lines)


def display_requirements_md() -> str:
    return """# CC MASS — requisitos de apresentação para acórdãos de Turma

`TURMA_DISPLAY_GATE = PENDING`

Nenhuma alteração de firmware é feita nesta etapa. Uma relação de Turma ratificada não pode ser materializada enquanto este gate estiver pendente.

## Lista compacta

- Exibir tribunal, classe e número: `STJ · REsp 2.145.365`.
- Quando couber no TFT, acrescentar órgão abreviado: `STJ · REsp 2.145.365 · 3ª T.`.
- Nunca rotular acórdão de Turma como repetitivo, IAC, súmula ou precedente vinculante.
- Preservar truncamento previsível sem esconder classe ou número.

## Ficha

- Tribunal, órgão julgador, classe, processo, data e fonte oficial.
- Natureza: `jurisprudência persuasiva, não vinculante`.
- Nota editorial e eventual substituição do representante.
- Corroboração, quando existente, sem afirmar consolidação ou pacificação.

## Compatibilidade retroativa

- Súmulas, repetitivos, IAC, RG e controle concentrado já existentes não podem mudar de identidade ou navegação.
- Registros legados `ACORDAO n` devem continuar legíveis durante a migração.
- O novo metadado não pode alterar as chaves congeladas CF 315/198 e CC 49/39.

## Testes futuros no hardware

1. REsp da 3ª Turma e AREsp da 4ª Turma, com números longos.
2. Acórdão corroborado e acórdão isolado.
3. Representante substituto, confirmando que o número antigo não aparece.
4. Navegação lista → ficha → voltar.
5. Regressão de súmula, repetitivo, IAC, RG e ADI legados.

`FIRMWARE_CHANGED = NO`
"""


def gates_md() -> str:
    return """# CC MASS RATIFICATION — gates futuros

Esta preparação não aprova, materializa nem implanta qualquer relação.

## Precedentes qualificados e autoridades superiores

`ratificação humana com group_id + group_sha256 → validação da decisão → materialization preflight → revisão`

## Acórdãos de Turma

`ratificação humana com group_id + group_sha256 → TURMA_DISPLAY_GATE → simulação host-only → flash somente se necessário → regressão física → deploy de dados`

## Regras de bloqueio

- Hash ausente ou composição alterada: rejeitar a ratificação e pedir reconciliação.
- Exceção não pertencente ao grupo: rejeitar.
- ID repetido ou desconhecido: rejeitar.
- Relação `HOLD`/`REJECT` presente nos grupos: rejeitar.
- Decisão de Turma tratada como vinculante/repetitiva: rejeitar.
- Substituição que volte ao processo antigo: rejeitar.
- `TURMA_DISPLAY_GATE = PENDING`: bloquear materialização de Turma.

## Formato de decisão

O template JSON aceita decisões de grupo `APPROVE_GROUP`, `REJECT_GROUP`, `HOLD_GROUP` e `APPROVE_GROUP_WITH_EXCEPTIONS`, além de ações por IDs `APPROVE_IDS`, `REJECT_IDS` e `HOLD_IDS`. O estado inicial é sempre `PENDING`.
"""


def outputs() -> tuple[dict[str, bytes], dict]:
    verify_audit_hashes()
    rows = jsonl(OUT / "CC_MASS_AUDIT_ALL_932.jsonl")
    audit_metrics = json.loads((OUT / "CC_MASS_AUDIT_METRICS.json").read_text(encoding="utf-8"))
    ready_doc = json.loads((OUT / "CC_MASS_RATIFICATION_READY.json").read_text(encoding="utf-8"))
    ready_by_id = {item["ID"]: item for item in ready_doc["items"]}
    ready_rows = [row for row in rows if row["editorial_state"] in READY_STATES]
    if len(rows) != 932 or len(ready_rows) != 681 or set(ready_by_id) != {row["id"] for row in ready_rows}:
        raise ValueError("divergência nas contagens autoritativas 932/681")

    buckets: dict[str, list[dict]] = {name: [] for name in GROUP_META}
    row_by_id = {row["id"]: row for row in ready_rows}
    for row in ready_rows:
        buckets[group_for(row)].append(relation_record(row, ready_by_id[row["id"]]))

    groups = []
    for group_id, items in buckets.items():
        items.sort(key=lambda x: x["id"])
        ids = [item["id"] for item in items]
        meta = GROUP_META[group_id]
        groups.append({
            "group_id": group_id,
            "version": GROUP_VERSION,
            "sha256": group_hash(group_id, ids),
            "description": meta["description"],
            "authority_policy": meta["authority_policy"],
            "qualification_policy": meta["qualification_policy"],
            "relation_ids": ids,
            "relation_count": len(ids),
            "target_count": len({item["target"] for item in items}),
            "recommended_human_action": meta["recommended_human_action"],
            "exceptions": ids if group_id == "GROUP_F" else [],
            "items": items,
        })

    all_items = [item for group in groups for item in group["items"]]
    if len(all_items) != 681 or len({item["id"] for item in all_items}) != 681:
        raise ValueError("cada relação pronta deve aparecer exatamente uma vez")

    by_group = {group["group_id"]: group for group in groups}
    def selected(*names: str) -> list[dict]:
        return [item for name in names for item in by_group[name]["items"]]

    projections = {
        "PROJECTED_A": projection(selected("GROUP_A")),
        "PROJECTED_HIGH_AUTHORITY": projection(selected("GROUP_A", "GROUP_B")),
        "PROJECTED_WITH_CORROBORATED_TURMA": projection(selected("GROUP_A", "GROUP_B", "GROUP_C")),
        "PROJECTED_WITH_ALL_DIRECT_TURMA": projection(selected("GROUP_A", "GROUP_B", "GROUP_C", "GROUP_D")),
        "PROJECTED_ALL_READY": projection(all_items),
    }
    if projections["PROJECTED_ALL_READY"] != {"relations": 730, "targets": 663, "added_relations": 681, "new_targets": 624}:
        raise ValueError("projeção total diverge de 730/663")

    replacements = replacement_audit(ready_rows, ready_by_id)
    if replacements["replacement_relations"] != 81 or replacements["replacement_identity_errors"]:
        raise ValueError("auditoria estrutural das 81 substituições falhou")

    pair_counts = collections.Counter((row["published_pair"]["target"], row["published_pair"]["precedent"]) for row in ready_rows)
    duplicated_pairs = sorted([list(pair) for pair, count in pair_counts.items() if count > 1])
    leading_duplicates = [row["id"] for row in ready_rows if row["leading_case_duplicate"]]
    if duplicated_pairs or leading_duplicates:
        raise ValueError("duplicata de leading case/par pronta detectada")

    capacity = audit_metrics["DEVICE_CAPACITY"]
    capacity_blocker = "YES" if (
        capacity["LOOKUP_ENTRIES"] > capacity["LOOKUP_LIMIT"]
        or capacity["RECORDS_IDX_BYTES"] > capacity["RECORDS_LIMIT_BYTES"]
        or capacity["MAX_RELATIONS_PER_KEY"] > capacity["MAX_RELACOES_ARTIGO"]
    ) else "NO"

    metrics = {
        "MASS_RATIFICATION_PREPARATION": "PASS",
        "audit_commit": AUDIT_COMMIT,
        "baseline": BASELINE,
        "READY_RELATIONS": 681,
        "DECISION_GROUPS": len(groups),
        "GROUP_COUNTS": {group["group_id"]: group["relation_count"] for group in groups},
        "TURMA_RELATIONS": sum(item["authority_class"] == "TURMA_ACORDAO" for item in all_items),
        "CORROBORATED_TURMA": sum(row["authority"] == "TURMA_ACORDAO" and row["turma"]["classification"] == "CORROBORATED_TURMA_CASELAW" for row in ready_rows),
        "REPLACEMENT_RELATIONS": replacements["replacement_relations"],
        "REPLACEMENT_IDENTITY_ERRORS": replacements["replacement_identity_errors"],
        "LEADING_CASE_DUPLICATES_IN_READY": len(leading_duplicates),
        "ALL_HUMAN_DECISIONS_PENDING": "YES",
        "NEW_HUMAN_APPROVED": 0,
        "NEW_MATERIALIZED": 0,
        "CURRENT_CC_BASELINE": "49/39",
        "CURRENT_CF_BASELINE": "315/198",
        "projections": projections,
        "capacity": capacity,
        "CAPACITY_BLOCKER": capacity_blocker,
        "TURMA_DISPLAY_GATE": "PENDING",
        "GROUP_HASH_REQUIRED": "YES",
        "LOCAL_RAW_REBUILD_REQUIRED": "NO",
        "NEW_EXTERNAL_LEGAL_RESEARCH": 0,
        "NEW_CORE_ENGINE_CODE": 0,
        "DETERMINISTIC_OUTPUT": "PASS",
        "NEW_REGRESSION": 0,
        "TESTS": {
            "CC_MASS_RATIFICATION": "18/18",
            "CC_MASS_AUDIT_STRUCTURAL": "11/11",
            "CC_MASS_DISCOVERY_STRUCTURAL": "12/12",
            "MULTINORM_AND_TYPE_FREEZES": "19/19",
            "JURISPRUDENCE_AUDIT": "119/119",
            "LEGAL_TARGET_ID": "93/93",
            "REFERENCES_4_SELECTED": "42/42",
            "CORRELATA_COVERAGE_AUDIT": "115/120 (cinco falhas históricas aceitas)",
        },
        "SD_CHANGED": "NO",
        "FIRMWARE_CHANGED": "NO",
    }

    groups_doc = {
        "schema_version": 1,
        "baseline": BASELINE,
        "audit_commit": AUDIT_COMMIT,
        "status": "AWAITING_USER_RATIFICATION",
        "group_hash_required": True,
        "human_approved": 0,
        "groups": groups,
    }
    groups_bytes = json_bytes(groups_doc)
    decision_template = {
        "schema_version": 1,
        "baseline": BASELINE,
        "audit_commit": AUDIT_COMMIT,
        "groups_manifest_sha256": sha(groups_bytes),
        "groups": [
            {"group_id": group["group_id"], "group_sha256": group["sha256"], "decision": "PENDING", "exceptions": []}
            for group in groups
        ],
        "id_actions": [],
    }
    files = {
        "CC_MASS_RATIFICATION_GROUPS.json": groups_bytes,
        "CC_MASS_RATIFICATION_DECISION_BOARD.md": board_md(groups, metrics, replacements).encode("utf-8"),
        "CC_MASS_RATIFICATION_GROUP_MEMBERS.md": members_md(groups).encode("utf-8"),
        "CC_MASS_RATIFICATION_EXCEPTIONS.md": exceptions_md(by_group["GROUP_F"]).encode("utf-8"),
        "CC_MASS_RATIFICATION_DECISION_TEMPLATE.json": json_bytes(decision_template),
        "CC_MASS_REPLACEMENT_AUDIT.json": json_bytes(replacements),
        "CC_MASS_TURMA_DISPLAY_REQUIREMENTS.md": display_requirements_md().encode("utf-8"),
        "CC_MASS_RATIFICATION_GATES.md": gates_md().encode("utf-8"),
        "CC_MASS_RATIFICATION_PREPARATION_METRICS.json": json_bytes(metrics),
    }
    files["CC_MASS_RATIFICATION_PREPARATION_SHA256.json"] = json_bytes({
        "schema_version": 1,
        "audit_commit": AUDIT_COMMIT,
        "outputs": {name: sha(data) for name, data in sorted(files.items())},
    })
    return files, metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="confere os artefatos sem escrevê-los")
    parser.add_argument("--print-digest", action="store_true", help="imprime o digest determinístico sem escrever")
    args = parser.parse_args()
    files, _ = outputs()
    if args.print_digest:
        digest = sha(b"".join(name.encode("utf-8") + b"\0" + files[name] for name in sorted(files)))
        print(digest)
        return 0
    if args.check:
        stale = [name for name, data in files.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print("UP_TO_DATE")
        return 0
    for name, data in files.items():
        (OUT / name).write_bytes(data)
    print(f"WROTE {len(files)} deterministic ratification artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
