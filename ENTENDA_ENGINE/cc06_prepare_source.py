"""Prepare the isolated CC-06 structural source without touching device data."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LEGAL_TARGET_ID"))
import build_target_index as BT  # noqa: E402

OLD_BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "production_cc_001_114"
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_250"
OLD_SOURCE = OLD_BATCH / "SOURCE_CC2002_ARTS_001_114.txt"
OPERATIONAL = ROOT / "updater" / "backup_saida" / "antes_recuperacao_monovigente_20260913_162304" / "2- C#U00d3DIGO CIVIL" / "codigo_civil_ lei10.406 2002.txt"
SOURCE = BATCH / "SOURCE_CC2002_ARTS_001_250.txt"
PROVENANCE = BATCH / "SOURCE_PROVENANCE.json"
TARGET_INDEX = BATCH / "CC2002_TARGET_INDEX.json"
TARGET_STATUS = BATCH / "CC2002_TARGET_STATUS.json"
EXPECTED_OPERATIONAL_SHA256 = "7264b71ede9d7fffb4d7a6494556ac6593ade2419085bce1807131f23205034b"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main() -> None:
    operational_raw = OPERATIONAL.read_bytes()
    if sha(operational_raw) != EXPECTED_OPERATIONAL_SHA256:
        raise SystemExit("CC06_OPERATIONAL_SOURCE_HASH_MISMATCH")
    operational = operational_raw.decode("utf-8-sig")
    start = re.search(r"(?m)^Art\. 115\.\s", operational)
    end = re.search(r"(?m)^Art\. 251\.\s", operational)
    if not start or not end or end.start() <= start.start():
        raise SystemExit("CC06_ARTICLE_BOUNDARY_NOT_FOUND")
    old = OLD_SOURCE.read_text(encoding="utf-8")
    addition = operational[start.start():end.start()].rstrip() + "\n"
    combined = (old.rstrip() + "\n\n" + addition).encode("utf-8")
    BATCH.mkdir(parents=True, exist_ok=True)
    SOURCE.write_bytes(combined)

    idx = BT.build("CC2002", SOURCE)
    idx["source"]["path"] = str(SOURCE.relative_to(ROOT)).replace("\\", "/")
    if idx["target_id_duplicates"]:
        raise SystemExit("CC06_TARGET_ID_DUPLICATES")
    write_json(TARGET_INDEX, idx)

    historical = {
        "CC2002:ART.3:INC.I": "Revogado pela Lei 13.146/2015",
        "CC2002:ART.3:INC.II": "Revogado pela Lei 13.146/2015",
        "CC2002:ART.3:INC.III": "Revogado pela Lei 13.146/2015",
        "CC2002:ART.10:INC.III": "Revogado pela Lei 12.010/2009",
        "CC2002:ART.44:INC.VI": "Revogado pela MP 1.085/2021, convertida na Lei 14.382/2022",
        "CC2002:ART.57:PAR.UNICO": "Revogado pela Lei 11.127/2005",
        "CC2002:ART.62:PAR.UNICO:INC.X": "Vetado na Lei 13.151/2015",
        "CC2002:ART.69-A": "Artigo vetado na Lei 12.715/2012",
        "CC2002:ART.69-A:CAPUT": "Artigo vetado na Lei 12.715/2012",
        "CC2002:ART.194": "Revogado pela Lei 11.280/2006",
        "CC2002:ART.194:CAPUT": "Revogado pela Lei 11.280/2006",
        "CC2002:ART.206:PAR.1:INC.II": "Revogado pela Lei 15.040/2024, em vigor desde 10/12/2025",
        "CC2002:ART.227": "Caput revogado pela Lei 13.105/2015; parágrafo único permanece vigente",
        "CC2002:ART.227:CAPUT": "Caput revogado pela Lei 13.105/2015",
        "CC2002:ART.228:INC.II": "Revogado pela Lei 13.146/2015",
        "CC2002:ART.228:INC.III": "Revogado pela Lei 13.146/2015",
        "CC2002:ART.229": "Revogado pela Lei 13.105/2015",
        "CC2002:ART.229:CAPUT": "Revogado pela Lei 13.105/2015",
        "CC2002:ART.230": "Revogado pela Lei 13.105/2015",
        "CC2002:ART.230:CAPUT": "Revogado pela Lei 13.105/2015"
    }
    indexed = {t["target_id"] for t in idx["targets"]}
    missing = sorted(set(historical) - indexed)
    if missing:
        raise SystemExit("CC06_HISTORICAL_TARGET_NOT_INDEXED: " + ", ".join(missing))
    write_json(TARGET_STATUS, {
        "schema_version": 1,
        "target_index_sha256": sha(TARGET_INDEX.read_bytes()),
        "method": "Marcadores explícitos na fonte operacional consolidada, confrontados com a Câmara dos Deputados em 07/11/2026.",
        "counts": {"explicit_revoked_or_vetoed": len(historical)},
        "targets": {
            tid: {"status": "HISTORICAL_ONLY", "revoked_marker": True, "reason": reason}
            for tid, reason in historical.items()
        },
    })
    write_json(PROVENANCE, {
        "schema_version": 1,
        "norma_id": "CC2002",
        "scope": "Código Civil, arts. 1 a 250, com produção nova limitada aos arts. 115 a 250",
        "preserved_cc05_source_sha256": sha(OLD_SOURCE.read_bytes()),
        "operational_repository_source": str(OPERATIONAL.relative_to(ROOT)).replace("\\", "/"),
        "operational_source_sha256": sha(operational_raw),
        "new_scope_excerpt_sha256": sha(addition.encode("utf-8")),
        "combined_candidate_source_sha256": sha(combined),
        "official_confrontation": {
            "checked_on": "2026-11-07",
            "consolidated_text": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"
        },
        "device_source_modified": False,
    })
    articles = [t for t in idx["targets"] if t["kind"] == "ARTIGO"]
    print(json.dumps({
        "combined_source_sha256": sha(combined),
        "targets": idx["total_targets"],
        "article_targets": len(articles),
        "historical_targets": len(historical),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
