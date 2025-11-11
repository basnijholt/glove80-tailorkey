"""Placeholder layer sidebar widget."""

from __future__ import annotations

from textual.widgets import Static


class LayerSidebar(Static):
    """Shows a static blurb until dynamic data arrives."""

    DEFAULT_TEXT = "Layer Sidebar\n(coming soon)"

    def __init__(self) -> None:
        super().__init__(self.DEFAULT_TEXT, classes="layer-sidebar")

