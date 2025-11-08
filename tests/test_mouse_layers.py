import json
from pathlib import Path

import pytest

from tailorkey_builder.layers.mouse import build_mouse_layers


VARIANTS = [
    "windows",
    "mac",
    "dual",
    "bilateral_windows",
    "bilateral_mac",
]

LAYER_NAMES = ["Mouse", "MouseSlow", "MouseFast", "MouseWarp"]


def _load_canonical_layers(variant: str):
    path = Path("sources/variants") / f"{variant}.json"
    data = json.loads(path.read_text())
    layers = {}
    for layer_name in LAYER_NAMES:
        idx = data["layer_names"].index(layer_name)
        layers[layer_name] = data["layers"][idx]
    return layers


@pytest.mark.parametrize("variant", VARIANTS)
def test_mouse_layers_match_canonical(variant):
    expected = _load_canonical_layers(variant)
    generated = build_mouse_layers(variant)
    assert generated == expected
