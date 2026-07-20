from __future__ import annotations

from datetime import UTC, datetime

from nel_contracts.models.actor import ActorKind, ClaimedActor
from nel_contracts.models.content_identity import ContentIdentity

# Valid Crockford base32 ULIDs (26 chars, no I/L/O/U).
ULID_A = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
ULID_B = "01ARZ3NDEKTSV4RRFFQ69G5FB1"
ULID_C = "01ARZ3NDEKTSV4RRFFQ69G5FC2"

# A 64-hex SHA-256-shaped digest for fixtures.
DIGEST_64 = "a" * 64


def fixed_now() -> datetime:
    """A deterministic timezone-aware timestamp for fixtures."""
    return datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)


def human_actor() -> ClaimedActor:
    return ClaimedActor(actor_kind=ActorKind("human"))


def content_identity() -> ContentIdentity:
    return ContentIdentity(content_digest=DIGEST_64)
