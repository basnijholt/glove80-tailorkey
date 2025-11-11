# Glove80 Textual TUI Layout Editor Design (Repo-Aligned)

This plan targets the Python-first Glove80 toolchain that lives under `src/glove80`. Every interaction in the TUI is grounded in the same data the Typer CLI (`uv run glove80 generate …`) and release generator use today. All runtime edits eventually serialize back into the canonical `LayoutPayload` contract whose schema is exported at `docs/layout_payload.schema.json`.

## 1. Source Context & Guarantees
- **Authoritative inputs**: declarative specs and helpers in `src/glove80/families/*/specs`, feature bundles in `src/glove80/features`, and layer composition via `glove80.layouts.LayoutBuilder`.
- **Builder orchestration**: `glove80.layouts.builder.LayoutBuilder` merges layers, macros, hold taps, combos, and input listeners before `glove80.layouts.generator` writes JSON to `layouts/<family>/releases`. The TUI consumes/produces this exact `LayoutPayload` struct so the CLI and tests (`tests/<family>/`) remain deterministic.
- **Metadata**: `src/glove80/families/<family>/metadata.json` supplies UUIDs, titles, and release notes. The TUI must respect these fields (read-only unless author edits metadata via CLI).
- **Schema export**: `scripts/export_layout_schema.py` regenerates `docs/layout_payload.schema.json`. The TUI ships with that schema for validation and auto-complete of behaviors, device-tree additions, and advanced config.

## 2. Data Model Bridge

| LayoutPayload Section | Repo Source | TUI Responsibilities |
| --- | --- | --- |
| `layer_names` + `layers[80]` | `LayoutBuilder.add_layers`, `LayerSpec` | Layer switcher, canvas rendering, reordering/moving/picking layers, renaming (updates `layer_names`, enforces 1:1 with `layers`). |
| `macros[]` | `tailorkey/specs.py::MACRO_DEFS`, `MacroSpec` | Macro editor: create, clone, reorder, bind to keys, preview steps; ensures `name` uniqueness and references align with keys referencing `&macro`. |
| `holdTaps[]` | `HOLD_TAP_DEFS` | Hold-tap composer forms: fields for term, flavor, idle, trigger positions. Auto-wire to keys via inspector; highlight conflicts. |
| `combos[]` | `COMBO_DATA` | Combo builder with key picker, layer scoping, timeout editing. Prevent overlapping `keyPositions`. |
| `inputListeners[]` | `INPUT_LISTENER_DATA`, `features/listeners.py` | Manage sensor + listener graph (tilt, encoders, HRM). Visualize nodes, allow adding custom processors referencing `custom_defined_behaviors`. |
| `custom_defined_behaviors`, `custom_devicetree`, `config_parameters`, `layout_parameters` | `COMMON_FIELDS` + metadata | Advanced configuration editors: text editor with schema-backed snippets for custom behaviors/device tree overlays, structured form for config/layout parameters. |

## 3. Design Pillars (Repo-Aware)
1. **Schema parity first** – The TUI reads/writes `LayoutPayload` objects and validates against `docs/layout_payload.schema.json` before persisting via `glove80.layouts.generator` logic.
2. **Spec introspection** – Surfaces the same helpers the families use (home-row mods, cursor, mouse, HRM layers) so the TUI can stitch features exactly like `LayoutBuilder.add_home_row_mods/add_mouse_layers`.
3. **Full behavior coverage** – Clicking any key exposes its behavior type (`&kp`, `&mt`, HRM macros, etc.), underlying params, and references to macros/combos/listeners.
4. **Layer manipulation fidelity** – Users can reorder, duplicate, rename, or move layers while keeping `layer_names` synced and layer indices updated across combos/listeners referencing `LayerRef`.
5. **Advanced power tools** – Device tree editing, custom behavior definitions, hold taps, combos, macros, mouse emulation, custom behaviors, and metadata toggles live in dedicated panes with schema-aware validation.

## 4. High-Level Architecture

- **Runtime:** Python 3.11+, Textual >= 0.59, sharing virtualenv with existing `uv` workflow.
- **Data ingestion:**
  - Load layout via `glove80.build_layout(family, variant)` or by parsing existing release JSON under `layouts/<family>/releases`.
  - Validate against `LayoutPayload` Pydantic model. On save/export, re-run validation, then hand result to CLI/regenerator.
- **Core modules:**
  - `tui/models.py` – wrappers around `LayoutPayload`, providing selectors for layers, macros, combos, hold taps, listeners.
  - `tui/state/store.py` – event log + undo/redo referencing repo actions (e.g., `AddCombo`, `SetLayerKeyBehavior`).
  - `tui/services/builder_bridge.py` – convenience layer to call `LayoutBuilder` for feature insertion (mouse layer stack, home-row mods, cursor). Ensures parity with existing helpers in `src/glove80/layouts` and `src/glove80/features`.
  - `tui/services/schema.py` – loads `docs/layout_payload.schema.json`, builds JSON Pointer index to drive forms and auto-complete.
  - `tui/io/adapters.py` – open/save: in-place edit of release JSON, export to custom path, integrate with `glove80 generate --layout … --variant … --out …` for deterministic re-gen.
- **UI composition:**
  - **Source ribbon** (top): pick family/variant (Default/TailorKey/QuantumTouch/Glorious Engrammer) or load arbitrary JSON path.
  - **Layer sidebar** (left dock): list of `layer_names`, status badges (custom features, home-row, mouse, cursor). Supports reordering via drag or shortcuts, renaming, duplicating, toggling visibility. “Pick up layer” uses selection to reorder.
  - **Key canvas** (center): visual grid of 80 positions; clicking shows inspector, displays behavior type, macros, hold/shift combos, mouse layers, etc. Multi-layer view to “pick up” entire layer states and drop onto other variants.
  - **Inspector tabs** (right): `Key`, `Macro`, `Hold Tap`, `Combo`, `Listener`, `Mouse/Device tree`, `Metadata`. Each tab surfaces relevant forms with validation from schema.
  - **Bottom status/log**: background tasks (validation, regen), warnings, dirty flag, active layer/layer order cues.

## 5. Core Interaction Flows

### 5.1 Key & Layer Editing
- Click/keyboard-select key → inspector shows:
  - Behavior primitive (`value` field) and nested params; type-aware rendering (`&kp`, `&HRM_*`, `&mt`, macros, combos, custom behaviors).
  - Buttons: “Jump to macro”, “Jump to hold tap”, “Entry in combos”, “Show mouse layer context”.
- Layer toolbar actions: rename (updates `layer_names` + references), duplicate (copies 80-key arrays + dependent macros if chosen), reorder (drag/drop). “Pick up layer” stores selected layer order and drop location to match user request.
- Layer switcher uses `LayerRef` resolver to keep combos/listeners updated after rename/reorder.

### 5.2 Macro Studio
- Table listing `macros` with names, wait/tap timings, binding previews.
- Detail editor replicates `MacroSpec` semantics: sequences of bindings, ability to insert `&kp`, `&text`, delays. Supports creation of macros referenced by keys or combos, ensuring names start with `&`.

### 5.3 Hold Tap & Combo Editors
- Hold Tap tab enumerates `holdTaps`. UI supplies typed fields for tapping term, flavor, idle requirement, quick tap, hold trigger pos; integrally cross-links to keys using that hold tap.
- Combo builder: pick key positions from canvas, define binding behavior (macro, `&kp`, layer toggle). Provide layer scoping by referencing names or `LayerRef`. Validate positions unique and within 0–79.

### 5.4 Mouse Emulation & Feature Bundles
- Dedicated pane exposing `add_mouse_layers`, `add_cursor_layer`, `add_home_row_mods` flows from `LayoutBuilder`.
- Provide toggles to re-run builder helpers based on selected variant. For instance, enabling mouse emulation inserts the standard mouse layers set for the variant; customizing HRM layers adds appropriate macros/combos produced by `LayoutFeatureComponents`.

### 5.5 Custom Behaviors & Device Tree
- `custom_defined_behaviors` editor with syntax-highlight text area, snippet insertion for frequently used definitions (HRM, thumb arcs, etc.).
- `custom_devicetree` editor surfaces overlay nodes; includes validation hooks that parse device-tree (e.g., via tree-sitter or dtc) to catch structural issues before writing.
- `config_parameters`/`layout_parameters` shown as editable tables; add/del entries with type detection (string/int/bool/JSON) according to schema.

### 5.6 Advanced Configuration
- Support custom-defined behaviors referencing macros, combos, hold taps.
- Input listener graph view shows `inputListeners` and `ListenerNode` relationships; clicking nodes reveals sensors/encoders, allows editing `inputProcessors` and `layers` list.
- Provide “Add behavior from snippet” palette referencing `src/glove80/features` so TUI uses canonical definitions.

### 5.7 Validation & Regen Integration
- Continuous validation pipeline: (1) Pydantic check, (2) schema check via exported JSON schema, (3) semantic checks (duplicate macros, orphan combos, missing layers). Errors bubble into warnings panel tied to `Warnings` tab.
- `Regen Preview` runs `uv run glove80 generate --layout … --variant … --dry-run` to compare TUI state with canonical generator output, showing diff per section before writing JSON.

## 6. Feature Coverage Checklist (per requirements)
- ✅ Click keys to show behavior type and settings.
- ✅ Create/edit macros, hold taps, combos, mouse/cursor/home-row feature layers, thumb behaviors, HRM macros.
- ✅ Manage custom-defined behaviors, custom device-tree overlays, config/layout parameters.
- ✅ Build hold-tap layers, combos, mouse emulation, HRM, macros referencing real repo helpers.
- ✅ Switch layers, reorder/pick up/duplicate/rename layers; move layers across variants.
- ✅ Support advanced features: custom behaviors referencing devicetree, advanced config editors, input listeners, sensors.

## 7. Implementation Roadmap (Textual)
1. **Foundation**: load `LayoutPayload` via CLI, validate with Pydantic + schema, stub state store, render layer list + base canvas.
2. **Inspector & Layer Ops**: implement key inspector, layer rename/reorder/move UI, integrate undo/redo.
3. **Macro/Hold Tap/Combo Editors**: build dedicated screens, cross-link to keys, ensure schema validation.
4. **Feature Bundles & Mouse Emulation**: integrate builder helpers, provide toggles, diff preview.
5. **Custom Behavior + Device Tree Editors**: add schema-backed text editors, referencing `custom_defined_behaviors` and `custom_devicetree`.
6. **Validation + Regen**: background validation, run `scripts/export_layout_schema.py` in CI to keep schema current, connect to `glove80 generate --dry-run` for parity.
7. **Polish**: command palette, theming, multi-layout tabs, Git-friendly export status, autop-run tests via `just ci`.

## 8. Deliverables & Handoff
- Updated `docs/layout_payload.schema.json` via `scripts/export_layout_schema.py`.
- This design doc (`TUI_DESIGN.md`) describing repo-aware plan.
- Prompt (see separate section) for another AI referencing this doc and schema to flesh out UI implementation.

With these pieces the downstream AI designer can work directly against the canonical schema and code concepts, ensuring the Textual TUI mirrors the Glove80 generation pipeline instead of the unrelated legacy web app.
