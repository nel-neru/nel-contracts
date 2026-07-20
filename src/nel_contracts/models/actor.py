from __future__ import annotations

from typing import Literal

from nel_contracts.models.identifiers import StrictModel
from nel_contracts.models.openclass import OpenClassifier


class ActorKind(OpenClassifier):
    """Open vocabulary of actors that can express an intent."""

    @classmethod
    def known_values(cls) -> frozenset[str]:
        return frozenset(
            {
                "human",
                "script",
                "http",
                "mcp",
                "github_actions",
                "codex",
                "claude_code",
                "game_engine",
            }
        )

    @classmethod
    def default_deny_bucket(cls) -> str:
        # An unrecognized actor is treated as an untrusted external caller.
        return "external_unknown"


class KernelAttestation(StrictModel):
    """A kernel-authored attestation shape. The package ships **no** verification key, so a
    world-built instance of this shape is unverifiable and therefore untrusted (design §0)."""

    authority: Literal["kernel"] = "kernel"
    nonce: str
    signature: str


class ClaimedActor(StrictModel):
    """An inbound, self-asserted actor carried on a ``WorkIntent``.

    Every field is a claim. It is NOT an authorization input: the kernel re-derives the real
    actor from the authenticated channel identity (design §4). ``attestation_state`` is pinned
    to ``unattested`` so a public consumer cannot confuse it with a kernel-attested actor.
    """

    actor_kind: ActorKind
    display_name: str | None = None
    is_advisory: bool = True
    attestation_state: Literal["unattested"] = "unattested"


class AttestedActor(StrictModel):
    """A kernel-attested actor carried on kernel-authored records. Trust requires verifying
    ``attestation`` against the kernel — which the package cannot do (no key shipped)."""

    actor_kind: ActorKind
    attestation_state: Literal["kernel_attested"] = "kernel_attested"
    attestation: KernelAttestation
