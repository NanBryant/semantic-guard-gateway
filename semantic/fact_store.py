import json
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FACT_PATH = PROJECT_ROOT / "data" / "simulated" / "confidential_facts.jsonl"


def load_jsonl(path: str | Path) -> List[Dict]:
    target = Path(path)
    rows = []
    if not target.exists():
        raise FileNotFoundError(f"jsonl file not found: {target}")
    with target.open(encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {target}:{line_no}") from exc
    return rows


def load_facts(path: str | Path = DEFAULT_FACT_PATH) -> List[Dict]:
    return load_jsonl(path)


def expand_fact_texts(facts: List[Dict]) -> List[Dict]:
    rows = []
    for fact in facts:
        rows.append(
            {
                "fact_id": fact["fact_id"],
                "fact_type": fact["fact_type"],
                "confidential_level": fact["confidential_level"],
                "text": fact["fact_text"],
                "text_type": "fact_text",
            }
        )
        for paraphrase in fact.get("paraphrases", []):
            rows.append(
                {
                    "fact_id": fact["fact_id"],
                    "fact_type": fact["fact_type"],
                    "confidential_level": fact["confidential_level"],
                    "text": paraphrase,
                    "text_type": "paraphrase",
                }
            )
    return rows
