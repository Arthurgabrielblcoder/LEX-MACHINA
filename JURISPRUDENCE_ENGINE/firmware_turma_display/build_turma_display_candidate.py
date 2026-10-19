"""Gera e compila o firmware host-only do gate de display de acórdãos de Turma.

Base: firmware multinorma aprovado em fonte (tipos genéricos + patch multinorma).
Saída: fonte, binário, patch e relatório em firmware_turma_display/. Nunca acessa serial,
SD ou esptool e nunca faz flash.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
ROOT = ENGINE.parent
sys.path.insert(0, str(ENGINE / "firmware_multinorm"))
import build_multinorm_prototype as M  # noqa: E402


OUT = HERE / "candidate"
REPORT = HERE / "TURMA_DISPLAY_FIRMWARE_BUILD.json"
PATCH_FILE = HERE / "turma_display.patch"
INO = "LEX_MACHINA_DEVICE_V1_CANDIDATE.ino"
TMP = Path(tempfile.gettempdir()) / "lex_machina_turma_display"
E = "\r\n"
TYPES = M.types_module()
if not TYPES.AC.is_file():
    TYPES.AC = Path.home() / "AppData/Local/Programs/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_unified_diff(value: str) -> str:
    """Remove whitespace-only payload from added blank lines without changing source bytes."""
    return "".join("\n" if not line.strip() else line for line in value.splitlines(True))


def replace_exact(text: str, anchor: str, replacement: str) -> str:
    if text.count(anchor) != 1:
        raise SystemExit(f"ANCHOR_COUNT {text.count(anchor)} != 1: {anchor[:80]!r}")
    return text.replace(anchor, replacement)


def patched_text(base: str) -> str:
    text = base
    text = replace_exact(
        text,
        '{"ext","Ext"}',
        '{"ext","Ext"},{"resp","REsp"},{"aresp","AREsp"},{"eresp","EREsp"},{"earesp","EAREsp"}',
    )
    text = replace_exact(
        text,
        "  String status;" + E + "  String arquivo;",
        "  String status;" + E + "  String orgao;" + E + "  String dataJulgamento;" + E + "  String natureza;" + E + "  String arquivo;",
    )
    text = replace_exact(
        text,
        "String rotuloTipoJurisprudencia(const RelacaoJuridica &r);" + E,
        "String rotuloTipoJurisprudencia(const RelacaoJuridica &r);" + E
        + "String rotuloListaJurisprudencia(const RelacaoJuridica &r);" + E,
    )
    helpers = E.join([
        "// Display de Turma: identidade jurídica compacta, derivada apenas dos metadados oficiais opcionais do IDX.",
        "String formatarNumeroProcesso(String numero)", "{",
        "  String digitos=\"\";",
        "  for(size_t i=0;i<numero.length();i++){ if(numero[i]<'0' || numero[i]>'9') return numero; digitos+=numero[i]; }",
        "  String saida=\"\"; int primeiro=digitos.length()%3; if(primeiro==0) primeiro=3;",
        "  for(int i=0;i<(int)digitos.length();i++){ if(i>0 && (i-primeiro)%3==0) saida+=\".\"; saida+=digitos[i]; }",
        "  return saida;", "}", "",
        "String orgaoTurmaCompacto(const String &orgao)", "{",
        "  if(orgao==\"TERCEIRA TURMA\") return \"3ª T.\";",
        "  if(orgao==\"QUARTA TURMA\") return \"4ª T.\";",
        "  return \"\";", "}", "",
        "String rotuloListaJurisprudencia(const RelacaoJuridica &r)", "{",
        "  if(r.natureza!=\"PERSUASIVE_NON_BINDING\") return rotuloTipoJurisprudencia(r);",
        "  String tipo=r.tipo; tipo.toLowerCase(); const char *classe=rotuloClasseJuris(tipo);",
        "  String numero=formatarNumeroProcesso(r.numero); String turma=orgaoTurmaCompacto(r.orgao);",
        "  if(!classe || turma.length()==0) return r.tribunal+\" · Acórdão \"+numero;",
        "  return r.tribunal+\" \"+turma+\" · \"+String(classe)+\" \"+numero;",
        "}", "",
    ]) + E
    anchor = "String arquivoDetalheJurisCF(String identificador)" + E
    text = replace_exact(text, anchor, helpers + anchor)
    text = replace_exact(
        text,
        "  r.status=status;" + E + "  r.arquivo=arquivoDetalheJurisCF(identificador);",
        "  r.status=status;" + E + "  r.orgao=campoPipe(linha,8);" + E + "  r.dataJulgamento=campoPipe(linha,9);" + E
        + "  r.natureza=campoPipe(linha,10);" + E + "  r.arquivo=arquivoDetalheJurisCF(identificador);",
    )
    text = replace_exact(
        text,
        "    relacoesArtigo[i].status=\"\";" + E + "    relacoesArtigo[i].arquivo=\"\";",
        "    relacoesArtigo[i].status=\"\";" + E + "    relacoesArtigo[i].orgao=\"\";" + E
        + "    relacoesArtigo[i].dataJulgamento=\"\";" + E + "    relacoesArtigo[i].natureza=\"\";" + E
        + "    relacoesArtigo[i].arquivo=\"\";",
    )
    text = replace_exact(text, "    rotulo+=rotuloTipoJurisprudencia(r);" + E, "    rotulo+=rotuloListaJurisprudencia(r);" + E)
    return text


def compile_source(text: str, name: str):
    if not TYPES.AC.is_file():
        raise SystemExit(f"ARDUINO_CLI_NOT_FOUND {TYPES.AC}")
    sketch = TYPES.assemble(TMP / f"src_{name}")
    (sketch / INO).write_bytes(text.encode("utf-8"))
    info, binary = TYPES.compile_sketch(sketch, TMP / f"build_{name}")
    return info, binary


def build():
    base = M.multinorm_text(M.types_module().patched_text())
    candidate = patched_text(base)
    if TMP.exists():
        shutil.rmtree(TMP)
    before = json.loads((ENGINE / "firmware_multinorm/MULTINORM_PROTOTYPE_BUILD.json").read_text(encoding="utf-8"))["builds"]["multinorm"]
    after, binary = compile_source(candidate, "turma_after")
    diff = clean_unified_diff("".join(
        difflib.unified_diff(
            base.replace("\r\n", "\n").splitlines(True),
            candidate.replace("\r\n", "\n").splitlines(True),
            f"a/{INO} (multinorma)",
            f"b/{INO} (turma display)",
        )
    ))
    source = candidate.encode("utf-8")
    report = {
        "schema_version": 1,
        "status": "HOST_ONLY_CANDIDATE",
        "flashed": False,
        "sd_changed": False,
        "source_base": "JURISPRUDENCE_ENGINE/firmware_multinorm (tipos genéricos + multinorma)",
        "toolchain": {
            "arduino_cli": str(TYPES.AC),
            "core": "esp32:esp32 3.3.11",
            "fqbn": TYPES.FQBN,
            "build_property": TYPES.FLAGS,
            "physical_hardware": "ESP32-S3 Dev Module; PSRAM 8 MB; flash física 16 MB",
        },
        "before": before,
        "after": after,
        "delta": {
            "program_bytes": after["program_bytes"] - before["program_bytes"],
            "static_ram_bytes": after["static_ram_bytes"] - before["static_ram_bytes"],
            "app_bin_bytes": after["app_bin_bytes"] - before["app_bin_bytes"],
        },
        "candidate": {
            "source": f"candidate/{INO}",
            "source_sha256": sha(source),
            "binary": f"candidate/{INO}.bin",
            "binary_sha256": sha(binary),
            "patch": "turma_display.patch",
        },
        "schema": {
            "change": True,
            "backward_compatible": True,
            "optional_columns": ["ORGAO", "DATA", "NATUREZA"],
            "legacy_rows": "campos ausentes resultam em String vazia e preservam o rótulo legado",
        },
        "display": {
            "preferred": "STJ 3ª T. · REsp 2.145.365",
            "safe_fallback": "STJ · Acórdão 2.145.365",
            "metadata_internal_tokens_exposed": [],
        },
    }
    return source, binary, diff.encode("utf-8"), (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), report


def main() -> int:
    if "--check" in sys.argv:
        base = M.multinorm_text(M.types_module().patched_text())
        candidate = patched_text(base)
        diff = clean_unified_diff("".join(difflib.unified_diff(base.replace("\r\n", "\n").splitlines(True),
                                                               candidate.replace("\r\n", "\n").splitlines(True),
                                                               f"a/{INO} (multinorma)", f"b/{INO} (turma display)")))
        report = load_report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.is_file() else {}
        ok = (OUT.joinpath(INO).is_file() and OUT.joinpath(INO).read_bytes().replace(b"\r\n", b"\n") == candidate.encode("utf-8").replace(b"\r\n", b"\n")
              and PATCH_FILE.is_file() and PATCH_FILE.read_bytes().replace(b"\r\n", b"\n") == diff.encode("utf-8").replace(b"\r\n", b"\n")
              and OUT.joinpath(f"{INO}.bin").is_file()
              and sha(OUT.joinpath(f"{INO}.bin").read_bytes()) == report.get("candidate", {}).get("binary_sha256"))
        print("UP_TO_DATE" if ok else "STALE")
        return 0 if ok else 1
    source, binary, patch, report_raw, report = build()
    files = {
        OUT / INO: source,
        OUT / f"{INO}.bin": binary,
        PATCH_FILE: patch,
        REPORT: report_raw,
    }
    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps({"before": report["before"], "after": report["after"], "delta": report["delta"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
