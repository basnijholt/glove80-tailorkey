"""Shared helpers for declarative layer construction."""

from __future__ import annotations

from typing import Any, Sequence

from glove80.base import KeySpec, LayerRef, LayerSpec
from glove80.specs.utils import kp

Token = Any


def _normalize_param_token(param: Token) -> KeySpec:
    if isinstance(param, KeySpec):
        return param
    if isinstance(param, tuple):
        return _token_to_key(param)
    if isinstance(param, (str, int, LayerRef)):
        return KeySpec(param)
    raise TypeError(f"Unsupported parameter token type: {param!r}")  # pragma: no cover


def _token_to_key(token: Token) -> KeySpec:
    if isinstance(token, KeySpec):
        return token
    if isinstance(token, tuple):
        value = token[0]
        params = tuple(_normalize_param_token(param) for param in token[1:])
        return KeySpec(value, params)
    if isinstance(token, str):
        if token.startswith("&"):
            return KeySpec(token)
        return kp(token)
    if isinstance(token, (int, LayerRef)):
        return KeySpec(token)
    raise TypeError(f"Unsupported token type: {token!r}")  # pragma: no cover


def rows_to_layer_spec(rows: Sequence[Sequence[Token]]) -> LayerSpec:
    flat: list[Token] = [token for row in rows for token in row]
    if len(flat) != 80:  # pragma: no cover
        raise ValueError(f"Expected 80 entries for a layer, got {len(flat)}")
    overrides = {idx: _token_to_key(token) for idx, token in enumerate(flat)}
    return LayerSpec(overrides=overrides)


def _transparent_layer() -> LayerSpec:
    return LayerSpec(overrides={})


__all__ = ["rows_to_layer_spec", "_transparent_layer", "_token_to_key", "Token"]
