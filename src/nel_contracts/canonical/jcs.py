from __future__ import annotations

import hashlib
import math
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

# Reference canonicalizer for the Nel canonical serialization profile (design D14):
# RFC-8785 (JCS) — object keys sorted by UTF-16 code units, no insignificant whitespace,
# a fixed number encoding — extended with NFC string normalization and RFC-3339 UTC 'Z'
# timestamps at fixed fractional precision. The golden byte-fixtures in the conformance
# corpus pin these exact bytes; the ledger digest chain computes over them so all future
# language ports must reproduce identical bytes.

# Fixed fractional precision for canonical timestamps (microseconds).
_TIMESTAMP_FRACTIONAL_DIGITS = 6


def canonical_json(value: Any) -> str:
    """Return the canonical JSON text (a ``str``) for a JSON-compatible value."""
    return _emit(value)


def canonical_json_bytes(value: Any) -> bytes:
    """Return the canonical UTF-8 bytes for a JSON-compatible value."""
    return canonical_json(value).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def canonical_timestamp(value: datetime) -> str:
    """Format a timezone-aware datetime as an RFC-3339 UTC 'Z' string, fixed precision."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("canonical timestamps must be timezone-aware")
    moment = value.astimezone(UTC)
    fraction = f"{moment.microsecond:0{_TIMESTAMP_FRACTIONAL_DIGITS}d}"
    return f"{moment.strftime('%Y-%m-%dT%H:%M:%S')}.{fraction}Z"


def _emit(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _emit_string(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _emit_number(value)
    if isinstance(value, Mapping):
        return _emit_object(value)
    if isinstance(value, Sequence):
        return _emit_array(value)
    raise TypeError(f"value of type {type(value).__name__!r} is not JSON-canonicalizable")


def _emit_object(value: Mapping[Any, Any]) -> str:
    items: list[tuple[str, Any]] = []
    for raw_key, item in value.items():
        if not isinstance(raw_key, str):
            raise TypeError("canonical object keys must be strings")
        items.append((unicodedata.normalize("NFC", raw_key), item))
    # RFC-8785 orders keys by their UTF-16 code units; comparing UTF-16-BE byte sequences is
    # equivalent and correct for astral characters as well.
    items.sort(key=lambda pair: pair[0].encode("utf-16-be"))
    rendered = ",".join(f"{_emit_string(key)}:{_emit(item)}" for key, item in items)
    return "{" + rendered + "}"


def _emit_array(value: Sequence[Any]) -> str:
    return "[" + ",".join(_emit(item) for item in value) + "]"


def _emit_string(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    out: list[str] = ['"']
    for character in normalized:
        code = ord(character)
        if character == '"':
            out.append('\\"')
        elif character == "\\":
            out.append("\\\\")
        elif code == 0x08:
            out.append("\\b")
        elif code == 0x09:
            out.append("\\t")
        elif code == 0x0A:
            out.append("\\n")
        elif code == 0x0C:
            out.append("\\f")
        elif code == 0x0D:
            out.append("\\r")
        elif code < 0x20:
            out.append(f"\\u{code:04x}")
        else:
            out.append(character)
    out.append('"')
    return "".join(out)


def _emit_number(value: float) -> str:
    if math.isnan(value) or math.isinf(value):
        raise ValueError("NaN and Infinity are not valid canonical JSON numbers")
    if value == 0:
        return "0"
    if value.is_integer() and abs(value) < 1e21:
        return str(int(value))
    # TODO(K1/K3): full RFC-8785 / ECMAScript number formatting (exponent edge cases). The
    # conformance golden fixtures deliberately avoid non-integral floats until the four
    # language ports share a proven number formatter.
    return repr(value)
