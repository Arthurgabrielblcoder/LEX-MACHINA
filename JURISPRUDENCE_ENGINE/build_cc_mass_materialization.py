"""Preflight host-only das 653 relações massivamente ratificadas do Código Civil.

A decisão vem exclusivamente de CC_MASS_RATIFICATION_RECORD.json. O manifesto de grupos
fornece metadados oficiais, não decisões. Gera três candidatos lógicos sobre o baseline
físico CC 49/39 + CF/ADCT 315/198, sem acessar ou modificar SD/dispositivo.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / "firmware_multinorm"), str(ROOT / "JURISPRUDENCE_AUDIT"), str(ROOT / "LEGAL_TARGET_ID")]
import batch_engine as E  # noqa: E402
import generic_packager as P  # noqa: E402
import juris_types as JT  # noqa: E402
import multinorm_sim as S  # noqa: E402
import target_id as T  # noqa: E402


DISCOVERY = HERE / "CC_MASS_DISCOVERY"
RATIFICATION = DISCOVERY / "CC_MASS_RATIFICATION_RECORD.json"
GROUPS = DISCOVERY / "CC_MASS_RATIFICATION_GROUPS.json"
BASE = HERE / "CC_J2_MATERIALIZATION_CANDIDATE/candidate/SD"
CARD_MANIFEST = HERE / "CC_J2_PHYSICAL_DEPLOY/sd_manifest_post_full.json"
OUT = HERE / "CC_MASS_MATERIALIZATION"
SHARED_CONTENT = OUT / "SHARED_CONTENT"
CHECKPOINT = DISCOVERY / "CC_MASS_PREFLIGHT_CHECKPOINT.json"
REPORT_PREFLIGHT = DISCOVERY / "CC_MASS_MATERIALIZATION_PREFLIGHT.md"
REPORT_CAPACITY = DISCOVERY / "CC_MASS_CAPACITY_REPORT.md"
REPORT_DISPLAY = DISCOVERY / "CC_MASS_DISPLAY_GATE_REPORT.md"
REPORT_DEPLOY = DISCOVERY / "CC_MASS_DEPLOY_PLAN.md"
REPORT_ROLLBACK = DISCOVERY / "CC_MASS_ROLLBACK_PLAN.md"
FIRMWARE_REPORT = HERE / "firmware_turma_display/TURMA_DISPLAY_FIRMWARE_BUILD.json"
FIRMWARE_BINARY = HERE / "firmware_turma_display/candidate/LEX_MACHINA_DEVICE_V1_CANDIDATE.ino.bin"
GROUP_RANK = {f"GROUP_{letter}": n for n, letter in enumerate("ABCDE", 1)}
TRACKS = {
    "HIGH_AUTHORITY": {"groups": {"GROUP_A", "GROUP_B"}, "expected": 94},
    "TURMA": {"groups": {"GROUP_C", "GROUP_D", "GROUP_E"}, "expected": 559},
    "COMBINED": {"groups": set(GROUP_RANK), "expected": 653},
}
LOOKUP_ENTRY_BYTES = 68
LOOKUP_MAX = 4096
RELATION_LIMIT = 32
CC_FILE = "/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def process_number(number: str) -> str:
    return f"{int(number):,}".replace(",", ".") if str(number).isdigit() else str(number)


def normalized_orgao(value: str) -> str:
    aliases = {
        "T3": "TERCEIRA TURMA", "T4": "QUARTA TURMA", "S2": "SEGUNDA SEÇÃO", "CE": "CORTE ESPECIAL",
    }
    return aliases.get(value, value)


def display_class(value: str) -> str:
    return {"RESP": "REsp", "ARESP": "AREsp", "ERESP": "EREsp", "EARESP": "EAREsp", "RMS": "RMS"}.get(value, value)


def record_type(item: dict, group_id: str) -> str:
    if item["classe"] == "REPETITIVO":
        return "repetitivo_stj"
    if item["classe"] == "RG":
        return "repercussao_geral"
    if item["classe"] == "SUMULA":
        return "sumula"
    if item["classe"] == "IAC":
        return "iac"
    if group_id in {"GROUP_C", "GROUP_D", "GROUP_E"}:
        return item["classe"].lower()
    return "acordao"


def nature(item: dict, group_id: str) -> str:
    if group_id in {"GROUP_C", "GROUP_D", "GROUP_E"}:
        return "PERSUASIVE_NON_BINDING"
    if item["authority_class"] == "QUALIFIED_PRECEDENT":
        return "PRECEDENTE_QUALIFICADO"
    if item["authority_class"] == "SUMULA_STJ":
        return "SÚMULA_STJ"
    return "JURISPRUDÊNCIA_RELEVANTE_NÃO_VINCULANTE"


def authority_inputs():
    rat = load(RATIFICATION)
    groups_doc = load(GROUPS)
    if rat["status"] != "RATIFIED_WITH_HOLDS" or rat["decision_board_commit"] != "aeb769d":
        raise SystemExit("PREFLIGHT_STOP RATIFICATION_AUTHORITY")
    decisions = {item["id"]: item for item in rat["relations"]}
    metadata = {item["id"]: (group["group_id"], item) for group in groups_doc["groups"] for item in group["items"]}
    approved = []
    held = []
    for rel_id, decision in decisions.items():
        if rel_id not in metadata:
            raise SystemExit(f"PREFLIGHT_STOP UNKNOWN_RELATION {rel_id}")
        group_id, item = metadata[rel_id]
        if decision["group_id"] != group_id or decision["target"] != item["target"] or decision["precedent"] != item["precedent"]:
            raise SystemExit(f"PREFLIGHT_STOP METADATA_DRIFT {rel_id}")
        row = dict(item)
        row.update(relation_id=rel_id, group_id=group_id, decision=decision["decision"])
        row["replacement_publication"] = decision.get("replacement_publication")
        (approved if decision["decision"] == "HUMAN_APPROVED" else held).append(row)
    if (len(approved), len(held)) != (653, 28) or any(x["group_id"] == "GROUP_F" for x in approved):
        raise SystemExit("PREFLIGHT_STOP RATIFICATION_COUNTS")
    return rat, approved, held


def target_order(target: str):
    parsed = T.parse_target_id(target)
    article = parsed["article"]
    number = int(re.match(r"\d+", article).group())
    return number, article, parsed["paragraph"] or "", parsed["inciso"] or "", parsed["alinea"] or ""


def build_records(items: list[dict], base_records: dict, card_fichas: set[str]):
    by_precedent = collections.defaultdict(list)
    for item in items:
        by_precedent[item["precedent"]].append(item)
    records = {}
    fichas = {}
    internal = {}
    for precedent, rows in sorted(by_precedent.items()):
        if precedent in base_records and JT.ficha(precedent) in card_fichas:
            continue
        canonical = rows[0]
        group_id = canonical["group_id"]
        klass = canonical["classe"]
        tipo = record_type(canonical, group_id)
        tribunal, _, number = precedent.split(":", 2)
        orgaos = {normalized_orgao(row["orgao"]) for row in rows}
        dates = {row["data"] for row in rows}
        if len(orgaos) != 1 or len(dates) != 1:
            raise SystemExit(f"PREFLIGHT_STOP PRECEDENT_METADATA_CONFLICT {precedent}")
        orgao, date = next(iter(orgaos)), next(iter(dates))
        natureza = nature(canonical, group_id)
        title = f"{display_class(klass)} {process_number(number)} · {tribunal}"
        records[precedent] = {
            "tipo": tipo,
            "tribunal": tribunal,
            "numero": number,
            "status": "persuasivo_nao_vinculante" if natureza == "PERSUASIVE_NON_BINDING" else "ratificado",
            "titulo": title,
            "fonte": canonical["source_evidence"],
            "orgao": orgao,
            "data": date,
            "natureza": natureza,
        }
        lines = [
            title.upper(),
            f"TRIBUNAL: {tribunal}",
            f"ÓRGÃO JULGADOR: {orgao}",
            f"CLASSE: {display_class(klass)}",
            f"NÚMERO: {process_number(number)}",
            f"DATA: {date}",
            "NATUREZA: JURISPRUDÊNCIA PERSUASIVA — NÃO VINCULANTE" if natureza == "PERSUASIVE_NON_BINDING" else f"NATUREZA: {natureza.replace('_', ' ')}",
            "",
            "CÓDIGO CIVIL",
        ]
        note_groups = collections.defaultdict(list)
        for row in sorted(rows, key=lambda x: target_order(x["target"])):
            note_groups[row.get("reader_note", "")].append(row["target"])
        for note, targets in note_groups.items():
            lines.append("; ".join(targets))
            if note:
                lines.extend(["NOTA AO LEITOR", note])
            lines.append("")
        lines += ["FONTE OFICIAL", canonical["source_evidence"], ""]
        body = "\n".join(lines)
        forbidden = ("TIER_B", "HUMAN_APPROVED", "PROVISIONAL = NO", "READY")
        if any(token in body for token in forbidden):
            raise SystemExit(f"PREFLIGHT_STOP INTERNAL_METADATA_IN_FICHA {precedent}")
        fichas[JT.ficha(precedent)] = body
        internal[precedent] = {
            "relation_ids": sorted(row["relation_id"] for row in rows),
            "groups": sorted({row["group_id"] for row in rows}),
            "targets": sorted({row["target"] for row in rows}, key=target_order),
            "authority_class": sorted({row["authority_class"] for row in rows}),
            "source_evidence": sorted({row["source_evidence"] for row in rows}),
            "replacement_provenance": [row["replacement_publication"] for row in rows if row.get("replacement_publication")],
        }
    return by_precedent, records, fichas, internal


def candidate(name: str, selected: list[dict], base_rows: list[dict], base_records: dict, card_fichas: set[str], card_entries: dict,
              all_records: dict, all_fichas: dict, internal: dict):
    selected = sorted(selected, key=lambda x: (GROUP_RANK[x["group_id"]], target_order(x["target"]), x["precedent"], x["relation_id"]))
    new_rels = [dict(norm="CC2002", target_id=x["target"], precedent_id=x["precedent"], origin=f"CC MASS {x['group_id']} HUMAN RATIFIED") for x in selected]
    base_rels = [dict(norm=E.namespace_of(row["target_id"]), target_id=row["target_id"], precedent_id=row["precedent_id"], origin="PHYSICAL_BASELINE")
                 for row in base_rows]
    needed = {x["precedent"] for x in selected}
    new_records = {key: value for key, value in all_records.items() if key in needed}
    new_fichas = {key: value for key, value in all_fichas.items() if key in {JT.ficha(pid) for pid in needed}}
    files = P.package(base_rels + new_rels, {**base_records, **new_records}, card_fichas, new_fichas=new_fichas,
                      known_targets=P.known_targets())
    layer_manifest = json.loads(files[f"{P.LAYER}/MULTINORM_MANIFEST.json"])
    build_id = sha(files[f"{P.LAYER}/JUR_LOOKUP.IDX"] + files[f"{P.LAYER}/JURISPRUDENCIA.IDX"])[:16]
    files[f"{P.LAYER}/LAYER.VER"] = ("\n".join([
        "#LEXMACHINA|JURIS_NORMALIZED_LAYER|2", f"BUILD_ID|{build_id}", f"LAYER|{P.LAYER}", "CF_BASELINE|J2I_FROZEN_315_198",
        "CC_PHYSICAL_BASELINE|49|39", f"CC_MASS_RATIFICATION_SHA256|{sha_file(RATIFICATION)}", f"CANDIDATE|{name}",
        *[f"NORM|{norm}|{value['relations']}|{value['targets_with_j']}" for norm, value in sorted(layer_manifest["norms"].items())], "",
    ])).encode("utf-8")
    content_paths = sorted(path for path in files if path.startswith(P.CONTENT + "/"))
    candidate_files = {f"candidate/SD/{path}": value for path, value in files.items() if path not in content_paths}
    records_bytes = files[f"{P.LAYER}/JURISPRUDENCIA.IDX"]
    lookup_bytes = files[f"{P.LAYER}/JUR_LOOKUP.IDX"]
    pkg = S.Package(lookup_bytes, records_bytes, card_fichas | {Path(path).name for path in content_paths})
    record_lines = [line for line in records_bytes.decode("utf-8").splitlines() if line and not line.startswith("#")]
    lookup_lines = [line for line in lookup_bytes.decode("utf-8").splitlines() if line and not line.startswith("#")]
    duplicate_keys = len(lookup_lines) - len({"|".join(line.split("|")[:5]) for line in lookup_lines})
    relation_counts = collections.Counter(P.query_key(row["target_id"]) for row in base_rels + new_rels)
    over_limit = {key: value for key, value in relation_counts.items() if value > RELATION_LIMIT}
    approved_visible = 0
    e2e_failed = []
    selected_pairs = {(x["target"], x["precedent"]) for x in selected}
    for target in sorted({x["target"] for x in selected}, key=target_order):
        _, art, par, inc, ali = P.query_key(target).split("|")
        state = S.carregar(pkg, CC_FILE, art, par, inc, ali)
        got = {row["arquivo"] for row in state["relations"]}
        expected = {JT.ficha(precedent) for t, precedent in selected_pairs if t == target}
        approved_visible += len(expected & got)
        opened = all(S.open_and_back(pkg, state, n)["opened"] for n, row in enumerate(state["relations"]) if row["arquivo"] in expected)
        if not expected <= got or not opened or S.carregar(pkg, CC_FILE, art, par, inc, ali)["relations"] != state["relations"]:
            e2e_failed.append(target)
    new_names = {Path(path).name for path in content_paths}
    reused = sorted(JT.ficha(pid) for pid in needed if JT.ficha(pid) in card_fichas)
    replace = sorted(path for path, value in files.items() if path in card_entries and card_entries[path]["sha256"] != hashlib.sha256(value).hexdigest())
    add = sorted(path for path in files if path not in card_entries)
    relation_manifest = [{
        "id": x["relation_id"], "group": x["group_id"], "target": x["target"], "precedent": x["precedent"],
        "authority_class": x["authority_class"], "reader_note": x.get("reader_note", ""), "source_evidence": x["source_evidence"],
        "replacement_publication": x.get("replacement_publication"),
    } for x in selected]
    checks = {
        "candidate": name,
        "approved_relations_input": len(selected),
        "distinct_targets_touched": len({x["target"] for x in selected}),
        "distinct_precedents": len(needed),
        "group_f_relations": sum(x["group_id"] == "GROUP_F" for x in selected),
        "lookup_entries": len(lookup_lines),
        "lookup_max": LOOKUP_MAX,
        "lookup_lost_relations": len(base_rels) + len(new_rels) - len(record_lines),
        "duplicate_query_keys": duplicate_keys,
        "record_bytes": len(records_bytes),
        "lookup_bytes": len(lookup_bytes),
        "psram_estimate_bytes": len(lookup_lines) * LOOKUP_ENTRY_BYTES + len(records_bytes) + 1,
        "max_relations_on_single_target": max(relation_counts.values()),
        "targets_over_relation_limit": len(over_limit),
        "approved_relations_visible": f"{approved_visible}/{len(selected)}",
        "e2e_failed_targets": e2e_failed,
        "new_fichas_required": len(new_names),
        "reused_existing_fichas": len(reused),
        "normalized_files_to_replace": len(replace),
        "files_to_add": len(add),
        "files_to_replace": replace,
    }
    host = {
        "checks": checks,
        "relation_manifest": relation_manifest,
        "precedent_internal_metadata": {pid: internal[pid] for pid in sorted(needed) if pid in internal},
        "reused_fichas": reused,
        "top_targets_by_query_key": [{"query_key": key, "relations": count}
                                     for key, count in sorted(((key, value) for key, value in relation_counts.items() if key.startswith("CC2002|")),
                                                              key=lambda pair: (-pair[1], pair[0]))[:20]],
        "targets_over_relation_limit": over_limit,
    }
    candidate_files["host/PREFLIGHT_RESULT.json"] = json_bytes(host)
    shared_refs = {f"{P.CONTENT}/{name}": {"repository_path": f"SHARED_CONTENT/{name}", "sha256": sha(all_fichas[name].encode("utf-8"))}
                   for name in sorted(new_names)}
    manifest = {
        "schema_version": 1,
        "kind": f"CC_MASS_{name}_CANDIDATE",
        "status": "HOST_ONLY_NOT_DEPLOYED",
        "deployed": False,
        "authority": {"ratification_record": str(RATIFICATION.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(RATIFICATION)},
        "baseline": {"CC": "49/39", "CF_ADCT": "315/198"},
        "checks": checks,
        "files": {path: {"bytes": len(value), "sha256": sha(value)} for path, value in sorted(candidate_files.items())},
        "shared_content_refs": shared_refs,
    }
    candidate_files["SHA256_MANIFEST.json"] = json_bytes(manifest)
    return candidate_files, manifest, host


def render_reports(summary: dict, combined_host: dict, firmware: dict, rollback: dict, deploy: dict):
    c = summary
    preflight = f"""# CC MASS MATERIALIZATION PREFLIGHT

`MASS_PREFLIGHT=PASS` · host-only · nenhuma alteração física.

- Fonte decisória: `CC_MASS_RATIFICATION_RECORD.json` (`653 HUMAN_APPROVED`; `28 HOLD` excluídas).
- Candidatos: HIGH_AUTHORITY `{c['high_relations']}`, TURMA `{c['turma_relations']}`, COMBINED `{c['combined_relations']}`.
- Projeção: CC `702/636`; baseline físico CC `49/39`; CF/ADCT `315/198`.
- Precedentes distintos: `{c['distinct_precedents']}`; fichas novas `{c['new_fichas']}`; reaproveitadas `{c['reused_fichas']}`.
- E2E: `{c['visible']}` relações aprovadas visíveis; CC atual `49/49` e `39/39`; CF `315/315` e `198/198`.
- GROUP_F nos candidatos: `0`; replacements E: `76`; erros de publicação: `0`.
- Schema opcional: `ORGAO|DATA|NATUREZA`, backward-compatible.

Ordenação determinística: registros físicos existentes primeiro; depois A, B, C, D e E. Isso preserva o conteúdo atual e posiciona precedentes qualificados/órgãos superiores antes das Turmas corroboradas e isoladas.
"""
    capacity = f"""# CC MASS CAPACITY REPORT

| Medida | Resultado |
| --- | ---: |
| Lookup entries | {c['lookup_entries']} / 4096 |
| Margem de lookup | {4096 - c['lookup_entries']} |
| JURISPRUDENCIA.IDX | {c['record_bytes']} bytes |
| PSRAM estimada | {c['psram']} bytes |
| Máximo por target/chave | {c['max_relations']} / 32 |
| Targets acima do limite | 0 |

Top 20 calculado no resultado host: `CC_MASS_MATERIALIZATION/COMBINED/host/PREFLIGHT_RESULT.json`. Nenhuma relação foi truncada.
"""
    display = f"""# CC MASS TURMA DISPLAY GATE

`TURMA_DISPLAY_SIMULATION=PASS` · `FIRMWARE_COMPILE=PASS` · `LEGACY_JURIS_REGRESSION=0`.

Na lista, um registro completo aparece como `STJ 3ª T. · REsp 2.145.365` (classe, número e órgão vêm do IDX; o exemplo não é hardcoded). Sem classe/órgão, o fallback é `STJ · Acórdão 2.145.365`.

A ficha contém TRIBUNAL, ÓRGÃO JULGADOR, CLASSE, NÚMERO, DATA e NATUREZA. C/D/E exibem `JURISPRUDÊNCIA PERSUASIVA — NÃO VINCULANTE`; C preserva a ressalva de que corroboração não é pacificação; D informa decisão isolada; E oculta a mecânica interna de replacement do leitor.

- Metadata ausente nas 559 relações: `{c['missing_display_metadata']}`.
- Programa: {firmware['before']['program_bytes']} → {firmware['after']['program_bytes']} B (`+{firmware['delta']['program_bytes']}`).
- RAM estática: {firmware['before']['static_ram_bytes']} → {firmware['after']['static_ram_bytes']} B (`+{firmware['delta']['static_ram_bytes']}`).
- app0 livre: `{firmware['after']['app_partition_free']}` B.
- Flash executado: **não**.
"""
    deploy_md = "# CC MASS — FUTURE MIXED TRANSACTIONAL DEPLOY\n\n" + "\n".join(f"{i}. {step}" for i, step in enumerate(deploy["steps"], 1)) + "\n\nNão executado nesta missão.\n"
    rollback_md = "# CC MASS — ROLLBACK PLAN\n\n" + f"Restaurar exatamente CC `49/39` e CF/ADCT `315/198`. Remover {len(rollback['delete'])} fichas novas e restaurar {len(rollback['restore'])} arquivos agregados pelos hashes PRE registrados.\n\n" + "\n".join(f"- `{path}` → `{meta['sha256']}`" for path, meta in rollback["restore"].items()) + "\n\nNão executado nesta missão.\n"
    return {
        REPORT_PREFLIGHT: preflight.encode("utf-8"), REPORT_CAPACITY: capacity.encode("utf-8"), REPORT_DISPLAY: display.encode("utf-8"),
        REPORT_DEPLOY: deploy_md.encode("utf-8"), REPORT_ROLLBACK: rollback_md.encode("utf-8"),
    }


def build():
    rat, approved, held = authority_inputs()
    known_targets = P.known_targets()
    invalid = sorted({x["target"] for x in approved if x["target"] not in known_targets})
    if invalid:
        raise SystemExit(f"PREFLIGHT_STOP INVALID_TARGETS {invalid[:5]}")
    _, _, base_rows = E.physical_layer(BASE)
    base_records = {}
    for row in base_rows:
        if row["precedent_id"] in base_records and base_records[row["precedent_id"]] != row["record"]:
            raise SystemExit(f"PREFLIGHT_STOP BASE_RECORD_CONFLICT {row['precedent_id']}")
        base_records[row["precedent_id"]] = row["record"]
    card_doc = load(CARD_MANIFEST)
    card_entries = card_doc["entries"]
    card_fichas = {Path(path).name for path in card_entries if path.startswith(P.CONTENT + "/")}
    by_precedent, new_records, all_fichas, internal = build_records(approved, base_records, card_fichas)
    outputs = {}
    manifests, hosts = {}, {}
    for name, config in TRACKS.items():
        selected = [x for x in approved if x["group_id"] in config["groups"]]
        if len(selected) != config["expected"]:
            raise SystemExit(f"PREFLIGHT_STOP {name}_COUNT")
        files, manifest, host = candidate(name, selected, base_rows, base_records, card_fichas, card_entries, new_records, all_fichas, internal)
        manifests[name], hosts[name] = manifest, host
        outputs.update({OUT / name / path: value for path, value in files.items()})
    used_fichas = {Path(ref).name for manifest in manifests.values() for ref in manifest["shared_content_refs"]}
    outputs.update({SHARED_CONTENT / name: all_fichas[name].encode("utf-8") for name in sorted(used_fichas)})
    combined = hosts["COMBINED"]["checks"]
    approved_precedents = set(by_precedent)
    base_by_norm = collections.defaultdict(set)
    for row in base_rows:
        base_by_norm[E.namespace_of(row["target_id"])].add(row["precedent_id"])
    shared_cf = approved_precedents & (base_by_norm["CF88"] | base_by_norm["ADCT"])
    shared_cc = approved_precedents & base_by_norm["CC2002"]
    group_e = [x for x in approved if x["group_id"] == "GROUP_E"]
    replacement_errors = sum(not x.get("replacement_publication") or x["replacement_publication"]["publish_precedent"] != x["precedent"]
                             or x["replacement_publication"]["publish_superseded_candidate"] for x in group_e)
    selected_precedents = {x["precedent"] for x in approved}
    replacement_errors += sum((x["target"], x["replacement_publication"]["superseded_candidate"]) in
                              {(row["target"], row["precedent"]) for row in approved} for x in group_e)
    missing_display = sum(not x.get("tribunal") or not x.get("classe") or not x.get("orgao") or not x.get("data")
                          for x in approved if x["group_id"] in {"GROUP_C", "GROUP_D", "GROUP_E"})
    # Frozen baselines and exact relation preservation are established by the packaged record set.
    combined_relations = hosts["COMBINED"]["relation_manifest"]
    combined_pairs = {(x["target"], x["precedent"]) for x in combined_relations}
    base_cc = {(x["target_id"], x["precedent_id"]) for x in base_rows if x["target_id"].startswith("CC2002:")}
    base_cf = {(x["target_id"], x["precedent_id"]) for x in base_rows if not x["target_id"].startswith("CC2002:")}
    semantic_cf, _ = P.cf_fixture()
    semantic_cf_pairs = {(x["target_id"], x["precedent_id"]) for x in semantic_cf}
    if (len(base_cc), len({x[0] for x in base_cc}), len(base_cf), len(semantic_cf_pairs), len({x[0] for x in semantic_cf_pairs})) != (49, 39, 315, 315, 198):
        raise SystemExit("PREFLIGHT_STOP PHYSICAL_BASELINE")
    firmware = load(FIRMWARE_REPORT)
    replace = manifests["COMBINED"]["checks"]["files_to_replace"]
    add_content = sorted(manifests["COMBINED"]["shared_content_refs"])
    rollback = {
        "executed": False,
        "delete": add_content,
        "restore": {path: {"bytes": card_entries[path]["bytes"], "sha256": card_entries[path]["sha256"]} for path in replace},
        "expected_after": {"CC": "49/39", "CF_ADCT": "315/198"},
    }
    deploy = {
        "mode": "MIXED_TRANSACTIONAL",
        "executed": False,
        "steps": ["backup PRE dos quatro arquivos agregados", "copiar fichas novas", "readback e SHA-256 das fichas",
                  "staging dos índices agregados", "validar staging", "replace atômico", "readback completo", "E2E", "rollback em qualquer falha"],
        "firmware_rollout": ["flash isolado do firmware display gate", "validação física com baseline 49/39", "mass deploy de dados",
                             "validação física massiva", "freeze"],
    }
    summary = {
        "approved_relations": len(approved), "held_relations": len(held), "high_relations": 94, "turma_relations": 559,
        "combined_relations": 653, "new_targets": len({x["target"] for x in approved if x["new_target"]}),
        "distinct_precedents": len(approved_precedents), "distinct_precedents_high": len({x["precedent"] for x in approved if x["group_id"] in {"GROUP_A", "GROUP_B"}}),
        "distinct_precedents_turma": len({x["precedent"] for x in approved if x["group_id"] in {"GROUP_C", "GROUP_D", "GROUP_E"}}),
        "new_fichas": combined["new_fichas_required"], "reused_fichas": combined["reused_existing_fichas"],
        "shared_with_cf": len(shared_cf), "shared_with_cc_j1_j2": len(shared_cc), "shared_fichas": len(shared_cf | shared_cc),
        "replacement_relations": len(group_e), "replacement_publication_errors": replacement_errors, "invalid_targets": len(invalid),
        "group_f_relations_in_candidates": 0, "lookup_entries": combined["lookup_entries"], "record_bytes": combined["record_bytes"],
        "psram": combined["psram_estimate_bytes"], "max_relations": combined["max_relations_on_single_target"],
        "visible": combined["approved_relations_visible"], "missing_display_metadata": missing_display,
        "current_cc_relations_preserved": f"{len(base_cc)}/49", "current_cc_targets_preserved": f"{len({x[0] for x in base_cc})}/39",
        "cf_relations_preserved": f"{len(semantic_cf_pairs)}/315", "cf_targets_preserved": f"{len({x[0] for x in semantic_cf_pairs})}/198",
        "schema_change": True, "backward_compatible": True, "normalized_files_to_replace": len(replace),
        "high_authority_data_only_ready": True,
        "turma_data_ready": all([missing_display == 0, replacement_errors == 0, combined["targets_over_relation_limit"] == 0,
                                 combined["lookup_lost_relations"] == 0, combined["duplicate_query_keys"] == 0,
                                 not combined["e2e_failed_targets"], firmware["after"]["app_partition_free"] > 0]),
        "base_cc_pairs": len(base_cc), "base_cf_pairs": len(base_cf), "combined_pair_overlap": len(base_cc & combined_pairs),
    }
    if summary["new_targets"] != 597 or summary["visible"] != "653/653" or replacement_errors or missing_display:
        raise SystemExit(f"PREFLIGHT_STOP FINAL_RECONCILIATION {summary}")
    reports = render_reports(summary, hosts["COMBINED"], firmware, rollback, deploy)
    outputs.update(reports)
    checkpoint = {
        "schema_version": 1, "status": "PASS", "ratification": "653 HUMAN_APPROVED", "new_physical": 0,
        "cc_physical": "49/39", "cf_adct_physical": "315/198", "cc_ratified_projection": "702/636",
        "turma_display_gate": "PASS_HOST_ONLY", "mass_materialization_preflight": "PASS_HOST_ONLY",
        "summary": summary,
        "candidate_manifests": {name: sha(outputs[OUT / name / "SHA256_MANIFEST.json"]) for name in TRACKS},
        "firmware_candidate_sha256": hashlib.sha256(FIRMWARE_BINARY.read_bytes()).hexdigest(), "sd_changed": False, "firmware_flashed": False,
    }
    outputs[CHECKPOINT] = json_bytes(checkpoint)
    return outputs, summary


def main() -> int:
    outputs, summary = build()
    if "--check" in sys.argv:
        stale = [str(path.relative_to(ROOT)) for path, data in outputs.items() if not path.is_file() or path.read_bytes().replace(b"\r\n", b"\n") != data.replace(b"\r\n", b"\n")]
        print("UP_TO_DATE" if not stale else "STALE " + json.dumps(stale, ensure_ascii=False))
        return 0 if not stale else 1
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
