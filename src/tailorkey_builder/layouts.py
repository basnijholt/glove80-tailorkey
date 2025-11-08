"""Compose full TailorKey layouts from generated layers."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Dict

from .layers import build_all_layers

ROOT = Path(__file__).resolve().parents[2]
VARIANT_METADATA = json.loads((ROOT / "sources" / "variant_metadata.json").read_text())


def load_canonical_variant(variant: str) -> Dict:
    meta = VARIANT_METADATA[variant]
    path = ROOT / meta["output"]
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_layout(variant: str) -> Dict:
    """Build the complete layout dictionary for the given variant."""

    canonical = load_canonical_variant(variant)
    layout = deepcopy(canonical)

    generated_layers = build_all_layers(variant)
    ordered_layers = []
    for name in layout["layer_names"]:
        if name not in generated_layers:
            raise KeyError(f"No generated layer data for '{name}' in variant '{variant}'")
        ordered_layers.append(generated_layers[name])

    layout["layers"] = ordered_layers
    return layout
