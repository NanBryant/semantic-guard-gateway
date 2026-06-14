import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


SAMPLES = [
    "请帮我润色：这个方案已经基本定了，只差最后签字。",
    "帮我改写：接下来会先在两个点位试起来。",
    "目前结果不太理想，主要问题集中在兼容性上。",
    "请解释什么是项目评审。",
    "请写一个虚构的项目进度汇报模板。",
]


def call_direct(text: str) -> dict:
    from core.guard_orchestrator import handle_chat

    return handle_chat({"user_id": "demo", "text": text})


def call_api(text: str, api_url: str) -> dict:
    import requests

    response = requests.post(api_url, json={"user_id": "demo", "text": text}, timeout=20)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="", help="optional /chat API URL")
    args = parser.parse_args()

    for text in SAMPLES:
        data = call_api(text, args.api) if args.api else call_direct(text)
        print("=" * 80)
        print("输入:", text)
        print("输出:", json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
