"""Miscellaneous stub widgets for the initial scaffold."""

from __future__ import annotations

from textual.widgets import Static


class InspectorPanel(Static):
    """Temporary placeholder for the Inspector tab set."""

    def __init__(self) -> None:
        super().__init__("Inspector\nTabs coming soon", classes="inspector-panel")

