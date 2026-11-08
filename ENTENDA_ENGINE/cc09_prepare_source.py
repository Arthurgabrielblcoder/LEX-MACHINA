"""Prepare the isolated CC-09 structural source without touching device data."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LEGAL_TARGET_ID"))
import build_target_index as BT  # noqa: E402

CC08 = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_550"
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_700"
OLD_SOURCE, OLD_STATUS = CC08 / "SOURCE_CC2002_ARTS_001_550.txt", CC08 / "CC2002_TARGET_STATUS.json"
OPERATIONAL = ROOT / "updater" / "backup_saida" / "antes_recuperacao_monovigente_20260913_162304" / "2- C#U00d3DIGO CIVIL" / "codigo_civil_ lei10.406 2002.txt"
SOURCE, TARGET_INDEX, TARGET_STATUS = BATCH / "SOURCE_CC2002_ARTS_001_700.txt", BATCH / "CC2002_TARGET_INDEX.json", BATCH / "CC2002_TARGET_STATUS.json"
PROVENANCE = BATCH / "SOURCE_PROVENANCE.json"
OFFICIAL_HTML = ROOT / "ENTENDA_ENGINE" / "derived" / "CC07_CODIGO_CIVIL_CAMARA.html"
EXPECTED_OPERATIONAL_SHA256 = "7264b71ede9d7fffb4d7a6494556ac6593ade2419085bce1807131f23205034b"

def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

def main() -> None:
    raw = OPERATIONAL.read_bytes()
    if sha(raw) != EXPECTED_OPERATIONAL_SHA256: raise SystemExit("CC09_OPERATIONAL_SOURCE_HASH_MISMATCH")
    text = raw.decode("utf-8-sig")
    start, end = re.search(r"(?m)^Art\. 551\.\s", text), re.search(r"(?m)^Art\. 701\.\s", text)
    if not start or not end: raise SystemExit("CC09_ARTICLE_BOUNDARY_NOT_FOUND")
    addition = text[start.start():end.start()].rstrip() + "\n"
    combined = (OLD_SOURCE.read_text(encoding="utf-8").rstrip() + "\n\n" + addition).encode("utf-8")
    BATCH.mkdir(parents=True, exist_ok=True); SOURCE.write_bytes(combined)
    idx = BT.build("CC2002", SOURCE); idx["source"]["path"] = str(SOURCE.relative_to(ROOT)).replace("\\", "/")
    if idx["target_id_duplicates"]: raise SystemExit("CC09_TARGET_ID_DUPLICATES")
    write_json(TARGET_INDEX, idx)
    historical = json.loads(OLD_STATUS.read_text(encoding="utf-8"))["targets"]
    write_json(TARGET_STATUS, {"schema_version": 1, "target_index_sha256": sha(TARGET_INDEX.read_bytes()), "method": "Marcadores explícitos na fonte operacional confrontados com a versão consolidada da Câmara dos Deputados em 08/11/2026.", "counts": {"explicit_revoked_or_vetoed": len(historical)}, "targets": historical})
    write_json(PROVENANCE, {"schema_version": 1, "norma_id": "CC2002", "scope": "Código Civil, arts. 1 a 700, com produção nova limitada aos arts. 551 a 700", "preserved_cc08_source_sha256": sha(OLD_SOURCE.read_bytes()), "operational_repository_source": str(OPERATIONAL.relative_to(ROOT)).replace("\\", "/"), "operational_source_sha256": sha(raw), "new_scope_excerpt_sha256": sha(addition.encode("utf-8")), "combined_candidate_source_sha256": sha(combined), "official_confrontation": {"checked_on": "2026-11-08", "consolidated_text": "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html", "downloaded_html_sha256": sha(OFFICIAL_HTML.read_bytes())}, "device_source_modified": False})
    scoped = [t for t in idx["targets"] if t["kind"] == "ARTIGO" and 551 <= int(t["article"].split("-")[0]) <= 700]
    print(json.dumps({"combined_source_sha256": sha(combined), "new_scope_sha256": sha(addition.encode("utf-8")), "numbered_positions": 150, "article_targets_examined": len(scoped), "active_articles_expected": len(scoped), "intercalated": [], "historical_in_new_scope": []}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
