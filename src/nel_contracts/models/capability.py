from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from nel_contracts.models.identifiers import Slug, StrictModel, UtcTimestamp
from nel_contracts.models.openclass import OpenClassifier


class CapabilityClassification(OpenClassifier):
    """Open vocabulary classifying a capability's blast radius."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset({"internal_only", "external"})

    @classmethod
    def default_deny_bucket(cls) -> str:
        # Default-deny: an absent/unknown classification is external, therefore blocked.
        return "external"


class Capability(StrictModel):
    """A neutral capability shape under a default-deny classification.

    ``internal_only`` additionally requires a structurally verified ``egress == "none"``.
    Any capability whose executor touches the network or credentials is ``external``
    regardless of label (resolves the "internal_only allowlist is not self-completing"
    finding).
    """

    capability_id: Slug
    classification: CapabilityClassification
    egress: Literal["none", "kernel_channel", "external"] = "external"
    description: str | None = None

    @model_validator(mode="after")
    def enforce_default_deny(self) -> Capability:
        classification = self.classification.classification
        if classification == "internal_only" and self.egress != "none":
            raise ValueError("internal_only capability requires egress=none")
        if self.egress != "none" and classification != "external":
            raise ValueError("a capability with egress must be classified external")
        return self


class MediatedCapabilityGrant(StrictModel):
    """A kernel-internal, per-approval grant shape. It is never a bearer token and there is
    no ``request_capability`` port verb; construction here carries no authority."""

    capability_id: Slug
    single_use: bool = True
    expires_at: UtcTimestamp | None = None
