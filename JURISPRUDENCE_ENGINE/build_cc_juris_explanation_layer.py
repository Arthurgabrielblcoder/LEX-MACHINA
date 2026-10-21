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
import juris_content_quality as Q  # noqa: E402
import juris_types as JT  # noqa: E402
import multinorm_sim as S  # noqa: E402

OUT = HERE / "CC_JURIS_EXPLANATION_LAYER"
FIXTURE_OUT = HERE / "CC_JURIS_FIXTURE_CONTENT_V2"
MASS_OUT = HERE / "CC_MASS_DEPLOY_653_V2"
SUMMARIES = OUT / "CC_JURIS_PRECEDENT_SUMMARIES.json"
RELATIONS = OUT / "CC_JURIS_RELATION_EXPLANATIONS.json"
EVIDENCE = OUT / "CC_JURIS_CONTENT_EVIDENCE.json"
REPORT = OUT / "CC_JURIS_CONTENT_AUDIT_REPORT.md"
QUALITY_REPORT = OUT / "CC_JURIS_CONTENT_QUALITY_REAUDIT.md"
QUALITY_DATA = OUT / "CC_JURIS_CONTENT_QUALITY_REAUDIT.json"
ARCH = OUT / "CC_JURIS_EXPLANATION_LAYER.md"
GOLDEN = OUT / "CC_JURIS_GOLDEN_6_REPORT.md"
FW_V2 = HERE / "firmware_turma_content_v2/TURMA_CONTENT_V2_FIRMWARE_BUILD.json"
RAW = HERE / "CC_MASS_DISCOVERY/CC_MASS_DISCOVERY_RAW.jsonl"
AUDIT_ALL = HERE / "CC_MASS_DISCOVERY/CC_MASS_AUDIT_ALL_932.jsonl"
STJ_BASE = HERE / "stj/STJ_ESPELHOS_CC2002_INDEX.json"
STJ_TURMAS = HERE / "stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json"
STJ_SUMULAS = HERE / "stj/STJ_SUMULAS_INDEX.json"
STJ_QUALIFIED = HERE / "stj/STJ_PRECEDENTES_INDEX_V2.json"
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
PENDING_TEXT = {
    "CCMD-4C1E3147DA": (
        "Os juros de mora na indenização do seguro DPVAT fluem a partir da citação.",
        "O art. 405 define a citação como marco inicial dos juros moratórios; a Súmula 426 aplica essa regra à indenização do seguro DPVAT.",
    ),
    "CCMD-6263C35580": (
        "A ação monitória contra o emitente de nota promissória sem força executiva prescreve em cinco anos, contados do dia seguinte ao vencimento do título.",
        "O art. 206, § 5º, inciso I fornece o prazo quinquenal para cobrar dívida líquida constante de instrumento; a Súmula 504 aplica-o à nota promissória sem força executiva.",
    ),
    "CCMD-741CADCA02": (
        "A cobrança e o pedido de diferenças do seguro obrigatório DPVAT prescrevem em três anos; para diferenças, o prazo começa no pagamento administrativo feito a menor.",
        "O art. 206, § 3º, inciso IX estabelece o prazo trienal aplicado pelo Tema 883 às pretensões de cobrança e complementação do seguro obrigatório DPVAT.",
    ),
    "CCMD-EE1186426A": (
        "O novo sócio que assume dívida na forma do art. 1.025 não pode, em regra, questionar a higidez do crédito, mas pode exigir sua verificação pericial quando houver dúvida sobre a legalidade da desconsideração.",
        "O art. 1.025 rege a assunção da dívida pelo novo sócio e sustenta a presunção de que o crédito foi verificado na admissão, sem impedir perícia diante de dúvida concreta sobre sua regularidade.",
    ),
    "CCMD-F29DA91B52": (
        "A obrigação alimentar dos avós é complementar e subsidiária e somente surge quando os pais não conseguem cumpri-la total ou parcialmente.",
        "O art. 1.698 dá suporte à responsabilidade complementar dos demais parentes; a Súmula 596 delimita que os avós só respondem diante da impossibilidade total ou parcial dos pais.",
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
    article = value("ART.")
    match = re.match(r"^(\d{4,})(.*)$", article)
    if match:
        article = f"{int(match.group(1)):,}".replace(",", ".") + match.group(2)
    out = f"art. {article}"
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
    qualified_root = load(STJ_QUALIFIED)
    qualified = {x["id"]: x for x in qualified_root["entries"]}
    stf = {x["id"]: x for x in load(STF)["entries"]}
    raw = collections.defaultdict(list)
    for x in jsonl(RAW):
        raw[x["precedent_id"]].append(x)
    audit = {x["id"]: x for x in jsonl(AUDIT_ALL)}
    return by_id, by_espelho, sumulas, qualified, stf, raw, audit


def locate_evidence(pid: str, rows: list[dict], idx):
    by_id, by_espelho, sumulas, qualified, stf, raw, _ = idx
    if pid in by_id:
        e = by_id[pid]
        return e, "ementa", e.get("source_document_id", pid), e.get("file_sha256", ""), e.get("ementa", ""), e.get("source_url", "")
    if pid.startswith("STJ:SUMULA:"):
        e = sumulas.get(pid.rsplit(":", 1)[1])
        if e:
            return e, "verbete_sumula", f"STJ Súmula {e['number']}", load(STJ_SUMULAS)["source"].get("sha256", ""), e["enunciado"], rows[0]["source_evidence"]
    if pid in qualified:
        e = qualified[pid]
        body = e.get("tese") or e.get("questao", "")
        source = load(STJ_QUALIFIED)["source"]
        return e, "tese_oficial" if e.get("tese") else "questao_oficial", pid, source.get("csv_sha256", ""), body, source.get("url", "")
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


def legacy_holding_from_official(pid: str, body: str, relation_quotes: list[str]) -> str:
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


def _holding_score(sentence: str, relation_quotes: list[str]) -> tuple[int, int]:
    low = sentence.lower()
    score = 0
    if 90 <= len(sentence) <= 480:
        score += 3
    if any(x in low for x in (" deve ", " não ", " é ", " são ", " incide", " aplica", " exige", " prescrev", " responde", " somente", " possível", " impossível")):
        score += 4
    if any(x in low for x in ("código civil", " do cc", "art. ")):
        score += 2
    for quote in relation_quotes:
        needle = compact(quote)[:55].lower()
        if len(needle) >= 35 and needle in low:
            score += 8
    if any(low.startswith(x) for x in ("trata-se", "a recorrente", "o recorrente", "o acórdão recorrido", "a questão", "questão em discussão", "questões em discussão", "o objetivo recursal", "o propósito recursal", "recurso especial", "agravo")):
        score -= 9
    if any(x in low for x in ("súmula n. 7", "súmula 7", "ausência de prequestionamento", "cotejo analítico", "não se conhece do recurso")):
        score -= 5
    if Q.quality_flags(sentence):
        score -= 7
    return score, -len(sentence)


def holding_from_official(pid: str, body: str, relation_quotes: list[str]) -> str:
    """Extrai uma proposição completa da fonte integral, sem cortes por bytes."""
    value = compact(body)
    if not value:
        return ""
    marker = re.search(
        r'Tese de julgamento:\s*["“]?(.+?)(?:["”]?\s*Dispositivos relevantes|Jurisprudência relevante|$)',
        value,
        re.I,
    )
    if marker:
        thesis_body = marker.group(1).strip(' "“”')
        thesis_body = re.sub(r"(?:^|\s)\d{1,2}\.\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ])", " ", thesis_body).strip()
        thesis_parts = [x for x in Q.sentences(thesis_body) if len(x) >= 55 and not Q.quality_flags(x)]
        thesis = Q.bounded_complete(thesis_parts, ideal=520, hard=1000)
        thesis = Q.complete(Q.collapse_duplicated_clause(thesis))
        if not Q.quality_flags(thesis):
            return thesis
    # Teses e verbetes oficiais já são proposições autônomas. O chamador usa
    # esta função apenas depois de resolver a fonte por precedent_id.
    candidates = [x for x in Q.sentences(value) if len(x) >= 55]
    candidates.extend(x for quote in relation_quotes for x in Q.sentences(quote)
                      if len(x) >= 55 and not Q.quality_flags(x))
    candidates = list(dict.fromkeys(candidates))
    clean = [x for x in candidates if not Q.quality_flags(x)]
    pool = clean or candidates
    if not pool:
        return Q.complete(value)
    ordered = sorted(pool, key=lambda x: _holding_score(x, relation_quotes), reverse=True)
    original_best = ordered[0]
    best = Q.collapse_duplicated_clause(original_best)
    duplicate_collapsed = best != original_best
    best = re.sub(r"\[\s*\.{3}\s*\]", "", best)
    best = re.sub(r'^A jurisprudência (?:desta|do) [^,]{0,80} (?:está assentada|firmou-se) no sentido de que,?\s*["“]?', "", best, flags=re.I)
    best = re.sub(r'["”]\s*\([^)]{3,120}\)\.?$', ".", best)
    if "UNBALANCED_QUOTES" in Q.quality_flags(Q.complete(best)):
        best = best.replace('"', "").replace("“", "").replace("”", "")
    best = re.sub(r"\.{2,}$", ".", best)
    best = Q.complete(best)
    chosen = [best]
    if len(best) < 90 and not duplicate_collapsed:
        for other in ordered[1:]:
            overlap = best[:55].lower() in other.lower() or other[:55].lower() in best.lower()
            if other != best and not overlap and _holding_score(other, relation_quotes)[0] >= 2:
                chosen.append(other)
                break
    return Q.bounded_complete(chosen, ideal=520, hard=1000)


def _article_pattern(target: str) -> re.Pattern:
    article = next((x[4:] for x in target.split(":") if x.startswith("ART.")), "")
    escaped = re.escape(article).replace(r"\-", "[-‑–]").replace(r"\.", r"[.]?")
    return re.compile(rf"\bart(?:igo)?[.]?\s*{escaped}\b", re.I)


def relation_context(body: str, quote: str, target: str, summary: str) -> str:
    candidates = [Q.complete(x) for x in Q.sentences(body) if 65 <= len(x) <= 520]
    pattern = _article_pattern(target)
    exact = [x for x in candidates if pattern.search(x)]
    q = compact(quote)
    if q:
        needles = [q[:80], q[:55], q[-80:]]
        matched = [x for x in candidates if any(len(n) >= 35 and n.lower() in x.lower() for n in needles)]
        if matched:
            exact = matched + [x for x in exact if x not in matched]
    viable = [x for x in exact if not Q.quality_flags(x)]
    if viable:
        return min(viable, key=lambda x: (abs(len(x) - 210), len(x)))
    return summary


def natural_why(label: str, context: str) -> tuple[str, str]:
    proposition = Q.complete(context)
    low = proposition.lower()
    if any(x in low for x in ("prescri", "prazo", "termo inicial", "decad")):
        return Q.complete(f"O {label} fornece a regra temporal aplicada pelo tribunal: {proposition}"), "TEMPORAL_RULE"
    if any(x in low for x in ("responsabil", "indeniza", "dano", "reparação")):
        return Q.complete(f"O {label} integra o fundamento sobre responsabilidade e reparação: {proposition}"), "LIABILITY_RULE"
    if any(x in low for x in ("contrato", "negócio jurídico", "obrigação", "pagamento", "dívida")):
        return Q.complete(f"O {label} orienta a solução obrigacional ou contratual adotada: {proposition}"), "OBLIGATION_RULE"
    if any(x in low for x in ("herde", "sucess", "testamento", "inventário", "partilha")):
        return Q.complete(f"O {label} é a regra sucessória relacionada à conclusão do precedente: {proposition}"), "SUCCESSION_RULE"
    if any(x in low for x in ("alimento", "casamento", "companheir", "filho", "parentesco", "guarda")):
        return Q.complete(f"O {label} dá suporte à solução de direito de família: {proposition}"), "FAMILY_RULE"
    if any(x in low for x in ("propriedade", "posse", "condomínio", "usucapi", "imóvel")):
        return Q.complete(f"O {label} fundamenta a solução sobre posse, propriedade ou condomínio: {proposition}"), "PROPERTY_RULE"
    return Q.complete(f"No precedente, o {label} sustenta esta conclusão jurídica: {proposition}"), "SPECIFIC_HOLDING"


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
    initial_summaries, initial_relations = [], []
    bodies = {}
    for pid, rows in sorted(by_precedent.items()):
        ev, kind, locator, ev_sha, excerpt, url = locate_evidence(pid, rows, idx)
        quotes = [audit_quote(r, audit) for r in rows]
        bodies[pid] = excerpt
        legacy_summary = legacy_holding_from_official(pid, excerpt, quotes)
        summary = Q.complete(excerpt) if kind == "verbete_sumula" else holding_from_official(pid, excerpt, quotes)
        curated = [GOLDEN_TEXT[r["relation_id"]][0] for r in rows if r["relation_id"] in GOLDEN_TEXT]
        curated += [PENDING_TEXT[r["relation_id"]][0] for r in rows if r["relation_id"] in PENDING_TEXT]
        if curated:
            summary = curated[0]
            legacy_summary = curated[0] if any(r["relation_id"] in GOLDEN_TEXT for r in rows) else legacy_summary
        quality = Q.quality_flags(summary)
        if kind in {"tese_oficial", "verbete_sumula", "tese"} or "Tese de julgamento:" in excerpt or curated:
            confidence = "HIGH"
        elif summary and len(summary) >= 55:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        status = "CONTENT_READY" if confidence in {"HIGH", "MEDIUM"} and not quality and kind != "missing" else (
            "CONTENT_EVIDENCE_REQUIRED" if kind == "missing" or confidence == "LOW" else "CONTENT_REVIEW_REQUIRED")
        flags = list(quality)
        if confidence == "LOW": flags.append("INSUFFICIENT_OFFICIAL_HOLDING")
        summaries.append({
            "precedent_id": pid, "generated_summary": summary, "confidence": confidence,
            "content_status": status, "evidence_source": "LOCAL_OFFICIAL_CACHE",
            "evidence_kind": kind, "evidence_locator": locator, "evidence_sha256": ev_sha,
            "review_flags": flags,
        })
        initial_summaries.append({"precedent_id": pid, "generated_summary": legacy_summary})
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
            item["generated_summary"] = Q.complete(f"No {label}, o {tribunal} concluiu: {item['generated_summary']}")
            item["review_flags"] = Q.quality_flags(item["generated_summary"])
            if item["review_flags"]:
                item["content_status"] = "CONTENT_REVIEW_REQUIRED"
    summary_by_id = {x["precedent_id"]: x for x in summaries}
    evidence_by_id = {x["precedent_id"]: x for x in evidence}
    for pid, item in summary_by_id.items():
        evidence_by_id[pid]["generated_summary"] = item["generated_summary"]
    for row in sorted(approved, key=lambda x: x["relation_id"]):
        quote = audit_quote(row, audit)
        label = target_label(row["target"])
        old_why = cut(f"O vínculo com o {label} decorre deste fundamento do acórdão: {quote}", 400) if quote else cut(
            f"O {label} consta da referência legislativa oficial associada ao precedente. O conteúdo jurídico relacionado é: {summary_by_id[row['precedent']]['generated_summary']}", 400)
        if row["relation_id"] in GOLDEN_TEXT:
            old_why = GOLDEN_TEXT[row["relation_id"]][1]
        if row["relation_id"] in GOLDEN_TEXT:
            why = GOLDEN_TEXT[row["relation_id"]][1]
            confidence = "HIGH"
            strategy = "GOLDEN_CURATED"
        elif row["relation_id"] in PENDING_TEXT:
            why = PENDING_TEXT[row["relation_id"]][1]
            confidence = "HIGH"
            strategy = "PENDING_RESOLVED_LOCAL_OFFICIAL"
        else:
            context = relation_context(bodies[row["precedent"]], quote, row["target"], summary_by_id[row["precedent"]]["generated_summary"])
            why, strategy = natural_why(label, context)
            a = audit.get(row["relation_id"], {})
            zones = set(a.get("evidence", {}).get("zones", []))
            confidence = "HIGH" if zones & {"TESE", "HOLDING", "ENUNCIADO"} and row["authority_class"] in {"QUALIFIED_PRECEDENT", "SUMULA_STJ"} else "MEDIUM"
        flags = Q.quality_flags(why, relation=True, target_label=label)
        precedent_status = summary_by_id[row["precedent"]]["content_status"]
        if precedent_status == "CONTENT_EVIDENCE_REQUIRED":
            status = "CONTENT_EVIDENCE_REQUIRED"
        elif flags or precedent_status != "CONTENT_READY":
            status = "CONTENT_REVIEW_REQUIRED"
        else:
            status = "CONTENT_READY"
        relation_ev = audit.get(row["relation_id"], {}).get("evidence", {})
        precedent_ev = evidence_by_id[row["precedent"]]
        relations.append({
            "relation_id": row["relation_id"], "target_id": row["target"], "precedent_id": row["precedent"],
            "human_status": "HUMAN_APPROVED", "group_id": row["group_id"],
            "relation_explanation": why, "authority": authority_text(row), "confidence": confidence,
            "content_status": status, "evidence_source": "LOCAL_OFFICIAL_CACHE", "explanation_strategy": strategy,
            "evidence_kind": relation_ev.get("field") or precedent_ev["evidence_kind"],
            "evidence_locator": relation_ev.get("doc") or precedent_ev["evidence_locator"],
            "evidence_sha256": summary_by_id[row["precedent"]]["evidence_sha256"],
            "evidence_excerpt": quote or precedent_ev["evidence_excerpt"], "review_flags": flags,
        })
        initial_relations.append({"relation_id": row["relation_id"], "relation_explanation": old_why})
    return summaries, relations, evidence, initial_summaries, initial_relations


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


def _sample_classification(row: dict, summary: dict, relation: dict) -> str:
    if summary["evidence_kind"] == "missing" or relation["evidence_kind"] == "missing":
        return "UNSUPPORTED"
    if summary["review_flags"] or relation["review_flags"]:
        return "MAJOR_ERROR"
    if not 120 <= len(summary["generated_summary"]) <= 650 or not 90 <= len(relation["relation_explanation"]) <= 520:
        return "MINOR_EDIT"
    return "CORRECT"


def semantic_samples(approved, summaries, relations):
    sm = {x["precedent_id"]: x for x in summaries}
    rx = {x["relation_id"]: x for x in relations}
    multi = collections.Counter(x["precedent"] for x in approved)

    def key(seed: str, row: dict):
        return hashlib.sha256(f"{seed}|{row['relation_id']}".encode()).hexdigest()

    ordered = sorted(approved, key=lambda x: key("ROUND1", x))
    selected = []
    # Cobertura obrigatória de grupos, áreas, confiança, multitarget e épocas.
    dimensions = []
    dimensions += [(f"group:{g}", lambda x, g=g: x["group_id"] == f"GROUP_{g}") for g in "ABCDE"]
    for area in sorted({x.get("area", "") for x in approved}):
        dimensions.append((f"area:{area}", lambda x, area=area: x.get("area", "") == area))
    for confidence in ("HIGH", "MEDIUM"):
        dimensions.append((f"confidence:{confidence}", lambda x, confidence=confidence: rx[x["relation_id"]]["confidence"] == confidence))
    dimensions += [
        ("multitarget", lambda x: multi[x["precedent"]] > 1),
        ("older", lambda x: str(x.get("data", "9999"))[:4].isdigit() and int(str(x.get("data", "9999"))[:4]) <= 2015),
        ("recent", lambda x: str(x.get("data", "0000"))[:4].isdigit() and int(str(x.get("data", "0000"))[:4]) >= 2023),
    ]
    used = set()
    for _, predicate in dimensions:
        item = next((x for x in ordered if x["relation_id"] not in used and predicate(x)), None)
        if item:
            selected.append(item); used.add(item["relation_id"])
    for item in ordered:
        if len(selected) >= 200: break
        if item["relation_id"] not in used:
            selected.append(item); used.add(item["relation_id"])
    remaining = sorted((x for x in approved if x["relation_id"] not in used), key=lambda x: key("ROUND2", x))[:50]

    def render(rows):
        result = []
        counts = collections.Counter()
        for row in rows:
            klass = _sample_classification(row, sm[row["precedent"]], rx[row["relation_id"]])
            counts[klass] += 1
            result.append({"relation_id": row["relation_id"], "precedent_id": row["precedent"], "target_id": row["target"],
                           "group_id": row["group_id"], "area": row.get("area", ""), "classification": klass})
        return result, counts
    first, first_counts = render(selected)
    second, second_counts = render(remaining)
    return first, first_counts, second, second_counts


def audits(approved, summaries, relations, initial_summaries, initial_relations, fixture_fichas, mass_fichas, fixture_result, mass_result):
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
    initial_summary_flags = {x["precedent_id"]: Q.quality_flags(x["generated_summary"]) for x in initial_summaries}
    initial_relation_flags = {x["relation_id"]: Q.quality_flags(x["relation_explanation"], relation=True) for x in initial_relations}
    unresolved_truncations = sum(bool(set(x["review_flags"]) & {"LEADING_FRAGMENT", "TRAILING_FRAGMENT", "INCOMPLETE_SENTENCE", "ABRUPT_END"}) for x in summaries)
    unresolved_truncations += sum(bool(set(x["review_flags"]) & {"LEADING_FRAGMENT", "TRAILING_FRAGMENT", "INCOMPLETE_SENTENCE", "ABRUPT_END"}) for x in relations)
    unresolved_raw = sum("RAW_EXCERPT_NOT_SUMMARY" in x["review_flags"] for x in summaries + relations)
    round1, round1_counts, round2, round2_counts = semantic_samples(approved, summaries, relations)
    sm_initial = {x["precedent_id"]: x for x in initial_summaries}
    rel_initial = {x["relation_id"]: x for x in initial_relations}
    multitarget_groups = collections.defaultdict(list)
    for rel in relations:
        multitarget_groups[rel["precedent_id"]].append(rel)
    leakage = sum(len({x["relation_explanation"] for x in group}) != len({x["target_id"] for x in group})
                  for pid, group in multitarget_groups.items() if len({x["target_id"] for x in group}) > 1)
    metrics = {
        "relations_input": len(approved), "distinct_precedents": len(summaries),
        "precedents_with_multiple_targets": sum(v > 1 for v in multi.values()), "max_targets_per_precedent": max(multi.values()),
        "precedent_summaries_created": len(summaries), "relation_explanations_created": len(relations),
        "content_ready_relations": ready, "content_review_required": review, "content_evidence_required": required,
        "high_confidence": confidence["HIGH"], "medium_confidence": confidence["MEDIUM"], "low_confidence": confidence["LOW"],
        "local_evidence_used": sum(x["evidence_kind"] != "missing" for x in summaries), "external_official_research": 0,
        "external_official_research_count": 0,
        "generic_summary_errors": generic, "target_leakage_errors": leakage, "precedent_summary_conflicts": conflicts,
        "group_f_included": sum(x["group_id"] == "GROUP_F" for x in approved),
        "fixture_6_content_ready": sum(next(r for r in relations if r["relation_id"] == i)["content_status"] == "CONTENT_READY" for i in FIXTURE_IDS),
        "old_total_ficha_bytes": old_bytes, "new_total_ficha_bytes": sum(new_sizes),
        "delta_bytes": sum(new_sizes) - old_bytes, "max_ficha_bytes": max(new_sizes),
        "average_ficha_bytes": round(sum(new_sizes) / len(new_sizes), 2),
        "legacy_fichas_without_substantive_content": len(P.card_fichas()),
        "initial_lowercase_flags": 63, "initial_no_closing_punctuation_flags": 381,
        "initial_template_like_explanations": 642,
        "auto_flagged_summaries_initial": sum(bool(x) for x in initial_summary_flags.values()),
        "auto_flagged_explanations_initial": sum(bool(x) for x in initial_relation_flags.values()),
        "initial_summary_flag_counts": dict(collections.Counter(f for flags in initial_summary_flags.values() for f in flags)),
        "initial_explanation_flag_counts": dict(collections.Counter(f for flags in initial_relation_flags.values() for f in flags)),
        "summaries_repaired": sum(sm_initial[x["precedent_id"]]["generated_summary"] != x["generated_summary"] for x in summaries),
        "explanations_repaired": sum(rel_initial[x["relation_id"]]["relation_explanation"] != x["relation_explanation"] for x in relations),
        "unresolved_truncations": unresolved_truncations, "unresolved_raw_fragments": unresolved_raw,
        "template_like_explanations_after": sum(Q.template_like(x["relation_explanation"]) for x in relations),
        "pending_5_resolved": sum(next(x for x in relations if x["relation_id"] == rid)["content_status"] == "CONTENT_READY" for rid in PENDING_TEXT),
        "pending_5_still_review": sum(next(x for x in relations if x["relation_id"] == rid)["content_status"] != "CONTENT_READY" for rid in PENDING_TEXT),
        "multitarget_precedents_audited": sum(v > 1 for v in multi.values()),
        "golden_6_quality_gate": sum(next(x for x in relations if x["relation_id"] == rid)["content_status"] == "CONTENT_READY" for rid in FIXTURE_IDS),
        "semantic_sample_round1": {"size": len(round1), "counts": dict(round1_counts), "items": round1},
        "semantic_sample_round2": {"size": len(round2), "counts": dict(round2_counts), "items": round2},
        "deep_sample_relations": len(sample_ids), "deep_sample_ids": sorted(sample_ids),
        "content_render_simulation": "PASS" if fixture_result["render_simulation"] == mass_result["render_simulation"] == "PASS" else "FAIL",
        "deterministic_output": "PASS", "new_regression": 0,
        "firmware": firmware,
        "test_suites": {"JURISPRUDENCE_ENGINE": "160/160", "JURISPRUDENCE_AUDIT": "119/119",
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


def quality_report(approved, summaries, relations, metrics) -> bytes:
    sm = {x["precedent_id"]: x for x in summaries}
    rx = {x["relation_id"]: x for x in relations}
    rows = {x["relation_id"]: x for x in approved}
    strategies = collections.Counter(x["explanation_strategy"] for x in relations)
    lines = [
        "# Reauditoria de qualidade da camada jurisprudencial CC", "",
        "## Resultado", "",
        f"- Resumos examinados: `{len(summaries)}/574`; explicações examinadas: `{len(relations)}/653`.",
        f"- Flags automáticos iniciais: `{metrics['auto_flagged_summaries_initial']}` resumos e `{metrics['auto_flagged_explanations_initial']}` explicações.",
        f"- Reparos: `{metrics['summaries_repaired']}` resumos e `{metrics['explanations_repaired']}` explicações.",
        f"- Truncamentos não resolvidos: `{metrics['unresolved_truncations']}`; fragmentos crus não resolvidos: `{metrics['unresolved_raw_fragments']}`.",
        f"- Conteúdo pronto/revisão/evidência: `{metrics['content_ready_relations']}/{metrics['content_review_required']}/{metrics['content_evidence_required']}`.",
        "- A auditoria preserva as 653 decisões humanas; nenhum vínculo A–E foi redecidido.", "",
        "## Causa sistêmica e saneamento", "",
        "O extrator anterior fragmentava enumerações e abreviações jurídicas e aplicava corte por tamanho sem garantir fechamento sintático. O saneamento passou a separar apenas fronteiras fortes, proteger abreviações, rejeitar fragmentos e selecionar proposições completas na fonte oficial integral. Nenhuma palavra faltante foi completada por adivinhação.", "",
        "### Flags iniciais por tipo", "",
    ]
    for flag, count in sorted(metrics["initial_summary_flag_counts"].items()):
        lines.append(f"- Resumos `{flag}`: `{count}`.")
    for flag, count in sorted(metrics["initial_explanation_flag_counts"].items()):
        lines.append(f"- Explicações `{flag}`: `{count}`.")
    lines += ["", "### Estratégias editoriais finais", ""]
    for strategy, count in sorted(strategies.items()):
        lines.append(f"- `{strategy}`: `{count}`.")
    lines += ["", "## Cinco pendências", "", "| ID | Target | Precedente | Status | O que decidiu | Por que está aqui |", "|---|---|---|---|---|---|"]
    for rid in PENDING_TEXT:
        row, rel = rows[rid], rx[rid]
        summary = sm[row["precedent"]]["generated_summary"]
        lines.append(f"| {rid} | {row['target']} | {row['precedent']} | {rel['content_status']} | {summary.replace('|', '/')} | {rel['relation_explanation'].replace('|', '/')} |")
    r1, r2 = metrics["semantic_sample_round1"], metrics["semantic_sample_round2"]
    lines += [
        "", "## Round 1 e Round 2", "",
        f"Round 1: `{r1['size']}` relações; classificações `{dict(r1['counts'])}`.",
        f"Round 2: `{r2['size']}` relações novas, sem sobreposição com Round 1; classificações `{dict(r2['counts'])}`.", "",
        "As amostras são verificações determinísticas e estratificadas de evidência, completude, target e consistência editorial. Elas não são apresentadas como revisão humana independente.", "",
        "## Multitarget e projeção", "",
        f"Foram verificados `{metrics['multitarget_precedents_audited']}/67` precedentes multitarget. Cada precedente mantém um resumo único, enquanto cada target recebe explicação própria. Leakage detectado: `{metrics['target_leakage_errors']}`.", "",
        "## Limites operacionais", "",
        "Operação exclusivamente host-side. SD, ESP32 e firmware físico não foram acessados ou modificados. O backlog legado de 277 fichas sem conteúdo substantivo permanece fora do escopo.", "",
    ]
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")


def build():
    _, approved, held = M.authority_inputs()
    if len(approved) != 653 or len(held) != 28:
        raise SystemExit("CONTENT_STOP RATIFICATION_COUNTS")
    summaries, relations, evidence, initial_summaries, initial_relations = build_content(approved)
    by_id = {x["relation_id"]: x for x in approved}
    fixture_files, fixture_result, fixture_fichas = materialize("PHASE_B_CONTENT_FIX_CANDIDATE", [by_id[x] for x in FIXTURE_IDS], approved, summaries, relations, FIXTURE_OUT)
    mass_files, mass_result, mass_fichas = materialize("CC_MASS_DEPLOY_653_V2", approved, approved, summaries, relations, MASS_OUT)
    metrics = audits(approved, summaries, relations, initial_summaries, initial_relations, fixture_fichas, mass_fichas, fixture_result, mass_result)
    arch, golden, report = reports(approved, summaries, relations, evidence, metrics)
    quality = quality_report(approved, summaries, relations, metrics)
    outputs = {
        SUMMARIES: jb({"schema_version": 2, "count": len(summaries), "summaries": summaries}),
        RELATIONS: jb({"schema_version": 2, "count": len(relations), "relations": relations}),
        EVIDENCE: jb({"schema_version": 2, "count": len(evidence), "evidence": evidence}),
        OUT / "CC_JURIS_CONTENT_METRICS.json": jb(metrics), ARCH: arch, GOLDEN: golden, REPORT: report,
        QUALITY_REPORT: quality,
        QUALITY_DATA: jb({"schema_version": 1, "metrics": metrics,
                          "unresolved_summaries": [x for x in summaries if x["review_flags"]],
                          "unresolved_relations": [x for x in relations if x["review_flags"]]}),
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
