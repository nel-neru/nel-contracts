from __future__ import annotations

from nel_contracts.models.identifiers import Sha256Hex, StrictModel, Ulid, UtcTimestamp
from nel_contracts.models.openclass import OpenClassifier


class EvidenceClassification(OpenClassifier):
    """Open vocabulary classifying an evidence event."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset({"verification", "review", "adjudication", "capture", "ledger"})

    @classmethod
    def default_deny_bucket(cls) -> str:
        return "unclassified"


class EvidenceEvent(StrictModel):
    """A neutral, digest-bound evidence record.

    ``content_digest`` binds to the produced artifact by digest, never by embedding its bytes.
    """

    evidence_id: Ulid
    classification: EvidenceClassification
    content_digest: Sha256Hex
    produced_at: UtcTimestamp
    summary: str | None = None
    # TODO(K2/W3): ``artifact_refs`` binding to the Artifact/ArtifactType contract lands with
    # the W3 Artifact foundation; kept out of the G1 neutral skeleton.
