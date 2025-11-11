"""Footer/status bar that mirrors selection state."""

from __future__ import annotations

from textual import on
from textual.widgets import Static

from ..messages import SelectionChanged, StoreUpdated


class FooterBar(Static):
    """Lightweight status line that surfaces selection + dirty state."""

    def __init__(self) -> None:
        super().__init__(classes="footer-bar")
        self._layer_name = "—"
        self._key_index: int | None = None
        self._dirty = False

    def on_mount(self) -> None:
        self._render_status()

    def _render_status(self) -> None:
        key_fragment = "--" if self._key_index is None else f"#{self._key_index:02d}"
        dirty_fragment = "yes" if self._dirty else "no"
        self.update(f"Layer: {self._layer_name} · Key: {key_fragment} · dirty={dirty_fragment}")

    @on(SelectionChanged)
    def _handle_selection(self, event: SelectionChanged) -> None:
        self._layer_name = event.layer_name or "—"
        self._key_index = event.key_index
        self._render_status()

    @on(StoreUpdated)
    def _handle_store_update(self, _: StoreUpdated) -> None:
        self._dirty = True
        self._render_status()
