"""Compose MoErgo default layouts from declarative specs."""

from __future__ import annotations

from glove80.base import LayerMap, build_layer_from_spec
from glove80.layouts.common import compose_layout
from glove80.layouts.family import REGISTRY, LayoutFamily

from .specs import VARIANT_SPECS, VariantSpec


def _build_layers_map(spec: VariantSpec) -> LayerMap:
    return {name: build_layer_from_spec(layer_spec) for name, layer_spec in spec.layer_specs.items()}


class Family(LayoutFamily):
    name = "default"

    def variants(self) -> dict[str, VariantSpec]:
        return dict(VARIANT_SPECS)

    def metadata_key(self) -> str:
        return "default"

    def build(self, variant: str) -> dict:
        try:
            spec = VARIANT_SPECS[variant]
        except KeyError as exc:  # pragma: no cover
            msg = f"Unknown default layout '{variant}'. Available: {sorted(VARIANT_SPECS)}"
            raise KeyError(msg) from exc

        generated_layers = _build_layers_map(spec)
        return compose_layout(
            spec.common_fields,
            layer_names=spec.layer_names,
            generated_layers=generated_layers,
            metadata_key=self.metadata_key(),
            variant=variant,
            input_listeners=list(spec.input_listeners),
        )


REGISTRY.register(Family())

__all__ = ["Family"]
