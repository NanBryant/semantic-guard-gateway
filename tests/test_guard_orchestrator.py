import json

from core.guard_orchestrator import handle_chat
from llm.client import reset_call_log, was_called
from policy.audit_logger import DEFAULT_AUDIT_LOG
from semantic.semantic_detector import reset_default_detector


def setup_function():
    reset_call_log()
    reset_default_detector()


def test_block_does_not_call_llm_and_hides_high_risk_text():
    secret_text = "这个方案已经基本定了，只差最后签字。"
    response = handle_chat({"user_id": "u1", "text": f"请帮我润色：{secret_text}"})

    assert response["action"] == "block"
    assert was_called() is False
    dumped = json.dumps(response, ensure_ascii=False)
    assert secret_text not in dumped
    assert response["sentence_results"][1]["risk_level"] == "high"


def test_allow_calls_llm():
    response = handle_chat({"user_id": "u1", "text": "请解释什么是项目评审。"})
    assert response["action"] == "allow"
    assert was_called() is True
    assert response["llm_response"]


def test_audit_log_uses_hash_not_plain_high_risk_text():
    secret_text = "接下来会先在两个点位试起来。"
    handle_chat({"user_id": "u1", "text": secret_text})
    last_line = DEFAULT_AUDIT_LOG.read_text(encoding="utf-8").strip().splitlines()[-1]
    assert secret_text not in last_line
    record = json.loads(last_line)
    assert record["sentences"][0]["text_hash"]
