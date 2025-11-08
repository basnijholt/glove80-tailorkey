"""QuantumTouch MouseSlow layer (transparent helper)."""

from __future__ import annotations

from ...base import Layer, LayerSpec, build_layer_from_spec


MOUSE_SLOW_LAYER_SPEC = LayerSpec(overrides={})


def build_mouse_slow_layer(_variant: str) -> Layer:
    return build_layer_from_spec(MOUSE_SLOW_LAYER_SPEC)
