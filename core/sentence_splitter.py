import re
from typing import Dict, List


TERMINATORS = set("。！？!?；;：:")
ORDINAL_BOUNDARY = re.compile(r"(第[一二三四五六七八九十]+句)(?=第[一二三四五六七八九十]+句)")


def _split_ordinal_demo_text(text: str) -> List[str]:
    """Split compact demo text such as `第一句第二句。` used in the guide."""
    parts: List[str] = []
    start = 0
    for match in ORDINAL_BOUNDARY.finditer(text):
        end = match.end(1)
        parts.append(text[start:end])
        start = end
    parts.append(text[start:])
    return [p for p in parts if p.strip()]


def split_sentences(text: str) -> List[Dict[str, str]]:
    """Split user input into sentence records with stable sentence ids."""
    text = (text or "").strip()
    if not text:
        return []

    raw_parts: List[str] = []
    buf: List[str] = []
    for char in text:
        if char in "\r\n":
            sentence = "".join(buf).strip()
            if sentence:
                raw_parts.append(sentence)
            buf = []
            continue
        buf.append(char)
        if char in TERMINATORS:
            sentence = "".join(buf).strip()
            if sentence:
                raw_parts.append(sentence)
            buf = []

    tail = "".join(buf).strip()
    if tail:
        raw_parts.append(tail)

    normalized_parts: List[str] = []
    for part in raw_parts:
        normalized_parts.extend(_split_ordinal_demo_text(part))

    results: List[Dict[str, str]] = []
    for part in normalized_parts:
        sentence = part.strip()
        if sentence:
            results.append({"sentence_id": f"s{len(results) + 1}", "text": sentence})
    return results
