from __future__ import annotations

from nel_contracts.models.identifiers import RepoRef, Sha256Hex, StrictModel
from nel_contracts.models.openclass import OpenClassifier


class VisibilityLevel(OpenClassifier):
    """Open vocabulary for content/repository exposure."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset({"private", "public"})

    @classmethod
    def default_deny_bucket(cls) -> str:
        # Fail-closed: an unknown visibility is treated as the most-exposed value so the
        # public-release gate always applies.
        return "public"


class RepositoryVisibility(StrictModel):
    """A digest-snapshotted and live-reconciled repository visibility.

    A public-release-class operation requires the snapshot to match the live value; a
    mismatch blocks (enforced kernel-side; :meth:`matches` is the shape-level check).
    """

    repo: RepoRef
    snapshot: VisibilityLevel
    snapshot_digest: Sha256Hex | None = None
    live: VisibilityLevel | None = None

    def matches(self) -> bool:
        """True only when the live value is known and equals the snapshot."""
        if self.live is None:
            return False
        return self.snapshot.classification == self.live.classification
