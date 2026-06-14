from typing import Dict, Iterable, List


def _risk_level(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.6:
        return "medium"
    return "low"


def _evidence_types(items: Iterable[Dict]) -> List[str]:
    result = []
    for item in items:
        kind = item.get("type")
        if kind and kind not in result:
            result.append(kind)
    return result


def _public_sentence_result(item: Dict) -> Dict:
    semantic_result = item.get("semantic_result", {})
    rule_result = item.get("rule_result", {})
    score = max(
        float(semantic_result.get("risk_score", 0.0) or 0.0),
        float(rule_result.get("risk_score", 0.0) or 0.0),
    )
    risk_types = sorted(
        set(semantic_result.get("risk_types", []) or [])
        | set(rule_result.get("risk_types", []) or [])
    )
    evidence = list(semantic_result.get("evidence", []) or []) + list(
        rule_result.get("evidence", []) or []
    )
    level = _risk_level(score)
    return {
        "sentence_id": item["sentence_id"],
        "risk_level": level,
        "risk_score": round(score, 4),
        "risk_types": risk_types,
        "evidence_types": _evidence_types(evidence),
        "action": "block_sentence" if level == "high" else "allow",
    }


def make_semantic_decision(
    sentence_results: List[Dict], mode: str = "strict", block_threshold: float = 0.75
) -> Dict:
    public_results = [_public_sentence_result(item) for item in sentence_results]
    max_score = max((item["risk_score"] for item in public_results), default=0.0)
    high_items = [item for item in public_results if item["risk_score"] >= block_threshold]

    if mode == "allow":
        action = "allow"
    elif mode == "sentence_only" and high_items:
        action = "sentence_only"
    elif high_items:
        action = "block"
    else:
        action = "allow"

    return {
        "action": action,
        "risk_score": round(max_score, 4),
        "public_sentence_results": public_results,
        "blocked_sentence_ids": [item["sentence_id"] for item in high_items],
        "mode": mode,
    }
