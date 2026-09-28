#!/usr/bin/env python3
"""External opt-in runner for the non-authoritative D05 shadow comparison."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import runpy
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from SHADOW_CONSUMER_ADAPTER import ADAPTER_VERSION
from SHADOW_CONSUMER_ADAPTER.diagnostic import redact_sensitive, safe_binding_summary, write_diagnostic
from SHADOW_CONSUMER_ADAPTER.legacy_observer import LegacyObserver
from SHADOW_CONSUMER_ADAPTER.runtime_compare import compare_runtime, shadow_runtime_summary


CONSUMER_RELATIVE = Path("LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/compilar_catalogo.py")
OUTPUT_NAMES = ("CATALOGO_EXPANSAO_200.json", "CATALOGO_TOTAL_69_MAIS_APTAS.json")


class ShadowResolutionFailure(Exception):
    """Known fail-closed Shadow failure, isolated from the Legacy result."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class LegacyResult:
    exit_code: int
    stdout: str | None = None
    stderr: str | None = None
    output_hashes: dict[str, str] = field(default_factory=dict)
    value: Any = None


@dataclass(frozen=True)
class RunnerResult:
    legacy_result: LegacyResult
    diagnostic: dict[str, Any]
    diagnostic_written: bool
    warnings: tuple[str, ...]


def _milliseconds(start: float) -> float:
    return round((time.perf_counter() - start) * 1000.0, 6)


def _performance(legacy: float, shadow: float, comparison: float, diagnostic: float, total: float) -> dict[str, float | None]:
    overhead = shadow + comparison + diagnostic
    percent = round(overhead * 100.0 / legacy, 6) if legacy > 0 else None
    return {
        "legacy_duration_ms": legacy,
        "shadow_duration_ms": shadow,
        "shadow_resolution_duration_ms": shadow,
        "comparison_duration_ms": comparison,
        "diagnostic_write_duration_ms": diagnostic,
        "total_duration_ms": total,
        "adapter_wall_duration_ms": total,
        "shadow_overhead_ms": round(overhead, 6),
        "overhead_absolute_ms": round(overhead, 6),
        "shadow_overhead_percent": percent,
        "overhead_percent_vs_direct_legacy": percent,
    }


def run_adapter(
    *,
    shadow_enabled: bool,
    legacy_executor: Callable[[LegacyObserver | None], LegacyResult],
    observer: LegacyObserver | None = None,
    shadow_worker: Callable[[], dict[str, Any]] | None = None,
    diagnostic_path: Path | None = None,
    diagnostic_writer: Callable[[Path, dict[str, Any]], None] = write_diagnostic,
    warning_sink: Callable[[str], None] | None = None,
    bindings: dict[str, str] | None = None,
) -> RunnerResult:
    """Run Legacy first and isolate all Shadow/comparison/telemetry failures."""
    wall_start = time.perf_counter()
    legacy_start = time.perf_counter()
    legacy_result = legacy_executor(observer if shadow_enabled else None)
    legacy_ms = _milliseconds(legacy_start)
    shadow_ms = comparison_ms = diagnostic_ms = 0.0
    shadow_status = "SHADOW_DISABLED"
    shadow_summary: dict[str, Any] = {}
    comparison = {"status": "NOT_RUN", "dimensions": [], "mismatches": []}
    shadow_errors: list[dict[str, str]] = []
    adapter_errors: list[dict[str, str]] = []

    if shadow_enabled:
        shadow_start = time.perf_counter()
        try:
            if shadow_worker is None:
                raise ShadowResolutionFailure("SHADOW_WORKER_MISSING", "Shadow worker was not configured")
            shadow_summary = shadow_worker()
            shadow_status = "SHADOW_OK"
        except ShadowResolutionFailure as exc:
            shadow_status = "SHADOW_FAIL_CLOSED"
            shadow_errors.append({"code": exc.code, "message": redact_sensitive(exc)})
        except Exception as exc:  # explicit outer adapter boundary; never silent
            shadow_status = "SHADOW_INTERNAL_ERROR"
            adapter_errors.append({"code": "ADAPTER_INTERNAL_FAILURE", "message": redact_sensitive(exc)})
        shadow_ms = _milliseconds(shadow_start)

        comparison_start = time.perf_counter()
        try:
            legacy_summary = observer.summary() if observer else {"sets": {}}
            comparison = compare_runtime(legacy_summary, shadow_summary, shadow_status=shadow_status)
        except Exception as exc:  # comparison failure remains diagnostic-only
            shadow_status = "SHADOW_INTERNAL_ERROR"
            adapter_errors.append({"code": "ADAPTER_INTERNAL_FAILURE", "message": redact_sensitive(exc)})
            comparison = compare_runtime({}, {}, shadow_status="SHADOW_INTERNAL_ERROR")
        comparison_ms = _milliseconds(comparison_start)

    diagnostic = {
        "artifact_class": "DERIVED_DIAGNOSTIC",
        "authority": "NON_AUTHORITATIVE",
        "adapter_version": ADAPTER_VERSION,
        "consumer": CONSUMER_RELATIVE.as_posix(),
        "legacy_authoritative": True,
        "shadow_authoritative": False,
        "shadow_enabled": shadow_enabled,
        "legacy_status": "PASS" if legacy_result.exit_code == 0 else "FAIL",
        "legacy_exit_status": legacy_result.exit_code,
        "shadow_status": shadow_status,
        "legacy_runtime_summary": observer.summary() if shadow_enabled and observer else {},
        "shadow_runtime_summary": shadow_summary,
        "comparison": comparison,
        "mismatches": comparison.get("mismatches", []),
        "shadow_errors": shadow_errors,
        "adapter_errors": adapter_errors,
        "legacy_output_hashes": legacy_result.output_hashes,
        "shadow_did_affect_output": False,
        "bindings": safe_binding_summary(bindings or {}),
        "performance": {},
        "diagnostic_status": "NOT_REQUESTED" if diagnostic_path is None else "PENDING",
    }
    diagnostic["performance"] = _performance(legacy_ms, shadow_ms, comparison_ms, 0.0, _milliseconds(wall_start))

    warnings: list[str] = []
    written = False
    if diagnostic_path is not None:
        write_start = time.perf_counter()
        try:
            diagnostic_writer(diagnostic_path, diagnostic)
            diagnostic_ms = _milliseconds(write_start)
            diagnostic["diagnostic_status"] = "WRITTEN"
            diagnostic["performance"] = _performance(legacy_ms, shadow_ms, comparison_ms, diagnostic_ms, _milliseconds(wall_start))
            diagnostic_writer(diagnostic_path, diagnostic)
            written = True
        except Exception as exc:  # telemetry cannot become a Legacy failure
            warning = f"shadow diagnostic write failed: {redact_sensitive(exc)}"
            warnings.append(warning)
            diagnostic["diagnostic_status"] = "WRITE_FAILED"
            adapter_errors.append({"code": "DIAGNOSTIC_WRITE_FAILED", "message": redact_sensitive(exc)})
            if warning_sink:
                warning_sink(warning)
    diagnostic["performance"] = _performance(legacy_ms, shadow_ms, comparison_ms, diagnostic_ms, _milliseconds(wall_start))
    return RunnerResult(legacy_result=legacy_result, diagnostic=diagnostic, diagnostic_written=written, warnings=tuple(warnings))


def _hash_outputs(output_root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name in OUTPUT_NAMES:
        path = output_root / name
        if path.is_file():
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _legacy_subprocess(consumer: Path, legacy_args: list[str]) -> LegacyResult:
    completed = subprocess.run([sys.executable, str(consumer), *legacy_args], check=False)
    output_root = Path(legacy_args[0]) if legacy_args else consumer.parent
    return LegacyResult(exit_code=completed.returncode, output_hashes=_hash_outputs(output_root))


def _legacy_observed_in_process(consumer: Path, legacy_args: list[str], observer: LegacyObserver) -> LegacyResult:
    """Future SCA1B2 entrypoint; intentionally not called by this phase's tests."""
    old_argv = sys.argv[:]
    observer.install()
    try:
        sys.argv = [str(consumer), *legacy_args]
        try:
            runpy.run_path(str(consumer), run_name="__main__")
            exit_code = 0
        except SystemExit as exc:
            exit_code = int(exc.code or 0)
    finally:
        sys.argv = old_argv
    output_root = Path(legacy_args[0]) if legacy_args else consumer.parent
    return LegacyResult(exit_code=exit_code, output_hashes=_hash_outputs(output_root))


def _parse_bindings(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--bind requires ID=PATH")
        root_id, path = value.split("=", 1)
        if not root_id or not path or root_id in result:
            raise ValueError("--bind requires unique non-empty ID=PATH values")
        result[root_id] = path
    return result


def _real_shadow_worker(registry: Path, lock: Path, lock_sha256: str, bindings: dict[str, str]) -> dict[str, Any]:
    module = importlib.import_module("SHADOW_RESOLVER.resolve_selection")
    try:
        resolved, _runtime_only_bindings = module.build_resolved_selection(registry, lock, lock_sha256, bindings)
        return shadow_runtime_summary(resolved)
    except module.ResolutionError as exc:
        code = getattr(exc, "code", "SHADOW_RESOLUTION_FAILURE")
        raise ShadowResolutionFailure(code, redact_sensitive(exc)) from exc
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ShadowResolutionFailure("SHADOW_RESOLUTION_FAILURE", redact_sensitive(exc)) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shadow-compare", action="store_true", default=False)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--expected-lock-sha256")
    parser.add_argument("--bind", action="append", default=[])
    parser.add_argument("--legacy-output-root", type=Path)
    parser.add_argument("--diagnostic-output", type=Path)
    parser.add_argument("legacy_args", nargs="*")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    consumer = repo / CONSUMER_RELATIVE
    if not args.shadow_compare:
        return _legacy_subprocess(consumer, args.legacy_args).exit_code
    if not all((args.registry, args.lock, args.expected_lock_sha256, args.legacy_output_root)):
        build_parser().error("Shadow ON requires --registry, --lock, --expected-lock-sha256 and --legacy-output-root")
    bindings = _parse_bindings(args.bind)
    observer = LegacyObserver(args.legacy_output_root, consumer.parents[1])
    diagnostic_path = args.diagnostic_output or Path(tempfile.gettempdir()) / "D05_SHADOW_CONSUMER_RUN.json"
    result = run_adapter(
        shadow_enabled=True,
        legacy_executor=lambda active: _legacy_observed_in_process(consumer, args.legacy_args, active or observer),
        observer=observer,
        shadow_worker=lambda: _real_shadow_worker(args.registry, args.lock, args.expected_lock_sha256, bindings),
        diagnostic_path=diagnostic_path,
        warning_sink=lambda message: print(message, file=sys.stderr),
        bindings=bindings,
    )
    return result.legacy_result.exit_code


if __name__ == "__main__":
    sys.exit(main())
