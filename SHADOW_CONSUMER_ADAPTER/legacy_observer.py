"""Read-only CPython audit observer for the D05 legacy catalog consumer."""

from __future__ import annotations

import os
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


BOUNDARY = "LEGACY_SELECTION_COMPLETE_BEFORE_FIRST_FUNCTIONAL_OUTPUT_WRITE"


@dataclass(frozen=True)
class LegacyFileEvent:
    sequence: int
    audit_event: str
    operation: str
    mode: str
    path: str
    relative_to_d05: str | None


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _operation(mode: Any, flags: Any) -> str:
    rendered = "" if mode is None else str(mode)
    if any(char in rendered for char in "wax+"):
        return "WRITE"
    if isinstance(flags, int):
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        if flags & write_flags:
            return "WRITE"
    return "READ" if "r" in rendered or rendered == "" else "OTHER"


class LegacyObserver:
    """Records open events without changing arguments, returns, bytes, or errors."""

    def __init__(self, output_root: Path, d05_root: Path | None = None):
        self.output_root = Path(os.path.abspath(output_root))
        self.d05_root = Path(os.path.abspath(d05_root)) if d05_root else None
        self.events: list[LegacyFileEvent] = []
        self._sealed_events: tuple[LegacyFileEvent, ...] | None = None
        self.boundary_event: LegacyFileEvent | None = None

    @property
    def sealed(self) -> bool:
        return self._sealed_events is not None

    @property
    def selection_events(self) -> tuple[LegacyFileEvent, ...]:
        source = self._sealed_events if self._sealed_events is not None else tuple(self.events)
        return tuple(event for event in source if event.operation == "READ")

    def audit_hook(self, event: str, args: tuple[Any, ...]) -> None:
        if event != "open" or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        try:
            path = Path(os.path.abspath(os.fsdecode(args[0])))
        except (OSError, TypeError, ValueError):
            return
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else None
        operation = _operation(mode, flags)
        relative = None
        if self.d05_root and _within(path, self.d05_root):
            relative = path.relative_to(self.d05_root).as_posix()
        item = LegacyFileEvent(
            sequence=len(self.events) + 1,
            audit_event=event,
            operation=operation,
            mode="" if mode is None else str(mode),
            path=str(path),
            relative_to_d05=relative,
        )
        if operation == "WRITE" and _within(path, self.output_root) and not self.sealed:
            self._sealed_events = tuple(self.events)
            self.boundary_event = item
        self.events.append(item)

    def install(self) -> None:
        sys.addaudithook(self.audit_hook)

    def summary(self) -> dict[str, Any]:
        reads = list(self.selection_events)
        triage = [event.relative_to_d05 for event in reads if event.relative_to_d05 and event.relative_to_d05.startswith("02_TRIAGEM/LOTE_")]
        dossiers = [event.relative_to_d05 for event in reads if event.relative_to_d05 and event.relative_to_d05.startswith("04_DOSSIERS/")]
        wrapper = [event.relative_to_d05 for event in reads if event.relative_to_d05 == "00_ENTRADA/REFERENCIA_CATALOGO_69.json"]
        classified = set(triage + dossiers + wrapper)
        auxiliary = [event.relative_to_d05 or event.path for event in reads if (event.relative_to_d05 or event.path) not in classified]
        return {
            "boundary": BOUNDARY,
            "sealed": self.sealed,
            "boundary_event": asdict(self.boundary_event) if self.boundary_event else None,
            "event_count": len(reads),
            "events": [asdict(event) for event in reads],
            "sets": {
                "triage_batch_paths": {"observability": "MEMBER_LEVEL", "members": triage, "ordered": True},
                "base_catalog_work_ids": {
                    "observability": "MEMBER_LEVEL",
                    "members": [Path(item).stem for item in dossiers],
                    "paths": dossiers,
                    "ordered": True,
                },
                "triage_candidate_numbers": {"observability": "NOT_OBSERVABLE"},
                "catalog_69_ids": {"observability": "NOT_OBSERVABLE"},
            },
            "dependencies": ["CATALOG_69_EMBEDDED"] if wrapper else [],
            "dependency_reads": wrapper,
            "auxiliary_reads": auxiliary,
            "multiplicity": dict(Counter(event.relative_to_d05 or event.path for event in reads)),
        }
