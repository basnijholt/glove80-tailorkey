# TailorKey Layout Sources

This repository captures the released TailorKey ZMK layouts for the Glove80
keyboard and provides tooling to regenerate the published JSON files from a
single source of truth.

## Goals

- Preserve each TailorKey variant exactly as it was shared upstream.
- Regenerate the release JSON files from canonical sources deterministically.
- Enable CI workflows that publish the generated layout files as artifacts.
- Provide a clean place to continue evolving TailorKey while maintaining a
auditable history of every change.

## Repository Layout

```
.
├─ original/                   # published layouts (generated artifacts)
├─ sources/
│  ├─ variant_metadata.json    # mapping of variants → release metadata
│  └─ variants/                # canonical source JSON per layout variant
├─ src/
│  └─ tailorkey_builder/       # Python package for layered generation
├─ scripts/
│  └─ generate_tailorkey_layouts.py
├─ tests/                      # pytest suites (release + layer builders)
└─ README.md
```

- **sources/variants** contains the original layouts, one file per variant.
  These are treated as the authoritative copies that should be edited when
  making changes.
- **sources/variant_metadata.json** lists each variant, the path to its
  canonical source, the release filename, and the metadata (uuid, parent_uuid,
  tags, notes, etc.) that should be applied when regenerating the published
  JSON.
- **scripts/generate_tailorkey_layouts.py** copies the canonical source JSON to
  the release file path and overwrites its headline metadata so it matches the
  upstream release exactly.
- **original/** is where the generator writes the published JSON files that ship
  with releases or get uploaded as CI artifacts.
- **src/tailorkey_builder** is the growing Python package that will eventually
  synthesize every layer from shared building blocks (starting with mouse
  layers).
- **tests/** contains pytest suites that validate both the published layouts and
  individual generator modules.

## Regeneration Workflow

1. Modify the canonical source in `sources/variants/*.json` or adjust the
   metadata in `sources/variant_metadata.json`.
2. Run the generator:

   ```bash
   python3 scripts/generate_tailorkey_layouts.py
   ```

   The script rewrites every release JSON under `original/`. Because it pulls
   from the canonical source, the working tree will only show diffs for files
   you intentionally edited.

3. Run the tests:

   ```bash
   pytest
   ```

   The test suite reruns the generator for each variant and asserts that the
   release file exactly matches the canonical source. This guards against
   accidental edits to the public layouts.

## Continuous Integration

A future CI workflow can simply execute the two commands above. The generated
release JSON files can then be uploaded as build artifacts or attached to a
GitHub release, ensuring the hosted layouts always correspond to the committed
source files.
