from __future__ import annotations

from datetime import UTC, datetime

from nel_contracts.models.seam import (
    SeamObservation,
    SeamReceipt,
    SeamReference,
    SubmissionState,
)
from nel_contracts.models.work import WorkIntent


class SealedSeam:
    """The fail-closed default ``SeamPort`` (design §4).

    With no kernel wired, no external/irreversible action can proceed: ``submit_intent``
    refuses every intent with ``state=blocked`` and ``observe`` returns an ``unavailable``
    projection. Every result carries ``authority="projection"`` and ``attestation="unsigned"``
    — it is structurally impossible for the sealed default to mint an ``accepted``,
    kernel-authority, or signed result. This is accident-prevention and a fail-closed default,
    not the confinement boundary itself; the real controls are the K1 kernel preconditions.
    """

    def submit_intent(self, intent: WorkIntent) -> SeamReceipt:
        return SeamReceipt(
            intent_id=intent.intent_id,
            state=SubmissionState("blocked"),
            authority="projection",
            attestation="unsigned",
            issued_at=datetime.now(UTC),
        )

    def observe(self, ref: SeamReference) -> SeamObservation:
        return SeamObservation(
            reference=ref,
            state=SubmissionState("unavailable"),
            authority="projection",
            observed_at=datetime.now(UTC),
        )
