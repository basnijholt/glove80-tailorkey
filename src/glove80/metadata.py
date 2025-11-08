"""
Helpers for loading TailorKey variant metadata.

This keeps JSON parsing in one place (with types) so both the generator and the
library can share it safely.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, TypedDict

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METADATA_PATH = REPO_ROOT / "sources" / "variant_metadata.json"


class VariantMetadata(TypedDict):
    output: str
    title: str
    uuid: str
    parent_uuid: str
    date: int
    tags: List[str]
    notes: str


MetadataByVariant = Dict[str, VariantMetadata]


@lru_cache()
def load_metadata(path: Path | None = None) -> MetadataByVariant:
    """Load (and cache) the metadata file as typed objects."""

    metadata_path = path or DEFAULT_METADATA_PATH
    with metadata_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_variant_metadata(name: str, *, path: Path | None = None) -> VariantMetadata:
    """Return the metadata entry for a particular variant."""

    metadata = load_metadata(path)
    try:
        return metadata[name]
    except KeyError as exc:
        raise KeyError(f"Unknown variant '{name}'. Available: {sorted(metadata)}") from exc
