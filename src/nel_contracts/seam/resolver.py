from __future__ import annotations

from nel_contracts.models.identifiers import StrictModel
from nel_contracts.seam.port import SeamPort
from nel_contracts.seam.sealed import SealedSeam


class DeploymentBinding(StrictModel):
    """A deployment-supplied binding descriptor (a *shape*, not a client).

    A deployed kernel writes this to a well-known location the world runtime cannot forge into
    an in-process provider: the authenticated channel address plus the path to the kernel's
    public verification key. The package itself supplies none and ships no transport client
    and no verification key, so it can never turn a descriptor into a live seam on its own.
    """

    channel_address: str
    kernel_public_key_path: str


def _load_deployment_binding() -> DeploymentBinding | None:
    """Read the deployment-supplied binding descriptor. The package supplies none.

    TODO(K1): read and validate the kernel-written descriptor from its well-known location.
    """
    return None


def resolve_seam(*, binding: DeploymentBinding | None = None) -> SeamPort:
    """Resolve the seam, hardwired fail-closed (resolves Lens1-C1 / Lens2-H1).

    Returns :class:`SealedSeam` unless a deployment binding is present AND the out-of-process
    kernel channel is available — which the public package can never provide, because it ships
    no transport client and no kernel verification key. There is deliberately no
    ``register_seam_provider`` and no world-callable in-process provider override: only the
    K1 deployment can wire a non-sealed seam, out-of-process.
    """
    descriptor = binding if binding is not None else _load_deployment_binding()
    if descriptor is None:
        return SealedSeam()
    # A descriptor is present, but wiring the authenticated out-of-process kernel channel is a
    # K1 deployment concern. Absent that kernel-provided component, resolution stays sealed.
    # TODO(K1): construct the out-of-process authenticated kernel channel client here.
    return SealedSeam()
