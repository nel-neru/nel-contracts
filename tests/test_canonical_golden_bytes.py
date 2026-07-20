from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import pytest

from nel_contracts.canonical.jcs import canonical_json, canonical_json_bytes, canonical_timestamp
from tests.support import fixed_now

_FIXTURES = Path(__file__).resolve().parent.parent / "conformance" / "fixtures" / "canonical"


def test_key_sorting_and_unicode_are_hand_verifiable() -> None:
    # Keys sorted by UTF-16 code units: "a" (0x61) < "b" (0x62) < U+00E9; array order
    # preserved; non-ASCII emitted as literal UTF-8.
    value = {"b": 1, "a": [3, 2], "é": "café"}
    assert canonical_json(value) == '{"a":[3,2],"b":1,"é":"café"}'


def test_nfc_normalization() -> None:
    # Decomposed "e" + combining acute (U+0065 U+0301) normalizes to precomposed U+00E9.
    decomposed = unicodedata.normalize("NFD", "é")
    assert not unicodedata.is_normalized("NFC", decomposed)
    assert canonical_json({"k": decomposed}) == '{"k":"é"}'


def test_primitives_and_escaping() -> None:
    assert (
        canonical_json({"a": True, "b": False, "c": None, "d": 0, "e": -5})
        == '{"a":true,"b":false,"c":null,"d":0,"e":-5}'
    )
    assert canonical_json({"x": "a\nb\tc"}) == '{"x":"a\\nb\\tc"}'
    # A raw control character (U+0001) escapes to a lowercase-hex \\u sequence.
    assert canonical_json({"x": chr(1)}) == '{"x":"\\u0001"}'


def test_canonical_timestamp_is_fixed_precision_z() -> None:
    assert canonical_timestamp(fixed_now()) == "2026-07-20T12:00:00.000000Z"


def test_integral_float_serializes_as_integer() -> None:
    assert canonical_json({"x": 2.0}) == '{"x":2}'


def test_non_integral_number_is_rejected() -> None:
    # Fail closed rather than emit best-effort (possibly wrong) bytes for a non-integral number.
    with pytest.raises(ValueError, match="non-integral"):
        canonical_json({"x": 1.5})


def test_golden_byte_fixture_is_reproduced() -> None:
    source = json.loads((_FIXTURES / "basic.json").read_text(encoding="utf-8"))
    expected = (_FIXTURES / "basic.bytes").read_bytes()
    assert canonical_json_bytes(source) == expected
