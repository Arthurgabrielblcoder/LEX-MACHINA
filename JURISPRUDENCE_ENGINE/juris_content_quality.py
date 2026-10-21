"""Validadores determinísticos da camada editorial de jurisprudência.

O módulo não decide pertinência jurídica. Ele rejeita artefatos editoriais
objetivos (fragmentos, cortes, enumerações quebradas e cópia de cabeçalho) e
fornece utilitários conservadores para selecionar frases completas da fonte.
"""
from __future__ import annotations

import re


LOWER = "a-záàâãéêíóôõúüç"
UPPER = "A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ"
FINAL = re.compile(r"[.!?;:’'\"”)]$")
INCOMPLETE_END = re.compile(
    r"\b(?:a|ao|aos|as|com|como|da|das|de|do|dos|e|em|entre|mas|na|nas|no|nos|o|ou|para|pela|pelas|pelo|pelos|por|que|se|sem|um|uma)$",
    re.I,
)
RAW_PREFIX = re.compile(
    r"^(?:ementa|acórdão|relatório|a pretensão recursal|a sentença|prejudicam-se as demais alegações|quest(?:ão|ões) em discussão|o objetivo recursal|o propósito recursal|objetivo recursal|propósito recursal|recurso especial|agravo(?: interno)?(?: em recurso especial)?|processual civil|direito civil)\b",
    re.I,
)
ARTICLE_FRAGMENT = re.compile(r"^(?:[º°§,;:.]|do\s+(?:cpc|cc)\b|art\.\s*\d+[,;])", re.I)
ENUMERATION = re.compile(r"^(?:\(?\d{1,2}(?:\.\d{1,2})?(?:[.)]|-)?|\(?[ivx]{1,6}[.)]|\(?[a-z][.)])\s+", re.I)
TEMPLATE_LIKE = re.compile(
    r"^(?:O vínculo com o art\.|O art\..*consta da referência legislativa|A relação com o art\..*decorre deste fundamento)",
    re.I,
)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip(" \n\t")


def _quote_unbalanced(text: str) -> bool:
    if text.count("“") != text.count("”"):
        return True
    # Aspas retas internas são comuns nas fontes. Contamos apenas as que não
    # funcionam como apóstrofo entre letras.
    straight = re.sub(r"(?<=\w)'(?=\w)", "", text).count('"')
    return straight % 2 == 1


def quality_flags(text: str, *, relation: bool = False, target_label: str = "") -> list[str]:
    value = compact(text)
    flags: set[str] = set()
    if not value:
        return ["INCOMPLETE_SENTENCE", "RAW_EXCERPT_NOT_SUMMARY"]
    if re.match(fr"^[{LOWER}]", value):
        flags.update(("LEADING_FRAGMENT", "SUSPICIOUS_LOWERCASE_START"))
    if ARTICLE_FRAGMENT.match(value):
        flags.update(("LEADING_FRAGMENT", "SUSPICIOUS_ARTICLE_FRAGMENT"))
    if re.match(r"^\d+\s*[,;:]", value):
        flags.add("LEADING_FRAGMENT")
    if re.match(r"^E(?:,|\s+(?:esta|este|isso|por outro lado)\b)", value):
        flags.add("LEADING_FRAGMENT")
    if ENUMERATION.match(value):
        flags.add("BROKEN_ENUMERATION")
    if "..." in value or "…" in value or "[corte]" in value.lower() or "[trunc" in value.lower():
        flags.add("TRAILING_FRAGMENT")
    if value.count("(") != value.count(")"):
        flags.add("UNBALANCED_PARENTHESES")
    if _quote_unbalanced(value):
        flags.add("UNBALANCED_QUOTES")
    if not FINAL.search(value) or INCOMPLETE_END.search(value):
        flags.update(("INCOMPLETE_SENTENCE", "ABRUPT_END"))
    if re.search(r"\b(?:e|de|do|da|dos|das|em|por|para|inc|aut|cons|su|explor|parti|resoluçã)\.$", value, re.I):
        flags.update(("TRAILING_FRAGMENT", "ABRUPT_END"))
    if re.search(r"(?:;|\.)\s*[IVX]{1,6}\.$", value):
        flags.update(("BROKEN_ENUMERATION", "ABRUPT_END"))
    words = re.findall(fr"[{LOWER}{UPPER}]+", value)
    if words and len(words[-1]) <= 4 and not FINAL.search(value) and words[-1].lower() not in {"lei", "stj", "stf", "cpc", "civil"}:
        flags.add("TRAILING_FRAGMENT")
    letters = [c for c in value if c.isalpha()]
    upper_ratio = sum(c.isupper() for c in letters) / max(1, len(letters))
    numbered_blocks = len(re.findall(r"(?:^|[.!?]\s+)\d{1,2}\.\s", value))
    if RAW_PREFIX.match(value) or upper_ratio > .62 or numbered_blocks >= 2:
        flags.add("RAW_EXCERPT_NOT_SUMMARY")
    if re.search(r"\b(?:Tese de julgamento|Dispositivos relevantes citados|Jurisprudência relevante citada):", value, re.I):
        flags.add("RAW_EXCERPT_NOT_SUMMARY")
    if re.search(r"(?:^|[;.]\s+)[IVX]{1,6}\.\s", value):
        flags.add("BROKEN_ENUMERATION")
    prefix = value[:55].lower()
    if len(prefix) >= 45 and value.lower().find(prefix, 45) >= 0:
        flags.add("DUPLICATED_CLAUSE")
    if relation:
        if TEMPLATE_LIKE.match(value):
            flags.add("TEMPLATE_LIKE_EXPLANATION")
        if target_label and target_label.lower() not in value.lower():
            flags.add("TARGET_NOT_IDENTIFIED")
        if len(value) < 70:
            flags.add("GENERIC_OR_CIRCULAR_EXPLANATION")
    return sorted(flags)


def sentences(text: str) -> list[str]:
    """Separa somente em fronteiras fortes e preserva abreviações jurídicas."""
    value = compact(text).replace(" ? ", " — ")
    value = re.sub(
        r"\b(art|arts|inc|incs|n|ns|p|pp|vol|rel|resp|aresp|edcl|agint)\.",
        lambda m: m.group(1) + "§DOT§",
        value,
        flags=re.I,
    )
    value = re.sub(r"\s+-\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ])", ". ", value)
    value = re.sub(r"(?<=[.!?])(?=[IVX]{1,6}\s*[-–]\s*)", " ", value)
    parts = re.split(
        fr"(?<=[.!?])\s+(?=(?:(?:\d{{1,2}}(?:\.\d{{1,2}})?(?:[.)]|-)?|[IVX]{{1,6}}\s*[-–])\s+)?[\"“]?[{UPPER}])",
        value,
    )
    out = []
    for part in parts:
        item = compact(re.sub(r"^(?:\(?\d{1,2}(?:\.\d{1,2})?(?:[.)]|-)?|\(?[ivx]{1,6}(?:[.)]|\s*[-–]))\s+", "", part, flags=re.I)).replace("§DOT§", ".")
        if item:
            out.append(item)
    return out


def complete(text: str) -> str:
    value = compact(text).strip(" -–—")
    value = re.sub(r"^(?:\(?\d{1,2}(?:\.\d{1,2})?(?:[.)]|-)?|\(?[ivx]{1,6}(?:[.)]|\s*[-–]))\s+", "", value, flags=re.I)
    if not value:
        return value
    if re.match(fr"^[{LOWER}]", value):
        value = value[0].upper() + value[1:]
    if not FINAL.search(value):
        value += "."
    return value


def collapse_duplicated_clause(text: str) -> str:
    """Remove repetição literal longa introduzida pela junção da fonte."""
    value = compact(text)
    prefix = value[:55]
    if len(prefix) < 45:
        return value
    second = value.lower().find(prefix.lower(), 45)
    if second < 0:
        return value
    before = value[:second].strip(" -–—")
    parts = sentences(before)
    intact = [part for part in parts if FINAL.search(part) and not quality_flags(part)]
    return intact[0] if intact else complete(before)


def bounded_complete(parts: list[str], ideal: int = 450, hard: int = 900) -> str:
    """Combina frases inteiras; jamais corta palavra ou oração para caber."""
    chosen: list[str] = []
    for part in parts:
        item = complete(part)
        if not item:
            continue
        proposed = " ".join(chosen + [item])
        if chosen and len(proposed) > ideal:
            break
        chosen.append(item)
        if len(proposed) >= 180:
            break
    value = " ".join(chosen)
    if len(value) <= hard:
        return value
    # Uma frase íntegra acima do ideal é preferível a qualquer truncamento.
    return complete(chosen[0])


def template_like(text: str) -> bool:
    return bool(TEMPLATE_LIKE.match(compact(text)))
