"""Minimal Textual application shell for the Glove80 TUI (Milestone 1)."""

from __future__ import annotations

from typing import Iterable, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.message import Message

from .screens.editor import EditorScreen


class Glove80TuiApp(App[None]):
    """Entry point for the forthcoming Glove80 Textual editor."""

    TITLE = "Glove80 Layout Editor"
    CSS_PATH: Iterable[str] = ()
    BINDINGS = [
        Binding("ctrl+s", "save", "Save", show=False),
        Binding("ctrl+shift+s", "save_as", "Save As", show=False),
        Binding("ctrl+k", "palette", "Command Palette"),
        Binding("f5", "validate", "Validate"),
        Binding("f6", "regen", "Regen Preview"),
        Binding("ctrl+z", "undo", "Undo", show=False),
        Binding("ctrl+shift+z", "redo", "Redo", show=False),
    ]

    def __init__(
        self,
        *,
        initial_layout: Optional[str] = None,
        initial_variant: Optional[str] = None,
        enable_devtools: bool = False,
    ) -> None:
        super().__init__(enable_devtools=enable_devtools)
        self._initial_layout = initial_layout
        self._initial_variant = initial_variant

    def compose(self) -> ComposeResult:
        """Mount the primary editor screen."""

        yield EditorScreen(initial_layout=self._initial_layout, initial_variant=self._initial_variant)

    def action_palette(self) -> None:  # pragma: no cover - placeholder binding
        self.notify("Command palette will arrive in a later milestone.")

    def action_save(self) -> None:  # pragma: no cover - placeholder binding
        self.notify("Saving is disabled in the Milestone 1 scaffold.")

    action_save_as = action_save

    def action_validate(self) -> None:  # pragma: no cover - placeholder binding
        self.notify("Validation hooks land in Milestone 6.")

    def action_regen(self) -> None:  # pragma: no cover - placeholder binding
        self.notify("Regen preview is not available yet.")

    def action_undo(self) -> None:  # pragma: no cover - placeholder binding
        self.notify("Undo stack will arrive with editing milestones.")

    def action_redo(self) -> None:  # pragma: no cover - placeholder binding
        self.notify("Redo stack will arrive with editing milestones.")

    @on(Message)
    def log_message(self, event: Message) -> None:  # pragma: no cover - dev aid
        """Catch-all debug hook while the UI is mostly static."""

        self.log.debug("event=%s", event)

