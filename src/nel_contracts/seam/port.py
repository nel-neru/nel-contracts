from __future__ import annotations

from typing import Protocol, runtime_checkable

from nel_contracts.models.seam import SeamObservation, SeamReceipt, SeamReference
from nel_contracts.models.work import WorkIntent

# The governance-locked seam surface (design D12): EXACTLY one write verb and one read verb.
# There is deliberately no execute/deliver/push/publish/spend/get_credential/
# request_capability/request_approval/append_evidence/poll_* method. Adding any verb is an
# ADR-gated human precedent. The test ``test_seam_port_surface_locked`` pins this to two verbs.
SEAM_PORT_VERBS: tuple[str, str] = ("submit_intent", "observe")


@runtime_checkable
class SeamPort(Protocol):
    """The neutral inversion-of-control seam every world inhabitant calls.

    ``submit_intent`` expresses any external/irreversible action *only* as an intent; a gated
    category comes back as ``state=blocked`` with an ``approval_request_id`` (so approval needs
    no separate verb). ``observe`` is a pull-only projection scoped by authenticated caller
    identity — never authoritative caller-side. The concrete external-acting provider lives
    only in the private kernel and is injected out-of-process; the package default is sealed.
    """

    def submit_intent(self, intent: WorkIntent) -> SeamReceipt: ...

    def observe(self, ref: SeamReference) -> SeamObservation: ...
