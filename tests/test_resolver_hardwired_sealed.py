from __future__ import annotations

import nel_contracts
import nel_contracts.seam.resolver as resolver_module
from nel_contracts.seam.resolver import DeploymentBinding, resolve_seam
from nel_contracts.seam.sealed import SealedSeam


def test_default_resolution_is_sealed() -> None:
    assert isinstance(resolve_seam(), SealedSeam)


def test_binding_descriptor_still_resolves_sealed() -> None:
    # Even a well-formed deployment binding cannot yield a live seam from the public package:
    # it ships no transport client and no kernel verification key (K1 concern).
    binding = DeploymentBinding(
        channel_address="uds:///run/nel/kernel.sock",
        kernel_public_key_path="/etc/nel/kernel.pub",
    )
    assert isinstance(resolve_seam(binding=binding), SealedSeam)


def test_no_world_callable_provider_override_exists() -> None:
    assert not hasattr(nel_contracts, "register_seam_provider")
    assert not hasattr(resolver_module, "register_seam_provider")
    assert "register_seam_provider" not in nel_contracts.__all__
