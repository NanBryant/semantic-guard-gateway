import re
from typing import Dict, List


RULES = [
    ("phone_number", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("api_key", re.compile(r"\b(?:sk|ak|api[_-]?key)[-_A-Za-z0-9]{12,}\b", re.I)),
    ("token", re.compile(r"\b(?:token|secret|bearer)\s*[:=]\s*[-_A-Za-z0-9]{12,}\b", re.I)),
]


def detect_rule_sensitive(sentence: str) -> Dict:
    """Detect first-stage sensitive entities without returning raw matched values."""
    hits: List[Dict[str, str]] = []
    for risk_type, pattern in RULES:
        if pattern.search(sentence or ""):
            hits.append({"type": "rule_pattern", "risk_type": risk_type})

    if not hits:
        return {
            "is_rule_sensitive": False,
            "risk_score": 0.0,
            "risk_types": [],
            "suggested_action": "allow",
            "evidence": [],
        }

    risk_types = sorted({hit["risk_type"] for hit in hits})
    return {
        "is_rule_sensitive": True,
        "risk_score": 0.9,
        "risk_types": risk_types,
        "suggested_action": "block_sentence",
        "evidence": hits,
    }
