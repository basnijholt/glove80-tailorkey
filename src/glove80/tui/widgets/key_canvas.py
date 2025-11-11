"""Placeholder key canvas widget."""

from __future__ import annotations

from textual.widgets import Static


class KeyCanvas(Static):
    """Simple message until the real geometry is implemented."""

    def __init__(self) -> None:
        super().__init__("Key Canvas\n80-key grid coming soon", classes="key-canvas")

