"""HUAP-inspired append-only JSONL trace with a local SHA-256 chain.

Hash-chain corruption is detectable against an independently trusted anchor;
without an external anchor, complete trace replacement remains possible.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Iterator


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"Not JSON serializable: {type(obj)!r}")


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, default=_json_default, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def _digest(envelope: dict) -> str:
    return hashlib.sha256(canonical_json(envelope).encode("utf-8")).hexdigest()


class AuditIntegrityError(ValueError):
    pass


class AuditLog:
    """Single-process writer. Do not share one path across multiple processes in v0.1."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.lock = RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._sequence = 0
        self._previous = "0" * 64
        if self.path.exists() and self.path.stat().st_size:
            events = list(verified_events(self.path))
            self._sequence = events[-1]["seq"]
            self._previous = events[-1]["hash"]

    def append(self, kind: str, data: dict) -> dict:
        with self.lock:
            event = {
                "v": "samanvaya.audit.v0.1", "seq": self._sequence + 1,
                "ts": datetime.now(timezone.utc).isoformat(),
                "kind": kind, "data": data, "previous_hash": self._previous,
            }
            event["hash"] = _digest(event)
            line = canonical_json(event) + "\n"
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
            self._sequence += 1
            self._previous = event["hash"]
            return event


def verified_events(path: str | Path) -> Iterator[dict]:
    previous = "0" * 64
    expected_seq = 1
    with Path(path).open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            try:
                obj = json.loads(line)
                declared_hash = obj.pop("hash")
                if obj.get("seq") != expected_seq or obj.get("previous_hash") != previous:
                    raise AuditIntegrityError(f"Broken sequence/chain at line {lineno}")
                if _digest(obj) != declared_hash:
                    raise AuditIntegrityError(f"Event hash mismatch at line {lineno}")
                obj["hash"] = declared_hash
            except (ValueError, KeyError, TypeError) as exc:
                raise AuditIntegrityError(f"Invalid trace at line {lineno}: {exc}") from exc
            yield obj
            previous = declared_hash
            expected_seq += 1


def diff_traces(first: str | Path, second: str | Path) -> list[dict]:
    """HUAP-inspired semantic diff ignoring timestamp / hash-chain metadata."""
    a = [(e["kind"], e["data"]) for e in verified_events(first)]
    b = [(e["kind"], e["data"]) for e in verified_events(second)]
    diffs: list[dict] = []
    for idx in range(max(len(a), len(b))):
        left = a[idx] if idx < len(a) else None
        right = b[idx] if idx < len(b) else None
        if left != right:
            diffs.append({"index": idx, "left": left, "right": right})
    return diffs
