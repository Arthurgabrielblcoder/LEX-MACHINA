from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import argparse, hashlib, json, re, sys

CORPUS_NAME = "99_LEXDATA_ESP32_OFICIAL_V4_TESTE"
OUT_DIR = Path("saida") / "AUDITORIA_FINAL_LEXDATA_V4"
EXPECTED_NORMS = 72
EXPECTED_JURIS = 80

ARTIGO_FINAL = {
    "CF88":"250","CC2002":"2046","CPC2015":"1072","CP1940":"361",
    "CPP1941":"811","CTN1966":"218","CE1965":"383","CLT1943":"922",
    "CDC1990":"119","ECA1990":"267","IDOSO2003":"118","LBI2015":"127",
    "LEP1984":"204","DROGAS2006":"60","MARIA2006":"46","HEDIONDOS1990":"13",
    "LIC2021":"194","MCI2014":"32","LGPD2018":"65","LAI2011":"47",
    "PAF1999":"70","LIA1992":"25","RJU1990":"253","CUSTEIO1991":"105",
    "BENEF1991":"156","FALENCIA2005":"201","SA1976":"300","RPEM1994":"67",
    "LRP1973":"299","CIDADE2001":"58","PNMA1981":"21","CRIMAMB1998":"82",
    "JEC1995":"97","ELEICOES1997":"107","PARTIDOS1995":"63","INELEG1990":"28",
    "ACAOPOP1965":"22","MS2009":"29","ARBIT1996":"44","MED2015":"48",
    "JEF2001":"27","JEFAZ2009":"28","ABUSO2019":"45","ORCRIM2013":"27",
    "LAVAGEM1998":"18","ARMAS2003":"37","TORTURA1997":"4","COND1964":"70",
    "EXECFISC1980":"42","FINPUB1964":"115","LRF2000":"75","LPI1996":"244",
    "LDA1998":"115","COOP1971":"117","TERRA1964":"128","REFAGR1993":"28",
    "MINER1967":"98","CBA1986":"324","CVM1976":"35","SEGUROS1966":"153",
    "LIQFIN1974":"57","CONSORCIO2008":"49","INQUIL1991":"90","SFI1997":"42",
    "TEMP1974":"20","GREVE1989":"19","FGTS1990":"32","RPS1999":"382",
    "ALIMENTOS1968":"29","PATERN1992":"10","ALIMGRAV2008":"12","ALIENPAR2010":"11",
}

ANCHORS = {
    "CF88":["1","5","37","60","250"],
    "CC2002":["1","421","927","1784","2046"],
    "CPC2015":["1","100","300","500","1000","1072"],
    "CTN1966":["1","5","100","218"],
    "ECA1990":["1","53","101","190-F","227-C","240","267"],
    "LEP1984":["1","9-A","82","138","204"],
    "MARIA2006":["1","7","10-A","12-C","17-A","46"],
    "LIC2021":["1","50","100","150","194"],
    "RPS1999":["1","100","200","300","382"],
    "LIQFIN1974":["1","10","19","36","50","57"],
}

SAMPLES = ANCHORS.copy()

ARTICLE_RE = re.compile(
    r"^Art(?:igo)?\s*\.?\s*"
    r"(\d{1,3}(?:\.\d{3})+|\d{1,4})"
    r"\s*(?:º|°|o)?(?:\s*-\s*([A-Za-z]{1,4}))?",
    re.IGNORECASE,
)

def canon(num, suffix=None):
    out = str(int(num.replace(".", "")))
    if suffix:
        out += "-" + suffix.upper()
    return out

def article_at_start(text):
    m = ARTICLE_RE.match(text.lstrip())
    return None if not m else canon(m.group(1), m.group(2))

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def read_idx(path):
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rows.append(line.split("|"))
    return rows

def official_domain(url):
    try:
        host = urlparse(url).netloc.casefold().split(":", 1)[0]
    except Exception:
        return False
    return (
        host == "normas.leg.br"
        or host.endswith(".normas.leg.br")
        or host == "planalto.gov.br"
        or host.endswith(".planalto.gov.br")
    )

def audit(sd_root: Path):
    corpus = sd_root / CORPUS_NAME
    errors, alerts, details, samples = [], [], [], []

    if not corpus.is_dir():
        raise FileNotFoundError(f"Corpus não encontrado: {corpus}")

    required = ["NORMAS.IDX","ARTIGOS.IDX","MENU.IDX","JURIS.IDX","FONTES.JSON","META.JSON"]
    for name in required:
        if not (corpus / name).is_file():
            errors.append(f"Arquivo obrigatório ausente: {name}")
    if errors:
        return build_result(corpus, errors, alerts, details, samples, 0, 0, 0, 0)

    # META
    meta = load_json(corpus / "META.JSON")
    if meta.get("formato") != "OFICIAL4":
        errors.append(f"META formato inesperado: {meta.get('formato')!r}")
    if int(meta.get("normas_ok", -1)) != 72:
        errors.append(f"META normas_ok != 72: {meta.get('normas_ok')}")
    if int(meta.get("juris_ok", -1)) != 80:
        errors.append(f"META juris_ok != 80: {meta.get('juris_ok')}")
    if int(meta.get("erros", -1)) != 0:
        errors.append(f"META registra erros: {meta.get('erros')}")

    # FONTES
    fontes = load_json(corpus / "FONTES.JSON")
    fonte_map = {}
    if not isinstance(fontes, list):
        errors.append("FONTES.JSON não contém lista.")
        fontes = []
    for item in fontes:
        if not isinstance(item, dict):
            errors.append("Registro inválido em FONTES.JSON.")
            continue
        ident = str(item.get("id", "")).strip()
        if not ident:
            errors.append("Fonte sem ID.")
            continue
        if ident in fonte_map:
            errors.append(f"Fonte duplicada: {ident}")
            continue
        fonte_map[ident] = item
        url = str(item.get("fonte", "")).strip()
        if not official_domain(url):
            errors.append(f"{ident}: fonte fora de domínio oficial aceito: {url}")
    if len(fonte_map) != 72:
        errors.append(f"FONTES.JSON possui {len(fonte_map)} normas, esperado 72.")

    # NORMAS
    norm_rows = read_idx(corpus / "NORMAS.IDX")
    if len(norm_rows) != 72:
        errors.append(f"NORMAS.IDX possui {len(norm_rows)} linhas, esperado 72.")
    norms = {}
    for row in norm_rows:
        if len(row) != 9:
            errors.append(f"NORMAS.IDX linha com {len(row)} campos: {row}")
            continue
        ident, sigla, prioridade, ramo, nome, runtime_path, art_count, byte_count, metodo = row
        if ident in norms:
            errors.append(f"NORMAS.IDX ID duplicado: {ident}")
            continue
        try:
            art_count = int(art_count)
            byte_count = int(byte_count)
        except ValueError:
            errors.append(f"{ident}: contagens inválidas em NORMAS.IDX.")
            continue
        expected_path = f"/{CORPUS_NAME}/LEIS/{ident}.TXT"
        if runtime_path != expected_path:
            errors.append(f"{ident}: caminho runtime divergente: {runtime_path}")
        norms[ident] = {
            "nome": nome, "artigos": art_count, "bytes": byte_count,
            "metodo": metodo, "runtime_path": runtime_path
        }

    expected_ids = set(ARTIGO_FINAL)
    if set(norms) != expected_ids:
        missing = sorted(expected_ids - set(norms))
        extra = sorted(set(norms) - expected_ids)
        if missing:
            errors.append("Normas ausentes: " + ", ".join(missing))
        if extra:
            errors.append("Normas extras: " + ", ".join(extra))

    # MENU
    menu_rows = read_idx(corpus / "MENU.IDX")
    if len(menu_rows) != 72:
        errors.append(f"MENU.IDX possui {len(menu_rows)} linhas, esperado 72.")
    menu_ids, orders = [], []
    for row in menu_rows:
        if len(row) != 5:
            errors.append(f"MENU.IDX linha inválida: {row}")
            continue
        try:
            orders.append(int(row[0]))
        except ValueError:
            errors.append(f"MENU.IDX ordem inválida: {row[0]}")
            continue
        menu_ids.append(row[1])
    if orders != list(range(1, len(orders) + 1)):
        errors.append("MENU.IDX não está ordenado de 1 a 72.")
    if set(menu_ids) != set(norms):
        errors.append("MENU.IDX e NORMAS.IDX não possuem os mesmos IDs.")

    # JURIS
    juris_rows = read_idx(corpus / "JURIS.IDX")
    if len(juris_rows) != 80:
        errors.append(f"JURIS.IDX possui {len(juris_rows)} linhas, esperado 80.")
    for row in juris_rows:
        if len(row) != 6:
            errors.append(f"JURIS.IDX linha inválida: {row}")

    # ARTIGOS
    art_rows = read_idx(corpus / "ARTIGOS.IDX")
    by_norm = {ident: [] for ident in norms}
    for row in art_rows:
        if len(row) != 4:
            errors.append(f"ARTIGOS.IDX linha inválida: {row}")
            continue
        ident, art, off, size = row
        if ident not in by_norm:
            errors.append(f"ARTIGOS.IDX refere norma inexistente: {ident}")
            continue
        try:
            off, size = int(off), int(size)
        except ValueError:
            errors.append(f"{ident} Art. {art}: offset/tamanho inválidos.")
            continue
        by_norm[ident].append({"artigo": art, "offset": off, "tamanho": size})

    total_index = sum(len(v) for v in by_norm.values())
    total_reopened = 0

    # LEIS + TODOS OS OFFSETS
    for ident in sorted(norms):
        info = norms[ident]
        law_path = corpus / "LEIS" / f"{ident}.TXT"
        if not law_path.is_file():
            errors.append(f"{ident}: arquivo canônico ausente.")
            continue

        real_size = law_path.stat().st_size
        if real_size != info["bytes"]:
            errors.append(f"{ident}: bytes reais {real_size} != NORMAS.IDX {info['bytes']}.")

        fonte = fonte_map.get(ident)
        if not fonte:
            errors.append(f"{ident}: não existe em FONTES.JSON.")
        else:
            expected_sha = str(fonte.get("sha256", "")).strip().casefold()
            real_sha = sha256_file(law_path).casefold()
            if not expected_sha or expected_sha != real_sha:
                errors.append(f"{ident}: SHA-256 divergente.")
            try:
                if int(fonte.get("artigos", -1)) != info["artigos"]:
                    errors.append(f"{ident}: FONTES.JSON e NORMAS.IDX divergem na contagem.")
            except Exception:
                errors.append(f"{ident}: contagem de artigos inválida em FONTES.JSON.")

        regs = by_norm.get(ident, [])
        if len(regs) != info["artigos"]:
            errors.append(f"{ident}: ARTIGOS.IDX={len(regs)} e NORMAS.IDX={info['artigos']}.")

        if not regs:
            continue

        labels = [r["artigo"] for r in regs]
        if len(labels) != len(set(labels)):
            errors.append(f"{ident}: artigos duplicados em ARTIGOS.IDX.")
        if labels[0] != "1":
            errors.append(f"{ident}: primeiro artigo {labels[0]} != 1.")
        if labels[-1] != ARTIGO_FINAL[ident]:
            errors.append(f"{ident}: último artigo {labels[-1]} != {ARTIGO_FINAL[ident]}.")

        label_set = set(labels)
        for anchor in ANCHORS.get(ident, []):
            if anchor not in label_set:
                errors.append(f"{ident}: âncora ausente Art. {anchor}.")

        with law_path.open("rb") as f:
            expected_offset = 0
            for reg in regs:
                art, off, size = reg["artigo"], reg["offset"], reg["tamanho"]
                if off != expected_offset:
                    errors.append(f"{ident} Art. {art}: offset {off} != {expected_offset}.")
                if off < 0 or size <= 0 or off + size > real_size:
                    errors.append(f"{ident} Art. {art}: faixa inválida.")
                    continue
                f.seek(off)
                raw = f.read(size)
                if len(raw) != size:
                    errors.append(f"{ident} Art. {art}: leitura curta.")
                    continue
                try:
                    txt = raw.decode("utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    errors.append(f"{ident} Art. {art}: UTF-8 inválido: {exc}")
                    continue
                found = article_at_start(txt)
                if found != art:
                    errors.append(f"{ident}: índice Art. {art}, offset lê Art. {found}.")
                total_reopened += 1
                expected_offset = off + size
            if expected_offset != real_size:
                errors.append(f"{ident}: último artigo termina em {expected_offset}, arquivo possui {real_size}.")

        # Whole-file residue scan.
        try:
            whole = law_path.read_text(encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            whole = ""
        if whole:
            low = whole.casefold()
            for marker in ("<html", "<body", "<script", "please enable javascript"):
                if marker in low:
                    errors.append(f"{ident}: resíduo técnico encontrado: {marker}")
            if "\ufffd" in whole:
                alerts.append(f"{ident}: caractere U+FFFD encontrado.")

        details.append({
            "id": ident,
            "artigos": len(regs),
            "primeiro": labels[0],
            "ultimo": labels[-1],
            "bytes": real_size,
            "metodo": info["metodo"],
        })

        # Human samples
        reg_map = {r["artigo"]: r for r in regs}
        with law_path.open("rb") as f:
            for art in SAMPLES.get(ident, []):
                reg = reg_map.get(art)
                if not reg:
                    samples.append(f"[FALHA] {ident} Art. {art}: não indexado.")
                    continue
                f.seek(reg["offset"])
                raw = f.read(min(reg["tamanho"], 700))
                txt = raw.decode("utf-8", errors="replace")
                txt = re.sub(r"\s+", " ", txt).strip()
                samples.append(
                    f"[OK] {ident} Art. {art} | offset={reg['offset']} | tamanho={reg['tamanho']}"
                )
                samples.append("    " + txt[:560])

    try:
        meta_articles = int(meta.get("artigos_total", -1))
    except Exception:
        meta_articles = -1
    if meta_articles != total_index:
        errors.append(f"META artigos_total={meta_articles} != ARTIGOS.IDX={total_index}.")

    return build_result(
        corpus, errors, alerts, details, samples,
        len(norms), len(juris_rows), total_index, total_reopened
    )

def build_result(corpus, errors, alerts, details, samples, norms, juris, total_index, reopened):
    approved = (
        norms == 72
        and juris == 80
        and total_index > 0
        and reopened == total_index
        and not errors
        and not alerts
    )
    return {
        "aprovado": approved,
        "corpus": str(corpus),
        "normas": norms,
        "jurisprudencias": juris,
        "artigos_idx": total_index,
        "artigos_reabertos": reopened,
        "erros": errors,
        "alertas": alerts,
        "detalhes": details,
        "amostras": samples,
    }

def save_reports(result):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    txt = OUT_DIR / "RELATORIO_AUDITORIA_FINAL.txt"
    js = OUT_DIR / "RELATORIO_AUDITORIA_FINAL.json"
    sm = OUT_DIR / "AMOSTRAS_AUDITORIA.txt"

    lines = [
        "LEX MACHINA",
        "AUDITORIA FINAL DO CORPUS OFICIAL V4",
        "=" * 88,
        "",
        f"CORPUS: {result['corpus']}",
        f"NORMAS: {result['normas']}/72",
        f"JURISPRUDÊNCIAS: {result['jurisprudencias']}/80",
        f"ARTIGOS EM ARTIGOS.IDX: {result['artigos_idx']}",
        f"ARTIGOS REABERTOS E VALIDADOS: {result['artigos_reabertos']}/{result['artigos_idx']}",
        f"ERROS: {len(result['erros'])}",
        f"ALERTAS: {len(result['alertas'])}",
        "",
        "RESULTADO: " + ("APROVADO" if result["aprovado"] else "REPROVADO"),
        "",
        "=" * 88,
        "DIAGNÓSTICO POR NORMA",
        "=" * 88,
        "",
    ]

    for d in result["detalhes"]:
        lines.append(
            f"[OK] {d['id']} | artigos={d['artigos']} | primeiro={d['primeiro']} "
            f"| ultimo={d['ultimo']} | bytes={d['bytes']} | metodo={d['metodo']}"
        )

    if result["erros"]:
        lines += ["", "=" * 88, "ERROS", "=" * 88, ""]
        lines += ["- " + e for e in result["erros"]]

    if result["alertas"]:
        lines += ["", "=" * 88, "ALERTAS", "=" * 88, ""]
        lines += ["- " + a for a in result["alertas"]]

    lines += ["", "=" * 88, "CONCLUSÃO", "=" * 88, ""]
    if result["aprovado"]:
        lines += [
            "APROVADO: corpus tecnicamente coerente para integração com o firmware do ESP32.",
            "Todos os registros de ARTIGOS.IDX foram reabertos no microSD.",
            "Os 72 arquivos coincidem por SHA-256 com FONTES.JSON.",
        ]
    else:
        lines.append(
            "REPROVADO: não integrar ao firmware enquanto houver erros ou alertas."
        )

    txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    js.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    sm.write_text(
        "LEX MACHINA\nAMOSTRAS DA AUDITORIA FINAL V4\n"
        + "=" * 88 + "\n\n"
        + "\n".join(result["amostras"]) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return txt, js, sm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("origem", help="Raiz do microSD. Ex.: D:\\")
    args = parser.parse_args()

    sd = Path(args.origem)
    if not sd.is_dir():
        raise FileNotFoundError(f"Origem inválida: {sd}")

    print()
    print("LEX MACHINA")
    print("AUDITORIA FINAL DO CORPUS OFICIAL V4")
    print("=" * 72)
    print("Modo: SOMENTE LEITURA")
    print(f"MicroSD: {sd}")
    print()

    result = audit(sd)
    txt, js, sm = save_reports(result)

    print(f"Normas: {result['normas']}/72")
    print(f"Jurisprudências: {result['jurisprudencias']}/80")
    print(f"Artigos em índice: {result['artigos_idx']}")
    print(
        f"Artigos reabertos: "
        f"{result['artigos_reabertos']}/{result['artigos_idx']}"
    )
    print(f"Erros: {len(result['erros'])}")
    print(f"Alertas: {len(result['alertas'])}")
    print()
    print(
        "✓ AUDITORIA FINAL APROVADA"
        if result["aprovado"]
        else "⚠ AUDITORIA FINAL REPROVADA"
    )
    print()
    print(f"Relatório: {txt}")
    print(f"Amostras: {sm}")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print()
        print("ERRO FATAL:")
        print(exc)
        sys.exit(1)
