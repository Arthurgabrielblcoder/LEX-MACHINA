"""Safe, non-canonical diagnostic helpers."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


SENSITIVE_KEY = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|authorization|credential|signature|sig)")
ASSIGNMENT = re.compile(r"(?i)\b(token|secret|password|passwd|api[_-]?key|authorization|credential|signature|sig)\s*[:=]\s*([^\s,;]+)")
URL = re.compile(r"https?://[^\s<>'\"]+")


def redact_sensitive(text: Any) -> str:
    rendered = str(text)
    rendered = ASSIGNMENT.sub(lambda match: f"{match.group(1)}=<redacted>", rendered)

    def strip_query(match: re.Match[str]) -> str:
        raw = match.group(0)
        try:
            parts = urlsplit(raw)
            return urlunsplit((parts.scheme, parts.netloc, parts.path, "<redacted>" if parts.query else "", ""))
        except ValueError:
            return "<redacted-url>"

    return URL.sub(strip_query, rendered)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, child in value.items():
            clean[str(key)] = "<redacted>" if SENSITIVE_KEY.search(str(key)) else sanitize(child)
        return clean
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return redact_sensitive(value)
    return value


def safe_binding_summary(bindings: dict[str, str]) -> list[dict[str, str]]:
    return [{"storage_root_id": root_id, "status": "PROVIDED"} for root_id in sorted(bindings)]


def write_diagnostic(path: Path, value: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = sanitize(value)
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_bytes(raw)
    os.replace(temporary, path)
