"""Compose QuantumTouch layouts from declarative layer specs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.layouts.common import compose_layout
from glove80.layouts.family import REGISTRY, LayoutFamily

from .layers import build_all_layers
from .specs import (
    COMBO_DATA,
    COMMON_FIELDS,
    HOLD_TAP_DEFS,
    HOLD_TAP_ORDER,
    INPUT_LISTENER_DATA,
    LAYER_NAMES,
    MACRO_DEFS,
    MACRO_ORDER,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class Family(LayoutFamily):
    name = "quantum_touch"

    def variants(self) -> Sequence[str]:
        return ["default"]

    def metadata_key(self) -> str:
        return "quantum_touch"

    def build(self, variant: str = "default") -> dict:
        combos = list(COMBO_DATA["default"])  # already Pydantic models
        listeners = list(INPUT_LISTENER_DATA["default"])  # already models
        macros = [MACRO_DEFS[name] for name in MACRO_ORDER]
        hold_taps = [HOLD_TAP_DEFS[name] for name in HOLD_TAP_ORDER]
        generated_layers = build_all_layers(variant)

        return compose_layout(
            COMMON_FIELDS,
            layer_names=LAYER_NAMES,
            generated_layers=generated_layers,
            metadata_key=self.metadata_key(),
            variant=variant,
            macros=macros,
            hold_taps=hold_taps,
            combos=combos,
            input_listeners=listeners,
        )


REGISTRY.register(Family())

__all__ = ["Family"]
