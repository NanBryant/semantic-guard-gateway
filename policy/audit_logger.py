import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_LOG = PROJECT_ROOT / "reports" / "audit_semantic.log"


def text_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def write_audit_log(
    request_id: str,
    user_id: str,
    sentence_results: List[Dict],
    decision: Dict,
    log_path: Path | None = None,
) -> None:
    safe_sentences = []
    for item in sentence_results:
        semantic_result = item.get("semantic_result", {})
        rule_result = item.get("rule_result", {})
        safe_sentences.append(
            {
                "sentence_id": item["sentence_id"],
                "text_hash": text_hash(item.get("text", "")),
                "semantic_risk_score": semantic_result.get("risk_score", 0.0),
                "rule_risk_score": rule_result.get("risk_score", 0.0),
                "risk_types": sorted(
                    set(semantic_result.get("risk_types", []) or [])
                    | set(rule_result.get("risk_types", []) or [])
                ),
                "semantic_action": semantic_result.get("suggested_action", "allow"),
                "rule_action": rule_result.get("suggested_action", "allow"),
            }
        )

    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "user_id": user_id,
        "final_action": decision.get("action"),
        "risk_score": decision.get("risk_score", 0.0),
        "mode": decision.get("mode", "strict"),
        "llm_status": "LLM_NOT_CALLED"
        if decision.get("action") == "block"
        else "LLM_CALLED",
        "sentences": safe_sentences,
    }

    target = Path(log_path) if log_path else DEFAULT_AUDIT_LOG
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
