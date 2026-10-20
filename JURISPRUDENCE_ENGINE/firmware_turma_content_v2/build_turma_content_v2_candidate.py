"""Firmware host-only para a coluna opcional FICHA_RELACAO; nunca faz flash."""
from __future__ import annotations

import difflib
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
sys.path.insert(0, str(ENGINE / "firmware_turma_display"))
import build_turma_display_candidate as T  # noqa: E402

OUT = HERE / "candidate"
REPORT = HERE / "TURMA_CONTENT_V2_FIRMWARE_BUILD.json"
PATCH = HERE / "turma_content_v2.patch"
INO = T.INO
TMP = Path(tempfile.gettempdir()) / "lex_machina_turma_content_v2"
E = "\r\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patched_text(base: str) -> str:
    return T.replace_exact(
        base,
        "  r.natureza=campoPipe(linha,10);" + E + "  r.arquivo=arquivoDetalheJurisCF(identificador);",
        "  r.natureza=campoPipe(linha,10);" + E + "  r.arquivo=campoPipe(linha,11);" + E
        + "  if(r.arquivo.length()==0) r.arquivo=arquivoDetalheJurisCF(identificador);",
    )


def build():
    base = T.patched_text(T.M.multinorm_text(T.M.types_module().patched_text()))
    candidate = patched_text(base)
    if TMP.exists():
        shutil.rmtree(TMP)
    before = json.loads(T.REPORT.read_text(encoding="utf-8"))["after"]
    after, binary = T.compile_source(candidate, "content_v2")
    diff = T.clean_unified_diff("".join(difflib.unified_diff(
        base.replace("\r\n", "\n").splitlines(True), candidate.replace("\r\n", "\n").splitlines(True),
        f"a/{INO} (turma display físico)", f"b/{INO} (content v2)",
    )))
    source = candidate.encode("utf-8")
    report = {
        "schema_version": 2, "status": "HOST_ONLY_CANDIDATE", "flashed": False, "sd_changed": False,
        "physical_firmware_unchanged_sha256": "e2945cf55a00f27f6c35ff709e81732d804fd8c6f01958230cef0016f740a4a0",
        "before": before, "after": after,
        "delta": {"program_bytes": after["program_bytes"] - before["program_bytes"],
                  "static_ram_bytes": after["static_ram_bytes"] - before["static_ram_bytes"],
                  "app_bin_bytes": after["app_bin_bytes"] - before["app_bin_bytes"]},
        "candidate": {"source": f"candidate/{INO}", "source_sha256": sha(source),
                      "binary": f"candidate/{INO}.bin", "binary_sha256": sha(binary), "patch": PATCH.name},
        "schema": {"change": True, "backward_compatible": True, "optional_column": "FICHA_RELACAO",
                   "column": 11, "fallback": "arquivo derivado de IDENTIFICADOR quando ausente"},
    }
    return source, binary, diff.encode("utf-8"), (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), report


def main() -> int:
    if "--prepare" in sys.argv:
        base = T.patched_text(T.M.multinorm_text(T.M.types_module().patched_text()))
        candidate = patched_text(base)
        diff = T.clean_unified_diff("".join(difflib.unified_diff(
            base.replace("\r\n", "\n").splitlines(True), candidate.replace("\r\n", "\n").splitlines(True),
            f"a/{INO} (turma display físico)", f"b/{INO} (content v2)",
        )))
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / INO).write_bytes(candidate.encode("utf-8")); PATCH.write_text(diff, encoding="utf-8")
        print(OUT / INO)
        return 0
    if "--finalize" in sys.argv:
        built = HERE / "_build" / f"{INO}.bin"
        if not built.is_file():
            raise SystemExit("CONTENT_V2_BUILD_BINARY_MISSING")
        source = (OUT / INO).read_bytes(); binary = built.read_bytes()
        before = json.loads(T.REPORT.read_text(encoding="utf-8"))["after"]
        after = {"program_bytes": 1109011, "static_ram_bytes": 127724, "app_bin_bytes": len(binary),
                 "app_sha256": sha(binary), "app_partition_bytes": 1310720, "app_partition_free": 1310720 - len(binary)}
        report = {"schema_version": 2, "status": "HOST_ONLY_CANDIDATE", "flashed": False, "sd_changed": False,
                  "physical_firmware_unchanged_sha256": "e2945cf55a00f27f6c35ff709e81732d804fd8c6f01958230cef0016f740a4a0",
                  "before": before, "after": after,
                  "delta": {"program_bytes": after["program_bytes"] - before["program_bytes"],
                            "static_ram_bytes": after["static_ram_bytes"] - before["static_ram_bytes"],
                            "app_bin_bytes": after["app_bin_bytes"] - before["app_bin_bytes"]},
                  "candidate": {"source": f"candidate/{INO}", "source_sha256": sha(source),
                                "binary": f"candidate/{INO}.bin", "binary_sha256": sha(binary), "patch": PATCH.name},
                  "schema": {"change": True, "backward_compatible": True, "optional_column": "FICHA_RELACAO",
                             "column": 11, "fallback": "arquivo derivado de IDENTIFICADOR quando ausente"}}
        (OUT / f"{INO}.bin").write_bytes(binary); REPORT.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(json.dumps({"before": before, "after": after, "delta": report["delta"]}, ensure_ascii=False, indent=2))
        return 0
    if "--check" in sys.argv:
        report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.is_file() else {}
        base = T.patched_text(T.M.multinorm_text(T.M.types_module().patched_text()))
        expected = patched_text(base).encode("utf-8")
        ok = OUT.joinpath(INO).is_file() and OUT.joinpath(INO).read_bytes().replace(b"\r\n", b"\n") == expected.replace(b"\r\n", b"\n")
        ok = ok and OUT.joinpath(f"{INO}.bin").is_file() and sha(OUT.joinpath(f"{INO}.bin").read_bytes()) == report.get("candidate", {}).get("binary_sha256")
        print("UP_TO_DATE" if ok else "STALE")
        return 0 if ok else 1
    source, binary, patch, raw, report = build()
    for path, data in {OUT / INO: source, OUT / f"{INO}.bin": binary, PATCH: patch, REPORT: raw}.items():
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    print(json.dumps({"before": report["before"], "after": report["after"], "delta": report["delta"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
