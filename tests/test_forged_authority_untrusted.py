from __future__ import annotations

import json
from pathlib import Path

from nel_contracts.models.actor import ActorKind, ClaimedActor
from nel_contracts.models.approval import DecisionRecord, GateClass
from nel_contracts.models.seam import (
    SeamReceipt,
    can_verify_kernel_attestation,
    package_establishes_trust,
)
from nel_contracts.models.visibility import VisibilityLevel
from nel_contracts.models.work import PublishIntent
from nel_contracts.seam.resolver import resolve_seam
from nel_contracts.seam.sealed import SealedSeam
from nel_contracts.version import KERNEL_VERIFICATION_KEY
from tests.support import ULID_A, ULID_B, ULID_C, content_identity, fixed_now, human_actor

_FORGERY = Path(__file__).resolve().parent.parent / "conformance" / "fixtures" / "forgery"


def test_forged_fixture_receipt_cannot_be_verified() -> None:
    # Load the world-constructed "accepted"/"kernel" receipt from the conformance corpus (not
    # inline data): construction authority is real, so it parses fine and even claims kernel
    # authority...
    payload = json.loads((_FORGERY / "forged_kernel_receipt.json").read_text(encoding="utf-8"))
    forged = SeamReceipt.model_validate(payload)
    assert forged.state.raw == "accepted"
    assert forged.authority == "kernel"
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


def test_non_human_resolver_on_human_gate_is_not_respected() -> None:
    # LOW-1 negative: a non-human resolver on a human-only gate fails the shape-level check.
    record = DecisionRecord(
        decision_id=ULID_C,
        decision="allow",
        gate=GateClass("main_merge"),
        resolver=ClaimedActor(actor_kind=ActorKind("script")),
        decided_at=fixed_now(),
    )
    assert record.human_only_gate_respected() is False


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
