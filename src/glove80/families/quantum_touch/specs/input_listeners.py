"""Input listener definitions for QuantumTouch (Pydantic models)."""

from __future__ import annotations

from glove80.base import LayerRef
from glove80.layouts.schema import InputListener, InputProcessor, ListenerNode

LAYER_SEQUENCE = ("MouseSlow", "MouseFast", "MouseWarp")


def _node(description: str, layer: str, processor: str, params: tuple[int, int]) -> ListenerNode:
    return ListenerNode(
        code=f"LAYER_{layer}",
        description=description,
        layers=[LayerRef(layer)],
        inputProcessors=[InputProcessor(code=processor, params=list(params))],
    )


def _listener(code: str, processor: str) -> InputListener:
    descriptions = ("LAYER_MouseSlow", "LAYER_MouseFast", "LAYER_MouseWarp")
    params = ((1, 9), (3, 1), (12, 1))
    nodes = [
        _node(desc, layer, processor, param)
        for desc, layer, param in zip(descriptions, LAYER_SEQUENCE, params, strict=False)
    ]
    return InputListener(code=code, nodes=list(nodes))


INPUT_LISTENER_DATA = {
    "default": (
        _listener("&mmv_input_listener", "&zip_xy_scaler"),
        _listener("&msc_input_listener", "&zip_scroll_scaler"),
    ),
}

__all__ = ["INPUT_LISTENER_DATA"]
