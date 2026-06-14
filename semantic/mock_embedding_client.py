import re
from collections import Counter
from typing import Counter as CounterType, Iterable, List


SYNONYM_REPLACEMENTS = [
    ("过会", "通过内部评审"),
    ("过评审", "通过内部评审"),
    ("走流程", "审批签字"),
    ("批复", "审批签字"),
    ("试起来", "试部署"),
    ("小范围用了", "小范围试部署"),
    ("小范围用", "小范围试部署"),
    ("两个点", "两个点位"),
    ("不是特别理想", "不理想"),
    ("没达到预期", "不理想"),
    ("卡在兼容性", "问题集中在兼容性"),
    ("下探空间", "报价折扣空间"),
]

DOMAIN_PHRASES = [
    "内部评审",
    "通过内部评审",
    "完成内部评审",
    "准备试点",
    "试部署",
    "两个点位",
    "小范围",
    "兼容性",
    "不理想",
    "第二套方案",
    "正式确认",
    "最后签字",
    "审批签字",
    "报价折扣空间",
    "采购",
    "供应商",
    "接手",
    "异常",
    "故障",
    "技术路线",
    "部署节点",
]


def normalize_text(text: str) -> str:
    value = re.sub(r"\s+", "", (text or "").lower())
    for source, target in SYNONYM_REPLACEMENTS:
        value = value.replace(source, target)
    return value


def _ngrams(text: str, sizes: Iterable[int]) -> Iterable[str]:
    for size in sizes:
        if len(text) < size:
            continue
        for idx in range(len(text) - size + 1):
            yield text[idx : idx + size]


class MockEmbeddingClient:
    """Deterministic local text vectorizer used for offline integration demos."""

    def embed(self, texts: List[str]) -> List[CounterType[str]]:
        vectors = []
        for text in texts:
            normalized = normalize_text(text)
            vector: CounterType[str] = Counter()
            for token in _ngrams(normalized, (2, 3)):
                vector[f"ng:{token}"] += 1.0
            for phrase in DOMAIN_PHRASES:
                if phrase in normalized:
                    vector[f"phrase:{phrase}"] += 4.0
            for word in re.findall(r"[a-zA-Z0-9_]+", normalized):
                vector[f"word:{word}"] += 1.0
            vectors.append(vector)
        return vectors
