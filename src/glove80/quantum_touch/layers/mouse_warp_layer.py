"""QuantumTouch MouseWarp layer."""

from __future__ import annotations

from ...base import Layer, LayerSpec, build_layer_from_spec


MOUSE_WARP_LAYER_SPEC = LayerSpec(overrides={})


def build_mouse_warp_layer(_variant: str) -> Layer:
    return build_layer_from_spec(MOUSE_WARP_LAYER_SPEC)
