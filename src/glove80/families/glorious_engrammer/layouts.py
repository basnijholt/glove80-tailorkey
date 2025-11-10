"""Compose the Glorious Engrammer layout."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from glove80.layouts.common import compose_layout
from glove80.layouts.family import REGISTRY, LayoutFamily

from .layers import build_all_layers
from .specs import VARIANT_SPECS

if TYPE_CHECKING:
    from collections.abc import Sequence

FIELD_ORDER: Sequence[str] = (
    "keyboard",
    "firmware_api_version",
    "locale",
    "uuid",
    "parent_uuid",
    "unlisted",
    "date",
    "creator",
    "title",
    "notes",
    "tags",
    "custom_defined_behaviors",
    "custom_devicetree",
    "config_parameters",
    "layout_parameters",
    "layer_names",
    "layers",
    "macros",
    "inputListeners",
    "holdTaps",
    "combos",
)


def _order_layout_fields(layout: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    for field in FIELD_ORDER:
        ordered[field] = layout[field]
    return ordered


class Family(LayoutFamily):
    name = "glorious_engrammer"

    def variants(self) -> Sequence[str]:
        return tuple(VARIANT_SPECS.keys())

    def metadata_key(self) -> str:
        return "glorious_engrammer"

    def build(self, variant: str) -> dict:
        try:
            spec = VARIANT_SPECS[variant]
        except KeyError as exc:
            msg = f"Unknown Glorious Engrammer variant '{variant}'. Available: {sorted(VARIANT_SPECS)}"
            raise KeyError(
                msg,
            ) from exc

        generated_layers = build_all_layers(variant)
        layout = compose_layout(
            spec.common_fields,
            layer_names=spec.layer_names,
            generated_layers={name: generated_layers[name] for name in spec.layer_names},
            metadata_key=self.metadata_key(),
            variant=variant,
        )
        return _order_layout_fields(layout)


REGISTRY.register(Family())

__all__ = ["Family"]
