from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import struct
import sys

CORPUS_NAME = "99_LEXDATA_ESP32_OFICIAL_V4_TESTE"
BIN_DIR_NAME = "BIN_V1"
BUILD_DIR = Path("saida") / "INDICES_BINARIOS_V1_BUILD"
EXPECTED_NORMS = 72
EXPECTED_JURIS = 80

MAGIC = b"LEXART01"
VERSION = 1
HEADER = struct.Struct("<8sHHI")
RECORD = struct.Struct("<I4sII")
HEADER_SIZE = HEADER.size
RECORD_SIZE = RECORD.size

ARTICLE_KEY_RE = re.compile(r"^(\d{1,10})(?:-([A-Za-z]{1,4}))?$")
ARTICLE_START_RE = re.compile(
    r"^Art(?:igo)?\s*\.?\s*(\d{1,3}(?:\.\d{3})+|\d{1,10})"
    r"\s*(?:º|°|o)?(?:\s*-\s*([A-Za-z]{1,4}))?",
    re.IGNORECASE,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_idx(path: Path) -> list[list[str]]:
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.split("|"))
    return out


def parse_article(article: str) -> tuple[int, str]:
    m = ARTICLE_KEY_RE.fullmatch(article.strip().upper())
    if not m:
        raise ValueError(f"Artigo não suportado: {article!r}")
    number = int(m.group(1))
    suffix = (m.group(2) or "").upper()
    if not (0 <= number <= 0xFFFFFFFF):
        raise ValueError(f"Número fora de uint32: {article}")
    if len(suffix.encode("ascii")) > 4:
        raise ValueError(f"Sufixo > 4 bytes: {article}")
    return number, suffix


def canonical_article(number: int, suffix: str) -> str:
    return str(number) + (("-" + suffix.upper()) if suffix else "")


def encode_suffix(suffix: str) -> bytes:
    return suffix.upper().encode("ascii").ljust(4, b"\x00")


def decode_suffix(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("ascii").upper()


def article_from_text_start(text: str) -> str | None:
    m = ARTICLE_START_RE.match(text.lstrip())
    if not m:
        return None
    number = int(m.group(1).replace(".", ""))
    return canonical_article(number, (m.group(2) or "").upper())


def load_corpus(sd_root: Path):
    corpus = sd_root / CORPUS_NAME
    if not corpus.is_dir():
        raise FileNotFoundError(f"Corpus não encontrado: {corpus}")

    for name in ("META.JSON", "NORMAS.IDX", "ARTIGOS.IDX", "JURIS.IDX"):
        if not (corpus / name).is_file():
            raise FileNotFoundError(f"Arquivo obrigatório ausente: {corpus / name}")

    meta = load_json(corpus / "META.JSON")
    if meta.get("formato") != "OFICIAL4":
        raise RuntimeError(f"Corpus não é OFICIAL4: {meta.get('formato')!r}")
    if int(meta.get("normas_ok", -1)) != EXPECTED_NORMS:
        raise RuntimeError("META.JSON não registra 72 normas.")
    if int(meta.get("juris_ok", -1)) != EXPECTED_JURIS:
        raise RuntimeError("META.JSON não registra 80 jurisprudências.")
    if int(meta.get("erros", -1)) != 0:
        raise RuntimeError("META.JSON registra erros.")

    norm_rows = read_idx(corpus / "NORMAS.IDX")
    if len(norm_rows) != EXPECTED_NORMS:
        raise RuntimeError(f"NORMAS.IDX possui {len(norm_rows)} normas.")

    norms = {}
    for row in norm_rows:
        if len(row) != 9:
            raise RuntimeError(f"Linha inválida em NORMAS.IDX: {row}")
        ident, sigla, prioridade, ramo, nome, runtime, count, byte_count, metodo = row
        if ident in norms:
            raise RuntimeError(f"ID duplicado em NORMAS.IDX: {ident}")
        norms[ident] = {
            "id": ident,
            "nome": nome,
            "runtime": runtime,
            "count": int(count),
            "bytes": int(byte_count),
            "metodo": metodo,
        }

    by_norm = {ident: [] for ident in norms}
    art_rows = read_idx(corpus / "ARTIGOS.IDX")
    for row in art_rows:
        if len(row) != 4:
            raise RuntimeError(f"Linha inválida em ARTIGOS.IDX: {row}")
        ident, article, offset, size = row
        if ident not in by_norm:
            raise RuntimeError(f"ARTIGOS.IDX refere norma inexistente: {ident}")
        number, suffix = parse_article(article)
        off = int(offset)
        sz = int(size)
        if not (0 <= off <= 0xFFFFFFFF):
            raise RuntimeError(f"{ident} {article}: offset fora de uint32")
        if not (1 <= sz <= 0xFFFFFFFF):
            raise RuntimeError(f"{ident} {article}: tamanho fora de uint32")
        by_norm[ident].append({
            "article": canonical_article(number, suffix),
            "number": number,
            "suffix": suffix,
            "offset": off,
            "size": sz,
        })

    return corpus, meta, norms, by_norm, len(art_rows)


def validate_source(corpus: Path, norms: dict, by_norm: dict):
    errors = []
    reopened = 0

    for ident in sorted(norms):
        law = corpus / "LEIS" / f"{ident}.TXT"
        if not law.is_file():
            errors.append(f"{ident}: arquivo LEIS ausente.")
            continue
        real_size = law.stat().st_size
        if real_size != norms[ident]["bytes"]:
            errors.append(f"{ident}: tamanho do TXT diverge de NORMAS.IDX.")

        records = by_norm[ident]
        if len(records) != norms[ident]["count"]:
            errors.append(f"{ident}: contagem ARTIGOS.IDX != NORMAS.IDX.")

        labels = [r["article"] for r in records]
        if len(labels) != len(set(labels)):
            errors.append(f"{ident}: artigo duplicado em ARTIGOS.IDX.")

        with law.open("rb") as f:
            for r in records:
                if r["offset"] + r["size"] > real_size:
                    errors.append(f"{ident} Art. {r['article']}: faixa inválida.")
                    continue
                f.seek(r["offset"])
                raw = f.read(r["size"])
                if len(raw) != r["size"]:
                    errors.append(f"{ident} Art. {r['article']}: leitura curta.")
                    continue
                try:
                    text = raw.decode("utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    errors.append(f"{ident} Art. {r['article']}: UTF-8 inválido: {exc}")
                    continue
                found = article_from_text_start(text)
                if found != r["article"]:
                    errors.append(
                        f"{ident}: índice diz Art. {r['article']}, offset lê Art. {found}."
                    )
                    continue
                reopened += 1

    return errors, reopened


def write_bin(path: Path, records: list[dict]):
    ordered = sorted(records, key=lambda r: (r["number"], r["suffix"].encode("ascii")))
    seen = set()
    for r in ordered:
        key = (r["number"], r["suffix"])
        if key in seen:
            raise RuntimeError(f"{path.name}: chave duplicada {r['article']}")
        seen.add(key)

    with path.open("wb") as f:
        f.write(HEADER.pack(MAGIC, VERSION, RECORD_SIZE, len(ordered)))
        for r in ordered:
            f.write(RECORD.pack(
                r["number"],
                encode_suffix(r["suffix"]),
                r["offset"],
                r["size"],
            ))

    expected = HEADER_SIZE + len(ordered) * RECORD_SIZE
    if path.stat().st_size != expected:
        raise RuntimeError(f"{path.name}: tamanho inválido após escrita.")
    return ordered


def read_header(f):
    raw = f.read(HEADER_SIZE)
    if len(raw) != HEADER_SIZE:
        raise RuntimeError("Cabeçalho truncado.")
    magic, version, rec_size, count = HEADER.unpack(raw)
    if magic != MAGIC:
        raise RuntimeError(f"Magic inválido: {magic!r}")
    if version != VERSION:
        raise RuntimeError(f"Versão inválida: {version}")
    if rec_size != RECORD_SIZE:
        raise RuntimeError(f"record_size inválido: {rec_size}")
    return count


def read_record(f, index: int):
    f.seek(HEADER_SIZE + index * RECORD_SIZE)
    raw = f.read(RECORD_SIZE)
    if len(raw) != RECORD_SIZE:
        raise RuntimeError(f"Registro {index} truncado.")
    number, suffix_raw, offset, size = RECORD.unpack(raw)
    suffix = decode_suffix(suffix_raw)
    return {
        "number": number,
        "suffix": suffix,
        "article": canonical_article(number, suffix),
        "offset": offset,
        "size": size,
    }


def compare_key(a_num, a_suffix, b_num, b_suffix):
    if a_num < b_num:
        return -1
    if a_num > b_num:
        return 1
    a = a_suffix.encode("ascii")
    b = b_suffix.encode("ascii")
    return -1 if a < b else (1 if a > b else 0)


def binary_find(path: Path, number: int, suffix: str):
    steps = 0
    with path.open("rb") as f:
        count = read_header(f)
        low, high = 0, count - 1
        while low <= high:
            steps += 1
            mid = (low + high) // 2
            rec = read_record(f, mid)
            cmpv = compare_key(rec["number"], rec["suffix"], number, suffix)
            if cmpv == 0:
                return rec, steps
            if cmpv < 0:
                low = mid + 1
            else:
                high = mid - 1
    return None, steps


def validate_bin(path: Path, source_records: list[dict]):
    errors = []
    validated = 0
    max_steps = 0

    with path.open("rb") as f:
        count = read_header(f)
    if count != len(source_records):
        errors.append(f"{path.name}: count={count}, esperado={len(source_records)}")

    for src in source_records:
        found, steps = binary_find(path, src["number"], src["suffix"])
        max_steps = max(max_steps, steps)
        if found is None:
            errors.append(f"{path.name}: Art. {src['article']} não encontrado.")
            continue
        if found["offset"] != src["offset"] or found["size"] != src["size"]:
            errors.append(f"{path.name}: Art. {src['article']} offset/tamanho divergentes.")
            continue
        if found["article"] != src["article"]:
            errors.append(f"{path.name}: chave divergente em Art. {src['article']}.")
            continue
        validated += 1

    return errors, validated, max_steps


def build_all(norms: dict, by_norm: dict):
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    errors = []
    details = []
    manifest = [
        "#LEXMACHINA|NORMAS_BIN|1",
        "#ID|CAMINHO|REGISTROS|BYTES|RECORD_SIZE|MAX_STEPS|SHA256",
    ]
    total = 0
    validated_total = 0

    largest = {"id": "", "records": -1, "bytes": -1, "steps": 0}

    for ident in sorted(norms):
        path = BUILD_DIR / f"{ident}.BIN"
        try:
            ordered = write_bin(path, by_norm[ident])
            bin_errors, validated, max_steps = validate_bin(path, ordered)
            errors.extend(f"{ident}: {e}" for e in bin_errors)
        except Exception as exc:
            errors.append(f"{ident}: falha ao gerar/validar BIN: {exc}")
            continue

        count = len(ordered)
        size = path.stat().st_size
        digest = sha256_file(path)
        total += count
        validated_total += validated

        if count > largest["records"]:
            largest = {"id": ident, "records": count, "bytes": size, "steps": max_steps}

        runtime = f"/{CORPUS_NAME}/{BIN_DIR_NAME}/{ident}.BIN"
        manifest.append(
            "|".join([
                ident,
                runtime,
                str(count),
                str(size),
                str(RECORD_SIZE),
                str(max_steps),
                digest,
            ])
        )
        details.append({
            "id": ident,
            "records": count,
            "bytes": size,
            "max_steps": max_steps,
            "sha256": digest,
        })

    (BUILD_DIR / "NORMAS_BIN.IDX").write_text(
        "\n".join(manifest) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    approved = (
        len(details) == EXPECTED_NORMS
        and total == sum(len(v) for v in by_norm.values())
        and validated_total == total
        and not errors
    )

    meta = {
        "lex_machina": True,
        "formato": "ARTBIN1",
        "magic_ascii": MAGIC.decode("ascii"),
        "version": VERSION,
        "endianness": "little",
        "header_size": HEADER_SIZE,
        "record_size": RECORD_SIZE,
        "record_struct": "<I4sII",
        "normas": len(details),
        "registros": total,
        "registros_validados_por_busca_binaria": validated_total,
        "erros": len(errors),
        "maior_indice": largest,
    }
    (BUILD_DIR / "META.JSON").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "LEX MACHINA",
        "ÍNDICES BINÁRIOS V1 PARA ESP32",
        "=" * 88,
        "",
        f"NORMAS: {len(details)}/{EXPECTED_NORMS}",
        f"REGISTROS BINÁRIOS: {total}",
        f"REGISTROS VALIDADOS POR BUSCA BINÁRIA: {validated_total}/{total}",
        f"HEADER_SIZE: {HEADER_SIZE} bytes",
        f"RECORD_SIZE: {RECORD_SIZE} bytes",
        f"ERROS: {len(errors)}",
        "ALERTAS: 0",
        "",
        "RESULTADO: " + ("APROVADO" if approved else "REPROVADO"),
        "",
        "=" * 88,
        "DIAGNÓSTICO POR NORMA",
        "=" * 88,
        "",
    ]
    for d in details:
        lines.append(
            f"[OK] {d['id']} | registros={d['records']} | bytes={d['bytes']} "
            f"| max_steps={d['max_steps']} | sha256={d['sha256']}"
        )
    lines += [
        "",
        "=" * 88,
        "MAIOR ÍNDICE",
        "=" * 88,
        "",
        f"ID: {largest['id']}",
        f"REGISTROS: {largest['records']}",
        f"BYTES: {largest['bytes']}",
        f"MÁXIMO DE PASSOS DE BUSCA BINÁRIA: {largest['steps']}",
        "",
    ]
    if errors:
        lines += ["=" * 88, "ERROS", "=" * 88, ""]
        lines += ["- " + e for e in errors]
        lines.append("")
    lines += ["=" * 88, "CONCLUSÃO", "=" * 88, ""]
    if approved:
        lines += [
            "APROVADO: os 72 índices binários reproduzem integralmente o ARTIGOS.IDX auditado.",
            "Cada artigo foi localizado novamente por busca binária e teve offset/tamanho conferidos.",
        ]
    else:
        lines.append("REPROVADO: BIN_V1 não deve ser publicado no microSD.")

    (BUILD_DIR / "RELATORIO_INDICES_BINARIOS.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return {
        "approved": approved,
        "errors": errors,
        "details": details,
        "total": total,
        "validated": validated_total,
        "largest": largest,
    }


def verify_copy(source: Path, dest: Path):
    source_files = sorted(p.relative_to(source) for p in source.rglob("*") if p.is_file())
    dest_files = sorted(p.relative_to(dest) for p in dest.rglob("*") if p.is_file())
    if source_files != dest_files:
        raise RuntimeError("Lista de arquivos divergiu após cópia.")
    for rel in source_files:
        a = source / rel
        b = dest / rel
        if a.stat().st_size != b.stat().st_size:
            raise RuntimeError(f"Tamanho divergiu após cópia: {rel}")
        if sha256_file(a) != sha256_file(b):
            raise RuntimeError(f"SHA-256 divergiu após cópia: {rel}")


def publish(corpus: Path) -> Path:
    dest = corpus / BIN_DIR_NAME
    temp = corpus / (BIN_DIR_NAME + "_NOVO")
    prev = corpus / (BIN_DIR_NAME + "_ANTERIOR")

    if temp.exists():
        shutil.rmtree(temp)
    shutil.copytree(BUILD_DIR, temp)
    verify_copy(BUILD_DIR, temp)

    if prev.exists():
        shutil.rmtree(prev)
    if dest.exists():
        os.replace(dest, prev)

    try:
        os.replace(temp, dest)
    except Exception:
        if prev.exists() and not dest.exists():
            os.replace(prev, dest)
        raise

    verify_copy(BUILD_DIR, dest)
    if prev.exists():
        shutil.rmtree(prev, ignore_errors=True)
    return dest


def main():
    parser = argparse.ArgumentParser(
        description="LEX MACHINA - gera índices binários V1 a partir do corpus V4 auditado."
    )
    parser.add_argument("origem", help="Raiz do microSD. Ex.: D:\\")
    args = parser.parse_args()

    sd_root = Path(args.origem)
    if not sd_root.is_dir():
        raise FileNotFoundError(f"Raiz do microSD inválida: {sd_root}")

    print()
    print("LEX MACHINA")
    print("GERADOR DE ÍNDICES BINÁRIOS V1")
    print("=" * 72)
    print(f"MicroSD: {sd_root}")
    print("Os arquivos jurídicos NÃO serão alterados.")
    print()

    corpus, meta, norms, by_norm, total_articles = load_corpus(sd_root)
    print(f"Corpus: {corpus}")
    print(f"Normas: {len(norms)}")
    print(f"Artigos em ARTIGOS.IDX: {total_articles}")
    print()

    print("[1/3] Reabrindo todos os artigos do corpus...")
    source_errors, source_reopened = validate_source(corpus, norms, by_norm)
    print(f"Artigos reabertos: {source_reopened}/{total_articles}")
    if source_errors:
        print("FALHA: corpus fonte não passou na revalidação.")
        for e in source_errors[:30]:
            print(" - " + e)
        print("Nada foi publicado no microSD.")
        return

    print()
    print("[2/3] Gerando e validando 72 índices binários...")
    result = build_all(norms, by_norm)
    print(f"Normas binárias: {len(result['details'])}/{EXPECTED_NORMS}")
    print(f"Registros: {result['validated']}/{result['total']}")
    print(f"Erros: {len(result['errors'])}")
    print("Alertas: 0")
    if not result["approved"]:
        print("⚠ BUILD BINÁRIO REPROVADO")
        print(f"Diagnóstico: {BUILD_DIR}")
        print("Nada foi publicado no microSD.")
        return

    print()
    print("[3/3] Publicando BIN_V1 no microSD...")
    dest = publish(corpus)

    print()
    print("=" * 72)
    print("✓ ÍNDICES BINÁRIOS V1 APROVADOS")
    print(f"Publicado em: {dest}")
    print(f"Registros binários: {result['total']}")
    largest = result["largest"]
    print(
        f"Maior índice: {largest['id']} "
        f"({largest['records']} registros, {largest['bytes']} bytes)"
    )
    print(f"Máximo de passos de busca binária: {largest['steps']}")
    print(f"Relatório: {dest / 'RELATORIO_INDICES_BINARIOS.txt'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print()
        print("ERRO FATAL:")
        print(exc)
        sys.exit(1)
