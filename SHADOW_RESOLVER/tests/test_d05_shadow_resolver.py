#!/usr/bin/env python3
"""Sixteen fail-closed integration cases for the D05 shadow resolver."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1]))

from resolve_selection import ResolutionError, build_resolved_selection, canonical_bytes  # noqa: E402


LOCK_HASH = "5d9f6d0ba4fa1895f70a139510b0d441d62e187eb63ad99de030820946c29f39"
REAL_REGISTRY = REPO / "ARTIFACT_REGISTRY" / "index.json"
REAL_LOCK = REPO / "DATASET_LOCKS" / "d05-historical-parity-v1.lock.json"
REAL_BINDINGS = {
    "CATALOG_69_ROOT": str((REPO / "LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1").resolve()),
    "D05_MANAGED_ROOT": str((REPO / "LEX_MACHINA_REFERENCIAS_V2" / "09_CATALOGO_EXPANSAO_200").resolve()),
}


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Fixture:
    def __init__(self, base: Path):
        self.base = base
        self.registry_dir = base / "registry"
        self.lock_dir = base / "locks"
        self.registry = self.registry_dir / "index.json"
        self.fragment = self.registry_dir / "datasets" / "d05.catalogo-expansao-200.json"
        self.lock = self.lock_dir / "d05-historical-parity-v1.lock.json"
        shutil.copytree(REPO / "ARTIFACT_REGISTRY" / "schemas", self.registry_dir / "schemas")
        shutil.copytree(REPO / "DATASET_LOCKS" / "schemas", self.lock_dir / "schemas")
        shutil.copy2(REAL_REGISTRY, self.registry)
        self.fragment.parent.mkdir(parents=True)
        shutil.copy2(REPO / "ARTIFACT_REGISTRY" / "datasets" / "d05.catalogo-expansao-200.json", self.fragment)
        shutil.copy2(REAL_LOCK, self.lock)

    def repin(self, fragment: Any | None = None, index: Any | None = None, lock: Any | None = None) -> str:
        fragment = read(self.fragment) if fragment is None else fragment
        index = read(self.registry) if index is None else index
        lock = read(self.lock) if lock is None else lock
        write(self.fragment, fragment)
        index["fragments"][0]["size"] = self.fragment.stat().st_size
        index["fragments"][0]["sha256"] = sha(self.fragment)
        lock["registry_fragments"][0]["sha256"] = index["fragments"][0]["sha256"]
        write(self.registry, index)
        lock["registry_index_sha256"] = sha(self.registry)
        write(self.lock, lock)
        return sha(self.lock)


def expect_failure(name: str, expected_codes: set[str], action: Callable[[], None]) -> dict[str, Any]:
    try:
        action()
    except ResolutionError as exc:
        if exc.code not in expected_codes:
            return {"name": name, "result": "FAIL", "observed": exc.code, "expected": sorted(expected_codes)}
        return {"name": name, "result": "PASS", "observed": exc.code}
    except OSError as exc:
        return {"name": name, "result": "FAIL", "observed": f"OS_ERROR:{exc}"}
    return {"name": name, "result": "FAIL", "observed": "UNEXPECTED_SUCCESS"}


def call(registry: Path = REAL_REGISTRY, lock: Path = REAL_LOCK, lock_hash: str = LOCK_HASH,
         bindings: dict[str, str] | None = None) -> None:
    build_resolved_selection(registry, lock, lock_hash, REAL_BINDINGS if bindings is None else bindings)


def first_artifact(fragment: dict[str, Any], lock: dict[str, Any]) -> dict[str, Any]:
    occurrence = lock["selection_sets"][0]["items"][0]["occurrence_id"]
    return next(item for item in fragment["artifacts"] if item["occurrence_id"] == occurrence)


def materialize_root(base: Path, fragment: dict[str, Any], *, omit: set[str] | None = None) -> Path:
    omit = omit or set()
    root = base / "d05-root"
    source_root = Path(REAL_BINDINGS["D05_MANAGED_ROOT"])
    for artifact in fragment["artifacts"]:
        if artifact["storage_root_id"] != "D05_MANAGED_ROOT" or artifact["occurrence_id"] in omit:
            continue
        source = source_root.joinpath(*artifact["relative_path"].split("/"))
        target = root.joinpath(*artifact["relative_path"].split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)
    return root


def run_suite() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="lex-r1b-tests-") as temporary:
        base = Path(temporary)

        fixture = Fixture(base / "registry-hash")
        index = read(fixture.registry)
        index["fragments"][0]["path"] = "datasets/changed.json"
        write(fixture.registry, index)
        results.append(expect_failure("registry_hash_mismatch", {"REGISTRY_HASH_MISMATCH"}, lambda: call(fixture.registry, fixture.lock, LOCK_HASH)))

        results.append(expect_failure("lock_hash_mismatch", {"LOCK_HASH_MISMATCH"}, lambda: call(lock_hash="0" * 64)))

        missing_binding = {"D05_MANAGED_ROOT": REAL_BINDINGS["D05_MANAGED_ROOT"]}
        results.append(expect_failure("root_binding_missing", {"ROOT_BINDING_MISSING_OR_DUPLICATE"}, lambda: call(bindings=missing_binding)))

        unknown_binding = dict(REAL_BINDINGS, UNKNOWN_ROOT=str(base))
        results.append(expect_failure("root_binding_unknown", {"ROOT_BINDING_MISSING_OR_DUPLICATE"}, lambda: call(bindings=unknown_binding)))

        fixture = Fixture(base / "missing-occurrence")
        lock = read(fixture.lock)
        lock["selection_sets"][0]["items"][0]["occurrence_id"] = "D05_MANAGED_ROOT:DOES_NOT_EXIST.json"
        write(fixture.lock, lock)
        results.append(expect_failure("occurrence_missing", {"OCCURRENCE_NOT_FOUND_OR_AMBIGUOUS"}, lambda: call(fixture.registry, fixture.lock, sha(fixture.lock))))

        fixture = Fixture(base / "ambiguous-occurrence")
        fragment, lock = read(fixture.fragment), read(fixture.lock)
        duplicate = dict(first_artifact(fragment, lock))
        duplicate["relative_path"] = "AMBIGUOUS_DUPLICATE.json"
        fragment["artifacts"].append(duplicate)
        expected = fixture.repin(fragment=fragment, lock=lock)
        results.append(expect_failure("occurrence_ambiguous", {"OCCURRENCE_NOT_FOUND_OR_AMBIGUOUS"}, lambda: call(fixture.registry, fixture.lock, expected)))

        fragment, lock = read(REPO / "ARTIFACT_REGISTRY" / "datasets" / "d05.catalogo-expansao-200.json"), read(REAL_LOCK)
        artifact = first_artifact(fragment, lock)
        empty_root = base / "empty-root"
        empty_root.mkdir()
        absent_bindings = dict(REAL_BINDINGS, D05_MANAGED_ROOT=str(empty_root))
        results.append(expect_failure("file_missing", {"FILE_MISSING"}, lambda: call(bindings=absent_bindings)))

        bad_root = base / "size-root"
        bad_target = bad_root.joinpath(*artifact["relative_path"].split("/"))
        bad_target.parent.mkdir(parents=True)
        bad_target.write_bytes(b"x")
        size_bindings = dict(REAL_BINDINGS, D05_MANAGED_ROOT=str(bad_root))
        results.append(expect_failure("size_mismatch", {"SIZE_MISMATCH"}, lambda: call(bindings=size_bindings)))

        hash_root = base / "hash-root"
        hash_target = hash_root.joinpath(*artifact["relative_path"].split("/"))
        hash_target.parent.mkdir(parents=True)
        source_bytes = Path(REAL_BINDINGS["D05_MANAGED_ROOT"]).joinpath(*artifact["relative_path"].split("/")).read_bytes()
        changed = bytearray(source_bytes)
        changed[0] ^= 1
        hash_target.write_bytes(changed)
        hash_bindings = dict(REAL_BINDINGS, D05_MANAGED_ROOT=str(hash_root))
        results.append(expect_failure("sha256_mismatch", {"SHA256_MISMATCH"}, lambda: call(bindings=hash_bindings)))

        fixture = Fixture(base / "traversal")
        fragment, lock = read(fixture.fragment), read(fixture.lock)
        first_artifact(fragment, lock)["relative_path"] = "../escape.json"
        expected = fixture.repin(fragment=fragment, lock=lock)
        results.append(expect_failure("path_traversal", {"UNSAFE_PATH"}, lambda: call(fixture.registry, fixture.lock, expected)))

        fixture = Fixture(base / "absolute")
        fragment, lock = read(fixture.fragment), read(fixture.lock)
        first_artifact(fragment, lock)["relative_path"] = "C:/absolute.json"
        expected = fixture.repin(fragment=fragment, lock=lock)
        results.append(expect_failure("absolute_relative_path", {"UNSAFE_PATH"}, lambda: call(fixture.registry, fixture.lock, expected)))

        link_root = base / "link-root"
        link_target = link_root.joinpath(*artifact["relative_path"].split("/"))
        link_target.parent.mkdir(parents=True)
        outside = base / "outside.json"
        outside.write_bytes(source_bytes)
        try:
            os.symlink(outside, link_target)
            link_bindings = dict(REAL_BINDINGS, D05_MANAGED_ROOT=str(link_root))
            results.append(expect_failure("junction_reparse_escape", {"SYMLINK_OR_JUNCTION_ESCAPE"}, lambda: call(bindings=link_bindings)))
        except OSError:
            link_target.parent.rmdir()
            outside_dir = base / "outside-directory"
            outside_dir.mkdir()
            (outside_dir / link_target.name).write_bytes(source_bytes)
            created = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link_target.parent), str(outside_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            if created.returncode == 0:
                link_bindings = dict(REAL_BINDINGS, D05_MANAGED_ROOT=str(link_root))
                results.append(expect_failure("junction_reparse_escape", {"SYMLINK_OR_JUNCTION_ESCAPE"}, lambda: call(bindings=link_bindings)))
                os.rmdir(link_target.parent)
            else:
                results.append({"name": "junction_reparse_escape", "result": "NOT_RUN", "reason": created.stderr.strip() or created.stdout.strip()})

        fixture = Fixture(base / "ordinal")
        lock = read(fixture.lock)
        lock["selection_sets"][0]["items"][1]["ordinal"] = 1
        write(fixture.lock, lock)
        results.append(expect_failure("ordinal_duplicate", {"ORDINAL_INVALID"}, lambda: call(fixture.registry, fixture.lock, sha(fixture.lock))))

        fixture = Fixture(base / "multiplicity")
        lock = read(fixture.lock)
        lock["selection_sets"][0]["items"].pop()
        write(fixture.lock, lock)
        results.append(expect_failure("multiplicity_reduced", {"MULTIPLICITY_CHANGED"}, lambda: call(fixture.registry, fixture.lock, sha(fixture.lock))))

        fixture = Fixture(base / "wildcard")
        lock = read(fixture.lock)
        lock["selection_sets"][0]["items"][0]["occurrence_id"] = "D05_MANAGED_ROOT:*.json"
        write(fixture.lock, lock)
        results.append(expect_failure("wildcard_or_fallback", {"IMPLICIT_DISCOVERY_REQUESTED"}, lambda: call(fixture.registry, fixture.lock, sha(fixture.lock))))

        restricted = set(lock_id for lock_id in read(REAL_LOCK)["constraints"]["restricted_local_occurrence_ids"])
        full_root = materialize_root(base / "restricted", fragment=read(REPO / "ARTIFACT_REGISTRY" / "datasets" / "d05.catalogo-expansao-200.json"), omit=restricted)
        restricted_bindings = dict(REAL_BINDINGS, D05_MANAGED_ROOT=str(full_root))
        results.append(expect_failure("restricted_local_missing", {"RESTRICTED_LOCAL_MISSING"}, lambda: call(bindings=restricted_bindings)))

    passed = sum(item["result"] == "PASS" for item in results)
    return {
        "expected_fail_closed": 16,
        "fail_closed_passed": passed,
        "result": "PASS" if passed == 16 else "FAIL",
        "tests": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_suite()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical_bytes(result))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
