"""Compose QuantumTouch layouts from declarative layer specs."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Dict

from ..metadata import get_variant_metadata
from .layers import build_all_layers

ROOT = Path(__file__).resolve().parents[3]


def _load_canonical_variant(variant: str) -> Dict:
    meta = get_variant_metadata(variant, layout="quantum_touch")
    path = ROOT / meta["output"]
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_layout(variant: str = "default") -> Dict:
    """Return the canonical QuantumTouch layout with generated layers overlaid."""

    canonical = _load_canonical_variant(variant)
    layout = deepcopy(canonical)

    generated_layers = build_all_layers(variant)
    canonical_map = dict(zip(layout["layer_names"], layout["layers"]))

    ordered_layers = []
    for name in layout["layer_names"]:
        ordered_layers.append(generated_layers.get(name, canonical_map[name]))

    layout["layers"] = ordered_layers
    return layout
