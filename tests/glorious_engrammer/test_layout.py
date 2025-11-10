import pytest

from glove80 import build_layout as build_family_layout
from glove80.families.glorious_engrammer.layouts import FIELD_ORDER, _order_layout_fields
from tests.assertions import assert_layout_equal


def test_glorious_engrammer_matches_release(load_glorious_engrammer_variant) -> None:
    expected = load_glorious_engrammer_variant("v42_rc6_preview")
    built = build_family_layout("glorious_engrammer", "v42_rc6_preview")
    assert_layout_equal(built, expected, label="glorious_engrammer:v42_rc6_preview")


def test_field_order_guard_detects_schema_drift() -> None:
    layout = {field: field for field in FIELD_ORDER}
    layout["unexpected"] = "value"
    with pytest.raises(KeyError, match="Unexpected layout fields"):
        _order_layout_fields(layout)

    layout.pop("unexpected")
    missing_field = FIELD_ORDER[-1]
    layout.pop(missing_field)
    with pytest.raises(KeyError, match="missing fields"):
        _order_layout_fields(layout)
