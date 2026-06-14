from pathlib import Path
from typing import Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THRESHOLD_PATH = PROJECT_ROOT / "config" / "semantic_thresholds.yaml"

DEFAULT_THRESHOLDS = {
    "similarity_high": 0.82,
    "classifier_high": 0.80,
    "combo_similarity": 0.70,
    "combo_classifier": 0.65,
    "medium_similarity": 0.65,
    "medium_classifier": 0.60,
    "block_threshold": 0.75,
    "public_similarity_cap": 0.45,
}


def load_thresholds(path: str | Path = DEFAULT_THRESHOLD_PATH) -> Dict[str, float]:
    values = dict(DEFAULT_THRESHOLDS)
    target = Path(path)
    if not target.exists():
        return values

    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip().split("#", 1)[0].strip()
        if key in values and raw_value:
            values[key] = float(raw_value)
    return values
