from typing import Dict


BLOCK_MESSAGE = "检测到疑似内部保密事实，本次请求已拦截，未发送至模型。"
ALLOW_MESSAGE = "未检测到保密事实，已发送至模型。"
FAIL_CLOSED_MESSAGE = "检测服务异常，暂不放行。"


def build_block_response(request_id: str, decision: Dict, message: str = BLOCK_MESSAGE) -> Dict:
    return {
        "request_id": request_id,
        "action": "block",
        "risk_score": decision.get("risk_score", 1.0),
        "message": message,
        "sentence_results": decision.get("public_sentence_results", []),
    }


def build_allow_response(request_id: str, decision: Dict, llm_response: str) -> Dict:
    return {
        "request_id": request_id,
        "action": "allow",
        "risk_score": decision.get("risk_score", 0.0),
        "message": ALLOW_MESSAGE,
        "llm_response": llm_response,
        "sentence_results": decision.get("public_sentence_results", []),
    }


def build_fail_closed_response(request_id: str) -> Dict:
    return {
        "request_id": request_id,
        "action": "block",
        "risk_score": 1.0,
        "message": FAIL_CLOSED_MESSAGE,
        "sentence_results": [],
    }
