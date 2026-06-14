from typing import List


CALL_LOG: List[str] = []


def reset_call_log() -> None:
    CALL_LOG.clear()


def was_called() -> bool:
    return bool(CALL_LOG)


def call_llm(text: str) -> str:
    """Demo LLM client. Replace this with a real model gateway in production."""
    CALL_LOG.append(text or "")
    return "演示模型回复：未检测到保密事实，本请求已进入模型处理流程。"
