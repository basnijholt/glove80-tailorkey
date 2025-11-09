"""Lightweight helpers for sharing feature bundles across layouts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableSequence, Sequence

from glove80.base import LayerMap


@dataclass(frozen=True)
class LayoutFeatureComponents:
    """Small bundle of reusable layout pieces (macros, layers, etc.)."""

    macros: Sequence[Dict[str, Any]] = ()
    hold_taps: Sequence[Dict[str, Any]] = ()
    combos: Sequence[Dict[str, Any]] = ()
    input_listeners: Sequence[Dict[str, Any]] = ()
    layers: LayerMap = field(default_factory=dict)


def _ensure_section(layout: Mapping[str, MutableSequence[Dict[str, Any]]], key: str) -> MutableSequence[Dict[str, Any]]:
    section = layout.get(key)
    if section is None:
        raise KeyError(f"Layout is missing '{key}' section")
    return section  # type: ignore[return-value]


def apply_feature(layout: dict, components: LayoutFeatureComponents) -> None:
    """Mutate *layout* in-place by appending the provided components."""

    _ensure_section(layout, "macros").extend(components.macros)
    _ensure_section(layout, "holdTaps").extend(components.hold_taps)
    _ensure_section(layout, "combos").extend(components.combos)
    _ensure_section(layout, "inputListeners").extend(components.input_listeners)

    layer_names: MutableSequence[str] = layout.setdefault("layer_names", [])  # type: ignore[assignment]
    ordered_layers: MutableSequence[Any] = layout.setdefault("layers", [])  # type: ignore[assignment]
    layers_by_name: Dict[str, Any] = {name: layer for name, layer in zip(layer_names, ordered_layers)}

    for name, layer in components.layers.items():
        if name not in layers_by_name:
            layer_names.append(name)
        layers_by_name[name] = layer

    layout["layers"] = [layers_by_name[name] for name in layer_names]


__all__ = ["LayoutFeatureComponents", "apply_feature"]
