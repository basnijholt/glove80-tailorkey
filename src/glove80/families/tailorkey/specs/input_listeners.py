"""Input listener definitions for TailorKey variants (Pydantic models)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.base import LayerRef
from glove80.families.tailorkey.alpha_layouts import TAILORKEY_VARIANTS, base_variant_for
from glove80.layouts.schema import InputListener, InputProcessor, ListenerNode

if TYPE_CHECKING:
    from collections.abc import Sequence

LAYER_SEQUENCE = ("MouseSlow", "MouseFast", "MouseWarp")


def _node(description: str, layer: str, processor: str, params: Sequence[int]) -> ListenerNode:
    return ListenerNode(
        code=f"LAYER_{layer}",
        description=description,
        layers=[LayerRef(layer)],
        inputProcessors=[InputProcessor(code=processor, params=list(params))],
    )


def _listeners(
    slow_xy_desc: str,
    slow_scroll_desc: str,
    warp_desc_xy: str,
    warp_desc_scroll: str,
) -> tuple[InputListener, InputListener]:
    xy_nodes = [
        _node(slow_xy_desc, "MouseSlow", "&zip_xy_scaler", (1, 9)),
        _node("LAYER_MouseFast", "MouseFast", "&zip_xy_scaler", (3, 1)),
        _node(warp_desc_xy, "MouseWarp", "&zip_xy_scaler", (12, 1)),
    ]
    scroll_nodes = [
        _node(slow_scroll_desc, "MouseSlow", "&zip_scroll_scaler", (1, 9)),
        _node("LAYER_MouseFast", "MouseFast", "&zip_scroll_scaler", (3, 1)),
        _node(warp_desc_scroll, "MouseWarp", "&zip_scroll_scaler", (12, 1)),
    ]
    return (
        InputListener(code="&mmv_input_listener", nodes=list(xy_nodes)),
        InputListener(code="&msc_input_listener", nodes=list(scroll_nodes)),
    )


INPUT_LISTENER_DATA: dict[str, list[InputListener]] = {
    "windows": list(_listeners("LAYER_MouseSlow", "LAYER_MouseSlow", "LAYER_MouseFast", "LAYER_MouseWarp")),
    "mac": list(_listeners("LAYER_MouseSlow\n", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp")),
    "dual": list(_listeners("LAYER_MouseSlow", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp")),
    "bilateral_windows": list(_listeners("LAYER_MouseSlow", "LAYER_MouseSlow", "LAYER_MouseWarp", "LAYER_MouseWarp")),
    "bilateral_mac": list(_listeners("LAYER_MouseSlow\n", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp")),
}

for _variant in TAILORKEY_VARIANTS:
    if _variant not in INPUT_LISTENER_DATA:
        template = base_variant_for(_variant)
        INPUT_LISTENER_DATA[_variant] = list(INPUT_LISTENER_DATA[template])


__all__ = ["INPUT_LISTENER_DATA"]
