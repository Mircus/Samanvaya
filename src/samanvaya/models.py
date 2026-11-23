"""The minimal, immutable vocabulary of constitutional action.

This is a prototype schema; identities and evidence attestations are NOT cryptographically
verified in v0.1. See docs/SECURITY.md before integrating real tools.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Effect(str, Enum):
    READ = "read"
    WRITE = "write"
    EXTERNAL = "external"
    IRREVERSIBLE = "irreversible"


class EvidenceStatus(str, Enum):
    VERIFIED = "verified"  # A v0.1 assertion, not an attestation
    UNVERIFIED = "unverified"
    CONFLICTING = "conflicting"


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Evidence:
    source: str
    digest: str
    status: EvidenceStatus = EvidenceStatus.UNVERIFIED
    description: str = ""


@dataclass(frozen=True)
class ActionIntent:
    intent_id: str
    actor: str
    mandate_id: str
    action: str
    resource: str
    purpose: str
    effect: Effect
    evidence: tuple[Evidence, ...] = ()
    collective_id: str | None = None
    endorsements: tuple[str, ...] = ()
    harm_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Mandate:
    mandate_id: str
    issuer: str
    holder: str
    actions: tuple[str, ...]
    resource_scopes: tuple[str, ...]
    purposes: tuple[str, ...]
    allowed_effects: tuple[Effect, ...]
    expires_at: datetime
    max_uses: int = 1
    parent_id: str | None = None
    delegable: bool = False
    accountable_principal: str = ""


@dataclass(frozen=True)
class Collective:
    collective_id: str
    members: tuple[str, ...]
    quorum: int
    accountable_principal: str


@dataclass(frozen=True)
class HumanApproval:
    intent_id: str
    approver: str
    expires_at: datetime


@dataclass(frozen=True)
class Decision:
    verdict: Verdict
    reasons: tuple[str, ...]
    intent_id: str
    mandate_id: str
    checked_at: datetime

    @property
    def authorized(self) -> bool:
        return self.verdict is Verdict.ALLOW


@dataclass(frozen=True)
class ExecutionReceipt:
    decision: Decision
    executed: bool
    outcome: str  # blocked | completed | failed
    result: Any = field(default=None, repr=False)
    error: str | None = None
