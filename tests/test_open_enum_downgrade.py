from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from nel_contracts.models.actor import ActorKind
from nel_contracts.models.approval import GateClass
from nel_contracts.models.capability import CapabilityClassification
from nel_contracts.models.seam import SeamReceipt, SubmissionState
from nel_contracts.models.visibility import VisibilityLevel
from nel_contracts.models.work import (
    OtherIntent,
    WorkIntentUnion,
    coerce_work_intent,
)
from tests.support import ULID_A, human_actor

_OPENENUM = Path(__file__).resolve().parent.parent / "conformance" / "fixtures" / "openenum"


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


def test_unknown_intent_kind_downgrades_to_other_intent_from_fixture() -> None:
    # Load the unknown-kind payload from the conformance corpus (not inline data).
    payload = json.loads((_OPENENUM / "unknown_intent_kind.json").read_text(encoding="utf-8"))
    intent = coerce_work_intent(payload)
    assert isinstance(intent, OtherIntent)
    assert intent.declared_kind == "teleport"
    assert intent.kind == "other"


def test_both_paths_downgrade_unknown_kind_uniformly() -> None:
    # Uniform open enum (MEDIUM-1): BOTH coerce_work_intent AND the typed-union path route an
    # unknown kind to OtherIntent without raising.
    payload = json.loads((_OPENENUM / "unknown_intent_kind.json").read_text(encoding="utf-8"))

    coerced = coerce_work_intent(payload)
    assert isinstance(coerced, OtherIntent)

    typed = TypeAdapter(WorkIntentUnion).validate_python(payload)
    assert isinstance(typed, OtherIntent)
    assert typed.declared_kind == "teleport"


def test_typed_union_still_dispatches_known_kind() -> None:
    payload = {
        "kind": "publish",
        "intent_id": ULID_A,
        "actor": human_actor().model_dump(),
        "submitted_at": "2026-07-20T12:00:00Z",
        "content_identity": {"content_digest": "a" * 64},
        "target_visibility": "public",
    }
    result = TypeAdapter(WorkIntentUnion).validate_python(payload)
    assert type(result).__name__ == "PublishIntent"
