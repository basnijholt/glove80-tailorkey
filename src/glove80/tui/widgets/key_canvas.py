"""Interactive key canvas widget for Milestone 3."""

from __future__ import annotations

from typing import Sequence

from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.widget import Widget

from ..geometry import KEY_GRID_ROWS, Direction, move
from ..messages import FooterMessage, InspectorFocusRequested, SelectionChanged, StoreUpdated
from ..state import LayoutStore, SelectionState


class KeyCanvas(Widget):
    """Minimal 80-key grid with keyboard navigation."""

    can_focus = True
    BINDINGS = [
        Binding("left", "move_left", "←", show=False),
        Binding("right", "move_right", "→", show=False),
        Binding("up", "move_up", "↑", show=False),
        Binding("down", "move_down", "↓", show=False),
        Binding("h", "move_left", show=False),
        Binding("l", "move_right", show=False),
        Binding("k", "move_up", show=False),
        Binding("j", "move_down", show=False),
        Binding("enter", "inspect", "Inspect"),
        Binding("[", "prev_layer", "Prev Layer"),
        Binding("]", "next_layer", "Next Layer"),
        Binding(".", "copy_key", "Copy Key"),
    ]

    def __init__(self, *, store: LayoutStore) -> None:
        super().__init__(classes="key-canvas")
        self.store = store
        self._selection = self.store.selection
        self._previous_selection: SelectionState | None = None

    # ------------------------------------------------------------------
    # Textual lifecycle
    def on_mount(self) -> None:
        if self._selection.layer_index < 0 and self.store.layer_names:
            self._selection = self.store.set_selection(layer_index=0, key_index=0)

    def render(self) -> Text:
        slots = self._current_slots()
        text = Text()
        for row in KEY_GRID_ROWS:
            for idx in row:
                legend = self._slot_legend(slots, idx)
                if self._selection.key_index == idx:
                    style = "bold white on dark_cyan"
                else:
                    style = "grey70"
                text.append(f"[{legend:^4}]", style=style)
                text.append(" ")
            text.append("\n")
        return text

    # ------------------------------------------------------------------
    # Actions
    def action_move_left(self) -> None:
        self._move("left")

    def action_move_right(self) -> None:
        self._move("right")

    def action_move_up(self) -> None:
        self._move("up")

    def action_move_down(self) -> None:
        self._move("down")

    def action_inspect(self) -> None:
        if self._selection.layer_index < 0:
            return
        self.post_message(
            InspectorFocusRequested(
                layer_index=self._selection.layer_index,
                key_index=self._selection.key_index,
            )
        )

    def action_prev_layer(self) -> None:
        self._switch_layer(-1)

    def action_next_layer(self) -> None:
        self._switch_layer(1)

    def action_copy_key(self) -> None:
        if self._previous_selection is None or self._previous_selection.layer_index < 0:
            self._notify("Nothing to copy — visit a source layer first.")
            return
        if self._selection.layer_index < 0 or self._selection.key_index < 0:
            self._notify("No destination layer selected.")
            return
        if self._previous_selection.layer_index == self._selection.layer_index:
            self._notify("Select a different layer before copying.")
            return

        try:
            changed = self.store.copy_key_to_layer(
                source_layer_index=self._previous_selection.layer_index,
                target_layer_index=self._selection.layer_index,
                key_index=self._selection.key_index,
            )
        except IndexError as exc:
            self._notify(str(exc))
            return
        except ValueError as exc:  # pragma: no cover - defensive
            self._notify(str(exc))
            return

        if not changed:
            self._notify("Key already matches source binding.")
            return

        slot = self.store.state.layers[self._selection.layer_index].slots[self._selection.key_index]
        legend = self._slot_legend((slot,), 0) if slot else "--"
        self.post_message(StoreUpdated())
        message = (
            f"Copied key #{self._selection.key_index:02d}: {legend} → "
            f"{self.store.layer_names[self._selection.layer_index]}"
        )
        self.post_message(FooterMessage(message))
        self._notify(message)
        self.refresh()

    # ------------------------------------------------------------------
    def _move(self, direction: Direction) -> None:
        current = self._selection.key_index
        next_index = move(current, direction) if current >= 0 else 0
        if next_index is None:
            return
        self._selection = self.store.set_selected_key(next_index)
        self._broadcast_selection()
        self.refresh()

    def _current_slots(self) -> tuple[dict[str, object], ...]:
        if self._selection.layer_index < 0:
            return ()
        return self.store.state.layers[self._selection.layer_index].slots

    def _slot_legend(self, slots: Sequence[dict[str, object]], index: int) -> str:
        try:
            slot = slots[index]
        except (IndexError, TypeError):
            return "--"
        value = slot.get("value", "") if isinstance(slot, dict) else ""
        if not value:
            return "--"
        value_str = str(value)
        if value_str.startswith("&kp "):
            parts = value_str.split(" ", 1)
            if len(parts) > 1:
                return parts[1][:3].upper()
        if value_str.startswith("&"):
            return value_str[1:4].upper()
        return value_str[:4].upper()

    def _broadcast_selection(self) -> None:
        self.post_message(
            SelectionChanged(
                layer_index=self._selection.layer_index,
                layer_name=self.store.selected_layer_name,
                key_index=self._selection.key_index,
            )
        )

    # ------------------------------------------------------------------
    @on(StoreUpdated)
    def _handle_store_updated(self, _: StoreUpdated) -> None:
        self.refresh()

    @on(SelectionChanged)
    def _handle_external_selection(self, event: SelectionChanged) -> None:
        if event.layer_index < 0 or event.key_index < 0:
            return
        self._selection = SelectionState(layer_index=event.layer_index, key_index=event.key_index)
        self.refresh()

    # ------------------------------------------------------------------
    # Test helpers ------------------------------------------------------
    def selected_index_for_test(self) -> int:
        return self._selection.key_index

    def _switch_layer(self, delta: int) -> None:
        layer_names = self.store.layer_names
        if not layer_names:
            return
        current = self._selection.layer_index if self._selection.layer_index >= 0 else 0
        next_index = (current + delta) % len(layer_names)
        if next_index == current:
            return
        self._previous_selection = self._selection
        self._selection = self.store.set_active_layer(next_index)
        self._broadcast_selection()
        self.post_message(FooterMessage(f"Active layer → {layer_names[next_index]}"))
        self._notify(f"Layer switched to {layer_names[next_index]}")
        self.refresh()

    def _notify(self, message: str) -> None:
        try:
            self.app.notify(message)
        except Exception:  # pragma: no cover - Textual optional
            self.log.debug(message)
