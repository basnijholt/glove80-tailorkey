import json
from pathlib import Path

from glove80.metadata import get_variant_metadata

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_variant_json(variant: str) -> dict:
    meta = get_variant_metadata(variant)
    path = REPO_ROOT / meta["output"]
    return json.loads(path.read_text())
