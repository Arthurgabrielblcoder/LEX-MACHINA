#!/usr/bin/env python3
"""Isolated SCA1B1 tests. The real D05 consumer is never imported or executed."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
import sys

sys.path.insert(0, str(REPO))

from SHADOW_CONSUMER_ADAPTER.diagnostic import redact_sensitive, safe_binding_summary, write_diagnostic
from SHADOW_CONSUMER_ADAPTER.legacy_observer import BOUNDARY, LegacyObserver
from SHADOW_CONSUMER_ADAPTER.run_d05_catalog_shadow import (
    LegacyResult,
    ShadowResolutionFailure,
    build_parser,
    run_adapter,
)
from SHADOW_CONSUMER_ADAPTER.runtime_compare import compare_runtime


EXPECTED_CONSUMER_SHA256 = "4e53ca2a87bd0577facb4461b09b685223c4daabe869cfaff81610e6cdc66a7d"
CONSUMER = REPO / "LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/compilar_catalogo.py"


def legacy(value: str = "LEGACY-X") -> LegacyResult:
    return LegacyResult(0, stdout=value, output_hashes={"out.json": "a" * 64}, value=value)


def matching_summaries() -> tuple[dict, dict]:
    left = {
        "sets": {
            "triage_batch_paths": {"observability": "MEMBER_LEVEL", "members": ["a", "b"], "ordered": True},
            "base_catalog_work_ids": {"observability": "MEMBER_LEVEL", "members": ["w1", "w2"], "ordered": True},
            "triage_candidate_numbers": {"observability": "NOT_OBSERVABLE"},
        },
        "dependencies": ["wrapper-69"],
        "absences": None,
    }
    right = {
        "sets": {
            "triage_batch_paths": {"members": ["a", "b"], "ordered": True},
            "base_catalog_work_ids": {"members": ["w1", "w2"], "ordered": True},
            "triage_candidate_numbers": {"members": list(range(200)), "ordered": True},
        },
        "dependencies": ["wrapper-69"],
        "absences": ["not-runtime-observed"],
    }
    return left, right


def observed_fixture(base: Path) -> LegacyObserver:
    d05 = base / "d05"
    out = base / "out"
    observer = LegacyObserver(out, d05)
    observer.audit_hook("open", (d05 / "02_TRIAGEM/LOTE_01.json", "r", 0))
    observer.audit_hook("open", (d05 / "02_TRIAGEM/LOTE_02.json", "r", 0))
    observer.audit_hook("open", (d05 / "04_DOSSIERS/W001.json", "r", 0))
    observer.audit_hook("open", (d05 / "04_DOSSIERS/W001.json", "r", 0))
    observer.audit_hook("open", (d05 / "00_ENTRADA/REFERENCIA_CATALOGO_69.json", "r", 0))
    observer.audit_hook("open", (out / "CATALOGO_EXPANSAO_200.json", "w", 0))
    return observer


class AdapterTests(unittest.TestCase):
    def test_positive_01_flag_defaults_off(self) -> None:
        self.assertFalse(build_parser().parse_args([]).shadow_compare)

    def test_positive_02_off_does_not_require_registry(self) -> None:
        result = run_adapter(shadow_enabled=False, legacy_executor=lambda observer: legacy())
        self.assertEqual(result.legacy_result.value, "LEGACY-X")

    def test_positive_03_off_does_not_require_lock(self) -> None:
        result = run_adapter(shadow_enabled=False, legacy_executor=lambda observer: legacy(), shadow_worker=lambda: (_ for _ in ()).throw(AssertionError()))
        self.assertEqual(result.diagnostic["shadow_status"], "SHADOW_DISABLED")

    def test_positive_04_off_does_not_require_bindings_or_resolver_import(self) -> None:
        with patch("importlib.import_module", side_effect=AssertionError("must stay lazy")):
            result = run_adapter(shadow_enabled=False, legacy_executor=lambda observer: legacy())
        self.assertEqual(result.legacy_result.exit_code, 0)

    def test_positive_05_legacy_authority_true(self) -> None:
        result = run_adapter(shadow_enabled=False, legacy_executor=lambda observer: legacy())
        self.assertIs(result.diagnostic["legacy_authoritative"], True)

    def test_positive_06_shadow_authority_false(self) -> None:
        result = run_adapter(shadow_enabled=False, legacy_executor=lambda observer: legacy())
        self.assertIs(result.diagnostic["shadow_authoritative"], False)

    def test_positive_07_capture_preserves_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            summary = observed_fixture(Path(temporary)).summary()
        self.assertEqual(summary["sets"]["triage_batch_paths"]["members"], ["02_TRIAGEM/LOTE_01.json", "02_TRIAGEM/LOTE_02.json"])

    def test_positive_08_capture_preserves_multiplicity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            summary = observed_fixture(Path(temporary)).summary()
        self.assertEqual(summary["sets"]["base_catalog_work_ids"]["members"], ["W001", "W001"])

    def test_positive_09_first_functional_write_seals_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            observer = observed_fixture(base)
            observer.audit_hook("open", (base / "d05/04_DOSSIERS/AFTER.json", "r", 0))
            summary = observer.summary()
        self.assertTrue(summary["sealed"])
        self.assertEqual(summary["boundary"], BOUNDARY)
        self.assertNotIn("AFTER", summary["sets"]["base_catalog_work_ids"]["members"])

    def test_positive_10_comparison_match_preserves_not_observable(self) -> None:
        left, right = matching_summaries()
        result = compare_runtime(left, right)
        self.assertEqual(result["status"], "PASS_WITH_NOT_OBSERVABLE_DIMENSIONS")
        self.assertEqual(result["mismatches"], [])

    def test_positive_11_diagnostic_is_safe_and_noncanonical(self) -> None:
        captured: dict = {}
        result = run_adapter(
            shadow_enabled=False,
            legacy_executor=lambda observer: legacy(),
            bindings={"D05_MANAGED_ROOT": "C:/private/root"},
            diagnostic_path=Path("ignored.json"),
            diagnostic_writer=lambda path, value: captured.update(value),
        )
        self.assertEqual(captured["artifact_class"], "DERIVED_DIAGNOSTIC")
        self.assertEqual(captured["authority"], "NON_AUTHORITATIVE")
        self.assertNotIn("C:/private/root", json.dumps(captured))
        self.assertTrue(result.diagnostic_written)

    def test_positive_12_shadow_never_changes_simulated_legacy(self) -> None:
        left, right = matching_summaries()
        result = run_adapter(
            shadow_enabled=True,
            legacy_executor=lambda observer: legacy("UNCHANGED"),
            observer=type("FakeObserver", (), {"summary": lambda self: left})(),
            shadow_worker=lambda: right,
        )
        self.assertEqual(result.legacy_result.value, "UNCHANGED")
        self.assertIs(result.diagnostic["shadow_did_affect_output"], False)

    def test_positive_13_performance_formula_and_fields(self) -> None:
        result = run_adapter(shadow_enabled=False, legacy_executor=lambda observer: legacy())
        performance = result.diagnostic["performance"]
        required = {"legacy_duration_ms", "shadow_duration_ms", "comparison_duration_ms", "diagnostic_write_duration_ms", "total_duration_ms", "shadow_overhead_ms", "shadow_overhead_percent"}
        self.assertTrue(required <= set(performance))
        self.assertEqual(performance["shadow_overhead_ms"], round(performance["shadow_duration_ms"] + performance["comparison_duration_ms"] + performance["diagnostic_write_duration_ms"], 6))

    def test_positive_14_consumer_hash_is_unchanged_without_execution(self) -> None:
        self.assertEqual(hashlib.sha256(CONSUMER.read_bytes()).hexdigest(), EXPECTED_CONSUMER_SHA256)

    def test_positive_15_schema_requires_authority_and_safety_fields(self) -> None:
        schema = json.loads((REPO / "SHADOW_CONSUMER_ADAPTER/schemas/d05-shadow-consumer-run.schema.json").read_text(encoding="utf-8"))
        self.assertTrue({"legacy_authoritative", "shadow_authoritative", "shadow_did_affect_output", "performance"} <= set(schema["required"]))

    def _known_failure(self, code: str, message: str = "failure"):
        def fail() -> dict:
            raise ShadowResolutionFailure(code, message)
        return run_adapter(shadow_enabled=True, legacy_executor=lambda observer: legacy(), observer=type("O", (), {"summary": lambda self: {"sets": {}}})(), shadow_worker=fail)

    def test_negative_01_invalid_registry_is_fail_closed(self) -> None:
        self.assertEqual(self._known_failure("REGISTRY_HASH_MISMATCH").diagnostic["shadow_status"], "SHADOW_FAIL_CLOSED")

    def test_negative_02_invalid_lock_is_fail_closed(self) -> None:
        self.assertEqual(self._known_failure("LOCK_HASH_MISMATCH").legacy_result.value, "LEGACY-X")

    def test_negative_03_missing_binding_is_fail_closed(self) -> None:
        self.assertEqual(self._known_failure("ROOT_BINDING_MISSING_OR_DUPLICATE").legacy_result.exit_code, 0)

    def test_negative_04_missing_restricted_local_is_fail_closed(self) -> None:
        self.assertEqual(self._known_failure("RESTRICTED_LOCAL_MISSING").diagnostic["comparison"]["status"], "SHADOW_RESOLUTION_FAILURE")

    def test_negative_05_shadow_hash_mismatch(self) -> None:
        left, right = matching_summaries()
        left["sets"]["triage_batch_paths"]["byte_hashes"] = {"a": "1"}
        right["sets"]["triage_batch_paths"]["byte_hashes"] = {"a": "2"}
        self.assertIn("BYTE_MISMATCH", {item["status"] for item in compare_runtime(left, right)["mismatches"]})

    def test_negative_06_shadow_member_mismatch(self) -> None:
        left, right = matching_summaries()
        right["sets"]["triage_batch_paths"]["members"] = ["a", "c"]
        statuses = {item["status"] for item in compare_runtime(left, right)["mismatches"]}
        self.assertTrue({"LEGACY_ONLY", "SHADOW_ONLY"} <= statuses)

    def test_negative_07_order_mismatch(self) -> None:
        left, right = matching_summaries()
        right["sets"]["triage_batch_paths"]["members"].reverse()
        self.assertIn("ORDER_MISMATCH", {item["status"] for item in compare_runtime(left, right)["mismatches"]})

    def test_negative_08_multiplicity_mismatch(self) -> None:
        left, right = matching_summaries()
        right["sets"]["triage_batch_paths"]["members"].append("b")
        self.assertIn("MULTIPLICITY_MISMATCH", {item["status"] for item in compare_runtime(left, right)["mismatches"]})

    def test_negative_09_adapter_exception_visible(self) -> None:
        result = run_adapter(shadow_enabled=True, legacy_executor=lambda observer: legacy(), observer=type("O", (), {"summary": lambda self: {"sets": {}}})(), shadow_worker=lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        self.assertEqual(result.diagnostic["shadow_status"], "SHADOW_INTERNAL_ERROR")
        self.assertEqual(result.diagnostic["adapter_errors"][0]["code"], "ADAPTER_INTERNAL_FAILURE")

    def test_negative_10_diagnostic_not_writable_preserves_legacy(self) -> None:
        warnings: list[str] = []
        result = run_adapter(shadow_enabled=False, legacy_executor=lambda observer: legacy(), diagnostic_path=Path("denied"), diagnostic_writer=lambda path, value: (_ for _ in ()).throw(PermissionError("denied")), warning_sink=warnings.append)
        self.assertEqual(result.legacy_result.value, "LEGACY-X")
        self.assertEqual(result.diagnostic["diagnostic_status"], "WRITE_FAILED")
        self.assertTrue(warnings)

    def test_negative_11_secret_and_signed_url_are_redacted(self) -> None:
        rendered = redact_sensitive("token=abc https://example.test/x?sig=secret-value")
        self.assertNotIn("abc", rendered)
        self.assertNotIn("secret-value", rendered)
        self.assertIn("<redacted>", rendered)

    def test_negative_12_shadow_worker_failure_preserves_legacy(self) -> None:
        result = self._known_failure("SHADOW_WORKER_FAILURE")
        self.assertEqual(result.legacy_result.output_hashes, {"out.json": "a" * 64})
        self.assertIs(result.diagnostic["shadow_did_affect_output"], False)

    def test_critical_shadow_exception_cannot_change_legacy_result(self) -> None:
        result = run_adapter(shadow_enabled=True, legacy_executor=lambda observer: legacy("X"), observer=type("O", (), {"summary": lambda self: {"sets": {}}})(), shadow_worker=lambda: (_ for _ in ()).throw(RuntimeError("shadow exploded")))
        self.assertEqual(result.legacy_result.value, "X")
        self.assertNotEqual(result.diagnostic["shadow_status"], "SHADOW_OK")
        self.assertIs(result.diagnostic["shadow_did_affect_output"], False)

    def test_support_diagnostic_writer_redacts_nested_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "diagnostic.json"
            write_diagnostic(path, {"token": "raw", "message": "password=hunter2"})
            rendered = path.read_text(encoding="utf-8")
        self.assertNotIn("raw", rendered)
        self.assertNotIn("hunter2", rendered)

    def test_support_binding_summary_never_persists_paths(self) -> None:
        self.assertEqual(safe_binding_summary({"ROOT": "C:/private"}), [{"storage_root_id": "ROOT", "status": "PROVIDED"}])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AdapterTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    tests = [test.id().rsplit(".", 1)[-1] for test in unittest.defaultTestLoader.loadTestsFromTestCase(AdapterTests)]
    failures = {test.id().rsplit(".", 1)[-1] for test, _ in result.failures + result.errors}
    payload = {
        "adapter_phase": "SCA1B1",
        "adapter_scope": "ISOLATED_FIXTURES_AND_FAKES_ONLY",
        "consumer_executed": False,
        "consumer_sha256": hashlib.sha256(CONSUMER.read_bytes()).hexdigest(),
        "functional_outputs_produced": False,
        "pipeline_executed": False,
        "result": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "positive": {"cases": [name for name in tests if name.startswith("test_positive_")], "planned_minimum": 12, "run": sum(name.startswith("test_positive_") for name in tests), "passed": sum(name.startswith("test_positive_") and name not in failures for name in tests)},
        "negative": {"cases": [name for name in tests if name.startswith("test_negative_")], "planned_minimum": 12, "run": sum(name.startswith("test_negative_") for name in tests), "passed": sum(name.startswith("test_negative_") and name not in failures for name in tests)},
        "critical_isolation": {"run": 1, "passed": int("test_critical_shadow_exception_cannot_change_legacy_result" not in failures)},
        "failures": sorted(failures),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_bytes((json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
