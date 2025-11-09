"""Declarative builder for assembling Glove80 layout payloads."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, MutableSequence, Sequence

from glove80.base import LayerMap

from .common import compose_layout


def _unique_sequence(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


@dataclass
class _Sections:
    layer_names: list[str] = field(default_factory=list)
    layers: LayerMap = field(default_factory=dict)
    macros: OrderedDict[str, dict[str, Any]] = field(default_factory=OrderedDict)
    hold_taps: list[dict[str, Any]] = field(default_factory=list)
    combos: list[dict[str, Any]] = field(default_factory=list)
    input_listeners: list[dict[str, Any]] = field(default_factory=list)


class LayoutBuilder:
    """Mutable helper that coordinates every section of a layout payload."""

    def __init__(
        self,
        *,
        metadata_key: str,
        variant: str,
        common_fields: Mapping[str, Any],
        layer_names: Sequence[str] | None = None,
        resolve_refs: bool = True,
    ) -> None:
        self.metadata_key = metadata_key
        self.variant = variant
        self._common_fields: Mapping[str, Any] = dict(common_fields)
        self._resolve_refs = resolve_refs
        self._sections = _Sections(layer_names=_unique_sequence(layer_names or ()))

    # ------------------------------------------------------------------
    # Base section wiring
    # ------------------------------------------------------------------
    def set_layer_order(self, layer_names: Sequence[str]) -> "LayoutBuilder":
        self._sections.layer_names = _unique_sequence(layer_names)
        return self

    def add_layers(
        self,
        layers: LayerMap,
        *,
        insert_after: str | None = None,
        explicit_order: Sequence[str] | None = None,
    ) -> "LayoutBuilder":
        """Merge *layers* into the builder and update the layer order."""

        if not layers:
            return self

        order = list(explicit_order or layers.keys())
        for name in order:
            if name not in layers:
                raise KeyError(f"Layer '{name}' missing from provided mapping")
            self._sections.layers[name] = layers[name]
        self._insert_layer_names(order, after=insert_after)
        return self

    def update_layer(self, name: str, layer_data: Any) -> "LayoutBuilder":
        if name not in self._sections.layer_names:
            self._sections.layer_names.append(name)
        self._sections.layers[name] = layer_data
        return self

    def add_macros(
        self,
        macros: Sequence[Mapping[str, Any]],
        *,
        prepend: bool = False,
    ) -> "LayoutBuilder":
        if not macros:
            return self

        existing = self._sections.macros
        if prepend:
            # Build a new ordered dict that places the incoming macros up front.
            updated = OrderedDict()
            for macro in macros:
                name = _macro_name(macro)
                updated[name] = dict(macro)
            for name, macro in existing.items():
                if name not in updated:
                    updated[name] = macro
            self._sections.macros = updated
            return self

        for macro in macros:
            name = _macro_name(macro)
            existing[name] = dict(macro)
        return self

    def add_hold_taps(self, hold_taps: Sequence[Mapping[str, Any]]) -> "LayoutBuilder":
        self._sections.hold_taps.extend(dict(spec) for spec in hold_taps)
        return self

    def add_combos(self, combos: Sequence[Mapping[str, Any]]) -> "LayoutBuilder":
        self._sections.combos.extend(dict(spec) for spec in combos)
        return self

    def add_input_listeners(self, listeners: Sequence[Mapping[str, Any]]) -> "LayoutBuilder":
        self._sections.input_listeners.extend(dict(spec) for spec in listeners)
        return self

    # ------------------------------------------------------------------
    # Feature-oriented helpers
    # ------------------------------------------------------------------
    def add_mouse_layers(
        self,
        *,
        layers: LayerMap,
        macros: Sequence[Mapping[str, Any]] = (),
        combos: Sequence[Mapping[str, Any]] = (),
        listeners: Sequence[Mapping[str, Any]] = (),
        insert_after: str | None = None,
    ) -> "LayoutBuilder":
        self.add_layers(layers, insert_after=insert_after)
        self.add_macros(macros)
        self.add_combos(combos)
        self.add_input_listeners(listeners)
        return self

    def add_cursor_layer(
        self,
        *,
        layer_name: str,
        layer_data: Any,
        macros: Sequence[Mapping[str, Any]] = (),
        insert_after: str | None = None,
    ) -> "LayoutBuilder":
        if layer_name not in self._sections.layer_names:
            self._insert_layer_names([layer_name], after=insert_after)
        self._sections.layers[layer_name] = layer_data
        self.add_macros(macros)
        return self

    def add_home_row_mods(
        self,
        *,
        target_layer: str,
        layers: LayerMap,
        macros: Sequence[Mapping[str, Any]],
        hold_taps: Sequence[Mapping[str, Any]] = (),
        combos: Sequence[Mapping[str, Any]] = (),
        listeners: Sequence[Mapping[str, Any]] = (),
        extra_layer_order: Sequence[str] | None = None,
        insert_training_layers_after: str | None = None,
    ) -> "LayoutBuilder":
        """Attach home-row modifiers and their supporting structures."""

        if target_layer not in self._sections.layer_names:
            raise ValueError(f"Unknown target layer '{target_layer}'")

        insertion_anchor = insert_training_layers_after or target_layer
        self.add_layers(
            layers,
            insert_after=insertion_anchor,
            explicit_order=extra_layer_order,
        )
        self.add_macros(macros)
        self.add_hold_taps(hold_taps)
        self.add_combos(combos)
        self.add_input_listeners(listeners)
        return self

    # ------------------------------------------------------------------
    # Finalization
    # ------------------------------------------------------------------
    def build(self) -> dict[str, Any]:
        missing = [name for name in self._sections.layer_names if name not in self._sections.layers]
        if missing:
            raise KeyError(
                "Cannot build layout; missing layer data for: " + ", ".join(missing)
            )

        return compose_layout(
            self._common_fields,
            layer_names=self._sections.layer_names,
            generated_layers=self._sections.layers,
            metadata_key=self.metadata_key,
            variant=self.variant,
            macros=list(self._sections.macros.values()),
            hold_taps=self._sections.hold_taps,
            combos=self._sections.combos,
            input_listeners=self._sections.input_listeners,
            resolve_refs=self._resolve_refs,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _insert_layer_names(self, names: Sequence[str], *, after: str | None = None) -> None:
        if not names:
            return
        names = _unique_sequence(names)
        current = self._sections.layer_names
        if after is None:
            for name in names:
                if name not in current:
                    current.append(name)
            return

        filtered = [name for name in current if name not in names]
        try:
            anchor_index = filtered.index(after)
        except ValueError:
            raise ValueError(f"Layer '{after}' is not present in the order") from None
        updated = (
            filtered[: anchor_index + 1]
            + [name for name in names if name not in filtered]
            + filtered[anchor_index + 1 :]
        )
        self._sections.layer_names = updated


def _macro_name(macro: Mapping[str, Any]) -> str:
    try:
        name = macro["name"]
    except KeyError as exc:  # pragma: no cover - enforced via tests
        raise KeyError("Macro definitions must include a 'name'") from exc
    if not isinstance(name, str):  # pragma: no cover - sanity guard
        raise TypeError("Macro name must be a string")
    return name


__all__ = ["LayoutBuilder"]
