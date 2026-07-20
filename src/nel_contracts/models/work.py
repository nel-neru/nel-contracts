from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, model_validator

from nel_contracts.models.actor import ClaimedActor
from nel_contracts.models.content_identity import ContentIdentity
from nel_contracts.models.identifiers import (
    GitObjectId,
    RepoRef,
    ResourceRef,
    StrictModel,
    Ulid,
    UtcTimestamp,
)
from nel_contracts.models.openclass import OpenClassifier
from nel_contracts.models.visibility import VisibilityLevel


class DeliveryOperation(OpenClassifier):
    """Open vocabulary for a delivery operation."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset({"deliver", "push", "publish_artifact"})

    @classmethod
    def default_deny_bucket(cls) -> str:
        return "external"


class GitDeliveryExtension(StrictModel):
    """Git-specific delivery fields, kept out of the neutral ``DeliveryIntent`` base so the
    core stays repo-agnostic (resolves the "git baked into the neutral package" finding)."""

    content_tree_oid: GitObjectId
    base_ref: str
    git_operation: str


class WorkIntent(StrictModel):
    """Base for the only expression a world-inhabitant can form for an external/irreversible
    action. Concrete members discriminate on ``kind``. Every field is a claim; the kernel
    re-derives actor and classification (design §4)."""

    intent_id: Ulid
    actor: ClaimedActor
    submitted_at: UtcTimestamp


_FORBIDDEN_BODY_KEYS = frozenset(
    {
        "body",
        "rendered_body",
        "content",
        "html",
        "markdown",
        "text",
        "payload_body",
        "attachments",
    }
)


class PublishIntent(WorkIntent):
    """Publish an already-rendered artifact by identity only. Forbids any rendered-body field
    so the brain's body is never held in the intent (resolves the brain-body bypass)."""

    kind: Literal["publish"] = "publish"
    content_identity: ContentIdentity
    target_visibility: VisibilityLevel
    summary: str | None = None

    @model_validator(mode="before")
    @classmethod
    def forbid_rendered_body(cls, data: Any) -> Any:
        if isinstance(data, Mapping):
            present = _FORBIDDEN_BODY_KEYS & set(data.keys())
            if present:
                raise ValueError(f"PublishIntent must not carry a rendered body: {sorted(present)}")
        return data


class DeliveryIntent(WorkIntent):
    """Deliver content bound by identity. Git specifics live in ``git`` (a specialization),
    not in the neutral base."""

    kind: Literal["delivery"] = "delivery"
    content_identity: ContentIdentity
    operation: DeliveryOperation
    git: GitDeliveryExtension | None = None


class SpendIntent(WorkIntent):
    kind: Literal["spend"] = "spend"
    amount_minor: int = Field(ge=0)
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    payee: str


class DeployIntent(WorkIntent):
    kind: Literal["deploy"] = "deploy"
    environment: str
    content_identity: ContentIdentity


class ExternalReadIntent(WorkIntent):
    kind: Literal["external_read"] = "external_read"
    resource: ResourceRef


class VisibilityChangeIntent(WorkIntent):
    kind: Literal["visibility_change"] = "visibility_change"
    repo: RepoRef
    from_visibility: VisibilityLevel
    to_visibility: VisibilityLevel


class MigrationIntent(WorkIntent):
    kind: Literal["migration"] = "migration"
    description: str
    destructive: bool = True


class HistoryRewriteIntent(WorkIntent):
    kind: Literal["history_rewrite"] = "history_rewrite"
    repo: RepoRef
    ref: str


class PiiPolicyIntent(WorkIntent):
    kind: Literal["pii_policy"] = "pii_policy"
    description: str


class OtherIntent(WorkIntent):
    """The default-deny landing member. An unknown wire ``kind`` downgrades here, preserving
    the original in ``declared_kind`` (design D15)."""

    kind: Literal["other"] = "other"
    declared_kind: str | None = None
    summary: str | None = None


# The canonical discriminated union over ``kind`` (design: "WorkIntent discriminated union on
# kind"). Used for schema projection and as the typed surface of the ten members.
AnyWorkIntent = (
    PublishIntent
    | DeliveryIntent
    | SpendIntent
    | DeployIntent
    | ExternalReadIntent
    | VisibilityChangeIntent
    | MigrationIntent
    | HistoryRewriteIntent
    | PiiPolicyIntent
    | OtherIntent
)
_MEMBERS: dict[str, type[WorkIntent]] = {
    "publish": PublishIntent,
    "delivery": DeliveryIntent,
    "spend": SpendIntent,
    "deploy": DeployIntent,
    "external_read": ExternalReadIntent,
    "visibility_change": VisibilityChangeIntent,
    "migration": MigrationIntent,
    "history_rewrite": HistoryRewriteIntent,
    "pii_policy": PiiPolicyIntent,
    "other": OtherIntent,
}

KNOWN_INTENT_KINDS = frozenset(_MEMBERS)

_OTHER_BASE_KEYS = ("intent_id", "actor", "submitted_at", "summary")


def _downgrade_to_other(data: Mapping[str, Any]) -> dict[str, Any]:
    """Rewrite a payload with an unknown/absent ``kind`` into an ``OtherIntent`` payload,
    preserving the original tag in ``declared_kind`` (design D15)."""
    downgraded: dict[str, Any] = {key: data[key] for key in _OTHER_BASE_KEYS if key in data}
    kind = data.get("kind")
    downgraded["kind"] = "other"
    downgraded["declared_kind"] = kind if isinstance(kind, str) else None
    return downgraded


def _route_unknown_kind(data: Any) -> Any:
    """Before-validator for the typed union: an unknown ``kind`` is routed to ``OtherIntent``
    instead of raising, so the discriminated union has the same open-enum behavior as
    ``coerce_work_intent`` (design D15)."""
    if isinstance(data, Mapping):
        kind = data.get("kind")
        if not (isinstance(kind, str) and kind in KNOWN_INTENT_KINDS):
            return _downgrade_to_other(data)
    return data


# The canonical discriminated union over ``kind``. The discriminator is applied to the inner
# union; a before-validator wraps it (outer) so it runs FIRST and routes an unknown tag to
# ``OtherIntent`` before discrimination — the typed-union path never raises on an unknown kind,
# uniform open-enum behavior matching ``coerce_work_intent`` (design D15).
_DiscriminatedWorkIntent = Annotated[AnyWorkIntent, Field(discriminator="kind")]
WorkIntentUnion = Annotated[_DiscriminatedWorkIntent, BeforeValidator(_route_unknown_kind)]


def coerce_work_intent(payload: Mapping[str, Any]) -> WorkIntent:
    """Parse a wire payload into a concrete intent, running the selected member's validator on
    every submission. An unknown ``kind`` never raises: it downgrades to ``OtherIntent``
    (default-deny/external), preserving the original kind in ``declared_kind`` (design D15)."""
    data = dict(payload)
    kind = data.get("kind")
    if isinstance(kind, str) and kind in _MEMBERS:
        return _MEMBERS[kind].model_validate(data)
    return OtherIntent.model_validate(_downgrade_to_other(data))
