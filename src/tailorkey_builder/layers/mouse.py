"""Generate the TailorKey mouse-oriented layers."""

from __future__ import annotations

import json
from copy import deepcopy
from importlib import resources
from typing import Dict, List

Layer = List[Dict]


def _load_base_layers() -> Dict[str, Layer]:
    data_path = resources.files("tailorkey_builder.data").joinpath("mouse_layers.json")
    with data_path.open(encoding="utf-8") as handle:
        return json.load(handle)


_BASE_MOUSE_LAYERS: Dict[str, Layer] = _load_base_layers()


_MAC_MOUSE_PATCH = {
    30: {"value": "&sk", "params": [{"value": "RGUI", "params": []}]},
    32: {"value": "&sk", "params": [{"value": "RCTRL", "params": []}]},
    55: {"value": "&kp", "params": [{"value": "LG", "params": [{"value": "X", "params": []}]}]},
    56: {"value": "&kp", "params": [{"value": "LG", "params": [{"value": "C", "params": []}]}]},
    57: {"value": "&kp", "params": [{"value": "LG", "params": [{"value": "V", "params": []}]}]},
}

_DUAL_MOUSE_PATCH = {
    55: {"value": "&none", "params": []},
    56: {"value": "&none", "params": []},
    57: {"value": "&none", "params": []},
}

_BILATERAL_MOUSE_PATCH = {
    41: {"value": "&mo", "params": [{"value": 17, "params": []}]},
    42: {"value": "&mo", "params": [{"value": 18, "params": []}]},
    43: {"value": "&mo", "params": [{"value": 16, "params": []}]},
    48: {"value": "&mo", "params": [{"value": 16, "params": []}]},
    49: {"value": "&mo", "params": [{"value": 18, "params": []}]},
    50: {"value": "&mo", "params": [{"value": 17, "params": []}]},
}


def _apply_patch(layer: Layer, patch: Dict[int, Dict]) -> None:
    for index, replacement in patch.items():
        layer[index] = deepcopy(replacement)


def _copy_base_layers() -> Dict[str, Layer]:
    return {name: deepcopy(layer) for name, layer in _BASE_MOUSE_LAYERS.items()}


def build_mouse_layers(variant: str) -> Dict[str, Layer]:
    """Return the four mouse-related layers for the requested variant."""

    layers = _copy_base_layers()
    mouse = layers["Mouse"]

    if variant in {"mac", "bilateral_mac"}:
        _apply_patch(mouse, _MAC_MOUSE_PATCH)

    if variant == "dual":
        _apply_patch(mouse, _DUAL_MOUSE_PATCH)

    if variant in {"bilateral_windows", "bilateral_mac"}:
        _apply_patch(mouse, _BILATERAL_MOUSE_PATCH)

    return layers
