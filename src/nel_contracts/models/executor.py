from __future__ import annotations

from typing import Literal

from pydantic import Field

from nel_contracts.models.actor import ActorKind
from nel_contracts.models.identifiers import StrictModel, UtcTimestamp
from nel_contracts.models.openclass import OpenClassifier

# The neutral executor-competency vocabulary (design K3, realizing ADR-0009). This is COMPETENCY —
# what kind of bounded role a model runtime can serve — and is deliberately DISTINCT from
# ``models/capability.py::Capability``, whose egress default-deny invariant models blast radius,
# not competency. Do not overload one for the other.
EXECUTOR_CAPABILITY_IDENTIFIERS: tuple[str, ...] = (
    "implement",
    "review",
    "adjudicate",
)


class ExecutorCapability(OpenClassifier):
    """Open vocabulary of the bounded verbs an executor can serve (design D15).

    ``implement`` is the only workspace-write verb; ``review`` and ``adjudicate`` are read-only by
    construction on the kernel side. An unknown wire member downgrades to the ``non_executing``
    bucket: a capability nobody recognizes can never be scheduled, executed, or used to satisfy a
    routing requirement — the most restrictive interpretation, never a permissive one.
    """

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset(EXECUTOR_CAPABILITY_IDENTIFIERS)

    @classmethod
    def default_deny_bucket(cls) -> str:
        return "non_executing"


class RoutingSignal(StrictModel):
    """One ADVISORY calibration observation about a provider's review quality.

    Modeled on the non-authoritative ``ClaimedActor``: every field is a claim, and the shape is
    pinned ``is_advisory=True`` so a public consumer can never mistake it for an authorization
    input. The kernel's hard filters (active + capability + risk + independence) alone decide
    eligibility; a consumer of these signals may at most REORDER candidates its own filters
    already admitted, and must discard any proposal that is not an exact permutation.

    ``provider`` is the public ``ActorKind`` vocabulary — a kernel projecting its private runtime
    registry ids maps them at the boundary (``codex`` → ``codex``, ``claude`` → ``claude_code``),
    mirroring how kernel event actors stay kernel-private. Counts are non-authoritative
    aggregates of operator calibration; they carry no receipt and prove nothing.
    """

    provider: ActorKind
    is_advisory: Literal[True] = True
    finding_adoptions: int = Field(default=0, ge=0)
    false_positives: int = Field(default=0, ge=0)
    escaped_defects: int = Field(default=0, ge=0)
    observed_at: UtcTimestamp | None = None


class RoutingAdvice(StrictModel):
    """An ADVISORY preference over providers, derived from :class:`RoutingSignal` aggregates.

    ``preferred`` is at most a permutation hint over candidates the consumer's own hard filters
    admitted: it can never add a provider, never remove one, and never override an independence
    exclusion. A conforming consumer splices it exactly like the kernel does — reorder first,
    re-derive its exclusions AFTER reordering, and fall back to its own deterministic order when
    the hint is absent, malformed, or not an exact permutation. Pinned ``is_advisory=True``:
    this shape is structurally incapable of expressing an authoritative routing decision.
    """

    is_advisory: Literal[True] = True
    signals: list[RoutingSignal] = Field(default_factory=list)
    preferred: list[ActorKind] = Field(default_factory=list)
