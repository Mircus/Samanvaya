"""Read-only HUAP v0.1 JSONL ingestion. Legacy traces are NEVER authority.

Preserves the valuable observability contract while avoiding import of unsafe
legacy permissions or implicit tool execution.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REQUIRED_FIELDS = {"v", "ts", "name", "kind", "run_id", "span_id", "pod", "data"}


def inspect_huap_trace(path: str | Path) -> dict:
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    counts: dict[str, int] = {}
    runs: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                raise ValueError(f"Blank legacy trace line {line_no}")
            event = json.loads(line)
            if not isinstance(event, dict) or not REQUIRED_FIELDS <= set(event):
                raise ValueError(f"Invalid HUAP trace envelope at line {line_no}")
            counts[event["name"]] = counts.get(event["name"], 0) + 1
            runs.add(event["run_id"])
    return {"source_format": "huap.trace.v0.1", "sha256": digest,
            "events": sum(counts.values()), "kinds": counts,
            "run_ids": sorted(runs), "confers_authority": False}
