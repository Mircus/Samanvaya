"""Mandate registry: bound scope, expiry, finite use, revocation, delegation.

Issuers and revokers are caller-asserted strings in this prototype. The API enforces
structural checks but does not authenticate the caller: see SECURITY.md.
"""
from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock

from .models import Effect, Mandate, utcnow


def normalized_time(t: datetime) -> datetime:
    if t.tzinfo is None:
        raise ValueError("Datetime must include a timezone")
    return t.astimezone(timezone.utc)


def _resource_parts(s: str) -> tuple[str, str]:
    """A deliberately small resource grammar: kind:path/to/object.

    Reject ambiguous encodings and path traversal. This is NOT a general URL parser.
    """
    if not isinstance(s, str) or ":" not in s:
        raise ValueError("Resource must be 'kind:path'")
    scheme, path = s.split(":", 1)
    if not scheme or not scheme.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Invalid resource kind")
    if not path or path.startswith("/") or "//" in path or "\\" in path:
        raise ValueError("Invalid resource path")
    if any(c in s for c in ("?", "#", "%", "\n", "\r", "\t")):
        raise ValueError("Ambiguous resource encoding")
    if any(seg in (".", "..", "") for seg in path.split("/")):
        raise ValueError("Resource traversal or empty segment")
    return scheme, path


def in_scope(resource: str, scope: str) -> bool:
    """Exact resource or path-segment descendant, never lexical-prefix alone."""
    rkind, rpath = _resource_parts(resource)
    skind, spath = _resource_parts(scope)
    return rkind == skind and (rpath == spath or rpath.startswith(spath.rstrip("/") + "/"))


def _subscope(child: str, parent: str) -> bool:
    return in_scope(child, parent)


class MandateBook:
    def __init__(self, root_issuers: tuple[str, ...]):
        if not root_issuers or any(not r for r in root_issuers):
            raise ValueError("At least one root issuer must be configured")
        self.root_issuers = frozenset(root_issuers)
        self._mandates: dict[str, Mandate] = {}
        self._revoked: set[str] = set()
        self._use_count: dict[str, int] = {}
        self.lock = RLock()

    def issue(self, mandate: Mandate) -> None:
        with self.lock:
            if not mandate.mandate_id or not mandate.holder or not mandate.issuer:
                raise ValueError("Issuer, holder and mandate ID required")
            if mandate.mandate_id in self._mandates:
                raise ValueError("Mandate ID cannot be reissued")
            if normalized_time(mandate.expires_at) <= utcnow():
                raise ValueError("Cannot issue expired mandate")
            if mandate.max_uses <= 0 or not all((mandate.actions, mandate.purposes,
                                                 mandate.resource_scopes, mandate.allowed_effects)):
                raise ValueError("Mandate requires bounded nonempty scopes and positive quota")
            for r in mandate.resource_scopes:
                _resource_parts(r)
            if mandate.parent_id is None:
                if mandate.issuer not in self.root_issuers:
                    raise PermissionError("Untrusted issuer needs a delegating parent mandate")
            else:
                parent = self._mandates.get(mandate.parent_id)
                if not parent or not self.active(parent.mandate_id):
                    raise PermissionError("Parent mandate unavailable or inactive")
                if parent.holder != mandate.issuer or not parent.delegable:
                    raise PermissionError("Issuer cannot delegate parent mandate")
                if (not set(mandate.actions) <= set(parent.actions)
                        or not set(mandate.purposes) <= set(parent.purposes)
                        or not set(mandate.allowed_effects) <= set(parent.allowed_effects)
                        or not all(any(_subscope(c, p) for p in parent.resource_scopes)
                                   for c in mandate.resource_scopes)
                        or normalized_time(mandate.expires_at) > normalized_time(parent.expires_at)
                        or mandate.max_uses > parent.max_uses):
                    raise PermissionError("Delegation cannot enlarge authority")
            self._mandates[mandate.mandate_id] = mandate
            self._use_count[mandate.mandate_id] = 0

    def get(self, mandate_id: str) -> Mandate | None:
        with self.lock:
            return self._mandates.get(mandate_id)

    def lineage(self, mandate_id: str) -> tuple[str, ...]:
        with self.lock:
            seen: set[str] = set()
            chain: list[str] = []
            current: str | None = mandate_id
            while current:
                if current in seen:
                    raise ValueError("Cyclic mandate ancestry")
                seen.add(current)
                chain.append(current)
                m = self._mandates.get(current)
                if m is None:
                    break
                current = m.parent_id
            return tuple(chain)

    def active(self, mandate_id: str, at: datetime | None = None) -> bool:
        at = at or utcnow()
        with self.lock:
            chain = self.lineage(mandate_id)
            for ancestor in chain:
                m = self._mandates.get(ancestor)
                if not m or ancestor in self._revoked or normalized_time(m.expires_at) <= at:
                    return False
            return bool(chain)

    def quota_available(self, mandate_id: str) -> bool:
        with self.lock:
            for mid in self.lineage(mandate_id):
                m = self._mandates.get(mid)
                if not m or self._use_count[mid] >= m.max_uses:
                    return False
            return True

    def reserve(self, mandate_id: str, at: datetime | None = None) -> None:
        with self.lock:
            if not self.active(mandate_id, at=at) or not self.quota_available(mandate_id):
                raise PermissionError("Expired/revoked/exhausted mandate")
            for mid in self.lineage(mandate_id):
                self._use_count[mid] += 1

    def release_reservation(self, mandate_id: str) -> None:
        with self.lock:
            for mid in self.lineage(mandate_id):
                self._use_count[mid] -= 1

    def revoke(self, mandate_id: str, by: str) -> None:
        with self.lock:
            m = self._mandates.get(mandate_id)
            if not m:
                raise KeyError(mandate_id)
            if by not in self.root_issuers and by != m.issuer:
                raise PermissionError("Only root or original issuer may revoke")
            self._revoked.add(mandate_id)

    def usage(self, mandate_id: str) -> int:
        with self.lock:
            return self._use_count[mandate_id]
