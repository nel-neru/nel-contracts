from __future__ import annotations

import ast
import sys
from pathlib import Path

import nel_contracts

_PACKAGE_DIR = Path(nel_contracts.__file__).resolve().parent

# Private governor / world repos that the neutral public package must never import (design §5).
_FORBIDDEN_ROOTS = {"nel_os", "nel_dev_os", "pantheon", "nel_twin", "libraium", "provenfolio"}

# The only third-party roots a behavior-free contract package may import.
_ALLOWED_THIRD_PARTY = {"pydantic", "pydantic_core"}


def _iter_imports() -> list[tuple[str, str]]:
    """Every (file, imported-module) pair in the package, via a static import-graph walk."""
    found: list[tuple[str, str]] = []
    for path in _PACKAGE_DIR.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.append((str(path), alias.name))
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.append((str(path), node.module))
    return found


def test_no_private_imports() -> None:
    for path, module in _iter_imports():
        root = module.split(".")[0]
        assert root not in _FORBIDDEN_ROOTS, f"{path} imports private package {module!r}"


def test_only_permitted_third_party_imports() -> None:
    for path, module in _iter_imports():
        root = module.split(".")[0]
        if root in {"nel_contracts", "__future__"} or root in sys.stdlib_module_names:
            continue
        assert root in _ALLOWED_THIRD_PARTY, f"{path} imports unexpected third-party {module!r}"
