from semantic.semantic_detector import detect_confidential_sentence, reset_default_detector


def setup_function():
    reset_default_detector()


def test_keywordless_internal_decision_is_blocked():
    result = detect_confidential_sentence("这个方案已经基本定了，只差最后签字。")
    assert result["is_confidential_sentence"] is True
    assert result["suggested_action"] == "block_sentence"
    assert "internal_decision" in result["risk_types"]


def test_public_knowledge_question_is_allowed():
    result = detect_confidential_sentence("请解释什么是内部评审。")
    assert result["is_confidential_sentence"] is False
    assert result["suggested_action"] == "allow"


def test_deployment_and_evaluation_examples_are_blocked():
    deployment = detect_confidential_sentence("接下来会先在两个点位试起来。")
    evaluation = detect_confidential_sentence("目前结果不太理想，主要问题集中在兼容性上。")
    assert deployment["suggested_action"] == "block_sentence"
    assert "deployment_plan" in deployment["risk_types"]
    assert evaluation["suggested_action"] == "block_sentence"
    assert set(evaluation["risk_types"]) & {"evaluation_result", "vulnerability_status"}
