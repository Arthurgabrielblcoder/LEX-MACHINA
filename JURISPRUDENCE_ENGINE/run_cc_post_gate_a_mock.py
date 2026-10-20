"""Ensaios destrutivos somente em clones locais marcados como mock."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import build_cc_mass_materialization as M
import cc_transactional_deploy as D

HERE = Path(__file__).resolve().parent
LOCAL = HERE / "CC_MASS_DISCOVERY/_local/post_gate_a_mock"
FIXTURE_PROFILE = HERE / "CC_TURMA_PHYSICAL_FIXTURE/DEPLOY_PROFILE.json"
MASS_PROFILE = HERE / "CC_MASS_DEPLOY_653/DEPLOY_PROFILE.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted(root.rglob("*")) if p.is_file() and not p.relative_to(root).as_posix().startswith("._lex_mock_backups")}


def fresh(name: str) -> Path:
    root = LOCAL / name
    if root.exists(): shutil.rmtree(root)
    shutil.copytree(M.BASE, root)
    (root / ".lex_mock_sd.json").write_text('{"kind":"LEX_MACHINA_SYNTHETIC_SD","physical":false}\n', encoding="utf-8")
    return root


def run_cycle(name: str, profile: dict) -> dict:
    root = fresh(name); before = snapshot(root)
    dry = D.preflight(root, profile)
    deployed = D.deploy(root, profile, root / "._lex_mock_backups")
    verified = D.verify(root, profile)
    second = D.deploy(root, profile, root / "._lex_mock_backups")
    rolled = D.rollback(root, profile, root / "._lex_mock_backups")
    after = snapshot(root)
    return {"dry_run": dry["result"], "deploy": deployed["result"], "verify": verified["result"],
            "idempotency": second["result"], "rollback": rolled["result"],
            "pre_post_pre_byte_exact": before == after, "semantic": rolled["semantic"]}


def main() -> int:
    fixture = D.load_profile(FIXTURE_PROFILE); mass = D.load_profile(MASS_PROFILE)
    fixture_result = run_cycle("fixture_cycle", fixture)
    mass_result = run_cycle("mass_cycle", mass)
    failures = []
    for point in sorted(D.INJECTIONS):
        root = fresh("failure_" + point); before = snapshot(root)
        result = D.deploy(root, mass, root / "._lex_mock_backups", inject=point)
        failures.append({"point": point, "result": result["result"], "byte_exact": snapshot(root) == before,
                         "semantic": D.semantic_counts(root)})
    # Caminho alternativo: fixture validado -> massivo -> rollback ao fixture.
    root = fresh("post_fixture_path")
    D.deploy(root, fixture, root / "._lex_mock_backups_fixture")
    fixture_bytes = snapshot(root)
    promoted = D.deploy(root, mass, root / "._lex_mock_backups_mass")
    restored = D.rollback(root, mass, root / "._lex_mock_backups_mass")
    fixture_restore = snapshot(root) == fixture_bytes
    fixture_doc = {"schema_version": 1, "physical": False, "result": "PASS" if all((fixture_result["deploy"] == "DEPLOY_PASS",
        fixture_result["rollback"] == "ROLLBACK_PASS", fixture_result["pre_post_pre_byte_exact"])) else "FAIL", **fixture_result}
    mass_ok = all((mass_result["deploy"] == "DEPLOY_PASS", mass_result["verify"] == "VERIFY_PASS",
                   mass_result["idempotency"] == "ALREADY_DEPLOYED_NOOP", mass_result["rollback"] == "ROLLBACK_PASS",
                   mass_result["pre_post_pre_byte_exact"], all(x["result"] == "INJECTED_FAILURE_ROLLED_BACK" and x["byte_exact"] for x in failures),
                   promoted["result"] == "DEPLOY_PASS", restored["result"] == "ROLLBACK_PASS", fixture_restore))
    mass_doc = {"schema_version": 1, "physical": False, "result": "PASS" if mass_ok else "FAIL", **mass_result,
                "failure_injection": failures, "failure_injection_result": "PASS" if all(x["byte_exact"] for x in failures) else "FAIL",
                "post_fixture_validated_path": {"deploy": promoted["result"], "rollback": restored["result"], "fixture_byte_exact": fixture_restore},
                "expected": {"CC": "702/636", "CF_ADCT": "315/198", "relations_visible": "653/653", "new_targets": 597,
                             "new_fichas": 572, "reused_fichas": 2, "group_f": 0, "replacements": 76, "lookups": "833/4096"}}
    out1 = HERE / "CC_TURMA_PHYSICAL_FIXTURE/host/MOCK_RESULT.json"; out1.parent.mkdir(parents=True, exist_ok=True)
    out2 = HERE / "CC_MASS_DEPLOY_653/host/MOCK_RESULT.json"; out2.parent.mkdir(parents=True, exist_ok=True)
    out1.write_text(json.dumps(fixture_doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    out2.write_text(json.dumps(mass_doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"fixture": fixture_doc["result"], "mass": mass_doc["result"], "failure_cases": len(failures)}, indent=2))
    return 0 if fixture_doc["result"] == mass_doc["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
