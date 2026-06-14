import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from semantic.fact_types import ALLOWED_FACT_TYPES


FACT_PATH = ROOT / "data" / "simulated" / "confidential_facts.jsonl"
HARD_NEGATIVE_PATH = ROOT / "data" / "simulated" / "hard_negative.jsonl"


def load_jsonl(path: Path):
    with path.open(encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            if line.strip():
                yield line_no, json.loads(line)


def validate_facts(path: Path = FACT_PATH) -> Counter:
    seen = set()
    type_counter = Counter()
    for line_no, item in load_jsonl(path):
        fact_id = item.get("fact_id")
        assert fact_id and fact_id not in seen, f"duplicate fact_id at line {line_no}"
        seen.add(fact_id)
        assert item.get("fact_type") in ALLOWED_FACT_TYPES, f"invalid fact_type at line {line_no}"
        assert item.get("confidential_level") in {"low", "medium", "high", "critical"}, line_no
        assert item.get("fact_text"), f"missing fact_text at line {line_no}"
        assert isinstance(item.get("paraphrases"), list), f"paraphrases must be list at line {line_no}"
        assert len(item["paraphrases"]) >= 2, f"need at least two paraphrases at line {line_no}"
        assert item.get("source") == "simulation", f"source must be simulation at line {line_no}"
        assert item.get("status") in {"active", "inactive"}, f"invalid status at line {line_no}"
        type_counter[item["fact_type"]] += 1
    assert len(seen) >= 200, f"need at least 200 facts, got {len(seen)}"
    assert len(type_counter) >= 8, f"need at least 8 fact types, got {len(type_counter)}"
    return type_counter


def validate_hard_negatives(path: Path = HARD_NEGATIVE_PATH) -> int:
    seen = set()
    count = 0
    for line_no, item in load_jsonl(path):
        negative_id = item.get("negative_id")
        assert negative_id and negative_id not in seen, f"duplicate negative_id at line {line_no}"
        seen.add(negative_id)
        assert item.get("text"), f"missing text at line {line_no}"
        assert item.get("source") == "simulation", f"source must be simulation at line {line_no}"
        count += 1
    assert count >= 200, f"need at least 200 hard negatives, got {count}"
    return count


def main() -> None:
    type_counter = validate_facts()
    hard_negative_count = validate_hard_negatives()
    print(f"OK: {sum(type_counter.values())} facts validated")
    print(f"OK: {len(type_counter)} fact types covered")
    for fact_type, count in sorted(type_counter.items()):
        print(f"  {fact_type}: {count}")
    print(f"OK: {hard_negative_count} hard negatives validated")


if __name__ == "__main__":
    main()
