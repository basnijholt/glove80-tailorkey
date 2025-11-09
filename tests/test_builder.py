from __future__ import annotations

import copy

import pytest

from glove80.layouts.builder import LayoutBuilder
from glove80.layouts.common import BASE_COMMON_FIELDS, compose_layout


def _mock_layer(token: str) -> list[dict[str, object]]:
    return [{"value": token, "params": []} for _ in range(4)]


def test_builder_matches_compose_layout() -> None:
    layers = {
        "Typing": _mock_layer("&kp_A"),
        "Symbol": _mock_layer("&kp_HASH"),
    }
    macros = [{"name": "&macro_demo", "bindings": []}]
    combos = [{"name": "combo_demo", "layers": [0, 1]}]

    builder = LayoutBuilder(
        metadata_key="default",
        variant="factory_default",
        common_fields=BASE_COMMON_FIELDS,
        layer_names=["Typing", "Symbol"],
    )
    builder.add_layers(layers)
    builder.add_macros(macros)
    builder.add_combos(combos)

    built = builder.build()
    expected = compose_layout(
        BASE_COMMON_FIELDS,
        layer_names=["Typing", "Symbol"],
        macros=macros,
        combos=combos,
        hold_taps=[],
        input_listeners=[],
        generated_layers=layers,
        metadata_key="default",
        variant="factory_default",
    )

    assert built == expected


def test_add_home_row_mods_inserts_layers_and_sections() -> None:
    base_layers = {
        "Typing": _mock_layer("&kp_A"),
        "Symbol": _mock_layer("&kp_HASH"),
    }
    hrm_layers = {
        "HRM_layer": _mock_layer("&hrm"),
    }
    hrm_macros = [{"name": "&hrm_macro", "bindings": []}]

    builder = LayoutBuilder(
        metadata_key="tailorkey",
        variant="windows",
        common_fields=BASE_COMMON_FIELDS,
        layer_names=["Typing", "Symbol"],
    )
    builder.add_layers(base_layers)

    builder.add_home_row_mods(
        target_layer="Typing",
        layers=hrm_layers,
        macros=hrm_macros,
    )

    layout = builder.build()
    assert layout["macros"][0]["name"] == "&hrm_macro"
    assert layout["layer_names"][1] == "HRM_layer"
    assert layout["layers"][1] == hrm_layers["HRM_layer"]


def test_add_mouse_layers_respects_order() -> None:
    mouse_layers = {"Mouse": _mock_layer("&mouse")}

    builder = LayoutBuilder(
        metadata_key="tailorkey",
        variant="windows",
        common_fields=BASE_COMMON_FIELDS,
        layer_names=["Typing"],
    )
    builder.add_layers({"Typing": _mock_layer("&kp_A")})
    builder.add_mouse_layers(layers=mouse_layers, insert_after="Typing")

    layout = builder.build()
    assert layout["layer_names"][1] == "Mouse"
