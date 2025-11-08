"""Layer construction helpers and registry."""

from .autoshift import build_autoshift_layer
from .bilateral import build_bilateral_training_layers
from .cursor import build_cursor_layer
from .gaming import build_gaming_layer
from .hrm import build_hrm_layers
from .lower import build_lower_layer
from .magic import build_magic_layer
from .mouse import build_mouse_layers
from .symbol import build_symbol_layer
from .typing import build_typing_layer

from .base import Layer, LayerMap


def build_all_layers(variant: str) -> LayerMap:
    """Return every layer needed for the given variant."""

    layers: LayerMap = {}

    layers.update(build_hrm_layers(variant))
    layers["Typing"] = build_typing_layer(variant)
    layers["Autoshift"] = build_autoshift_layer(variant)
    layers["Cursor"] = build_cursor_layer(variant)
    if variant == "dual":
        layers["Cursor_macOS"] = build_cursor_layer("mac")
    layers["Symbol"] = build_symbol_layer(variant)
    layers["Gaming"] = build_gaming_layer(variant)
    layers["Lower"] = build_lower_layer(variant)
    layers.update(build_mouse_layers(variant))
    layers["Magic"] = build_magic_layer(variant)
    layers.update(build_bilateral_training_layers(variant))

    return layers


__all__ = [
    "Layer",
    "LayerMap",
    "build_all_layers",
    "build_autoshift_layer",
    "build_bilateral_training_layers",
    "build_cursor_layer",
    "build_gaming_layer",
    "build_hrm_layers",
    "build_lower_layer",
    "build_magic_layer",
    "build_mouse_layers",
    "build_symbol_layer",
    "build_typing_layer",
]
