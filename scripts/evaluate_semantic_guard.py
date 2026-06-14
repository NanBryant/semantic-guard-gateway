import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


CASE_PATH = ROOT / "data" / "simulated" / "semantic_test_cases.jsonl"
REPORT_PATH = ROOT / "reports" / "semantic_errors.json"


def load_cases(path: Path) -> List[Dict]:
    cases = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def predict_direct(text: str) -> Tuple[str, Dict]:
    from core.guard_orchestrator import handle_chat

    data = handle_chat({"user_id": "eval_user", "text": text})
    return data.get("action"), data


def predict_api(text: str, api_url: str) -> Tuple[str, Dict]:
    import requests

    response = requests.post(api_url, json={"user_id": "eval_user", "text": text}, timeout=20)
    response.raise_for_status()
    data = response.json()
    return data.get("action"), data


def p95(values: List[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=20, method="inclusive")[18]


def evaluate(cases: List[Dict], direct: bool, api_url: str) -> Dict:
    total = len(cases)
    correct = 0
    stats: Dict[str, Dict[str, int]] = {}
    errors = []
    latencies = []

    for case in cases:
        start = time.perf_counter()
        if direct:
            predicted, raw = predict_direct(case["text"])
        else:
            predicted, raw = predict_api(case["text"], api_url)
        latencies.append((time.perf_counter() - start) * 1000)

        expected = case["expected_action"]
        ok = predicted == expected
        correct += int(ok)
        category = case["category"]
        stats.setdefault(category, {"total": 0, "correct": 0})
        stats[category]["total"] += 1
        stats[category]["correct"] += int(ok)
        if not ok:
            errors.append(
                {
                    "case_id": case["case_id"],
                    "category": category,
                    "text": case["text"],
                    "expected": expected,
                    "predicted": predicted,
                    "raw": raw,
                }
            )

    expected_block = [case for case in cases if case["expected_action"] == "block"]
    expected_allow = [case for case in cases if case["expected_action"] == "allow"]
    missed_blocks = [
        err for err in errors if err["expected"] == "block" and err["predicted"] != "block"
    ]
    false_positives = [
        err for err in errors if err["expected"] == "allow" and err["predicted"] == "block"
    ]

    metrics = {
        "total": total,
        "overall_accuracy": correct / total if total else 0.0,
        "confidential_sentence_recall": 1 - (len(missed_blocks) / len(expected_block))
        if expected_block
        else 0.0,
        "false_positive_rate": len(false_positives) / len(expected_allow)
        if expected_allow
        else 0.0,
        "p95_latency_ms": round(p95(latencies), 2),
        "by_category": {
            category: {
                "total": data["total"],
                "accuracy": data["correct"] / data["total"] if data["total"] else 0.0,
            }
            for category, data in sorted(stats.items())
        },
        "errors": errors,
    }
    metrics["keywordless_recall"] = metrics["by_category"].get("keywordless_fact", {}).get(
        "accuracy", 0.0
    )
    metrics["paraphrase_recall"] = metrics["by_category"].get("paraphrase_fact", {}).get(
        "accuracy", 0.0
    )
    metrics["adversarial_recall"] = metrics["by_category"].get("adversarial", {}).get(
        "accuracy", 0.0
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct", action="store_true", help="call handle_chat directly")
    parser.add_argument("--api", default="http://127.0.0.1:8000/chat")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    cases = load_cases(CASE_PATH)
    if args.limit:
        cases = cases[: args.limit]

    metrics = evaluate(cases, direct=args.direct, api_url=args.api)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(metrics["errors"], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    printable = {key: value for key, value in metrics.items() if key != "errors"}
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    print(f"errors written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
