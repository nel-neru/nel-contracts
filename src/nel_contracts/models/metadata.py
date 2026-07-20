from __future__ import annotations

from datetime import datetime
from typing import Final

from pydantic import Field

from nel_contracts.models.identifiers import RepoRef, StrictModel, UtcTimestamp
from nel_contracts.models.openclass import OpenClassifier

# Default freshness window: a repository with no activity for this many days is stale (D10).
DEFAULT_STALE_AFTER_DAYS: Final[int] = 180


class FreshnessState(OpenClassifier):
    """Open vocabulary for repository freshness."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset({"active", "stale", "archived"})

    @classmethod
    def default_deny_bucket(cls) -> str:
        # Conservative: an unknown freshness is treated as stale.
        return "stale"


class RepoMetadata(StrictModel):
    """The GitHub-metadata freshness contract (design D10).

    Freshness is derived, not stored: ``archived`` wins, otherwise activity older than
    ``stale_after_days`` (default 180) is ``stale``, else ``active``.
    """

    repo: RepoRef
    last_activity_at: UtcTimestamp
    default_branch: str | None = None
    stars: int | None = Field(default=None, ge=0)
    archived: bool = False
    stale_after_days: int = Field(default=DEFAULT_STALE_AFTER_DAYS, ge=1)

    def freshness(self, *, now: datetime) -> FreshnessState:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        if self.archived:
            return FreshnessState("archived")
        age_days = (now - self.last_activity_at).days
        if age_days > self.stale_after_days:
            return FreshnessState("stale")
        return FreshnessState("active")
