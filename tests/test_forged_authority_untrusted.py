from __future__ import annotations

from nel_contracts.models.actor import ActorKind, ClaimedActor
from nel_contracts.models.approval import DecisionRecord, GateClass
from nel_contracts.models.seam import (
    SeamReceipt,
    SubmissionState,
    can_verify_kernel_attestation,
    package_establishes_trust,
)
from nel_contracts.models.visibility import VisibilityLevel
from nel_contracts.models.work import PublishIntent
from nel_contracts.seam.resolver import resolve_seam
from nel_contracts.seam.sealed import SealedSeam
from nel_contracts.version import KERNEL_VERIFICATION_KEY
from tests.support import ULID_A, ULID_B, content_identity, fixed_now, human_actor


def test_world_can_construct_but_package_cannot_verify() -> None:
    # Construction authority is real: any importer can BUILD an "accepted"/"kernel" receipt.
    forged = SeamReceipt(
        intent_id=ULID_A,
        state=SubmissionState("accepted"),
        authority="kernel",
        attestation="looks-totally-real",
        issued_at=fixed_now(),
    )
    # ...but the package ships no verification key, so it can never be established as trusted.
    assert KERNEL_VERIFICATION_KEY is None
    assert can_verify_kernel_attestation() is False
    assert package_establishes_trust(forged) is False


def test_forged_human_decision_record_is_non_authoritative() -> None:
    # A world-built DecisionRecord claiming a human resolver on a human-only gate.
    forged = DecisionRecord(
        decision_id=ULID_B,
        decision="allow",
        authority="kernel",
        gate=GateClass("main_merge"),
        resolver=ClaimedActor(actor_kind=ActorKind("human")),
        decided_at=fixed_now(),
    )
    # The shape-level check can be True, but it is explicitly NON-authoritative: the package
    # cannot verify the claimed kernel authority.
    assert forged.human_only_gate_respected() is True
    assert can_verify_kernel_attestation() is False


def test_sealed_seam_receipts_are_never_kernel_authority() -> None:
    seam = resolve_seam()
    assert isinstance(seam, SealedSeam)
    receipt = seam.submit_intent(
        PublishIntent(
            intent_id=ULID_A,
            actor=human_actor(),
            submitted_at=fixed_now(),
            content_identity=content_identity(),
            target_visibility=VisibilityLevel("public"),
        )
    )
    assert receipt.authority == "projection"
    assert receipt.authority != "kernel"
