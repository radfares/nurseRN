"""
Offline end-to-end RAG integration test (no network).

Goal:
- Prove ingestion -> retrieval -> SOURCE-bound grounded context works without OpenAI.
- Use a deterministic local embedder for query-time embedding (Chroma search).

This test is intentionally "integration-like":
- real ChromaDB collections on a tmp path
- real NurseRN ingestion service and RAGEnhancer logic
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List, Optional

import pytest

from src.knowledge.config import KnowledgeConfig, EmbedderConfig
from src.knowledge.embedders import BaseEmbedder, EmbedderSpec
from src.knowledge.ingestion_service import KnowledgeIngestionService
from src.knowledge.vector_store import VectorStoreFactory
from src.services.rag_enhancement import RAGEnhancer


def _hash_to_unit_vector(text: str, dims: int) -> List[float]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # Expand bytes deterministically.
    raw = list(h) * ((dims // len(h)) + 1)
    vec = [float(raw[i]) / 255.0 for i in range(dims)]
    # Avoid all-zero vectors.
    if all(v == 0.0 for v in vec):
        vec[0] = 1.0
    return vec


class DeterministicAgnoEmbedder:
    """
    Minimal embedder interface compatible with agno's ChromaDb wrapper.
    """

    def __init__(self, *, model_id: str, dimensions: int):
        self.id = model_id
        self.dimensions = dimensions

    def get_embedding(self, text: str) -> List[float]:
        return _hash_to_unit_vector(text, self.dimensions)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]


class DeterministicBaseEmbedder(BaseEmbedder):
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._call_count += 1
        return [_hash_to_unit_vector(t, self.spec.dimensions) for t in texts]


@pytest.fixture
def offline_embedder_spec() -> EmbedderSpec:
    return EmbedderSpec(provider="local", model="deterministic-test", dimensions=8)


@pytest.fixture
def offline_config(tmp_path, offline_embedder_spec: EmbedderSpec) -> KnowledgeConfig:
    # Keep dims small for fast tests.
    cfg = KnowledgeConfig(
        db_path=str(tmp_path / "chroma_db"),
        embedder=EmbedderConfig(
            provider="local",
            model=offline_embedder_spec.model,
            dimensions=offline_embedder_spec.dimensions,
            batch_size=100,
        ),
    )
    return cfg


def test_rag_end_to_end_grounded_context_offline(tmp_path, offline_config: KnowledgeConfig, offline_embedder_spec: EmbedderSpec):
    VectorStoreFactory.clear_instances()

    ingestion_embedder = DeterministicBaseEmbedder(spec=offline_embedder_spec, batch_size=100)
    ingestion_service = KnowledgeIngestionService(config=offline_config, embedder=ingestion_embedder)

    # Ingest a short "uploaded" document into the personal store.
    ingested = ingestion_service.ingest_text(
        text="Fall prevention bundle includes bed alarms, non-slip footwear, and hourly rounding.",
        doc_type="default",
        store_type="personal",
        source_type="personal",
        source_name="MyUpload.pdf",
        auto_commit=True,
    )
    assert ingested.success is True
    assert ingested.committed is True

    # Retrieval embedder must match the same embedding space.
    retrieval_embedder = DeterministicAgnoEmbedder(
        model_id=offline_embedder_spec.model,
        dimensions=offline_embedder_spec.dimensions,
    )

    enhancer = RAGEnhancer(cache_ttl=0, db_path=offline_config.db_path, embedder=retrieval_embedder)
    grounded = enhancer.get_grounded_context(
        query="fall prevention hourly rounding",
        agent_hint="general",
        n_results=2,
        use_cache=False,
    )

    ctx = grounded.get("context", "")
    assert "[[SOURCE:" in ctx
    assert "MyUpload.pdf" in ctx  # SOURCE label should include the filename

    results = grounded.get("results", [])
    assert results

    grounding = enhancer.extract_grounding_metadata(results)
    assert "MyUpload.pdf" in grounding.get("filenames", [])

