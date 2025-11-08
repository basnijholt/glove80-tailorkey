"""Generate the Lower layer across TailorKey variants."""

from __future__ import annotations

from .base import Layer, apply_patch_if, copy_layer, load_layer_from_data


_BASE_LOWER_LAYER: Layer = load_layer_from_data("Lower", filename="lower_layer.json")

_DUAL_PATCH = {
    54: {"value": "&to", "params": [{"value": 1, "params": []}]},
}


def build_lower_layer(variant: str) -> Layer:
    """Return the Lower layer customized for the given variant."""

    layer = copy_layer(_BASE_LOWER_LAYER)
    apply_patch_if(layer, variant == "dual", _DUAL_PATCH)
    return layer
