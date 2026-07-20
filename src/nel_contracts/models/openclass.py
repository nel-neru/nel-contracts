from __future__ import annotations

from typing import Any, Self

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class OpenClassifier:
    """Base for an open wire vocabulary (design D15).

    A wire value is any ``str``. Members listed in :meth:`known_values` classify to
    themselves; every unknown member downgrades to :meth:`default_deny_bucket` and **never
    raises**. This is the forward-compatibility contract: a newer producer can emit a member
    an older pinned consumer has never seen without breaking deserialization, and the unknown
    member resolves to the most restrictive (default-deny) bucket rather than silently to a
    permissive one.

    Strict, closed ``Enum`` types are reserved for internal kernel use only; on the wire the
    boundary is always open.
    """

    __slots__ = ("_raw",)

    def __init__(self, raw: str) -> None:
        self._raw = raw

    # --- subclass contract -------------------------------------------------------------
    @classmethod
    def known_values(cls) -> frozenset[str]:
        """The recognized members of this vocabulary."""
        raise NotImplementedError

    @classmethod
    def default_deny_bucket(cls) -> str:
        """The bucket an unknown member downgrades to (the most restrictive choice)."""
        raise NotImplementedError

    # --- value semantics ---------------------------------------------------------------
    @property
    def raw(self) -> str:
        """The exact wire string, preserved verbatim even when unknown."""
        return self._raw

    @property
    def is_known(self) -> bool:
        return self._raw in self.known_values()

    @property
    def classification(self) -> str:
        """The known member itself, or the default-deny bucket when unknown."""
        return self._raw if self.is_known else self.default_deny_bucket()

    def __str__(self) -> str:
        return self._raw

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._raw!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OpenClassifier):
            return type(self) is type(other) and self._raw == other._raw
        return NotImplemented

    def __hash__(self) -> int:
        return hash((type(self), self._raw))

    # --- pydantic integration ----------------------------------------------------------
    @classmethod
    def _coerce(cls, value: Any) -> Self:
        if isinstance(value, cls):
            return value
        if isinstance(value, OpenClassifier):
            return cls(value.raw)
        if isinstance(value, str):
            return cls(value)
        raise TypeError(f"{cls.__name__} wire value must be a string")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._coerce,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.raw,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        rendered: JsonSchemaValue = {"type": "string", "title": cls.__name__}
        known = sorted(cls.known_values())
        if known:
            # Non-restrictive: the wire stays open, so ``examples`` documents the known
            # members without turning them into an ``enum`` a newer member would violate.
            rendered["examples"] = known
        return rendered
