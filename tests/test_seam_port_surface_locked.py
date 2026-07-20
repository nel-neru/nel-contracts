from __future__ import annotations

from nel_contracts.seam.port import SEAM_PORT_VERBS, SeamPort
from nel_contracts.seam.sealed import SealedSeam

_FORBIDDEN_VERBS = frozenset(
    {
        "execute",
        "deliver",
        "push",
        "publish",
        "spend",
        "get_credential",
        "request_capability",
        "request_approval",
        "append_evidence",
        "poll",
    }
)


def _declared_members() -> set[str]:
    return {name for name in vars(SeamPort) if not name.startswith("_")}


def test_seam_port_exposes_exactly_two_verbs() -> None:
    assert _declared_members() == {"submit_intent", "observe"}
    assert set(SEAM_PORT_VERBS) == {"submit_intent", "observe"}


def test_seam_port_has_no_forbidden_verb() -> None:
    assert _declared_members().isdisjoint(_FORBIDDEN_VERBS)


def test_sealed_seam_satisfies_the_protocol() -> None:
    assert isinstance(SealedSeam(), SeamPort)
