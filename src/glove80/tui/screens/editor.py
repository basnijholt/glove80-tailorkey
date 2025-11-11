"""Primary editor screen used throughout the milestones."""

from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen

from ..state import LayoutStore
from ..widgets.footer import FooterBar
from ..widgets.inspector import InspectorPanel
from ..widgets.key_canvas import KeyCanvas
from ..widgets.layer_sidebar import LayerSidebar
from ..widgets.ribbon import ProjectRibbon


class EditorScreen(Screen[None]):
    """Static editor layout scaffolding."""

    def __init__(
        self,
        *,
        store: LayoutStore,
        initial_layout: Optional[str],
        initial_variant: Optional[str],
    ) -> None:
        super().__init__()
        self.store = store
        self._initial_layout = initial_layout or "default"
        self._initial_variant = initial_variant or "base"

    def compose(self) -> ComposeResult:
        sidebar = LayerSidebar(store=self.store)
        canvas = KeyCanvas(store=self.store)
        inspector = InspectorPanel(store=self.store)

        yield ProjectRibbon(current_layout=self._initial_layout, current_variant=self._initial_variant)
        yield Horizontal(sidebar, canvas, inspector, id="editor-workspace")
        yield FooterBar()
