# Default Layout Examples

Glove80 ships several stock layouts curated by MoErgo.
The `layouts/default` directory tracks the JSON artifacts exported from the layout editor so they can be referenced alongside TailorKey and QuantumTouch.

## Canonical Layouts (accessed 8 Nov 2025)
- [Glove80 Factory Default Layout](https://my.glove80.com/#/layout/glove80) (accessed 8 Nov 2025)
- [Glove80 Factory Default Layout for macOS](https://my.glove80.com/#/layout/glove80-macos) (accessed 8 Nov 2025)
- [Mouse Emulation Example](https://my.glove80.com/#/layout/mouse-emulation) (accessed 8 Nov 2025)
- [Colemak Layout](https://my.glove80.com/#/layout/colemak) (accessed 8 Nov 2025)
- [Colemak-DH Layout](https://my.glove80.com/#/layout/colemak-dh) (accessed 8 Nov 2025)
- [Dvorak Layout](https://my.glove80.com/#/layout/dvorak) (accessed 8 Nov 2025)
- [Workman Layout](https://my.glove80.com/#/layout/workman) (accessed 8 Nov 2025)
- [Kinesis Advantage-like Layout](https://my.glove80.com/#/layout/kinesis) (accessed 8 Nov 2025)

These JSON files are mirrored under `src/glove80/default/data` so the CLI can regenerate them deterministically.
Keeping them under version control ensures we can diff against MoErgo’s published versions while still treating the packaged data as the source of truth.
