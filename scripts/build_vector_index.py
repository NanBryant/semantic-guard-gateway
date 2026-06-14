import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from semantic.embedding_matcher import EmbeddingMatcher
from semantic.fact_store import expand_fact_texts, load_facts
from semantic.mock_embedding_client import MockEmbeddingClient
from semantic.thresholds import load_thresholds


def main() -> None:
    facts = load_facts(ROOT / "data" / "simulated" / "confidential_facts.jsonl")
    rows = expand_fact_texts(facts)
    thresholds = load_thresholds()
    matcher = EmbeddingMatcher(MockEmbeddingClient(), threshold=thresholds["combo_similarity"])
    matcher.build(rows)
    print(f"index built: {len(rows)} searchable texts from {len(facts)} facts")


if __name__ == "__main__":
    main()
