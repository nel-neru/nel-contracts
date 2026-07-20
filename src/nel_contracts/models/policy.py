from __future__ import annotations

from typing import Literal

from nel_contracts.models.approval import GateClass
from nel_contracts.models.identifiers import Slug, StrictModel, UtcTimestamp


class Policy(StrictModel):
    """A neutral policy identity. The real orchestration policy engine (default-deny
    classification, per-boundary decisions) is kernel-side (K1); this is the shared shape."""

    policy_id: Slug
    description: str | None = None


class PolicyOutcome(StrictModel):
    """The neutral outcome shape a policy evaluation projects. ``block`` names the gate; a
    world-built instance is non-authoritative."""

    outcome: Literal["allow", "block"]
    gate: GateClass | None = None
    reason: str | None = None
    decided_at: UtcTimestamp
    # TODO(K1): bounded-run/budget/timeout policy stays in the kernel and is intentionally
    # excluded from the neutral vocabulary (design §9).
