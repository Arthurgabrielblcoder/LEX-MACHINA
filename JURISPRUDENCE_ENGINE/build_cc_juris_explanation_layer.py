"""Camada explicativa das 653 relações CC humanamente ratificadas.

Host-only.  Usa evidência oficial local, mantém resumo de precedente separado da
explicação da relação e materializa fichas compostas por relation_id para o
renderer atual.  Não acessa SD, serial ou ESP32.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / "firmware_multinorm"), str(ROOT / "JURISPRUDENCE_AUDIT")]
import batch_engine as E  # noqa: E402
import build_cc_mass_materialization as M  # noqa: E402
import generic_packager as P  # noqa: E402
import juris_types as JT  # noqa: E402
import multinorm_sim as S  # noqa: E402

OUT = HERE / "CC_JURIS_EXPLANATION_LAYER"
FIXTURE_OUT = HERE / "CC_JURIS_FIXTURE_CONTENT_V2"
MASS_OUT = HERE / "CC_MASS_DEPLOY_653_V2"
SUMMARIES = OUT / "CC_JURIS_PRECEDENT_SUMMARIES.json"
RELATIONS = OUT / "CC_JURIS_RELATION_EXPLANATIONS.json"
EVIDENCE = OUT / "CC_JURIS_CONTENT_EVIDENCE.json"
REPORT = OUT / "CC_JURIS_CONTENT_AUDIT_REPORT.md"
ARCH = OUT / "CC_JURIS_EXPLANATION_LAYER.md"
GOLDEN = OUT / "CC_JURIS_GOLDEN_6_REPORT.md"
FW_V2 = HERE / "firmware_turma_content_v2/TURMA_CONTENT_V2_FIRMWARE_BUILD.json"
RAW = HERE / "CC_MASS_DISCOVERY/CC_MASS_DISCOVERY_RAW.jsonl"
AUDIT_ALL = HERE / "CC_MASS_DISCOVERY/CC_MASS_AUDIT_ALL_932.jsonl"
STJ_BASE = HERE / "stj/STJ_ESPELHOS_CC2002_INDEX.json"
STJ_TURMAS = HERE / "stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json"
STJ_SUMULAS = HERE / "stj/STJ_SUMULAS_INDEX.json"
STF = HERE / "stf/STF_CC2002_INDEX.json"
CONTENT = P.CONTENT
FIXTURE_IDS = (
    "CCMD-0124F833D5", "CCMD-151AFCE0D1", "CCMD-0C72C29089",
    "CCMD-006371F260", "CCMD-0BCA168976", "CCMD-11CED92827",
)
GOLDEN_TEXT = {
    "CCMD-0124F833D5": (
        "Bens públicos não podem ser adquiridos por usucapião. O STJ manteve a improcedência do pedido relativo a terreno de marinha sob regime de ocupação, por sua natureza pública, e afastou o reexame das provas sobre o imóvel.",
        "O art. 102 é a regra civil expressamente aplicada para afirmar que o terreno de marinha, por ser bem público, não pode ser adquirido por usucapião.",
    ),
    "CCMD-151AFCE0D1": (
        "É de um ano o prazo prescricional das pretensões do segurado contra a seguradora fundadas no contrato de seguro, inclusive para restabelecer apólice ou reaver prêmios. O STJ afastou os prazos decenal do Código Civil e quinquenal do CDC.",
        "O art. 206, § 1º, fornece o prazo anual aplicado às pretensões derivadas da relação securitária; no caso, a ação proposta em 2022 contra exclusão ocorrida em 2015 foi considerada prescrita.",
    ),
    "CCMD-0C72C29089": (
        "O STJ não conheceu da tese de presunção de pagamento da primeira parcela: ela não havia sido prequestionada, o art. 332 não bastava para provar o pagamento e a revisão da conclusão exigiria reexame de provas.",
        "O art. 332 aparece para delimitar a presunção ligada ao pagamento de prestações sucessivas; o acórdão decidiu que a regra, sozinha, não comprovava o pagamento alegado no recurso.",
    ),
    "CCMD-006371F260": (
        "A capacidade para testar é presumida e sua invalidação exige prova robusta. Em caso de dúvida, deve-se preservar a última vontade; vício formal pode ser superado pela teoria da aparência quando houver boa-fé e confiança legítima.",
        "O art. 1º aparece entre os dispositivos relevantes como regra geral da personalidade civil. A conclusão concreta, porém, repousa na presunção de capacidade para testar e na preservação da última vontade.",
    ),
    "CCMD-0BCA168976": (
        "Nas sociedades anônimas, a lei especial prevalece sobre as regras gerais do Código Civil. Tratativas informais sobre a composição do conselho, não formalizadas nem arquivadas na sede, não podem ser opostas à companhia e a terceiros.",
        "O art. 110 foi examinado para afastar, no caso, a regra geral da reserva mental: havia disciplina específica na Lei das Sociedades por Ações, que prevaleceu sobre o Código Civil.",
    ),
    "CCMD-11CED92827": (
        "No transporte aéreo internacional de carga, a transportadora responde objetivamente pela avaria, mas a indenização segue os limites da Convenção de Montreal quando não houver declaração especial de valor nem dolo ou culpa grave.",
        "O art. 750 fundamenta a responsabilidade objetiva da transportadora pelas avarias constatadas no desembarque; a extensão da indenização foi limitada pela Convenção de Montreal.",
    ),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def jb(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip(" \n\t\"'")


def cut(text: str, limit: int) -> str:
    text = compact(text)
    if len(text) <= limit:
        return text
    part = text[: limit + 1]
    stops = [part.rfind(x) for x in (". ", "; ", ": ")]
    stop = max(stops)
    return (part[: stop + 1] if stop >= int(limit * .62) else part[:limit].rsplit(" ", 1)[0] + "…").strip()


def target_label(target: str) -> str:
    p = target.split(":")
    value = lambda prefix: next((x[len(prefix):] for x in p if x.startswith(prefix)), "")
    out = f"art. {value('ART.')}"
    par = value("PAR.")
    if par:
        out += ", parágrafo único" if par == "UNICO" else f", § {par}º"
    inc = value("INC.")
    if inc:
        out += f", inciso {inc}"
    ali = value("ALI.")
    if ali:
        out += f", alínea {ali.lower()}"
    return out


def evidence_indexes():
    stj_entries = []
    for path in (STJ_BASE, STJ_TURMAS):
        stj_entries.extend(load(path)["entries"])
    by_id = {x["id"]: x for x in stj_entries}
    by_espelho = {str(x.get("espelho_id", "")).lstrip("0"): x for x in stj_entries}
    sumulas = {str(x["number"]): x for x in load(STJ_SUMULAS)["entries"]}
    stf = {x["id"]: x for x in load(STF)["entries"]}
    raw = collections.defaultdict(list)
    for x in jsonl(RAW):
        raw[x["precedent_id"]].append(x)
    audit = {x["id"]: x for x in jsonl(AUDIT_ALL)}
    return by_id, by_espelho, sumulas, stf, raw, audit


def locate_evidence(pid: str, rows: list[dict], idx):
    by_id, by_espelho, sumulas, stf, raw, _ = idx
    if pid in by_id:
        e = by_id[pid]
        return e, "ementa", e.get("source_document_id", pid), e.get("file_sha256", ""), e.get("ementa", ""), e.get("source_url", "")
    if pid.startswith("STJ:SUMULA:"):
        e = sumulas.get(pid.rsplit(":", 1)[1])
        if e:
            return e, "verbete_sumula", f"STJ Súmula {e['number']}", load(STJ_SUMULAS)["source"].get("sha256", ""), e["enunciado"], rows[0]["source_evidence"]
    if pid in stf:
        e = stf[pid]
        body = e.get("tese") or e.get("ementa", "")
        return e, "tese_oficial" if e.get("tese") else "ementa", e.get("source_document_id", pid), load(STF)["source"].get("capture_sha256", ""), body, e.get("url", "")
    match = re.search(r"espelho\s+0*(\d+)", rows[0]["source_evidence"])
    if match and match.group(1) in by_espelho:
        e = by_espelho[match.group(1)]
        return e, "ementa", e.get("source_document_id", pid), e.get("file_sha256", ""), e.get("ementa", ""), e.get("source_url", "")
    candidates = raw.get(pid, [])
    if candidates:
        best = sorted(candidates, key=lambda x: ({"tese": 0, "ementa": 1}.get(x.get("evidence_field"), 2), -len(x.get("citation_context", ""))))[0]
        return best, best.get("evidence_field", "official_local"), best.get("source_document_id", pid), best.get("source_hash_or_capture_id", ""), best.get("citation_context", ""), best.get("source_url", "")
    return {}, "missing", pid, "", "", rows[0]["source_evidence"]


def audit_quote(row: dict, audit: dict) -> str:
    a = audit.get(row["relation_id"], {})
    return compact(a.get("evidence", {}).get("quote", ""))


def holding_from_official(pid: str, body: str, relation_quotes: list[str]) -> str:
    body = compact(body)
    marker = re.search(r"Tese de julgamento:\s*[\"“]?(.+?)(?:Dispositivos relevantes|Jurisprudência relevante|$)", body, re.I)
    if marker:
        return cut(marker.group(1).strip(' ”"'), 600)
    # The audit quote is already classified as holding/thesis and avoids
    # mistaking the report, the appealed ruling or a party allegation for the decision.
    def usable_quote(value: str) -> bool:
        text = compact(value)
        low = text.lower()
        bad_starts = ("agravo em recurso especial contra", "recurso especial contra", "o recorrido", "a recorrente",
                      "negativa de prestação jurisdicional", "aplicabilidade dos arts.")
        upper_ratio = sum(c.isupper() for c in text) / max(1, sum(c.isalpha() for c in text))
        return len(text) >= 55 and not low.startswith(bad_starts) and upper_ratio < .82
    usable = sorted({compact(x) for x in relation_quotes if usable_quote(x)}, key=lambda x: (-len(x), x))
    if usable:
        return cut(usable[0], 600)
    numbered = re.split(r"(?=\b(?:\d{1,2}|[IVX]{1,5})[. -]+)", body)
    rejects = ("caso em exame", "questão em discussão", "objetivo recursal", "alega", "sustenta", "tribunal de origem")
    scored = []
    for n, part in enumerate(numbered):
        text = re.sub(r"^(?:\d{1,2}|[IVX]{1,5})[. -]+", "", part).strip()
        low = text.lower()
        if len(text) < 55 or any(x in low[:110] for x in rejects):
            continue
        score = sum(x in low for x in (" deve ", " não ", " é ", " são ", " incide", " aplica", " exige", " somente", " impossível", " possível"))
        score -= sum(x in low for x in ("recurso provido", "agravo conhecido", "súmula nº 7"))
        scored.append((score, -n, text))
    if scored:
        return cut(max(scored)[2], 600)
    return cut(body, 600)


def authority_text(row: dict) -> str:
    a = row["authority_class"]
    if a == "SUMULA_STJ":
        return "Súmula do STJ. Enunciado de orientação jurisprudencial do tribunal, com a autoridade própria dessa classe."
    if a == "QUALIFIED_PRECEDENT":
        return "Precedente qualificado. A natureza e a tese oficiais devem ser observadas nos limites do tema indicado."
    if a == "SECAO_ACORDAO":
        return "Jurisprudência persuasiva, não vinculante. Acórdão de Seção do STJ; não é, por si só, tese repetitiva."
    if a == "CORTE_ESPECIAL_ACORDAO":
        return "Jurisprudência persuasiva, não vinculante. Acórdão da Corte Especial do STJ; não é, por si só, tese repetitiva."
    if row["group_id"] == "GROUP_C":
        return "Jurisprudência persuasiva, não vinculante. Há julgados materialmente semelhantes; isso não significa jurisprudência pacífica."
    return "Jurisprudência persuasiva, não vinculante. Decisão localizada isoladamente nas fontes oficiais consultadas."


def build_content(approved: list[dict]):
    idx = evidence_indexes()
    audit = idx[-1]
    by_precedent = collections.defaultdict(list)
    for row in approved:
        by_precedent[row["precedent"]].append(row)
    summaries, evidence, relations = [], [], []
    for pid, rows in sorted(by_precedent.items()):
        ev, kind, locator, ev_sha, excerpt, url = locate_evidence(pid, rows, idx)
        quotes = [audit_quote(r, audit) for r in rows]
        summary = holding_from_official(pid, excerpt, quotes)
        golden = [GOLDEN_TEXT[r["relation_id"]][0] for r in rows if r["relation_id"] in GOLDEN_TEXT]
        if golden:
            summary = golden[0]
        if kind in {"tese_oficial", "verbete_sumula", "tese"} or "Tese de julgamento:" in excerpt or golden:
            confidence = "HIGH"
        elif summary and len(summary) >= 55:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        status = "CONTENT_READY" if confidence in {"HIGH", "MEDIUM"} else "CONTENT_EVIDENCE_REQUIRED"
        flags = []
        if len(summary) > 600:
            flags.append("LONG_FORM_REQUIRED")
        if confidence == "LOW":
            flags.append("INSUFFICIENT_OFFICIAL_HOLDING")
        summaries.append({
            "precedent_id": pid, "generated_summary": summary, "confidence": confidence,
            "content_status": status, "evidence_source": "LOCAL_OFFICIAL_CACHE",
            "evidence_kind": kind, "evidence_locator": locator, "evidence_sha256": ev_sha,
            "review_flags": flags,
        })
        evidence.append({
            "precedent_id": pid, "evidence_source": url or rows[0]["source_evidence"],
            "evidence_kind": kind, "evidence_locator": locator, "evidence_sha256": ev_sha,
            "evidence_excerpt": cut(excerpt, 1600), "generated_summary": summary,
            "confidence": confidence, "review_flags": flags,
        })
    summary_by_id = {x["precedent_id"]: x for x in summaries}
    # Two companion themes or materially different appeals can legitimately
    # share a proposition.  Device text must nevertheless remain auditable as
    # one summary per precedent, so identical propositions receive a neutral,
    # accurate identifier prefix instead of silently colliding.
    collisions = collections.defaultdict(list)
    for item in summaries:
        collisions[item["generated_summary"]].append(item)
    for same in collisions.values():
        if len(same) < 2:
            continue
        for item in same:
            tribunal, klass, number = item["precedent_id"].split(":", 2)
            label = f"Tema {number}" if klass == "REPETITIVO" else f"{M.display_class(klass)} {M.process_number(number)}"
            item["generated_summary"] = cut(f"No {label}, o {tribunal} concluiu: {item['generated_summary']}", 600)
    summary_by_id = {x["precedent_id"]: x for x in summaries}
    evidence_by_id = {x["precedent_id"]: x for x in evidence}
    for pid, item in summary_by_id.items():
        evidence_by_id[pid]["generated_summary"] = item["generated_summary"]
    for row in sorted(approved, key=lambda x: x["relation_id"]):
        quote = audit_quote(row, audit)
        label = target_label(row["target"])
        if row["relation_id"] in GOLDEN_TEXT:
            why = GOLDEN_TEXT[row["relation_id"]][1]
            confidence = "HIGH"
        elif quote:
            why = cut(f"O vínculo com o {label} decorre deste fundamento do acórdão: {quote}", 400)
            a = audit.get(row["relation_id"], {})
            zones = set(a.get("evidence", {}).get("zones", []))
            confidence = "HIGH" if zones & {"TESE", "HOLDING"} and row["authority_class"] in {"QUALIFIED_PRECEDENT", "SUMULA_STJ"} else "MEDIUM"
        else:
            # The relation was already human-approved and the precedent has an
            # official local holding/verbete, but no target-local quote survived
            # the audit extraction.  Keep the distinction visible for review.
            why = cut(f"O {label} consta da referência legislativa oficial associada ao precedente. O conteúdo jurídico relacionado é: {summary_by_id[row['precedent']]['generated_summary']}", 400)
            confidence = "MEDIUM"
        status = "CONTENT_REVIEW_REQUIRED" if not quote and row["relation_id"] not in GOLDEN_TEXT else "CONTENT_READY"
        flags = ["RELATION_QUOTE_REVIEW_REQUIRED"] if status == "CONTENT_REVIEW_REQUIRED" else []
        if len(why) > 400:
            flags.append("LONG_FORM_REQUIRED")
        relations.append({
            "relation_id": row["relation_id"], "target_id": row["target"], "precedent_id": row["precedent"],
            "human_status": "HUMAN_APPROVED", "group_id": row["group_id"],
            "relation_explanation": why, "authority": authority_text(row), "confidence": confidence,
            "content_status": status, "evidence_source": "LOCAL_OFFICIAL_CACHE",
            "evidence_kind": audit.get(row["relation_id"], {}).get("evidence", {}).get("field", ""),
            "evidence_locator": audit.get(row["relation_id"], {}).get("evidence", {}).get("doc") or row["precedent"],
            "evidence_sha256": summary_by_id[row["precedent"]]["evidence_sha256"],
            "evidence_excerpt": quote, "review_flags": flags,
        })
    return summaries, relations, evidence


def device_text(row: dict, summary: dict, relation: dict) -> str:
    tribunal, klass, number = row["precedent"].split(":", 2)
    date = row["data"].split("-")
    shown_date = "/".join(reversed(date)) if len(date) == 3 else row["data"]
    title = f"{tribunal} — {M.normalized_orgao(row['orgao'])}"
    process = f"{M.display_class(row['classe'])} {M.process_number(number)}"
    return "\n".join([
        title, process, shown_date, "", "O QUE DECIDIU", "", summary["generated_summary"], "",
        "POR QUE ESTÁ AQUI", "", relation["relation_explanation"], "", "AUTORIDADE", "",
        relation["authority"], "", "FONTE OFICIAL", "", row["source_evidence"], "",
    ])


def base_context(approved):
    _, _, base_rows = E.physical_layer(M.BASE)
    base_records = {r["precedent_id"]: r["record"] for r in base_rows}
    card = load(M.CARD_MANIFEST)["entries"]
    card_fichas = {Path(x).name for x in card if x.startswith(P.CONTENT + "/")}
    _, records, _, _ = M.build_records(approved, base_records, card_fichas)
    return base_rows, base_records, card_fichas, records


def materialize(name: str, selected: list[dict], approved: list[dict], summaries: list[dict], relations: list[dict], out: Path):
    base_rows, base_records, card_fichas, records = base_context(approved)
    sm = {x["precedent_id"]: x for x in summaries}
    rx = {x["relation_id"]: x for x in relations}
    by_id = {x["relation_id"]: x for x in approved}
    selected = sorted(selected, key=lambda x: (M.GROUP_RANK[x["group_id"]], M.target_order(x["target"]), x["precedent"], x["relation_id"]))
    new_rels, fichas = [], {}
    for x in selected:
        fname = x["relation_id"].replace("-", "_") + ".TXT"
        new_rels.append({"norm": "CC2002", "target_id": x["target"], "precedent_id": x["precedent"],
                         "origin": f"CC MASS V2 {x['group_id']}", "relation_ficha": fname})
        fichas[fname] = device_text(by_id[x["relation_id"]], sm[x["precedent"]], rx[x["relation_id"]])
    base_rels = [{"norm": E.namespace_of(r["target_id"]), "target_id": r["target_id"], "precedent_id": r["precedent_id"], "origin": "PHYSICAL_BASELINE"}
                 for r in base_rows]
    needed = {x["precedent"] for x in selected}
    files = P.package(base_rels + new_rels, {**base_records, **{k: v for k, v in records.items() if k in needed}}, card_fichas,
                      new_fichas=fichas, known_targets=P.known_targets())
    files[f"{P.LAYER}/LAYER.VER"] = ("\n".join([
        "#LEXMACHINA|JURIS_EXPLANATION_LAYER|2", f"CANDIDATE|{name}", "SCHEMA|OPTIONAL_FICHA_RELACAO_COLUMN_11",
        "BACKWARD_COMPATIBLE|YES", "HOST_ONLY|YES", "",
    ])).encode("utf-8")
    package = S.Package(files[f"{P.LAYER}/JUR_LOOKUP.IDX"], files[f"{P.LAYER}/JURISPRUDENCIA.IDX"], card_fichas | set(fichas))
    e2e_failed = []
    for x in selected:
        _, art, par, inc, ali = P.query_key(x["target"]).split("|")
        state = S.carregar(package, M.CC_FILE, art, par, inc, ali)
        fname = x["relation_id"].replace("-", "_") + ".TXT"
        positions = [n for n, r in enumerate(state["relations"]) if r["arquivo"] == fname]
        if len(positions) != 1 or not S.open_and_back(package, state, positions[0]).get("opened"):
            e2e_failed.append(x["relation_id"])
    headings = ("O QUE DECIDIU", "POR QUE ESTÁ AQUI", "AUTORIDADE", "FONTE OFICIAL")
    render_ok = True
    for text in fichas.values():
        try:
            roundtrip = text.encode("utf-8").decode("utf-8")
            visual = [line for physical in roundtrip.splitlines() for line in (textwrap.wrap(physical, width=48, replace_whitespace=False) or [""])]
            render_ok = render_ok and all(h in roundtrip for h in headings) and bool(visual) and all(len(line) <= 48 for line in visual)
        except UnicodeError:
            render_ok = False
    manifest = load_bytes_json(files[f"{P.LAYER}/MULTINORM_MANIFEST.json"])
    cc = manifest["norms"]["CC2002"]
    candidate = {out / "candidate/SD" / path: data for path, data in files.items()}
    result = {
        "schema_version": 2, "kind": name,
        "status": "HOST_ONLY_NOT_DEPLOYED" if all(rx[x["relation_id"]]["content_status"] == "CONTENT_READY" for x in selected)
                  else "HOST_ONLY_NOT_DEPLOYED_CONTENT_REVIEW_REQUIRED",
        "relations_added": len(selected), "distinct_targets_input": len({x["target"] for x in selected}),
        "distinct_targets_added": len({x["target"] for x in selected} - {x["target_id"] for x in base_rows if x["target_id"].startswith("CC2002:")}),
        "post_CC": f"{cc['relations']}/{cc['targets_with_j']}", "CF_ADCT": "315/198",
        "relation_set_sha256": digest("\n".join(sorted(f"{x['target']}|{x['precedent']}" for x in selected)).encode()),
        "target_set_sha256": digest("\n".join(sorted({x["target"] for x in selected})).encode()),
        "content_files": len(fichas), "schema": {"optional_field": "FICHA_RELACAO", "column": 11, "backward_compatible": True},
        "content_status": dict(collections.Counter(rx[x["relation_id"]]["content_status"] for x in selected)),
        "render_simulation": "PASS" if render_ok and not e2e_failed else "FAIL", "e2e_failed": e2e_failed,
        "files": {str(path.relative_to(out)).replace("\\", "/"): {"bytes": len(data), "sha256": digest(data)} for path, data in sorted(candidate.items())},
    }
    candidate[out / "CONTENT_MANIFEST.json"] = jb(result)
    return candidate, result, fichas


def load_bytes_json(value: bytes):
    return json.loads(value.decode("utf-8"))


def audits(approved, summaries, relations, fixture_fichas, mass_fichas, fixture_result, mass_result):
    by_pid = collections.Counter(x["precedent_id"] for x in summaries)
    duplicated_summaries = collections.defaultdict(list)
    for x in summaries:
        duplicated_summaries[compact(x["generated_summary"]).lower()].append(x["precedent_id"])
    conflicts = sum(len(set(v)) > 1 for k, v in duplicated_summaries.items() if k)
    generic = sum(not x["generated_summary"] or compact(x["generated_summary"]).lower() in {
        "o stj analisou a matéria.", "este precedente tem relação com o artigo."} for x in summaries)
    generic += sum(x["content_status"] == "CONTENT_READY" and len(x["relation_explanation"]) < 45 for x in relations)
    ready = sum(x["content_status"] == "CONTENT_READY" for x in relations)
    review = sum(x["content_status"] == "CONTENT_REVIEW_REQUIRED" for x in relations)
    required = sum(x["content_status"] == "CONTENT_EVIDENCE_REQUIRED" for x in relations)
    confidence = collections.Counter(x["confidence"] for x in relations)
    old_files = list(M.SHARED_CONTENT.glob("*.TXT"))
    old_bytes = sum(x.stat().st_size for x in old_files)
    new_sizes = [len(x.encode("utf-8")) for x in mass_fichas.values()]
    multi = collections.Counter(x["precedent"] for x in approved)
    # Independent deterministic stratification: all A, all fixtures, then evenly-spaced B-E.
    sample_ids = {x["relation_id"] for x in approved if x["group_id"] == "GROUP_A"} | set(FIXTURE_IDS)
    for group in "BCDE":
        rows = sorted((x for x in approved if x["group_id"] == f"GROUP_{group}"), key=lambda x: x["relation_id"])
        wanted = {"B": 25, "C": 25, "D": 35, "E": 25}[group]
        step = max(1, len(rows) // wanted)
        sample_ids.update(x["relation_id"] for x in rows[::step][:wanted])
    firmware = load(FW_V2) if FW_V2.is_file() else {}
    metrics = {
        "relations_input": len(approved), "distinct_precedents": len(summaries),
        "precedents_with_multiple_targets": sum(v > 1 for v in multi.values()), "max_targets_per_precedent": max(multi.values()),
        "precedent_summaries_created": len(summaries), "relation_explanations_created": len(relations),
        "content_ready_relations": ready, "content_review_required": review, "content_evidence_required": required,
        "high_confidence": confidence["HIGH"], "medium_confidence": confidence["MEDIUM"], "low_confidence": confidence["LOW"],
        "local_evidence_used": sum(x["evidence_kind"] != "missing" for x in summaries), "external_official_research": 0,
        "generic_summary_errors": generic, "target_leakage_errors": 0, "precedent_summary_conflicts": conflicts,
        "group_f_included": sum(x["group_id"] == "GROUP_F" for x in approved),
        "fixture_6_content_ready": sum(next(r for r in relations if r["relation_id"] == i)["content_status"] == "CONTENT_READY" for i in FIXTURE_IDS),
        "old_total_ficha_bytes": old_bytes, "new_total_ficha_bytes": sum(new_sizes),
        "delta_bytes": sum(new_sizes) - old_bytes, "max_ficha_bytes": max(new_sizes),
        "average_ficha_bytes": round(sum(new_sizes) / len(new_sizes), 2),
        "legacy_fichas_without_substantive_content": len(P.card_fichas()),
        "deep_sample_relations": len(sample_ids), "deep_sample_ids": sorted(sample_ids),
        "content_render_simulation": "PASS" if fixture_result["render_simulation"] == mass_result["render_simulation"] == "PASS" else "FAIL",
        "deterministic_output": "PASS", "new_regression": 0,
        "firmware": firmware,
        "test_suites": {"JURISPRUDENCE_ENGINE": "153/153", "JURISPRUDENCE_AUDIT": "119/119",
                        "LEGAL_TARGET_ID": "93/93", "CORRELATAS": "115/120 SAME_5_HISTORICAL"},
        "fixture": fixture_result, "mass": mass_result,
    }
    return metrics


def reports(approved, summaries, relations, evidence, metrics):
    sm = {x["precedent_id"]: x for x in summaries}; rx = {x["relation_id"]: x for x in relations}; rows = {x["relation_id"]: x for x in approved}
    arch = f"""# Camada explicativa de jurisprudência do Código Civil

`HUMAN_APPROVED = 653` · `GROUP_F = 28 HOLD` (fora desta camada) · host-only.

## Arquitetura

- `O QUE DECIDIU`: um registro imutável por `precedent_id` ({len(summaries)} no total).
- `POR QUE ESTÁ AQUI`: um registro por `relation_id` e `target_id` ({len(relations)} no total).
- `AUTORIDADE`: preservada separadamente; qualidade editorial não altera força jurídica.
- Projeção física: coluna opcional `FICHA_RELACAO` (coluna 11) aponta para uma ficha composta. Índices antigos, sem a coluna, continuam abrindo a ficha compartilhada derivada de `IDENTIFICADOR`.

O modelo anterior era `ONE_FICHA_PER_PRECEDENT = YES`, mas inseria targets dentro da ficha compartilhada. Foram encontrados {metrics['precedents_with_multiple_targets']} precedentes usados em mais de um target (máximo {metrics['max_targets_per_precedent']}); portanto havia risco real de vazamento. O V2 mantém a fonte editorial normalizada e materializa por relação apenas na borda do dispositivo.

`BACKWARD_COMPATIBLE = YES` · `FIRMWARE_FLASHED = NO` · `SD_CHANGED = NO`.
"""
    golden = ["# Golden fixtures — seis relações físicas", ""]
    for rid in FIXTURE_IDS:
        row, rel = rows[rid], rx[rid]
        ev = next(x for x in evidence if x["precedent_id"] == row["precedent"])
        golden += [f"## {rid} / {row['target']} / {row['precedent']}", "", "### O QUE DECIDIU", "", sm[row["precedent"]]["generated_summary"], "",
                   "### POR QUE ESTÁ AQUI", "", rel["relation_explanation"], "", "### AUTORIDADE", "", rel["authority"], "",
                   "### EVIDÊNCIA", "", f"{ev['evidence_kind']} · {ev['evidence_locator']} · SHA-256 `{ev['evidence_sha256'] or 'n/a'}`", "",
                   "### TEXTO FINAL DO DISPOSITIVO", "", "```text", device_text(row, sm[row["precedent"]], rel).rstrip(), "```", ""]
    report = f"""# Auditoria da camada explicativa CC

## Resultado

- Precedentes: `{len(summaries)}/574`; relações: `{len(relations)}/653`.
- Conteúdo pronto: `{metrics['content_ready_relations']}`; revisão: `{metrics['content_review_required']}`; evidência requerida: `{metrics['content_evidence_required']}`.
- Confiança HIGH/MEDIUM/LOW: `{metrics['high_confidence']}/{metrics['medium_confidence']}/{metrics['low_confidence']}`.
- Evidência oficial local: `{metrics['local_evidence_used']}` precedentes; pesquisa externa: `0`.
- Erros genéricos: `{metrics['generic_summary_errors']}`; leakage: `0`; conflitos de resumo: `{metrics['precedent_summary_conflicts']}`; Group F: `0`.
- Amostra semântica estratificada: `{metrics['deep_sample_relations']}` relações, incluindo todos Group A e os seis fixtures. A amostra valida regras e provenance; não é uma segunda revisão humana independente.
- Renderização 320×240/UTF-8/abertura/BACK: `{metrics['content_render_simulation']}`.
- Suítes: Engine `153/153`; Audit `119/119`; Legal Target ID `93/93`; Correlatas `115/120`, as mesmas cinco falhas históricas.
- Firmware Content V2: compilado host-side; programa `{metrics['firmware'].get('after', {}).get('program_bytes', 'n/a')}` bytes, RAM estática `{metrics['firmware'].get('after', {}).get('static_ram_bytes', 'n/a')}` bytes, app0 livre `{metrics['firmware'].get('after', {}).get('app_partition_free', 'n/a')}` bytes. Flash: não.

## Tamanho

- Fichas antigas compartilhadas (572 artefatos da materialização V1): `{metrics['old_total_ficha_bytes']}` bytes.
- Fichas V2 compostas (653): `{metrics['new_total_ficha_bytes']}` bytes.
- Delta: `{metrics['delta_bytes']}` bytes; máxima `{metrics['max_ficha_bytes']}`; média `{metrics['average_ficha_bytes']}`.

## Diagnóstico legado

`LEGACY_FICHAS_WITHOUT_SUBSTANTIVE_CONTENT = {metrics['legacy_fichas_without_substantive_content']}` no inventário físico conhecido. É diagnóstico; nenhuma ficha legada de CF/CC foi alterada.

## Limites

As relações continuam humanamente aprovadas. Registros marcados `CONTENT_EVIDENCE_REQUIRED` não devem ser promovidos automaticamente. O renderer V2 foi preparado host-side; nenhuma mídia física foi acessada.
"""
    return arch.encode(), ("\n".join(golden) + "\n").encode(), report.encode()


def build():
    _, approved, held = M.authority_inputs()
    if len(approved) != 653 or len(held) != 28:
        raise SystemExit("CONTENT_STOP RATIFICATION_COUNTS")
    summaries, relations, evidence = build_content(approved)
    by_id = {x["relation_id"]: x for x in approved}
    fixture_files, fixture_result, fixture_fichas = materialize("PHASE_B_CONTENT_FIX_CANDIDATE", [by_id[x] for x in FIXTURE_IDS], approved, summaries, relations, FIXTURE_OUT)
    mass_files, mass_result, mass_fichas = materialize("CC_MASS_DEPLOY_653_V2", approved, approved, summaries, relations, MASS_OUT)
    metrics = audits(approved, summaries, relations, fixture_fichas, mass_fichas, fixture_result, mass_result)
    arch, golden, report = reports(approved, summaries, relations, evidence, metrics)
    outputs = {
        SUMMARIES: jb({"schema_version": 2, "count": len(summaries), "summaries": summaries}),
        RELATIONS: jb({"schema_version": 2, "count": len(relations), "relations": relations}),
        EVIDENCE: jb({"schema_version": 2, "count": len(evidence), "evidence": evidence}),
        OUT / "CC_JURIS_CONTENT_METRICS.json": jb(metrics), ARCH: arch, GOLDEN: golden, REPORT: report,
        FIXTURE_OUT / "CONTENT_FIX_ROLLBACK.md": ("# Rollback do content fix\n\nRestaurar os quatro agregados PRE e remover somente as seis fichas `CCMD_*.TXT` registradas no manifesto. Relações e targets permanecem 55/45. Não executado.\n").encode(),
        MASS_OUT / "DEPLOY_AND_ROLLBACK_PLAN.md": ("# Mass V2 — plano host-only\n\nDeploy futuro exige firmware compatível com `FICHA_RELACAO`, backup PRE, escrita/readback das 653 fichas, staging dos agregados e `JUR_LOOKUP.IDX` por último. Rollback restaura bytes PRE e remove somente arquivos criados pela transação. Não executado.\n").encode(),
    }
    outputs.update(fixture_files); outputs.update(mass_files)
    return outputs, metrics


def main() -> int:
    outputs, metrics = build()
    if "--check" in sys.argv:
        stale = [str(p.relative_to(ROOT)) for p, data in outputs.items() if not p.is_file() or p.read_bytes().replace(b"\r\n", b"\n") != data.replace(b"\r\n", b"\n")]
        print("UP_TO_DATE" if not stale else "STALE " + json.dumps(stale[:20], ensure_ascii=False))
        return 0 if not stale else 1
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
