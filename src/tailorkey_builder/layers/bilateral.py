"""Bilateral-specific training layers."""

from __future__ import annotations

from .base import LayerMap, apply_patch, copy_layers_map, load_layers_map


_BASE_BILATERAL_LAYERS: LayerMap = load_layers_map("bilateral_layers.json")

_MAC_PATCHES = {
    "LeftIndex": {
        35: {
            "value": "&HRM_left_index_pinky_v1B_TKZ",
            "params": [{"value": "LCTRL", "params": []}, {"value": "A", "params": []}],
        },
        37: {
            "value": "&HRM_left_index_middy_v1B_TKZ",
            "params": [{"value": "LGUI", "params": []}, {"value": "D", "params": []}],
        },
    },
    "LeftMiddy": {
        35: {
            "value": "&HRM_left_middy_pinky_v1B_TKZ",
            "params": [{"value": "LCTRL", "params": []}, {"value": "A", "params": []}],
        },
    },
    "LeftRingy": {
        35: {
            "value": "&HRM_left_ring_pinky_v1B_TKZ",
            "params": [{"value": "LCTRL", "params": []}, {"value": "A", "params": []}],
        },
        37: {
            "value": "&HRM_left_ring_middy_v1B_TKZ",
            "params": [{"value": "LGUI", "params": []}, {"value": "D", "params": []}],
        },
    },
    "LeftPinky": {
        37: {
            "value": "&HRM_left_pinky_middy_v1B_TKZ",
            "params": [{"value": "LGUI", "params": []}, {"value": "D", "params": []}],
        },
    },
    "RightIndex": {
        42: {
            "value": "&HRM_right_index_middy_v1B_TKZ",
            "params": [{"value": "RGUI", "params": []}, {"value": "K", "params": []}],
        },
        44: {
            "value": "&HRM_right_index_pinky_v1B_TKZ",
            "params": [
                {"value": "LCTRL", "params": []},
                {"value": "SEMI", "params": []},
            ],
        },
    },
    "RightMiddy": {
        44: {
            "value": "&HRM_right_middy_pinky_v1B_TKZ",
            "params": [
                {"value": "RCTRL", "params": []},
                {"value": "SEMI", "params": []},
            ],
        },
    },
    "RightRingy": {
        42: {
            "value": "&HRM_right_ring_middy_v1B_TKZ",
            "params": [{"value": "RGUI", "params": []}, {"value": "K", "params": []}],
        },
        44: {
            "value": "&HRM_right_ring_pinky_v1B_TKZ",
            "params": [
                {"value": "RCTRL", "params": []},
                {"value": "SEMI", "params": []},
            ],
        },
    },
    "RightPinky": {
        42: {
            "value": "&HRM_right_pinky_middy_v1B_TKZ",
            "params": [{"value": "RGUI", "params": []}, {"value": "K", "params": []}],
        },
    },
}


def build_bilateral_training_layers(variant: str) -> LayerMap:
    """Return the eight bilateral training layers if needed."""

    if variant not in {"bilateral_windows", "bilateral_mac"}:
        return {}

    layers = copy_layers_map(_BASE_BILATERAL_LAYERS)
    if variant == "bilateral_mac":
        for name, patch in _MAC_PATCHES.items():
            apply_patch(layers[name], patch)

    return layers
