from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field, StringConstraints

from nel_contracts.models.content_identity import ContentIdentity
from nel_contracts.models.evidence import EvidenceEvent
from nel_contracts.models.identifiers import (
    GitObjectId,
    RepoRef,
    StrictModel,
    UtcTimestamp,
)
from nel_contracts.models.openclass import OpenClassifier
from nel_contracts.models.visibility import VisibilityLevel
from nel_contracts.models.work import KNOWN_INTENT_KINDS

# A neutral work-item identifier (design K2). A NEW dedicated type: NOT ``Ulid`` (which rejects the
# kernel ``task-YYYYMMDD-HHMMSS-<slug>`` shape) and NOT ``Slug`` (which caps at 64 chars, overflowed
# by a real task id whose ``task-20260720-141530-`` prefix already spends 21). This pattern is a
# superset of both the ULID and the kernel task-id shapes so every existing identity projects
# losslessly.
WorkItemId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,127}$")]

# The closed kernel ``TaskStatus`` (nel-os) mirrored as the open-vocabulary wire projection. This
# tuple is the 1:1 SSOT; a nel-os parity test asserts it equals ``TaskStatus`` (the same discipline
# as ``GATE_CLASS_IDENTIFIERS`` <-> ``human_gates``). Transition validity stays kernel LAW, so a
# projection only ever emits a known member; the open form exists purely for D15 forward-compat.
WORK_STATUS_IDENTIFIERS: tuple[str, ...] = (
    "planned",
    "running",
    "reviewing",
    "revising",
    "verifying",
    "delivering",
    "capturing",
    "blocked",
    "failed",
    "completed",
    "cancelled",
)

# The closed kernel ``RiskLevel`` mirrored as an open classifier whose default-deny bucket is the
# MOST restrictive value, so an unknown wire level is never treated as safer than it is.
RISK_LEVEL_IDENTIFIERS: tuple[str, ...] = ("low", "medium", "high", "critical")


class WorkStatus(OpenClassifier):
    """Open projection of the kernel ``TaskStatus`` (design D15).

    Known members are the ratified task-lifecycle states; an unknown wire status downgrades to the
    fail-closed ``blocked`` bucket (never proceeds). This is a WIRE projection only and is never
    persisted into the durable manifest, where the closed ``TaskStatus`` enum stays authoritative.
    """

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset(WORK_STATUS_IDENTIFIERS)

    @classmethod
    def default_deny_bucket(cls) -> str:
        return "blocked"


class WorkKind(OpenClassifier):
    """Open vocabulary for what kind of work a ``WorkItem`` is.

    ``git_implementation`` is the only existing specialization (every current ``TaskEnvelope``);
    ``implementation`` mirrors the legacy intent tag, and the ``WorkIntent`` kinds are included so a
    world intent that becomes a work item classifies consistently. Unknown downgrades to ``other``.
    """

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset({"git_implementation", "implementation"}) | KNOWN_INTENT_KINDS

    @classmethod
    def default_deny_bucket(cls) -> str:
        return "other"


class RiskLevel(OpenClassifier):
    """Open projection of the kernel ``RiskLevel``; unknown downgrades to the most restrictive
    ``critical`` so an unrecognised level is never under-gated."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset(RISK_LEVEL_IDENTIFIERS)

    @classmethod
    def default_deny_bucket(cls) -> str:
        return "critical"


class RiskClassification(StrictModel):
    """Neutral projection of the kernel ``TaskRisk``. ``destructive`` projects ``destructive_git``
    (git-ness is implied by the presence of a ``GitWorkExtension``, never a field here)."""

    level: RiskLevel
    network: bool = False
    deployment: bool = False
    secrets: bool = False
    destructive: bool = False


class GitWorkExtension(StrictModel):
    """Git-specific work fields, kept OUT of the neutral ``WorkItem`` core so the core stays
    repo-agnostic (mirrors ``GitDeliveryExtension``). PATH-FREE by construction: ``repo`` is a
    :class:`RepoRef` (which forbids filesystem paths), so no governor-local path can leak public.

    ``content_tree_oid``, ``commits``, and ``pull_requests`` are DERIVED at projection time from the
    kernel's verification/review/delivery evidence events, never from a persisted manifest field.
    Git-as-vocabulary, never git-as-location.
    """

    repo: RepoRef
    base_ref: str
    content_tree_oid: GitObjectId | None = None
    task_branch: str | None = None
    target_visibility: VisibilityLevel
    commits: list[str] = Field(default_factory=list)
    pull_requests: list[str] = Field(default_factory=list)


class WorkItem(StrictModel):
    """The neutral core aggregate SHAPE — 'any action in the world' (design K2 / ADR-0014 D3).

    Carries NO git, NO filesystem path, NO ownership/registry digest, and NO orchestration/routing:
    those live in the (public, path-free) :class:`GitWorkExtension` and the (private, kernel-side)
    ``KernelWorktreeBinding`` respectively. A world-built instance is non-authoritative exactly like
    a world-built ``SeamReceipt``; the kernel re-derives truth. In K2 this is a pure OUTWARD
    read-projection over the unchanged kernel ``TaskEnvelope`` — there is deliberately no inward
    build path in the package.
    """

    work_item_id: WorkItemId
    title: str
    kind: WorkKind
    acceptance: list[str] = Field(min_length=1)
    status: WorkStatus
    risk: RiskClassification
    # The "any action" hinge: git items carry a ``content_tree_oid`` via the extension; non-git
    # actions bind their content by digest. ``None`` is allowed for a not-yet-bound work item.
    content_identity: ContentIdentity | None = None
    # The durable replay cursor (mirrors the kernel manifest's ``projection_sequence``); a read
    # projection never advances it.
    projection_sequence: int = Field(ge=1)
    current_attempt_ref: str | None = None
    evidence_refs: list[EvidenceEvent] = Field(default_factory=list)
    created_at: UtcTimestamp
    updated_at: UtcTimestamp
    metadata: dict[str, Any] = Field(default_factory=dict)
