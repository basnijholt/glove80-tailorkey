"""Compose stock Glove80 layouts shipped by MoErgo."""

from __future__ import annotations

import json
from importlib import resources
from typing import Dict

from ..layouts.common import attach_variant_metadata

RESOURCE_MAP: Dict[str, str] = {
    "factory_default": "786290ed-6d54-4959-87bd-b3b7149ca95d_Glove80 Factory Default Layout.json",
    "factory_default_macos": "19dc00ef-126a-497b-bdd6-650d32eb566a_Glove80 Factory Default Layout for macOS.json",
    "mouse_emulation": "68e63743-8cdc-417e-9674-58eeb673e1f4_Mouse Emulation Example.json",
    "colemak": "a1417501-9d2c-4c96-81b5-17c4cab33e9c_Colemak Layout.json",
    "colemak_dh": "a402821d-ef11-49b6-81bf-dee2df364ec8_Colemak-DH Layout.json",
    "dvorak": "1c843d8b-045d-41c7-9887-14f0cbfed15b_Dvorak Layout.json",
    "workman": "612c142e-d46d-4bdf-ae8b-4902f5eeb145_Workman Layout.json",
    "kinesis": "242e140f-d342-418b-b9a1-d4b2fb2687c0_Kinesis Advantage-like Layout.json",
}


def _load_resource(filename: str) -> dict:
    data_path = resources.files("glove80.default.data").joinpath(filename)
    with data_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_layout(variant: str) -> dict:
    try:
        filename = RESOURCE_MAP[variant]
    except KeyError as exc:
        raise KeyError(f"Unknown default layout variant '{variant}'. Available: {sorted(RESOURCE_MAP)}") from exc

    layout = _load_resource(filename)
    attach_variant_metadata(layout, variant=variant, layout_key="default")
    return layout


__all__ = ["build_layout", "RESOURCE_MAP"]
