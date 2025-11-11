"""Footer/status bar placeholder."""

from __future__ import annotations

from datetime import datetime

from textual.widgets import Static


class FooterBar(Static):
    """Displays a static status line until live telemetry is wired up."""

    def __init__(self) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        super().__init__(f"Status · dirty=no · tasks=0 · {timestamp}", classes="footer-bar")

