"""Gaming layer generation."""

from __future__ import annotations

from .base import Layer, copy_layer, load_layer_from_data


_BASE_GAMING_LAYER: Layer = load_layer_from_data("Gaming", filename="gaming_layer.json")


def build_gaming_layer(_variant: str) -> Layer:
    return copy_layer(_BASE_GAMING_LAYER)
