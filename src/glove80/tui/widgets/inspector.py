"""Key Inspector tab implementation for Milestone 3."""

from __future__ import annotations

import json
from typing import Sequence

from textual import on
from textual.containers import Vertical
from textual.suggester import Suggester
from textual.widgets import Button, Input, Label, Static

from ..messages import SelectionChanged, StoreUpdated
from ..state import LayoutStore, SelectionState
from ..services import ValidationIssue, ValidationResult, ValidationService


class InspectorPanel(Vertical):
    """Wrapper that will eventually host multiple tabs."""

    def __init__(self, *, store: LayoutStore) -> None:
        super().__init__(classes="inspector-panel")
        self.store = store
        self.key_inspector = KeyInspector(store=store)

    def compose(self):  # type: ignore[override]
        yield Static("Inspector", classes="inspector-heading")
        yield self.key_inspector


class KeyInspector(Vertical):
    """Minimal form that edits a single key binding."""

    def __init__(self, *, store: LayoutStore) -> None:
        super().__init__(classes="key-inspector", id="key-inspector")
        self.store = store
        self.validator = ValidationService(layer_names=self.store.layer_names)
        self._selection: SelectionState | None = None
        self.value_input = Input(
            placeholder="&kp",
            id="key-value",
            suggester=_BehaviorSuggester(self.validator),
        )
        self.params_input = Input(
            placeholder="Param list (e.g., KC_A, Base)",
            id="key-params",
            suggester=_ParamSuggester(self.validator),
        )
        self.json_input = Input(
            placeholder='{"value": "&kp", "params": [{"value": "A", "params": []}]}',
            id="key-json",
        )
        self.value_error = Static("", classes="validation-hint hidden")
        self.params_error = Static("", classes="validation-hint hidden")

    def compose(self):  # type: ignore[override]
        yield Label("Key Behavior")
        yield self.value_input
        yield self.value_error
        yield Label("Params (comma separated)")
        yield self.params_input
        yield self.params_error
        yield Button("Apply", id="apply-form")
        yield Label("Raw JSON fallback")
        yield self.json_input
        yield Button("Apply JSON", id="apply-json")

    # ------------------------------------------------------------------
    def on_mount(self) -> None:
        if self.store.selection.layer_index >= 0:
            self._selection = self.store.selection
            self._load_from_store()
        else:
            self._toggle_inputs(False)

    def focus_value_field(self) -> None:
        self.value_input.focus()

    # ------------------------------------------------------------------
    @on(SelectionChanged)
    def _handle_selection_changed(self, event: SelectionChanged) -> None:
        if event.layer_index < 0 or event.key_index < 0:
            self._toggle_inputs(False)
            return
        self.validator.update_layers(self.store.layer_names)
        self._selection = SelectionState(layer_index=event.layer_index, key_index=event.key_index)
        self._load_from_store()

    @on(StoreUpdated)
    def _handle_store_updated(self, _: StoreUpdated) -> None:
        if self._selection is None:
            return
        self.validator.update_layers(self.store.layer_names)
        self._load_from_store()

    @on(Button.Pressed)
    def _handle_button(self, event: Button.Pressed) -> None:
        if event.button.id == "apply-form":
            self._apply_form()
        elif event.button.id == "apply-json":
            self._apply_json()

    # ------------------------------------------------------------------
    def _load_from_store(self) -> None:
        if self._selection is None:
            self._toggle_inputs(False)
            return
        try:
            slot = self.store.get_key(
                layer_index=self._selection.layer_index,
                key_index=self._selection.key_index,
            )
        except (IndexError, ValueError):
            self._toggle_inputs(False)
            return
        self._toggle_inputs(True)
        display_value, display_params = _display_tokens(slot)
        self.value_input.value = display_value
        self.params_input.value = ", ".join(display_params)
        self.json_input.value = json.dumps(slot, separators=(",", ":"))
        self._render_validation(ValidationResult(display_value, tuple(), tuple()))

    def _toggle_inputs(self, enabled: bool) -> None:
        self.value_input.disabled = not enabled
        self.params_input.disabled = not enabled
        self.json_input.disabled = not enabled

    def _apply_form(self) -> None:
        if self._selection is None:
            return
        value, inline = self._split_value_tokens()
        manual_params = [p.strip() for p in self.params_input.value.split(",") if p.strip()]
        combined_params: list[str] = [*inline, *manual_params]

        result = self.validator.validate(value, combined_params)
        self._render_validation(result)
        if not result.is_valid:
            return

        self.store.update_selected_key(value=result.value, params=list(result.params))
        self.post_message(StoreUpdated())
        self._load_from_store()

    def _apply_json(self) -> None:
        if self._selection is None:
            return
        raw = self.json_input.value.strip()
        if not raw:
            self.app.notify("JSON payload cannot be empty")
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:  # pragma: no cover - error UI
            self.app.notify(f"Invalid JSON: {exc}")
            return
        value = str(payload.get("value", ""))
        params = payload.get("params", [])
        if not isinstance(params, Sequence) or isinstance(params, (str, bytes)):
            self.app.notify("'params' must be a list")
            return
        result = self.validator.validate(value, list(params))
        self._render_validation(result)
        if not result.is_valid:
            return
        self.store.update_selected_key(value=result.value, params=list(result.params))
        self.post_message(StoreUpdated())
        self._load_from_store()

    # ------------------------------------------------------------------
    # Test helper -------------------------------------------------------
    def apply_value_for_test(self, value: str, params: Sequence[str] | None = None) -> None:
        self.value_input.value = value
        self.params_input.value = ", ".join(params or [])
        self._apply_form()

    # ------------------------------------------------------------------
    def _split_value_tokens(self) -> tuple[str, list[str]]:
        raw = self.value_input.value.strip()
        if not raw:
            return "", []
        tokens = raw.split()
        if tokens[0].startswith("&") and len(tokens) > 1:
            return tokens[0], tokens[1:]
        return raw, []

    def _render_validation(self, result: ValidationResult) -> None:
        self._set_field_state(self.value_input, self.value_error, result.first_issue("value"))
        self._set_field_state(self.params_input, self.params_error, result.first_issue("params"))

    @staticmethod
    def _set_field_state(widget: Input, label: Static, issue: ValidationIssue | None) -> None:
        if issue:
            widget.add_class("input-error")
            label.update(issue.message)
            label.remove_class("hidden")
        else:
            widget.remove_class("input-error")
            label.update("")
            label.add_class("hidden")


# ---------------------------------------------------------------------------
def _display_tokens(slot: dict[str, object]) -> tuple[str, list[str]]:
    raw_value = str(slot.get("value", ""))
    params = slot.get("params", [])

    if (not params) and raw_value.startswith("&") and " " in raw_value:
        pieces = raw_value.split()
        return pieces[0], pieces[1:]

    tokens: list[str] = []
    if isinstance(params, Sequence) and not isinstance(params, (str, bytes)):
        for entry in params:
            if isinstance(entry, dict):
                if "value" in entry:
                    tokens.append(str(entry.get("value")))
                elif "name" in entry:
                    tokens.append(str(entry.get("name")))
                else:
                    tokens.append(json.dumps(entry))
            else:
                tokens.append(str(entry))
    return raw_value, tokens


class _BehaviorSuggester(Suggester):
    def __init__(self, validator: ValidationService) -> None:
        super().__init__(use_cache=False)
        self._validator = validator

    async def get_suggestion(self, value: str) -> str | None:  # pragma: no cover - UI glue
        suggestions = self._validator.suggest_behaviors(value.strip(), limit=1)
        return suggestions[0] if suggestions else None


class _ParamSuggester(Suggester):
    def __init__(self, validator: ValidationService) -> None:
        super().__init__(use_cache=False)
        self._validator = validator

    async def get_suggestion(self, value: str) -> str | None:  # pragma: no cover - UI glue
        token = value.split(",")[-1].strip()
        if not token:
            return None
        keycode = self._validator.suggest_keycodes(token, limit=1)
        if keycode:
            return keycode[0]
        layer = self._validator.suggest_layers(token, limit=1)
        if layer:
            return layer[0]
        return None
