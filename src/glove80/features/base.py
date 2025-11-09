"""Helpers for applying reusable layout feature bundles."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from glove80.layouts.components import LayoutFeatureComponents

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableSequence


def _ensure_section(
    layout: Mapping[str, MutableSequence[dict[str, Any]]],
    key: str,
) -> MutableSequence[dict[str, Any]]:
    section = layout.get(key)
    if section is None:
        msg = f"Layout is missing '{key}' section"
        raise KeyError(msg)
    return section  # type: ignore[return-value]


def apply_feature(layout: dict, components: LayoutFeatureComponents) -> None:
    """Mutate *layout* in-place by appending the provided components."""
    existing_macros = list(_ensure_section(layout, "macros"))
    macros_by_name = {macro.get("name"): macro for macro in existing_macros if "name" in macro}
    macro_order = [macro.get("name") for macro in existing_macros if "name" in macro]

    def _set_macro(macro_dict: dict[str, Any]) -> None:
        name = macro_dict.get("name")
        if not isinstance(name, str):
            msg = "Feature macros must include a 'name'"
            raise KeyError(msg)
        macros_by_name[name] = macro_dict
        if name not in macro_order:
            macro_order.append(name)

    for macro in components.macros:
        _set_macro(macro)
    for macro in components.macro_overrides.values():
        _set_macro(macro)

    layout["macros"] = [macros_by_name[name] for name in macro_order]

    _ensure_section(layout, "holdTaps").extend(components.hold_taps)
    _ensure_section(layout, "combos").extend(components.combos)
    _ensure_section(layout, "inputListeners").extend(components.input_listeners)

    layer_names: MutableSequence[str] = layout.setdefault("layer_names", [])  # type: ignore[assignment]
    ordered_layers: MutableSequence[Any] = layout.setdefault("layers", [])  # type: ignore[assignment]
    layers_by_name: dict[str, Any] = dict(zip(layer_names, ordered_layers, strict=False))

    for name, layer in components.layers.items():
        if name not in layers_by_name:
            layer_names.append(name)
        layers_by_name[name] = layer

    layout["layers"] = [layers_by_name[name] for name in layer_names]


__all__ = ["LayoutFeatureComponents", "apply_feature"]
