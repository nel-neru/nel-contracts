#!/usr/bin/env python
"""CI guard: the runtime dependency closure is permissively licensed (design §2/§5).

The package ships a permissive-only runtime footprint (pydantic + stdlib). This checks the
installed license metadata of the runtime closure against an allowlist and fails on anything
non-permissive or unknown.

Minimal but real: the closure is a static list here. The full design derives it from the built
wheel/sdist metadata graph.
TODO(K1/K3): resolve the closure from wheel metadata rather than a static list.
"""

from __future__ import annotations

import sys
from importlib import metadata

# The runtime closure of ``nel-contracts`` (pydantic + its runtime deps).
_RUNTIME_CLOSURE = ("pydantic", "pydantic-core", "typing-extensions", "annotated-types")

# Permissive license identifiers/classifier fragments accepted for a public dependency.
_PERMISSIVE = (
    "mit",
    "bsd",
    "apache",
    "isc",
    "mpl-2.0",
    "mozilla public license 2.0",
    "python software foundation",
    "psf",
)


def _license_tokens(dist_name: str) -> list[str]:
    try:
        meta = metadata.metadata(dist_name)
    except metadata.PackageNotFoundError:
        return []
    tokens: list[str] = []
    for key in ("License-Expression", "License"):
        value = meta.get(key)
        if value:
            tokens.append(value)
    tokens.extend(meta.get_all("Classifier") or [])
    return [token.lower() for token in tokens if "license" in token.lower() or ":" not in token]


def _is_permissive(tokens: list[str]) -> bool:
    blob = " ".join(tokens)
    return any(fragment in blob for fragment in _PERMISSIVE)


def main() -> int:
    violations: list[str] = []
    for dist_name in _RUNTIME_CLOSURE:
        tokens = _license_tokens(dist_name)
        if not tokens:
            violations.append(f"{dist_name}: no license metadata found")
        elif not _is_permissive(tokens):
            violations.append(f"{dist_name}: non-permissive license {tokens}")
    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1
    print(f"runtime closure is permissively licensed ({len(_RUNTIME_CLOSURE)} dist(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
