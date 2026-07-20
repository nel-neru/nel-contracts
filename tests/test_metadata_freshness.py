from __future__ import annotations

from datetime import UTC, datetime, timedelta

from nel_contracts.models.identifiers import RepoRef
from nel_contracts.models.metadata import DEFAULT_STALE_AFTER_DAYS, RepoMetadata


def _metadata(*, last_activity: datetime, archived: bool = False) -> RepoMetadata:
    return RepoMetadata(
        repo=RepoRef(repo="pantheon"),
        last_activity_at=last_activity,
        default_branch="main",
        stars=42,
        archived=archived,
    )


def test_default_window_is_180_days() -> None:
    assert DEFAULT_STALE_AFTER_DAYS == 180
    assert _metadata(last_activity=datetime.now(UTC)).stale_after_days == 180


def test_recent_activity_is_active() -> None:
    now = datetime.now(UTC)
    meta = _metadata(last_activity=now - timedelta(days=10))
    assert meta.freshness(now=now).classification == "active"


def test_old_activity_is_stale() -> None:
    now = datetime.now(UTC)
    meta = _metadata(last_activity=now - timedelta(days=200))
    assert meta.freshness(now=now).classification == "stale"


def test_archived_wins_over_activity() -> None:
    now = datetime.now(UTC)
    meta = _metadata(last_activity=now, archived=True)
    assert meta.freshness(now=now).classification == "archived"
