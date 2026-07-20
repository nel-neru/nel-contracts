from __future__ import annotations

from typing import Literal

from pydantic import Field

from nel_contracts.models.approval import GateClass
from nel_contracts.models.identifiers import Sha256Hex, StrictModel, Ulid, UtcTimestamp
from nel_contracts.models.openclass import OpenClassifier
from nel_contracts.version import KERNEL_VERIFICATION_KEY

# The authority of a seam DTO. Kept a closed ``Literal`` (not an open classifier) because it
# is a foundational provenance field, not an extensible capability vocabulary. Crucially,
# authority is NOT world-mintable in any meaningful sense: possessing the class lets an
# importer *set* ``authority="kernel"``, but the package ships no way to *verify* it, so a
# world-built value is untrusted (design §0). ``observe`` results are always ``projection``.
SeamAuthority = Literal["projection", "kernel", "operator"]


class SubmissionState(OpenClassifier):
    """Open vocabulary for the state of a submitted intent."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset({"accepted", "pending", "blocked", "unavailable", "rejected"})

    @classmethod
    def default_deny_bucket(cls) -> str:
        # Fail-closed: an unknown state is treated as unavailable (nothing proceeds).
        return "unavailable"


class SeamReceipt(StrictModel):
    """The kernel-authored acknowledgement returned by ``submit_intent``.

    Carries no credential and no live handle. ``authority``/``attestation`` are only
    trustworthy after out-of-process kernel verification; a ``SealedSeam`` or world-built
    instance carries ``authority="projection"`` / ``attestation="unsigned"`` and is untrusted.
    """

    intent_id: Ulid
    state: SubmissionState
    authority: SeamAuthority = "projection"
    attestation: str = "unsigned"
    work_item_id: Ulid | None = None
    run_id: Ulid | None = None
    approval_request_id: Ulid | None = None
    block_reason: GateClass | None = None
    decision_ref: str | None = None
    issued_at: UtcTimestamp


class SeamReference(StrictModel):
    """A pull-only reference to one intent/work_item/run/approval, scoped by authenticated
    caller identity kernel-side."""

    ref_kind: Literal["intent", "work_item", "run", "approval"]
    ref_id: Ulid


class SeamObservation(StrictModel):
    """The single read-surface projection. ``authority`` is fixed to ``projection`` — an
    observation is never authoritative caller-side."""

    reference: SeamReference
    state: SubmissionState
    authority: Literal["projection"] = "projection"
    evidence_digests: list[Sha256Hex] = Field(default_factory=list)
    observed_at: UtcTimestamp


def can_verify_kernel_attestation() -> bool:
    """Whether the package holds a key to verify kernel attestation. Always False: the public
    package ships no verification key (see ``version.KERNEL_VERIFICATION_KEY``); trust is
    established only by the K1 out-of-process kernel."""
    return KERNEL_VERIFICATION_KEY is not None


def package_establishes_trust(receipt: SeamReceipt) -> bool:
    """Whether the package alone can establish that ``receipt`` is genuinely kernel-authored.

    Always False, grounded in key absence: even a receipt that *claims* ``authority="kernel"``
    cannot be verified in-world. Every consumer MUST re-verify against the kernel before acting.
    """
    return can_verify_kernel_attestation()
