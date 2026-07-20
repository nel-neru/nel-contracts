from __future__ import annotations

from nel_contracts.models.actor import ActorKind
from nel_contracts.models.approval import GateClass
from nel_contracts.models.capability import CapabilityClassification
from nel_contracts.models.seam import SeamReceipt, SubmissionState
from nel_contracts.models.visibility import VisibilityLevel
from nel_contracts.models.work import OtherIntent, coerce_work_intent
from tests.support import ULID_A, human_actor


def test_unknown_actor_kind_downgrades_without_raising() -> None:
    kind = ActorKind("frobnicate")
    assert kind.is_known is False
    assert kind.raw == "frobnicate"
    assert kind.classification == "external_unknown"


def test_unknown_submission_state_is_unavailable() -> None:
    assert SubmissionState("teleported").classification == "unavailable"


def test_unknown_gate_is_human_gated() -> None:
    gate = GateClass("brand_new_gate")
    assert gate.is_known is False
    assert gate.classification == "unknown_human_gated"
    assert gate.is_human_gated is True


def test_unknown_capability_classification_is_external() -> None:
    assert CapabilityClassification("weird").classification == "external"


def test_unknown_visibility_is_most_exposed() -> None:
    assert VisibilityLevel("classified").classification == "public"


def test_unknown_wire_enum_never_raises_validationerror() -> None:
    # A newer producer emits a state an older pinned consumer has never seen: it must parse.
    receipt = SeamReceipt.model_validate(
        {
            "intent_id": ULID_A,
            "state": "mystery_state_from_the_future",
            "issued_at": "2026-07-20T12:00:00Z",
        }
    )
    assert receipt.state.is_known is False
    assert receipt.state.classification == "unavailable"


def test_unknown_intent_kind_downgrades_to_other_intent() -> None:
    intent = coerce_work_intent(
        {
            "kind": "teleport",
            "intent_id": ULID_A,
            "actor": human_actor().model_dump(),
            "submitted_at": "2026-07-20T12:00:00Z",
        }
    )
    assert isinstance(intent, OtherIntent)
    assert intent.declared_kind == "teleport"
    assert intent.kind == "other"
