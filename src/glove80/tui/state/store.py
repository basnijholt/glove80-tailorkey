"""State management for the Glove80 TUI (Milestone 2)."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


LayerPayload = List[Dict[str, Any]]
ComboPayload = Dict[str, Any]
ListenerPayload = Dict[str, Any]


def _ensure_tuple(items: Iterable[Any]) -> Tuple[Any, ...]:
    return tuple(items)


@dataclass(frozen=True)
class LayerRecord:
    name: str
    slots: Tuple[Dict[str, Any], ...]


@dataclass(frozen=True)
class LayoutState:
    layer_names: Tuple[str, ...]
    layers: Tuple[LayerRecord, ...]
    combos: Tuple[ComboPayload, ...]
    listeners: Tuple[ListenerPayload, ...]

    @staticmethod
    def from_payload(payload: Mapping[str, Any]) -> LayoutState:
        layer_names = tuple(payload.get("layer_names", []))
        layer_records = []
        for name, slots in zip(layer_names, payload.get("layers", [])):
            layer_records.append(LayerRecord(name=name, slots=_ensure_tuple(deepcopy(slots))))
        combos = tuple(deepcopy(payload.get("combos", [])))
        listeners = tuple(deepcopy(payload.get("inputListeners", [])))
        return LayoutState(
            layer_names=tuple(layer_names),
            layers=tuple(layer_records),
            combos=combos,
            listeners=listeners,
        )


@dataclass(frozen=True)
class SelectionState:
    """Tracks the active layer/key pair for the UI."""

    layer_index: int
    key_index: int


class LayoutStore:
    """Mutable state container with undo/redo support."""

    def __init__(self, state: LayoutState) -> None:
        self._state = state
        self._undo_stack: List[LayoutState] = []
        self._redo_stack: List[LayoutState] = []
        self._clipboard: Optional[LayerRecord] = None
        self._selection = SelectionState(layer_index=0 if state.layers else -1, key_index=0 if state.layers else -1)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> LayoutStore:
        return cls(LayoutState.from_payload(payload))

    # ------------------------------------------------------------------
    # Properties
    @property
    def state(self) -> LayoutState:
        return self._state

    @property
    def layer_names(self) -> Tuple[str, ...]:
        return self._state.layer_names

    @property
    def selection(self) -> SelectionState:
        return self._selection

    @property
    def selected_layer_name(self) -> Optional[str]:
        if self._selection.layer_index < 0:
            return None
        if self._selection.layer_index >= len(self._state.layer_names):
            return None
        return self._state.layer_names[self._selection.layer_index]

    # ------------------------------------------------------------------
    # Public API
    def rename_layer(self, *, old_name: str, new_name: str) -> None:
        if old_name == new_name:
            return
        if old_name not in self._state.layer_names:
            raise ValueError(f"Unknown layer '{old_name}'")
        if new_name in self._state.layer_names:
            raise ValueError(f"Layer '{new_name}' already exists")
        rename_map = {old_name: new_name}
        self._record_snapshot()
        layer_names = tuple(new_name if name == old_name else name for name in self._state.layer_names)
        layers = []
        for record in self._state.layers:
            updated = record
            if record.name == old_name:
                updated = replace(record, name=new_name)
            updated_slots = tuple(_rewrite_layer_refs(slot, rename_map) for slot in updated.slots)
            updated = replace(updated, slots=updated_slots)
            layers.append(updated)
        combos = tuple(_rewrite_layer_refs(combo, rename_map) for combo in self._state.combos)
        listeners = tuple(_rewrite_layer_refs(listener, rename_map) for listener in self._state.listeners)
        self._state = LayoutState(
            layer_names=layer_names,
            layers=tuple(layers),
            combos=combos,
            listeners=listeners,
        )
        self._redo_stack.clear()

    def reorder_layer(self, *, source_index: int, dest_index: int) -> None:
        size = len(self._state.layer_names)
        if not (0 <= source_index < size and 0 <= dest_index < size):
            raise IndexError("Layer index out of range")
        if source_index == dest_index:
            return
        self._record_snapshot()
        names = list(self._state.layer_names)
        record = names.pop(source_index)
        names.insert(dest_index, record)
        layers = list(self._state.layers)
        layer_record = layers.pop(source_index)
        layers.insert(dest_index, layer_record)
        self._state = LayoutState(
            layer_names=tuple(names),
            layers=tuple(layers),
            combos=self._state.combos,
            listeners=self._state.listeners,
        )
        self._redo_stack.clear()

    def duplicate_layer(self, *, source_name: str, new_name: Optional[str] = None, insert_after: bool = True) -> None:
        if source_name not in self._state.layer_names:
            raise ValueError(f"Unknown layer '{source_name}'")
        new_name = new_name or _increment_name(source_name, set(self._state.layer_names))
        if new_name in self._state.layer_names:
            raise ValueError(f"Layer '{new_name}' already exists")
        self._record_snapshot()
        index = self._state.layer_names.index(source_name)
        insert_index = index + 1 if insert_after else index
        layer_names = list(self._state.layer_names)
        layer_names.insert(insert_index, new_name)
        layers = list(self._state.layers)
        source_layer = layers[index]
        layers.insert(insert_index, LayerRecord(name=new_name, slots=tuple(deepcopy(source_layer.slots))))
        self._state = LayoutState(
            layer_names=tuple(layer_names),
            layers=tuple(layers),
            combos=self._state.combos,
            listeners=self._state.listeners,
        )
        self._redo_stack.clear()

    def pick_up_layer(self, *, name: str) -> None:
        if name not in self._state.layer_names:
            raise ValueError(f"Unknown layer '{name}'")
        index = self._state.layer_names.index(name)
        self._clipboard = self._state.layers[index]

    def drop_layer(self, *, target_index: int) -> None:
        if self._clipboard is None:
            return
        size = len(self._state.layer_names)
        if not (0 <= target_index <= size):
            raise IndexError("Layer index out of range")
        self._record_snapshot()
        names = list(self._state.layer_names)
        layers = list(self._state.layers)
        if self._clipboard.name in names:
            orig_index = names.index(self._clipboard.name)
            names.pop(orig_index)
            layers.pop(orig_index)
            if orig_index < target_index:
                target_index -= 1
        names.insert(target_index, self._clipboard.name)
        layers.insert(target_index, self._clipboard)
        self._state = LayoutState(
            layer_names=tuple(names),
            layers=tuple(layers),
            combos=self._state.combos,
            listeners=self._state.listeners,
        )
        self._redo_stack.clear()

    # ------------------------------------------------------------------
    # Selection helpers
    def set_selection(self, *, layer_index: int, key_index: int) -> SelectionState:
        self._selection = SelectionState(
            layer_index=self._validate_layer_index(layer_index),
            key_index=self._validate_key_index(layer_index, key_index),
        )
        return self._selection

    def set_active_layer(self, layer_index: int) -> SelectionState:
        if not self._state.layers:
            self._selection = SelectionState(layer_index=-1, key_index=-1)
            return self._selection
        valid_layer = self._validate_layer_index(layer_index)
        key_index = self._selection.key_index if self._selection.layer_index >= 0 else 0
        key_index = self._validate_key_index(valid_layer, key_index)
        self._selection = SelectionState(layer_index=valid_layer, key_index=key_index)
        return self._selection

    def set_selected_key(self, key_index: int) -> SelectionState:
        if not self._state.layers:
            self._selection = SelectionState(layer_index=-1, key_index=-1)
            return self._selection
        layer_index = self._selection.layer_index if self._selection.layer_index >= 0 else 0
        layer_index = self._validate_layer_index(layer_index)
        self._selection = SelectionState(
            layer_index=layer_index,
            key_index=self._validate_key_index(layer_index, key_index),
        )
        return self._selection

    def get_key(self, *, layer_index: Optional[int] = None, key_index: Optional[int] = None) -> Dict[str, Any]:
        if not self._state.layers:
            raise ValueError("No layers available")
        resolved_layer = layer_index if layer_index is not None else self._selection.layer_index
        resolved_key = key_index if key_index is not None else self._selection.key_index
        resolved_layer = self._validate_layer_index(resolved_layer)
        resolved_key = self._validate_key_index(resolved_layer, resolved_key)
        slot = self._state.layers[resolved_layer].slots[resolved_key]
        return deepcopy(slot)

    def update_key(
        self,
        *,
        layer_index: int,
        key_index: int,
        value: str,
        params: Sequence[Any],
    ) -> None:
        if not value:
            raise ValueError("Key value cannot be empty")
        layer_index = self._validate_layer_index(layer_index)
        key_index = self._validate_key_index(layer_index, key_index)
        self._record_snapshot()
        layers = list(self._state.layers)
        target = layers[layer_index]
        slots = list(target.slots)
        slots[key_index] = {"value": value, "params": list(params)}
        layers[layer_index] = replace(target, slots=tuple(deepcopy(slot) for slot in slots))
        self._state = LayoutState(
            layer_names=self._state.layer_names,
            layers=tuple(layers),
            combos=self._state.combos,
            listeners=self._state.listeners,
        )
        self._redo_stack.clear()

    def update_selected_key(self, *, value: str, params: Sequence[Any]) -> None:
        if self._selection.layer_index < 0 or self._selection.key_index < 0:
            raise ValueError("No key selected")
        self.update_key(
            layer_index=self._selection.layer_index,
            key_index=self._selection.key_index,
            value=value,
            params=params,
        )

    # ------------------------------------------------------------------
    # Undo / Redo
    def undo(self) -> None:
        if not self._undo_stack:
            return
        self._redo_stack.append(self._state)
        self._state = self._undo_stack.pop()

    def redo(self) -> None:
        if not self._redo_stack:
            return
        self._undo_stack.append(self._state)
        self._state = self._redo_stack.pop()

    # ------------------------------------------------------------------
    def _record_snapshot(self) -> None:
        self._undo_stack.append(self._state)

    def _validate_layer_index(self, layer_index: int) -> int:
        if not (0 <= layer_index < len(self._state.layers)):
            raise IndexError("Layer index out of range")
        return layer_index

    def _validate_key_index(self, layer_index: int, key_index: int) -> int:
        slot_count = len(self._state.layers[layer_index].slots)
        if not (0 <= key_index < slot_count):
            raise IndexError("Key index out of range")
        return key_index


def _increment_name(base: str, existing: Iterable[str]) -> str:
    counter = 2
    candidate = f"{base} Copy"
    while candidate in existing:
        candidate = f"{base} ({counter})"
        counter += 1
    return candidate


def _rewrite_layer_refs(data: Any, rename_map: Mapping[str, str]) -> Any:
    if isinstance(data, dict):
        if set(data.keys()) == {"name"}:
            name = data["name"]
            if name in rename_map:
                updated = dict(data)
                updated["name"] = rename_map[name]
                return updated
            return data
        return {k: _rewrite_layer_refs(v, rename_map) for k, v in data.items()}
    if isinstance(data, list):
        return [_rewrite_layer_refs(item, rename_map) for item in data]
    if isinstance(data, tuple):
        return tuple(_rewrite_layer_refs(item, rename_map) for item in data)
    return data


# Convenience payload for bootstrapping the app
def _sample_layer_slots(binding: str) -> List[Dict[str, Any]]:
    tokens = binding.split()
    if tokens and tokens[0].startswith("&") and len(tokens) > 1:
        value = tokens[0]
        param_template = [{"value": tokens[1], "params": []}]
    else:
        value = binding
        param_template = []

    slots: List[Dict[str, Any]] = []
    for _ in range(80):
        slots.append({"value": value, "params": list(param_template)})
    return slots


DEFAULT_SAMPLE_LAYOUT: Dict[str, Any] = {
    "layer_names": ["Base", "Lower", "Raise"],
    "layers": [_sample_layer_slots("&kp A"), _sample_layer_slots("&kp B"), _sample_layer_slots("&kp C")],
    "combos": [
        {
            "name": "LayerToggle",
            "binding": {"value": "&mo", "params": [{"name": "Lower"}]},
            "keyPositions": [0, 1],
            "layers": [{"name": "Base"}],
        }
    ],
    "inputListeners": [
        {
            "code": "listener_0",
            "layers": [{"name": "Raise"}],
            "nodes": [],
            "inputProcessors": [],
        }
    ],
}
