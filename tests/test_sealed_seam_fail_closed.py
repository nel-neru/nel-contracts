from __future__ import annotations

from nel_contracts.models.seam import SeamReference, package_establishes_trust
from nel_contracts.models.visibility import VisibilityLevel
from nel_contracts.models.work import PublishIntent
from nel_contracts.seam.sealed import SealedSeam
from tests.support import ULID_A, content_identity, fixed_now, human_actor


def _publish_intent() -> PublishIntent:
    return PublishIntent(
        intent_id=ULID_A,
        actor=human_actor(),
        submitted_at=fixed_now(),
        content_identity=content_identity(),
        target_visibility=VisibilityLevel("public"),
    )


def test_submit_intent_is_fail_closed_and_non_authoritative() -> None:
    receipt = SealedSeam().submit_intent(_publish_intent())
    # Fail-closed: the sealed default refuses every external action.
    assert receipt.state.classification == "blocked"
    assert receipt.state.raw != "accepted"
    # Non-authoritative: it can never mint kernel authority or a signature.
    assert receipt.authority == "projection"
    assert receipt.attestation == "unsigned"
    assert package_establishes_trust(receipt) is False


def test_observe_is_unavailable_projection() -> None:
    observation = SealedSeam().observe(SeamReference(ref_kind="intent", ref_id=ULID_A))
    assert observation.state.classification == "unavailable"
    assert observation.authority == "projection"


def test_sealed_seam_never_returns_accepted() -> None:
    receipt = SealedSeam().submit_intent(_publish_intent())
    assert receipt.state.raw not in {"accepted", "pending"}
