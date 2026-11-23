"""The one supported execution boundary: authorize, audit, reserve, execute.

Design limit: this intercepts calls that use it. It is NOT a process sandbox.
Any direct arbitrary Python tool call bypasses it; production needs enforceable adapters.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .audit import AuditLog
from .constitution import ConstitutionalPolicy
from .models import ActionIntent, ExecutionReceipt, HumanApproval, Verdict


class ConstitutionalGateway:
    def __init__(self, policy: ConstitutionalPolicy, audit: AuditLog):
        self.policy = policy
        self.audit = audit

    def execute(self, intent: ActionIntent, operation: Callable[[], Any],
                approval: HumanApproval | None = None) -> ExecutionReceipt:
        # Serialize evaluation and reservation to protect finite-use quotas.
        with self.policy.mandates.lock:
            decision = self.policy.evaluate(intent, approval=approval)
            reserved = False
            if decision.verdict is Verdict.ALLOW:
                self.policy.mandates.reserve(intent.mandate_id)
                reserved = True
            try:
                self.audit.append("constitutional_decision", {
                    "intent": intent, "decision": decision,
                    "approval": approval,
                })
                if reserved:
                    self.audit.append("execution_started", {
                        "intent_id": intent.intent_id, "mandate_id": intent.mandate_id,
                    })
            except Exception:
                if reserved:
                    self.policy.mandates.release_reservation(intent.mandate_id)
                raise
            if not reserved:
                return ExecutionReceipt(decision, executed=False, outcome="blocked")
        try:
            result = operation()
            # Avoid leaking arbitrary tool outputs in the audit trail.
            self.audit.append("execution_finished", {
                "intent_id": intent.intent_id, "outcome": "completed",
            })
            return ExecutionReceipt(decision, executed=True, outcome="completed", result=result)
        except Exception as exc:
            self.audit.append("execution_finished", {
                "intent_id": intent.intent_id, "outcome": "failed",
                "exception_type": type(exc).__name__,
            })
            return ExecutionReceipt(decision, executed=True, outcome="failed",
                                    error=f"{type(exc).__name__}: {exc}")
