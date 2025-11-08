"""Autoshift layer generation."""

from __future__ import annotations

from .base import Layer, copy_layer, load_layer_from_data


_BASE_AUTOSHIFT_LAYER: Layer = load_layer_from_data(
    "Autoshift", filename="autoshift_layer.json"
)


def build_autoshift_layer(_variant: str) -> Layer:
    return copy_layer(_BASE_AUTOSHIFT_LAYER)
