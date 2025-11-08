import json
from pathlib import Path

import pytest

from tailorkey_builder.layers.lower import build_lower_layer


VARIANTS = [
    "windows",
    "mac",
    "dual",
    "bilateral_windows",
    "bilateral_mac",
]


def _load_canonical_layer(variant: str):
    path = Path("sources/variants") / f"{variant}.json"
    data = json.loads(path.read_text())
    idx = data["layer_names"].index("Lower")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", VARIANTS)
def test_lower_layer_matches_canonical(variant):
    assert build_lower_layer(variant) == _load_canonical_layer(variant)
