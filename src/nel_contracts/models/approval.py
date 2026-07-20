from __future__ import annotations

from typing import Literal

from nel_contracts.models.actor import AttestedActor, ClaimedActor
from nel_contracts.models.content_identity import ContentIdentity
from nel_contracts.models.identifiers import StrictModel, Ulid, UtcTimestamp
from nel_contracts.models.openclass import OpenClassifier

# The 1:1 human-gate SSOT (design D16). This tuple mirrors, in order, the ``human_gates``
# list in nel-os ``docs/plans/NEL_PLATFORM_IMPLEMENTATION_STATE.yaml``. It must not be
# renamed or narrowed; any change is ADR-gated and cross-checked by nel-os CI. The
# conformance test asserts an exact counterpart for every SSOT member.
GATE_CLASS_IDENTIFIERS: tuple[str, ...] = (
    "main_merge",
    "external_publish_or_public_repo_mutation",
    "payment_or_purchase",
    "missing_credentials_or_permissions",
    "legal_or_license_decision",
    "irreversible_destructive_migration",
    "history_rewrite",
    "pii_storage_policy_change",
    "irreversible_architecture_decision_without_adr_precedent",
)


class GateClass(OpenClassifier):
    """Open vocabulary bound 1:1 to the ratified human-gate SSOT (design D16).

    Every known member names a forever-human-only gate. An unknown gate downgrades to the
    default-deny bucket and is treated as human-gated (fail-closed), so a newer kernel can
    name a gate an older pinned consumer has never seen without ever downgrading it below
    human-gated.
    """

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset(GATE_CLASS_IDENTIFIERS)

    @classmethod
    def default_deny_bucket(cls) -> str:
        return "unknown_human_gated"

    @property
    def is_human_gated(self) -> bool:
        # Every known gate is human-only, and every unknown gate downgrades to human-gated.
        return True


class ApprovalRequest(StrictModel):
    """A durable, async approval request. A gated category returns ``state=blocked`` plus an
    ``approval_request_id`` — there is no separate approval port verb."""

    approval_request_id: Ulid
    gate: GateClass
    intent_id: Ulid
    content_identity: ContentIdentity | None = None
    requested_at: UtcTimestamp
    state: Literal["open", "resolved"] = "open"


class DecisionRecord(StrictModel):
    """An append-only decision authored before any adapter dispatch.

    A world-built instance carries no authority: trust requires kernel verification the
    package cannot perform (design §0). The human-only-gate check
    (``resolver`` must be a human for a human-gated ``allow``) is decided kernel-side; the
    shape-level :meth:`human_only_gate_respected` here is corroborating and non-authoritative.
    """

    decision_id: Ulid
    decision: Literal["allow", "block"]
    authority: Literal["projection", "kernel", "operator"] = "projection"
    gate: GateClass | None = None
    approval_request_id: Ulid | None = None
    resolver: ClaimedActor | AttestedActor
    decided_at: UtcTimestamp

    def human_only_gate_respected(self) -> bool:
        """Non-authoritative: True unless a human-gated ``allow`` was decided by a non-human
        resolver. The kernel is the authority; this only mirrors the shape."""
        if self.decision != "allow" or self.gate is None or not self.gate.is_human_gated:
            return True
        return self.resolver.actor_kind.classification == "human"
