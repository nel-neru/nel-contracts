from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, PlainSerializer, StringConstraints

from nel_contracts.canonical.jcs import canonical_timestamp


class StrictModel(BaseModel):
    """House base model: unknown keys are rejected so a body-shaped payload cannot smuggle
    fields past a typed boundary."""

    model_config = ConfigDict(extra="forbid")


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return value


# A timezone-aware timestamp that serializes to the canonical RFC-3339 UTC 'Z' form (D14)
# in JSON mode, so canonical bytes are a pure function of the JSON structure.
UtcTimestamp = Annotated[
    datetime,
    AfterValidator(_ensure_utc),
    PlainSerializer(canonical_timestamp, return_type=str, when_used="json"),
]

# A Crockford base32 ULID (26 chars, excludes I, L, O, U).
Ulid = Annotated[str, StringConstraints(pattern=r"^[0-9A-HJKMNP-TV-Z]{26}$")]

# A portable lowercase slug identifier (mirrors the nel-os registry id shape).
Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")]

# A lowercase hex SHA-256 digest.
Sha256Hex = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

# A full lowercase Git object id (SHA-1 or SHA-256 tree/commit oid).
GitObjectId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")]

# A ``MAJOR.MINOR`` schema/protocol version tag.
SchemaVersion = Annotated[str, StringConstraints(pattern=r"^[0-9]+\.[0-9]+$")]


class RepoRef(StrictModel):
    """A logical, portable repository reference. Carries no filesystem path (a public
    contract must never leak a governor-local ``C:\\Users`` path)."""

    repo: Slug
    host: str | None = None


class ResourceRef(StrictModel):
    """A neutral reference to a world resource the kernel projects."""

    resource_kind: str
    resource_id: str


class OpaqueScopeDescriptor(StrictModel):
    """An opaque capability-scope token. The world may carry it but never interprets it; its
    meaning is assigned and re-derived kernel-side (non-authoritative here)."""

    descriptor: str
