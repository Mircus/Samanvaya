"""Minimal standard-library CLI: demo, validate a trace, inspect legacy HUAP."""
from __future__ import annotations

import argparse
import json
from datetime import timedelta
from pathlib import Path

from .audit import AuditLog, verified_events
from .compat.huap_trace import inspect_huap_trace
from .constitution import ConstitutionConfig, ConstitutionalPolicy
from .gateway import ConstitutionalGateway
from .mandates import MandateBook
from .models import ActionIntent, Effect, Evidence, EvidenceStatus, Mandate, utcnow


def demo(path: str) -> int:
    book = MandateBook(root_issuers=("human:owner",))
    book.issue(Mandate("m1", "human:owner", "agent:researcher", ("read", "publish"),
                       ("repo:reports",), ("research",), (Effect.READ, Effect.EXTERNAL),
                       utcnow() + timedelta(hours=1), max_uses=3,
                       accountable_principal="human:owner"))
    gateway = ConstitutionalGateway(
        ConstitutionalPolicy(book, ConstitutionConfig(("human:owner",))), AuditLog(path))
    for intent in (
        ActionIntent("safe-read", "agent:researcher", "m1", "read", "repo:reports/draft",
                     "research", Effect.READ),
        ActionIntent("escalate-publish", "agent:researcher", "m1", "publish",
                     "repo:reports/final", "research", Effect.EXTERNAL,
                     (Evidence("local:review", "sha256:illustrative", EvidenceStatus.VERIFIED),)),
        ActionIntent("deny-deletion", "agent:researcher", "m1", "delete",
                     "repo:reports/final", "research", Effect.EXTERNAL),
    ):
        receipt = gateway.execute(intent, lambda: "action simulated")
        print(f"{intent.intent_id}: {receipt.decision.verdict.value} "
              f"({', '.join(receipt.decision.reasons)}), executed={receipt.executed}")
    print(f"Audit: {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Samanvaya constitutional kernel v0.1")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("demo", help="Run 3 simulated constitutional decisions")
    d.add_argument("--audit", default="./samanvaya-demo.jsonl")
    v = sub.add_parser("verify-audit", help="Check local hash chain and event order")
    v.add_argument("path")
    h = sub.add_parser("inspect-huap", help="Read legacy HUAP JSONL; never grants rights")
    h.add_argument("path")
    args = parser.parse_args()
    if args.command == "demo":
        return demo(args.audit)
    if args.command == "verify-audit":
        events = list(verified_events(args.path))
        print(json.dumps({"valid": True, "events": len(events),
                          "final_hash": events[-1]["hash"] if events else None}, indent=2))
        return 0
    if args.command == "inspect-huap":
        print(json.dumps(inspect_huap_trace(args.path), indent=2))
        return 0
    return 2
