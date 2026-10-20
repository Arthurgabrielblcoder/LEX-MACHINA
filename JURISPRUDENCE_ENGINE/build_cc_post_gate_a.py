"""Constrói os artefatos host-only posteriores ao Gate A físico (20/20)."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import batch_engine as E  # noqa: E402
import build_cc_mass_materialization as M  # noqa: E402
import generic_packager as P  # noqa: E402
import juris_types as JT  # noqa: E402

DATE = "2026-10-19"
START_HEAD = "9a7f617f6559ca117fb0be87a2e51b53486b5a31"
FIRMWARE_SHA = "e2945cf55a00f27f6c35ff709e81732d804fd8c6f01958230cef0016f740a4a0"
FIRMWARE_BIN = "LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin"
FIXTURE_IDS = (
    "CCMD-0124F833D5", "CCMD-151AFCE0D1", "CCMD-0C72C29089",
    "CCMD-006371F260", "CCMD-0BCA168976", "CCMD-11CED92827",
)
FIXTURE = HERE / "CC_TURMA_PHYSICAL_FIXTURE"
MASS = HERE / "CC_MASS_DEPLOY_653"
GATE = HERE / "firmware_turma_display"
NORMALIZED = "99_JURISPRUDENCIA_V2/06_NORMALIZADO"
CONTENT = "99_JURISPRUDENCIA_V2/03_CONTEUDO"
AGGREGATES = (
    f"{NORMALIZED}/JURISPRUDENCIA.IDX", f"{NORMALIZED}/MULTINORM_MANIFEST.json",
    f"{NORMALIZED}/LAYER.VER", f"{NORMALIZED}/JUR_LOOKUP.IDX",
)


def jb(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def meta(data: bytes, repository_path: str | None = None) -> dict:
    out = {"bytes": len(data), "sha256": sha(data)}
    if repository_path:
        out["repository_path"] = repository_path
    return out


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def aggregate_meta(source_root: Path, repository_prefix: str) -> dict:
    return {name: meta((source_root / name).read_bytes(), f"{repository_prefix}/{name}") for name in AGGREGATES}


def lookup_count(source_root: Path) -> int:
    return sum(1 for line in (source_root / AGGREGATES[-1]).read_text(encoding="utf-8").splitlines()
               if line and not line.startswith("#"))


def gate_outputs() -> dict[Path, bytes]:
    record = {
        "schema_version": 1, "date": DATE, "source_commit": START_HEAD,
        "scope": "FIRMWARE_REGRESSION_AND_LEGACY_COMPATIBILITY_ONLY",
        "FIRMWARE_GATE_A_PHYSICAL": "APPROVED", "TURMA_DISPLAY_PHYSICAL": "PENDING_PHASE_B",
        "technical_gate": "PASS", "user_validation": "20/20 PASS",
        "firmware": {"file": FIRMWARE_BIN, "sha256": FIRMWARE_SHA, "bytes": 1109120,
                     "program_bytes": 1108967, "static_ram_bytes": 127724,
                     "program_delta": 1604, "static_ram_delta": 1536, "app0_free_bytes": 201600},
        "hardware": {"board": "ESP32-S3", "flash_bytes": 16777216, "app0_offset": "0x10000", "app0_bytes": 1310720},
        "physical_baseline": {"CF_ADCT": "315/198", "CC": "49/39", "mass_relations_installed": 0},
        "flash_evidence": {"old_firmware_sha256": "38c4d71f77b89223860a6643ef9880416cb1f22a8ba933524e6b083442216bb2",
                           "old_identity": "PASS", "write": "PASS", "readback": "PASS", "boot": "PASS",
                           "partition_table_changed": False, "otadata_changed": False, "bootloader_changed": False,
                           "legacy_8_column_parse": "PASS"},
        "sd_changed_by_gate": False, "turma_relations_physically_tested": 0,
        "evidence_directory_local_only": "JURISPRUDENCE_ENGINE/firmware_turma_display/_local/physical_gate_a_20261019_222235",
    }
    md = f"""# Turma Display — aprovação física Gate A

`FIRMWARE_GATE_A_PHYSICAL = APPROVED`  
`TURMA_DISPLAY_PHYSICAL = PENDING_PHASE_B`

Em {DATE}, o gate técnico e o checklist humano **20/20** aprovaram apenas a regressão do firmware e sua compatibilidade com o formato legado. O firmware físico é `{FIRMWARE_SHA}` ({FIRMWARE_BIN}, 1.109.120 bytes).

- Baseline preservado: CF/ADCT `315/198`; CC `49/39`; nenhuma das 653 relações instalada.
- Flash, readback e boot: PASS; tabela de partições, otadata e bootloader: inalterados.
- Parser legado de oito colunas: PASS.
- O SD não foi alterado pelo gate.
- Nenhum dado de Turma foi fisicamente testado. A aprovação do renderer depende do fixture da Fase B.
"""
    return {GATE / "TURMA_DISPLAY_PHYSICAL_GATE_A_APPROVAL.json": jb(record),
            GATE / "TURMA_DISPLAY_PHYSICAL_GATE_A_APPROVAL.md": md.encode()}


def base_context():
    _, approved, held = M.authority_inputs()
    _, _, base_rows = E.physical_layer(M.BASE)
    base_records = {row["precedent_id"]: row["record"] for row in base_rows}
    card = M.load(M.CARD_MANIFEST)["entries"]
    card_fichas = {Path(path).name for path in card if path.startswith(P.CONTENT + "/")}
    _, all_records, all_fichas, internal = M.build_records(approved, base_records, card_fichas)
    return approved, held, base_rows, base_records, card, card_fichas, all_records, all_fichas, internal


def fixture_outputs(ctx) -> tuple[dict[Path, bytes], dict, dict]:
    approved, _, base_rows, base_records, card, card_fichas, records, fichas, internal = ctx
    by_id = {x["relation_id"]: x for x in approved}
    selected = [by_id[x] for x in FIXTURE_IDS]
    if set(FIXTURE_IDS) != set(by_id) & set(FIXTURE_IDS) or any(x["group_id"] not in {"GROUP_C", "GROUP_D", "GROUP_E"} for x in selected):
        raise SystemExit("FIXTURE_SELECTION_INVALID")
    if any(not x["new_target"] or x.get("special_reasons") for x in selected):
        raise SystemExit("FIXTURE_NOT_CLEAN")
    files, _, host = M.candidate("TURMA_FIXTURE_B", selected, base_rows, base_records, card_fichas, card,
                                  records, fichas, internal)
    outputs = {FIXTURE / path: data for path, data in files.items() if path.startswith("candidate/SD/")}
    needed = sorted({JT.ficha(x["precedent"]) for x in selected})
    for name in needed:
        outputs[FIXTURE / "candidate/SD" / CONTENT / name] = (M.SHARED_CONTENT / name).read_bytes()
    targets_added = len({x["target"] for x in selected})
    fixture_rows = [{"ID": x["relation_id"], "GROUP": x["group_id"], "TARGET": x["target"],
                     "TRIBUNAL": x["tribunal"], "ORGAO": x["orgao"], "CLASSE": x["classe"],
                     "PROCESSO": x["precedent"].split(":")[-1], "DATA": x["data"],
                     "NATUREZA": "PERSUASIVE_NON_BINDING", "FICHA": JT.ficha(x["precedent"]),
                     "SOURCE": x["source_evidence"], "REPLACEMENT_FROM": x.get("replacement_publication") or x.get("substituted_from")}
                    for x in selected]
    selection = {"schema_version": 1, "status": "HOST_READY_NOT_DEPLOYED", "relations_added": len(selected),
                 "targets_added": targets_added, "projected_CC": f"{49 + len(selected)}/{39 + targets_added}",
                 "group_f": 0, "fixtures": fixture_rows}
    outputs[FIXTURE / "FIXTURE_SELECTION.json"] = jb(selection)
    table = "\n".join(f"| {x['ID']} | {x['GROUP']} | {x['TARGET']} | {x['ORGAO']} | {x['CLASSE']} {x['PROCESSO']} | {x['REPLACEMENT_FROM'] or '—'} |" for x in fixture_rows)
    outputs[FIXTURE / "FIXTURE_SELECTION.md"] = ("# Fixture físico Turma — Fase B\n\n"
        "Seis relações humanas aprovadas, todas em targets novos, sem Group F ou ressalva temporal.\n\n"
        "| ID | Grupo | Target | Órgão | Processo | Replacement |\n| --- | --- | --- | --- | --- | --- |\n" + table +
        f"\n\nProjeção: CC `{49 + len(selected)}/{39 + targets_added}`. Não implantado fisicamente.\n").encode()
    candidate_prefix = rel(FIXTURE / "candidate/SD")
    fixture_root = FIXTURE / "candidate/SD"
    post_agg = {name: meta(outputs[FIXTURE / "candidate/SD" / name], f"{candidate_prefix}/{name}") for name in AGGREGATES}
    base_agg = aggregate_meta(M.BASE, rel(M.BASE))
    fixture_lookup_count = sum(1 for line in outputs[FIXTURE / "candidate/SD" / AGGREGATES[-1]].decode().splitlines() if line and not line.startswith("#"))
    content_meta = {}
    for name in needed:
        path = f"{CONTENT}/{name}"; data = outputs[FIXTURE / "candidate/SD" / path]
        content_meta[path] = meta(data, f"{candidate_prefix}/{path}")
    profile = {"schema_version": 1, "name": "CC_TURMA_FIXTURE_B", "confirmation_token": "CC_TURMA_FIXTURE_B",
               "firmware_requirement": {"sha256": FIRMWARE_SHA, "gate": "FIRMWARE_GATE_A_PHYSICAL=APPROVED"},
               "aggregate_order": list(AGGREGATES),
               "allowed_pre_states": {"CLEAN_BASELINE": {"aggregates": base_agg,
                    "semantic": {"cc_relations": 49, "cc_targets": 39, "lookup_entries": lookup_count(M.BASE)}, "content_present": []}},
               "post_state": {"aggregates": post_agg,
                    "semantic": {"cc_relations": 55, "cc_targets": 45, "lookup_entries": fixture_lookup_count}},
               "content_files": content_meta, "expected_CF_ADCT": "315/198", "real_execution_performed": False}
    outputs[FIXTURE / "DEPLOY_PROFILE.json"] = jb(profile)
    manifest_files = {rel(path): meta(data) for path, data in outputs.items() if path.is_relative_to(FIXTURE)}
    manifest = {"schema_version": 1, "kind": "CC_TURMA_PHYSICAL_FIXTURE_B", "status": "HOST_READY_NOT_DEPLOYED",
                "baseline": {"CC": "49/39", "CF_ADCT": "315/198"}, "post": {"CC": "55/45", "CF_ADCT": "315/198"},
                "firmware_requirement": FIRMWARE_SHA, "files": manifest_files}
    outputs[FIXTURE / "FIXTURE_MANIFEST.json"] = jb(manifest)
    plan = """# Deploy/rollback do fixture Fase B

Execução real é proibida nesta preparação. O script recusa escrita sem volume removível FAT/FAT32/exFAT, baseline byte-exato, confirmação `CC_TURMA_FIXTURE_B`, firmware Gate A declarado e backup externo.

Ordem: PRE → backup dos quatro agregados → seis fichas via temp/fsync/readback → staging no mesmo filesystem → replaces → `JUR_LOOKUP.IDX` por último → readback/recontagem. Rollback restaura os quatro bytes PRE e remove somente as fichas criadas pela transação.
"""
    outputs[FIXTURE / "DEPLOY_AND_ROLLBACK_PLAN.md"] = plan.encode()
    checks = [
        "Cada um dos seis targets abre e mostra jurisprudência.", "Rótulo compacto exibe tribunal, órgão, classe e número.",
        "CCMD-0124F833D5 exibe STJ 3ª T. e REsp.", "CCMD-151AFCE0D1 exibe STJ 4ª T. e AREsp.",
        "CCMD-0C72C29089 abre ficha e volta à mesma lista.", "CCMD-006371F260 abre ficha e volta à mesma lista.",
        "CCMD-0BCA168976 usa o precedente replacement publicado.", "CCMD-11CED92827 usa o precedente replacement publicado.",
        "Todas as fichas exibem natureza persuasiva e data.", "BACK preserva seleção/ordem em todos os fixtures.",
        "Regressão: abrir uma relação CF existente.", "Regressão: abrir relações CC-J1 e CC-J2 existentes.",
        "Regressão: ENTENDA, Correlatas e Referências nº4 permanecem navegáveis.",
    ]
    outputs[FIXTURE / "PHYSICAL_CHECKLIST_B.md"] = ("# Checklist físico Fase B\n\nResponder `1-13 OK` ou os números de falha.\n\n" +
        "\n".join(f"{i}. [ ] {text}" for i, text in enumerate(checks, 1)) + "\n").encode()
    return outputs, profile, selection


def mass_outputs(ctx, fixture_profile: dict) -> tuple[dict[Path, bytes], dict]:
    approved, _, _, _, card, _, _, _, _ = ctx
    combined = M.load(M.OUT / "COMBINED/host/PREFLIGHT_RESULT.json")
    checks = combined["checks"]
    content_meta = {}
    for name in sorted(Path(x).name for x in M.load(M.OUT / "COMBINED/SHA256_MANIFEST.json")["shared_content_refs"]):
        source = M.SHARED_CONTENT / name; path = f"{CONTENT}/{name}"
        content_meta[path] = meta(source.read_bytes(), rel(source))
    post_root = M.OUT / "COMBINED/candidate/SD"
    post_agg = aggregate_meta(post_root, rel(post_root))
    base_agg = aggregate_meta(M.BASE, rel(M.BASE))
    profile = {"schema_version": 1, "name": "CC_MASS_653", "confirmation_token": "CC_MASS_653",
               "firmware_requirement": {"sha256": FIRMWARE_SHA, "gate": "FIRMWARE_GATE_A_PHYSICAL=APPROVED"},
               "aggregate_order": list(AGGREGATES),
               "allowed_pre_states": {
                   "CLEAN_BASELINE": {"aggregates": base_agg, "semantic": {"cc_relations": 49, "cc_targets": 39, "lookup_entries": lookup_count(M.BASE)}, "content_present": []},
                   "POST_FIXTURE_VALIDATED": {"aggregates": fixture_profile["post_state"]["aggregates"],
                       "semantic": fixture_profile["post_state"]["semantic"], "content_present": sorted(fixture_profile["content_files"])}},
               "post_state": {"aggregates": post_agg, "semantic": {"cc_relations": 702, "cc_targets": 636, "lookup_entries": 833}},
               "content_files": content_meta, "expected_CF_ADCT": "315/198",
               "recommended_physical_path": "POST_FIXTURE_VALIDATED", "reason": "seis fichas já verificadas e seis writes aditivos a menos",
               "real_execution_performed": False}
    outputs = {MASS / "DEPLOY_PROFILE.json": jb(profile)}
    relations = [{"id": x["id"], "group": x["group"], "target": x["target"], "precedent": x["precedent"],
                  "ficha": JT.ficha(x["precedent"]), "replacement_publication": x["replacement_publication"]}
                 for x in combined["relation_manifest"]]
    authority = M.load(M.RATIFICATION)
    manifest = {"schema_version": 1, "kind": "CC_MASS_DEPLOY_653", "status": "HOST_READY_NOT_DEPLOYED",
                "source_commit": START_HEAD, "ratification_commit": authority["decision_board_commit"],
                "ratification_sha256": M.sha_file(M.RATIFICATION), "firmware_requirement": FIRMWARE_SHA,
                "baseline": {"CC": "49/39", "CF_ADCT": "315/198"}, "expected": {"relations": 653, "new_targets": 597,
                    "post_CC": "702/636", "distinct_precedents": 574, "new_fichas": 572, "reused_fichas": 2,
                    "replacement_relations": 76, "lookup_entries": "833/4096", "group_f": 0},
                "deploy_order": ["PRE gates", "backup 4 aggregates", "new fichas", "ficha readback", "stage 4 aggregates",
                    "verify staging", "atomic replace", "JUR_LOOKUP.IDX last", "full readback", "semantic recount"],
                "normalized_files": post_agg, "content_files": content_meta, "relations": relations}
    outputs[MASS / "AUTHORITATIVE_MANIFEST.json"] = jb(manifest)
    for name, groups in (("HIGH_AUTHORITY", {"GROUP_A", "GROUP_B"}), ("TURMA", {"GROUP_C", "GROUP_D", "GROUP_E"}),
                         ("COMBINED", {"GROUP_A", "GROUP_B", "GROUP_C", "GROUP_D", "GROUP_E"})):
        rows = [x for x in relations if x["group"] in groups]
        outputs[MASS / name / "MANIFEST.json"] = jb({"schema_version": 1, "subset": name, "relations": len(rows),
            "relation_ids": [x["id"] for x in rows], "shared_content": "../AUTHORITATIVE_MANIFEST.json#content_files",
            "candidate": f"JURISPRUDENCE_ENGINE/CC_MASS_MATERIALIZATION/{name}", "deployed": False})
    plan = """# Deploy massivo 653 — plano operacional

`RECOMMENDED_PHYSICAL_PATH = POST_FIXTURE_VALIDATED`: após a Fase B aprovada, promove diretamente ao conjunto 653 e evita seis escritas aditivas. `CLEAN_BASELINE` também é aceito. Ambos exigem hashes exatos e CF/ADCT 315/198.

O deploy real exige o token `CC_MASS_653`, declaração do firmware Gate A por SHA-256 e backup externo. A transação grava fichas ausentes, faz readback, prepara os quatro índices no mesmo filesystem, substitui `JUR_LOOKUP.IDX` por último e reconta 702/636 e 833 lookups. Rollback restaura exatamente o estado PRE detectado e apaga apenas fichas registradas na transação, sem glob.
"""
    outputs[MASS / "DEPLOY_AND_ROLLBACK_PLAN.md"] = plan.encode()
    return outputs, profile


def book(target: str) -> str:
    number = int(re.match(r"\d+", target.split("ART.", 1)[1]).group())
    if number <= 232: return "Parte Geral"
    if number <= 965: return "Obrigações"
    if number <= 1195: return "Empresa"
    if number <= 1510: return "Coisas"
    if number <= 1783: return "Família"
    return "Sucessões"


def checklist_outputs(ctx) -> dict[Path, bytes]:
    approved = ctx[0]
    selected = []
    for group, n in (("GROUP_A", 5), ("GROUP_B", 5), ("GROUP_C", 6), ("GROUP_D", 6), ("GROUP_E", 6)):
        rows = sorted((x for x in approved if x["group_id"] == group), key=lambda x: (book(x["target"]), x["target"], x["precedent"]))
        step = max(1, len(rows) // n); selected.extend(rows[::step][:n])
    combined = M.load(M.OUT / "COMBINED/host/PREFLIGHT_RESULT.json")
    by_pair = {(x["target"], x["precedent"]): x for x in approved}
    hotspots = []
    for hot in combined["top_targets_by_query_key"][:6]:
        prefix = hot["query_key"].replace("|", ":")
        candidate = next((x for x in approved if x["target"].startswith(prefix)), None)
        if candidate: hotspots.append((candidate, hot["relations"]))
    lines = ["# Checklist físico — deploy massivo CC 653", "", "Responder `1-48 OK` ou os números de falha.", ""]
    index = 1
    for row in selected:
        lines.append(f"{index}. [ ] {row['group_id']} · {book(row['target'])} · `{row['target']}` → `{row['precedent']}`: abre, rótulo/ordem corretos, ENTER/ficha e BACK.")
        index += 1
    for row, count in hotspots:
        lines.append(f"{index}. [ ] Hotspot `{row['target']}` ({count} relações): scroll completo, ordering, nenhuma omissão, BACK."); index += 1
    negatives = [x for x in ctx[1]][:4]
    for row in negatives:
        lines.append(f"{index}. [ ] Negativo: `{row['target']}` não deve publicar `{row['precedent']}` (Group F/HOLD)."); index += 1
    regressions = ["CC-J1 preservado", "CC-J2 preservado", "CF preservada", "ENTENDA + Correlatas preservados", "Referências nº4 preservadas"]
    for item in regressions:
        lines.append(f"{index}. [ ] Regressão: {item}."); index += 1
    while index <= 48:
        row = approved[(index * 37) % len(approved)]
        lines.append(f"{index}. [ ] Amostra complementar `{row['target']}` → `{row['precedent']}`: abre/ficha/BACK."); index += 1
    return {MASS / "CC_MASS_PHYSICAL_VALIDATION_CHECKLIST.md": ("\n".join(lines) + "\n").encode()}


def group_f_outputs(ctx) -> tuple[dict[Path, bytes], dict]:
    held = sorted(ctx[1], key=lambda x: x["relation_id"])
    cases = []
    for item in held:
        reason = "; ".join(item.get("special_reasons", []))
        low = reason.lower()
        if item["relation_id"] == "CCMD-72D7D2A523":
            recommendation, bucket = "APPROVE_WITH_HISTORICAL_NOTE", "RECOMMENDED_APPROVE"
            material = "O art. 1.723 foi objeto direto da interpretação conforme na ADI 4277, julgada com a ADPF 132; não é mera menção contextual."
            note = "STF, ADI 4277/ADPF 132: interpretação conforme do art. 1.723 para excluir sentido que impeça o reconhecimento da união estável entre pessoas do mesmo sexo."
            precision = "EXACT_ARTICLE"; temporal = "LOW_WITH_HISTORICAL_NOTE"
        elif "dispositivo-pai" in low:
            recommendation, bucket = "RELOCATE_TARGET", "RECOMMENDED_REJECT"
            material = "A fonte não sustenta automaticamente o caput inteiro; o fallback técnico não basta como vínculo jurídico."
            note = "Não publicar no pai sem localizar a subdivisão válida ou comprovar alcance integral do caput."
            precision = "PARENT_FALLBACK_INSUFFICIENT"; temporal = "LOW"
        elif "alterada" in low or "ambiguous" in low:
            recommendation, bucket = "NEEDS_EXTERNAL_EVIDENCE", "STILL_HOLD"
            material = "A evidência local não resolve se a razão de decidir sobrevive à redação/namespace vigente."
            note = "Manter em hold até confronto documentado entre redação do julgamento e redação atual."
            precision = "TEMPORAL_COMPARISON_REQUIRED"; temporal = "HIGH"
        elif "cc/1916" in low:
            recommendation, bucket = "APPROVE_WITH_HISTORICAL_NOTE", "RECOMMENDED_APPROVE"
            material = "O próprio registro local trata o artigo atual como correspondente; é útil historicamente, mas não deve aparentar julgamento sob o CC/2002."
            note = "Precedente histórico: decisão sob o CC/1916; correspondência com o CC/2002 deve ser lida com a ressalva temporal."
            precision = "EXPLICIT_HISTORICAL_CORRESPONDENCE"; temporal = "MEDIUM_NOTED"
        elif "normativa/histórica" in low and item["authority_class"] == "QUALIFIED_PRECEDENT":
            recommendation, bucket = "APPROVE_WITH_HISTORICAL_NOTE", "RECOMMENDED_APPROVE"
            material = "A equivalência local é materialmente útil e a autoridade qualificada reduz o risco, desde que a nota temporal seja explícita."
            note = "Aplicação histórica/equivalente; conferir a lei vigente no julgamento antes de transpor ao texto atual."
            precision = "NORMATIVE_EQUIVALENCE"; temporal = "MEDIUM_NOTED"
        else:
            recommendation, bucket = "KEEP_HOLD", "STILL_HOLD"
            material = "A correspondência histórica local é plausível, mas não demonstra com precisão suficiente identidade material atual."
            note = "Relação histórica em revisão; não tratar como interpretação direta do texto vigente."
            precision = "REQUIRES_CASE_TEXT_CONFIRMATION"; temporal = "MEDIUM"
        cases.append({"ID": item["relation_id"], "TARGET": item["target"], "PRECEDENT": item["precedent"],
            "CATEGORY": reason, "CURRENT_REASON": item.get("risk"), "SOURCE_EVIDENCE": item["source_evidence"],
            "LAW_VERSION_AT_JUDGMENT": "HISTORICAL_OR_DATE_SENSITIVE" if temporal != "LOW" else "CURRENT_UNRESOLVED",
            "CURRENT_LAW": item["target"], "MATERIAL_RELATION": material, "TEMPORAL_RISK": temporal,
            "TARGET_PRECISION": precision, "AUTHORITY": item["authority_class"], "READER_NOTE_PROPOSAL": note,
            "RECOMMENDATION": recommendation, "BUCKET": bucket, "HUMAN_APPROVED": False})
    counts = Counter(x["BUCKET"] for x in cases)
    doc = {"schema_version": 1, "status": "DEEP_REVIEW_ONLY_NOT_RATIFIED", "reviewed": len(cases),
           "HUMAN_APPROVED": 0, "EXTERNAL_RESEARCH_COUNT": 0,
           "counts": {"RECOMMENDED_APPROVE": counts["RECOMMENDED_APPROVE"], "RECOMMENDED_REJECT": counts["RECOMMENDED_REJECT"],
                      "STILL_HOLD": counts["STILL_HOLD"]}, "cases": cases}
    lines = ["# Group F — revisão aprofundada", "", "`HUMAN_APPROVED = 0` · nenhuma relação foi materializada.", "",
             f"- Recomendação de aprovação com nota: {counts['RECOMMENDED_APPROVE']}",
             f"- Recomendação de rejeição/relocação: {counts['RECOMMENDED_REJECT']}", f"- Ainda em hold: {counts['STILL_HOLD']}",
             "- Pesquisa externa adicional: 0 (a evidência local bastou para triagem; casos inconclusivos permanecem em hold).", "",
             "## ADI 4277 → CC art. 1.723", "", next(x["MATERIAL_RELATION"] for x in cases if x["ID"] == "CCMD-72D7D2A523"), "",
             "## Casos", ""]
    for x in cases:
        lines += [f"### {x['ID']} — {x['TARGET']} → {x['PRECEDENT']}", "",
                  f"Categoria: {x['CATEGORY']}. Evidência: {x['SOURCE_EVIDENCE']}. Relação material: {x['MATERIAL_RELATION']}", "",
                  f"Risco temporal: `{x['TEMPORAL_RISK']}`; precisão: `{x['TARGET_PRECISION']}`; autoridade: `{x['AUTHORITY']}`.", "",
                  f"Recomendação: `{x['RECOMMENDATION']}`. Nota proposta: {x['READER_NOTE_PROPOSAL']}", ""]
    return {HERE / "CC_GROUP_F_DEEP_REVIEW.json": jb(doc), HERE / "CC_GROUP_F_DEEP_REVIEW.md": ("\n".join(lines) + "\n").encode()}, doc


def build() -> tuple[dict[Path, bytes], dict]:
    ctx = base_context(); outputs = gate_outputs()
    fixture_files, fixture_profile, selection = fixture_outputs(ctx); outputs.update(fixture_files)
    mass_files, mass_profile = mass_outputs(ctx, fixture_profile); outputs.update(mass_files)
    outputs.update(checklist_outputs(ctx)); group_files, group_doc = group_f_outputs(ctx); outputs.update(group_files)
    summary = {"fixture": selection, "fixture_profile": fixture_profile, "mass_profile": mass_profile,
               "group_f": group_doc["counts"], "outputs": len(outputs)}
    return outputs, summary


def main() -> int:
    outputs, summary = build()
    if "--check" in sys.argv:
        stale = [rel(path) for path, data in outputs.items() if not path.is_file() or path.read_bytes().replace(b"\r\n", b"\n") != data.replace(b"\r\n", b"\n")]
        print("UP_TO_DATE" if not stale else "STALE " + json.dumps(stale, ensure_ascii=False)); return 0 if not stale else 1
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    print(json.dumps({"fixture": summary["fixture"], "group_f": summary["group_f"], "outputs": summary["outputs"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
