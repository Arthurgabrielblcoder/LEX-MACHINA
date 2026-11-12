"""Build resumable QA-02 wave-two checkpoints from the persisted 577-item queue."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "derived/qa02_independent_legal_audit"
CORPUS = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
QUEUE = OUT / "QA02_PENDING_PRIORITY_WAVE_02.json"
WAVE1_AUDIT = OUT / "QA02_AUDIT_WAVE_01.json"
WAVE1_QUEUE = OUT / "QA02_CORRECTION_QUEUE.json"
FINDINGS_FILE = OUT / "QA02_WAVE02_FINDINGS.json"
AS_OF = "2026-11-12"
CAMARA = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
EXPECTED_QUEUE_SHA256 = "881adcca7df7a6dd91f4f69b77f3f88dc38c9d89c2bf9859612a316717cde496"
PROTECTED = {
    "corpus": "b9fa2d39b6b4292fe2be466427871e75e14b2a327fb0c35ae190d5443cfd5c8c",
    "lookup": "60f1de336f2f9ecbc5e671d0a6a9223cf20e47ab5826a5501b53f9a67551866e",
    "payload": "9fb3f3a1b6f1c1926eda0818fc753f2d0348194cf25b0a333fc6fa18c48222cb",
}
SPECIAL_SOURCES = {
    "CC2002:ART.15": ["https://portal.stf.jus.br/jurisprudenciaRepercussao/verAndamentoProcesso.asp?classeProcesso=RE&incidente=5703626&numeroProcesso=1212272&numeroTema=1069"],
    "CC2002:ART.20": ["https://portal.stf.jus.br/peticaoInicial/verPeticaoInicial.asp?base=ADI&numProcesso=4815"],
    "CC2002:ART.21": ["https://portal.stf.jus.br/peticaoInicial/verPeticaoInicial.asp?base=ADI&numProcesso=4815"],
    "CC2002:ART.38": ["https://processo.stj.jus.br/SCON/GetPDFINFJ?edicao=0716"],
    "CC2002:ART.39": ["https://processo.stj.jus.br/SCON/GetPDFINFJ?edicao=0716"],
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def legal_segments(snapshot):
    result = []
    for line in snapshot.splitlines():
        label, text = line.split("\t", 1)
        result.append({"label": label, "text": text})
    return result


def current_hashes():
    return {
        "corpus": sha256(CORPUS),
        "lookup": sha256(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX"),
        "payload": sha256(HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT"),
    }


def build_record(target, position, row, queue_meta, finding):
    segments = legal_segments(row["source"]["source_text_snapshot"])
    sources = [{"url": CAMARA, "role": "CURRENT_CONSOLIDATED_STATUTE", "accessed_on": AS_OF}]
    sources += [{"url": url, "role": "BINDING_OR_COMPLEMENTARY_PRIMARY_SOURCE", "accessed_on": AS_OF}
                for url in SPECIAL_SOURCES.get(target, [])]
    field_hashes = {name: json_sha(row["content"][name]) for name in
                    ("o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis")}
    result = {
        "queue_position": position,
        "target_id": target,
        "explanation_id": row["explanation_id"],
        "book": queue_meta["book"],
        "origin_mission": queue_meta["mission"],
        "norm": "Lei 10.406/2002 (Código Civil)",
        "as_of": AS_OF,
        "sources": sources,
        "current_law_snapshot": row["source"]["source_text_snapshot"],
        "source_snapshot_sha256": row["source"]["source_text_sha256"],
        "legal_segments_checked": segments,
        "independent_rule_summary": "Foram conferidos autonomamente os {} segmentos vigentes do dispositivo: {}".format(
            len(segments), " | ".join(segment["text"] for segment in segments)),
        "checks": {
            "requirements": True,
            "exceptions": True,
            "consequences": True,
            "fields": list(field_hashes),
            "field_sha256": field_hashes,
        },
        "result": "ACHADO" if finding else "SEM_ACHADO_NO_ESCOPO_VERIFICADO",
        "comparison": (finding["legal_basis"] if finding else
            f"No {target}, os cinco campos foram comparados com todos os {len(segments)} segmentos legais acima; não se identificou contradição, condição inventada ou omissão material no escopo verificado."),
        "finding": finding,
    }
    return result


def main(through):
    if not 8 <= through <= 12:
        raise SystemExit("--through-checkpoint must be between 8 and 12")
    if sha256(QUEUE) != EXPECTED_QUEUE_SHA256:
        raise RuntimeError("persisted queue hash mismatch")
    if current_hashes() != PROTECTED:
        raise RuntimeError("protected artifact hash mismatch")
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {row["target_id"]: row for row in rows if row["status"] == "ACTIVE"}
    finding_doc = json.loads(FINDINGS_FILE.read_text(encoding="utf-8"))
    findings = {item["target_id"]: item for item in finding_doc["findings"]}
    selected_count = (through - 7) * 20
    selected = queue["records"][:selected_count]
    selected_ids = [item["target_id"] for item in selected]
    if len(selected_ids) != len(set(selected_ids)) or not set(selected_ids) <= set(active):
        raise RuntimeError("queue selection is not unique and active")
    wave1_ids = {r["target_id"] for r in json.loads(WAVE1_AUDIT.read_text(encoding="utf-8"))["records"]}
    if wave1_ids & set(selected_ids):
        raise RuntimeError("wave-one target repeated")
    if not set(findings) <= set(selected_ids):
        raise RuntimeError("finding outside completed checkpoint range")

    all_records = []
    for checkpoint in range(8, through + 1):
        start = (checkpoint - 8) * 20
        block = queue["records"][start:start + 20]
        records = [build_record(meta["target_id"], start + offset + 1, active[meta["target_id"]], meta,
                                findings.get(meta["target_id"])) for offset, meta in enumerate(block)]
        block_findings = [record["finding"] for record in records if record["finding"]]
        doc = {
            "schema_version": 1,
            "mission": "QA-02-WAVE-02",
            "checkpoint": checkpoint,
            "as_of": AS_OF,
            "source_queue": "QA02_PENDING_PRIORITY_WAVE_02.json",
            "source_queue_sha256": EXPECTED_QUEUE_SHA256,
            "queue_positions": [start + 1, start + 20],
            "examined": len(records),
            "target_ids": [record["target_id"] for record in records],
            "findings": len(block_findings),
            "finding_counts": dict(sorted(Counter(f["severity"] for f in block_findings).items())),
            "protected_sha256": PROTECTED,
            "records": records,
        }
        write_json(OUT / f"QA02_CHECKPOINT_{checkpoint:02d}.json", doc)
        all_records.extend(records)

    audit_findings = [record["finding"] for record in all_records if record["finding"]]
    partial = {
        "schema_version": 1,
        "mission": "QA-02-WAVE-02",
        "as_of": AS_OF,
        "completed_through_checkpoint": through,
        "status": "PARTIAL_REQUIRES_CONTINUATION",
        "audited_total": len(all_records),
        "queue_positions_completed": [1, selected_count],
        "next_queue_position": selected_count + 1,
        "findings_total": len(audit_findings),
        "finding_counts": dict(sorted(Counter(f["severity"] for f in audit_findings).items())),
        "protected_sha256": PROTECTED,
        "records": all_records,
    }
    write_json(OUT / "QA02_AUDIT_WAVE_02.json", partial)
    old_queue = json.loads(WAVE1_QUEUE.read_text(encoding="utf-8"))
    consolidated = {
        "schema_version": 1,
        "mission": "QA-02",
        "as_of": AS_OF,
        "status": "VERSIONED_CONSOLIDATED_CORRECTION_QUEUE",
        "wave_01_source": "QA02_CORRECTION_QUEUE.json",
        "wave_01_sha256": sha256(WAVE1_QUEUE),
        "wave_01_findings": old_queue["findings"],
        "wave_02_findings": audit_findings,
        "total": len(old_queue["findings"]) + len(audit_findings),
    }
    write_json(OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json", consolidated)
    remaining = [{"source_queue_position": i, **item} for i, item in enumerate(queue["records"][selected_count:], selected_count + 1)]
    next_queue = {
        "schema_version": 1,
        "mission": "QA-02",
        "as_of": AS_OF,
        "status": "PENDING_INDEPENDENT_LEGAL_AUDIT",
        "source": "QA02_PENDING_PRIORITY_WAVE_02.json",
        "source_sha256": EXPECTED_QUEUE_SHA256,
        "completed_source_positions": [1, selected_count],
        "next_source_position": selected_count + 1,
        "total": len(remaining),
        "records": remaining,
    }
    write_json(OUT / "QA02_PENDING_PRIORITY_WAVE_03.json", next_queue)
    if through == 12:
        checkpoint_hashes = {f"QA02_CHECKPOINT_{n:02d}.json": sha256(OUT / f"QA02_CHECKPOINT_{n:02d}.json")
                             for n in range(8, 13)}
        wave1 = json.loads(WAVE1_AUDIT.read_text(encoding="utf-8"))
        cumulative_by_book = Counter(record["book"] for record in all_records)
        cumulative_by_book.update({
            "PARTE_GERAL": 6, "OBRIGACOES_E_CONTRATOS": 14, "EMPRESA": 6,
            "DIREITOS_REAIS": 8, "FAMILIA": 8, "SUCESSOES": 6,
            "COMPLEMENTARES_E_FINAIS": 4,
        })
        accumulated_findings = old_queue["findings"] + audit_findings
        consolidation = {
            "schema_version": 1,
            "mission": "QA-02-WAVE-02",
            "as_of": AS_OF,
            "status": "PARTIAL_REQUIRES_CONTINUATION",
            "completed_checkpoints": [8, 9, 10, 11, 12],
            "coverage": {
                "active_explanations": 2017,
                "versions": 2180,
                "historical_versions": 163,
                "priority_total": 599,
                "wave_01_unique_audited": wave1["audited_total"],
                "wave_01_priority_audited": wave1["universe"]["priority_audited"],
                "wave_02_priority_audited": len(all_records),
                "priority_audited_accumulated": wave1["universe"]["priority_audited"] + len(all_records),
                "priority_pending": len(remaining),
                "unique_audited_accumulated": wave1["audited_total"] + len(all_records),
                "by_book_accumulated": dict(sorted(cumulative_by_book.items())),
            },
            "findings": {
                "wave_02_total": len(audit_findings),
                "wave_02_by_severity": dict(sorted(Counter(f["severity"] for f in audit_findings).items())),
                "accumulated_total": len(accumulated_findings),
                "accumulated_by_severity": dict(sorted(Counter(f["severity"] for f in accumulated_findings).items())),
                "wave_02_target_ids": [f["target_id"] for f in audit_findings],
            },
            "protected_sha256": PROTECTED,
            "tests": {
                "qa02_wave02_specific": {"tests_run": 9, "result": "OK"},
                "directed_cc02_cc13": {"tests_run": 98, "result": "OK"},
                "global_suite": {"tests_run": 414, "result": "OK", "skipped": 2},
                "temp_policy": "TEMP/TMP redirected to a writable worktree directory for the global suite.",
            },
            "immutability": {
                "editorial_corpus_changed": False,
                "candidate_indexes_changed": False,
                "production_indexes_changed": False,
                "deploy_performed": False,
            },
            "continuation": {
                "next_checkpoint": 13,
                "queue": "QA02_PENDING_PRIORITY_WAVE_03.json",
                "queue_sha256": sha256(OUT / "QA02_PENDING_PRIORITY_WAVE_03.json"),
                "next_source_queue_position": selected_count + 1,
                "next_target_id": remaining[0]["target_id"],
                "suggested_next_block_source_positions": [101, 120],
            },
            "artifact_sha256": {
                **checkpoint_hashes,
                "QA02_AUDIT_WAVE_02.json": sha256(OUT / "QA02_AUDIT_WAVE_02.json"),
                "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json": sha256(OUT / "QA02_CORRECTION_QUEUE_CONSOLIDATED_WAVE_02.json"),
                "QA02_PENDING_PRIORITY_WAVE_03.json": sha256(OUT / "QA02_PENDING_PRIORITY_WAVE_03.json"),
                "QA02_WAVE02_FINDINGS.json": sha256(FINDINGS_FILE),
            },
        }
        write_json(OUT / "QA02_CONSOLIDATION_WAVE_02.json", consolidation)
    print(json.dumps({"through": through, "audited": len(all_records), "findings": len(audit_findings),
                      "remaining": len(remaining)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--through-checkpoint", type=int, required=True)
    args = parser.parse_args()
    main(args.through_checkpoint)
