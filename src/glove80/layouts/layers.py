"""Shared helpers for declarative layer construction."""

from __future__ import annotations

from typing import Any, Sequence

from glove80.base import KeySpec, LayerSpec
from glove80.specs.utils import kp

Token = Any


def token_to_key(token: Token) -> KeySpec:
    if isinstance(token, KeySpec):
        return token
    if isinstance(token, tuple):
        value = token[0]
        params = tuple(token[1:])
        return KeySpec(value, params)
    if isinstance(token, str):
        if token.startswith("&"):
            return KeySpec(token)
        return kp(token)
    raise TypeError(f"Unsupported token type: {token!r}")


def rows_to_layer_spec(rows: Sequence[Sequence[Token]]) -> LayerSpec:
    flat: list[Token] = [token for row in rows for token in row]
    if len(flat) != 80:
        raise ValueError(f"Expected 80 entries for a layer, got {len(flat)}")
    overrides = {idx: token_to_key(token) for idx, token in enumerate(flat)}
    return LayerSpec(overrides=overrides)


def transparent_layer() -> LayerSpec:
    return LayerSpec(overrides={})


__all__ = ["rows_to_layer_spec", "transparent_layer", "token_to_key", "Token"]
