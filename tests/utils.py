import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
METADATA = json.loads((REPO_ROOT / "sources" / "variant_metadata.json").read_text())


def load_variant_json(variant: str) -> dict:
    meta = METADATA[variant if variant in METADATA else variant]
    path = REPO_ROOT / meta["output"]
    return json.loads(path.read_text())
