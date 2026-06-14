from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from core.response_schema import (
    build_allow_response,
    build_block_response,
    build_fail_closed_response,
)
from core.rule_detector import detect_rule_sensitive
from core.sentence_splitter import split_sentences
from llm.client import call_llm
from policy.audit_logger import write_audit_log
from policy.semantic_decision import make_semantic_decision
from semantic.semantic_detector import detect_confidential_sentence
from semantic.thresholds import load_thresholds


def generate_request_id() -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"req_{stamp}_{uuid4().hex[:8]}"


def _empty_allow_decision(mode: str) -> Dict:
    return {
        "action": "allow",
        "risk_score": 0.0,
        "public_sentence_results": [],
        "blocked_sentence_ids": [],
        "mode": mode,
    }


def _fail_closed_decision(mode: str) -> Dict:
    return {
        "action": "block",
        "risk_score": 1.0,
        "public_sentence_results": [],
        "blocked_sentence_ids": [],
        "mode": mode,
    }


def handle_chat(request: Dict) -> Dict:
    request_id = request.get("request_id") or generate_request_id()
    text = request.get("text", "")
    user_id = request.get("user_id", "demo_user")
    mode = request.get("mode", "strict")

    sentences = split_sentences(text)
    if not sentences:
        decision = _empty_allow_decision(mode)
        write_audit_log(request_id, user_id, [], decision)
        return build_allow_response(request_id, decision, call_llm(text))

    sentence_results: List[Dict] = []
    try:
        for item in sentences:
            sentence_text = item["text"]
            rule_result = detect_rule_sensitive(sentence_text)
            semantic_result = detect_confidential_sentence(sentence_text)
            sentence_results.append(
                {
                    "sentence_id": item["sentence_id"],
                    "text": sentence_text,
                    "rule_result": rule_result,
                    "semantic_result": semantic_result,
                }
            )
    except Exception:
        decision = _fail_closed_decision(mode)
        write_audit_log(request_id, user_id, sentence_results, decision)
        return build_fail_closed_response(request_id)

    thresholds = load_thresholds()
    decision = make_semantic_decision(
        sentence_results,
        mode=mode,
        block_threshold=thresholds["block_threshold"],
    )
    write_audit_log(request_id, user_id, sentence_results, decision)

    if decision["action"] == "block":
        return build_block_response(request_id, decision)

    llm_response = call_llm(text)
    return build_allow_response(request_id, decision, llm_response)
