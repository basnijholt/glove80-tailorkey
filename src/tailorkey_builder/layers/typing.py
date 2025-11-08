"""Typing layer generation."""

from __future__ import annotations

from .base import Layer, copy_layer, load_layer_from_data


_BASE_TYPING_LAYER: Layer = load_layer_from_data("Typing", filename="typing_layer.json")


def build_typing_layer(_variant: str) -> Layer:
    """The Typing layer is identical across all variants."""

    return copy_layer(_BASE_TYPING_LAYER)
