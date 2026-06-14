from pathlib import Path
from typing import Dict, Optional

from semantic.embedding_matcher import EmbeddingMatcher
from semantic.fact_store import DEFAULT_FACT_PATH, expand_fact_texts, load_facts
from semantic.llm_semantic_classifier import LLMSemanticClassifier
from semantic.mock_embedding_client import MockEmbeddingClient
from semantic.thresholds import load_thresholds


class SemanticDetector:
    def __init__(
        self,
        embedding_matcher: EmbeddingMatcher,
        classifier: LLMSemanticClassifier,
        thresholds: Optional[Dict[str, float]] = None,
    ):
        self.embedding_matcher = embedding_matcher
        self.classifier = classifier
        self.thresholds = thresholds or load_thresholds()

    def detect(self, sentence: str) -> Dict:
        sim_result = self.embedding_matcher.search(sentence, top_k=3)
        cls_result = self.classifier.classify(sentence)

        top_hit = sim_result.get("top_hit")
        raw_sim_score = float(top_hit["similarity"]) if top_hit else 0.0
        sim_score = raw_sim_score
        if cls_result.get("is_public_knowledge"):
            sim_score = min(sim_score, self.thresholds["public_similarity_cap"])

        cls_score = float(cls_result.get("risk_score", 0.0) or 0.0)
        evidence = [
            {
                "type": "fact_similarity",
                "matched_fact_id": top_hit.get("fact_id") if top_hit else None,
                "matched_fact_type": top_hit.get("fact_type") if top_hit else None,
                "similarity": round(raw_sim_score, 4),
                "effective_similarity": round(sim_score, 4),
            },
            {
                "type": "semantic_classifier",
                "confidence": round(cls_score, 4),
                "reason": cls_result.get("reason", ""),
            },
        ]

        high_by_similarity = sim_score >= self.thresholds["similarity_high"]
        high_by_classifier = cls_score >= self.thresholds["classifier_high"]
        high_by_combo = (
            sim_score >= self.thresholds["combo_similarity"]
            and cls_score >= self.thresholds["combo_classifier"]
        )

        if high_by_similarity or high_by_classifier or high_by_combo:
            final_score = max(sim_score, cls_score, self.thresholds["block_threshold"])
        else:
            final_score = max(sim_score, cls_score)

        risk_types = set(cls_result.get("risk_types", []) or [])
        if top_hit and sim_score >= self.thresholds["combo_similarity"]:
            risk_types.add(top_hit["fact_type"])

        is_confidential = final_score >= self.thresholds["block_threshold"]
        return {
            "is_confidential_sentence": is_confidential,
            "risk_score": round(final_score, 4),
            "risk_level": "high"
            if final_score >= 0.75
            else "medium"
            if final_score >= 0.6
            else "low",
            "risk_types": sorted(risk_types) if is_confidential else sorted(risk_types),
            "suggested_action": "block_sentence" if is_confidential else "allow",
            "evidence": evidence,
        }


_DEFAULT_DETECTOR: Optional[SemanticDetector] = None


def build_default_detector(fact_path: str | Path = DEFAULT_FACT_PATH) -> SemanticDetector:
    thresholds = load_thresholds()
    matcher = EmbeddingMatcher(MockEmbeddingClient(), threshold=thresholds["combo_similarity"])
    path = Path(fact_path)
    if path.exists():
        facts = load_facts(path)
        matcher.build(expand_fact_texts(facts))
    else:
        matcher.build([])
    return SemanticDetector(matcher, LLMSemanticClassifier(), thresholds)


def get_default_detector() -> SemanticDetector:
    global _DEFAULT_DETECTOR
    if _DEFAULT_DETECTOR is None:
        _DEFAULT_DETECTOR = build_default_detector()
    return _DEFAULT_DETECTOR


def reset_default_detector() -> None:
    global _DEFAULT_DETECTOR
    _DEFAULT_DETECTOR = None


def detect_confidential_sentence(sentence: str) -> Dict:
    return get_default_detector().detect(sentence)
