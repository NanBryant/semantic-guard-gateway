import math
from collections import Counter
from typing import Dict, List


def cosine_sparse(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[key] * b[key] for key in common)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return float(dot / (norm_a * norm_b))


class EmbeddingMatcher:
    def __init__(self, embedding_client, threshold: float = 0.78):
        self.embedding_client = embedding_client
        self.threshold = threshold
        self.rows: List[Dict] = []
        self.embeddings: List[Counter] = []

    def build(self, rows: List[Dict]) -> None:
        self.rows = list(rows)
        texts = [row["text"] for row in self.rows]
        self.embeddings = self.embedding_client.embed(texts) if texts else []

    def search(self, sentence: str, top_k: int = 3) -> Dict:
        if not self.rows:
            return {"matched": False, "top_hit": None, "top_k": []}

        query_vec = self.embedding_client.embed([sentence])[0]
        scored = [
            (idx, cosine_sparse(query_vec, vector))
            for idx, vector in enumerate(self.embeddings)
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        hits = []
        for idx, score in scored[:top_k]:
            row = self.rows[idx]
            hits.append(
                {
                    "fact_id": row["fact_id"],
                    "fact_type": row["fact_type"],
                    "text_type": row["text_type"],
                    "similarity": round(score, 4),
                }
            )
        best = hits[0] if hits else None
        return {
            "matched": bool(best and best["similarity"] >= self.threshold),
            "top_hit": best,
            "top_k": hits,
        }
