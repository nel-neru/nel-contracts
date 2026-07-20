#!/usr/bin/env python
"""CI guard: no private package in ANY dependency section (design §5).

``nel-contracts`` must never depend on the private governor (`nel-os`) or on any world repo,
in any form — ``[project.dependencies]``, any ``[project.optional-dependencies]`` extra, or a
PEP 735 ``[dependency-groups]`` group. The sole runtime dependency must be ``pydantic``.

Minimal but real: this resolves the declared dependency *sections* of ``pyproject.toml``. The
full design also resolves the built wheel/sdist metadata graph in CI; that stronger check is a
CI step layered on top of this one.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_PYPROJECT = _REPO_ROOT / "pyproject.toml"

# Public sibling NEL packages that ARE permitted as dependencies.
_ALLOWED_NEL = frozenset({"nel-contracts", "nel-runtime"})

# The only permitted runtime dependency.
_ALLOWED_RUNTIME = frozenset({"pydantic"})

# Private or forbidden-direction distributions (substring match, normalized).
_FORBIDDEN_SUBSTRINGS = ("nel-os", "nel-dev-os", "nel-twin", "pantheon", "libraium", "provenfolio")


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def _requirement_name(requirement: str) -> str:
    match = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
    if not match:
        return ""
    return _normalize(match.group(1))


def _is_private(requirement: str) -> bool:
    name = _requirement_name(requirement)
    normalized_req = _normalize(requirement)
    if any(token in normalized_req for token in _FORBIDDEN_SUBSTRINGS):
        return True
    return (name.startswith("nel-") or name == "nel") and name not in _ALLOWED_NEL


def _iter_sections(data: dict[str, object]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    project = data.get("project", {})
    if isinstance(project, dict):
        runtime = project.get("dependencies", [])
        if isinstance(runtime, list):
            sections.append(("project.dependencies", [str(item) for item in runtime]))
        optional = project.get("optional-dependencies", {})
        if isinstance(optional, dict):
            for extra, requirements in optional.items():
                if isinstance(requirements, list):
                    sections.append(
                        (f"optional-dependencies.{extra}", [str(item) for item in requirements])
                    )
    groups = data.get("dependency-groups", {})
    if isinstance(groups, dict):
        for group, requirements in groups.items():
            if isinstance(requirements, list):
                strings = [str(item) for item in requirements if isinstance(item, str)]
                sections.append((f"dependency-groups.{group}", strings))
    return sections


def main() -> int:
    if not _PYPROJECT.exists():
        print(f"pyproject not found: {_PYPROJECT}", file=sys.stderr)
        return 1
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    sections = _iter_sections(data)

    violations: list[str] = []
    for label, requirements in sections:
        for requirement in requirements:
            if _is_private(requirement):
                violations.append(f"[{label}] private/forbidden dependency: {requirement!r}")

    # The sole runtime dependency must be pydantic.
    runtime_names = {
        _requirement_name(item)
        for label, requirements in sections
        if label == "project.dependencies"
        for item in requirements
    }
    runtime_names.discard("")
    if runtime_names != set(_ALLOWED_RUNTIME):
        violations.append(
            f"[project.dependencies] runtime deps must be exactly {sorted(_ALLOWED_RUNTIME)}, "
            f"found {sorted(runtime_names)}"
        )

    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1
    print(f"no private dependencies ({len(sections)} section(s) checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
