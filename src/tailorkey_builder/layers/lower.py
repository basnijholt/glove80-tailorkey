"""Generate the Lower layer across TailorKey variants."""

from __future__ import annotations

import json
from copy import deepcopy
from importlib import resources
from typing import Dict, List

Layer = List[Dict]


def _load_base_layer() -> Layer:
    data_path = resources.files("tailorkey_builder.data").joinpath("lower_layer.json")
    with data_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data["Lower"]


_BASE_LOWER_LAYER: Layer = _load_base_layer()

_DUAL_PATCH = {
    54: {"value": "&to", "params": [{"value": 1, "params": []}]},
}


def _apply_patch(layer: Layer, patch: Dict[int, Dict]) -> None:
    for index, replacement in patch.items():
        layer[index] = deepcopy(replacement)


def build_lower_layer(variant: str) -> Layer:
    """Return the Lower layer customized for the given variant."""

    layer = deepcopy(_BASE_LOWER_LAYER)
    if variant == "dual":
        _apply_patch(layer, _DUAL_PATCH)
    return layer
