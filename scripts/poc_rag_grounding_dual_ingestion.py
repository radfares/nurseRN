#!/usr/bin/env python3
"""
POC: Dual-ingestion vs retrieval behavior (no mocks).

This demonstrates (in the strict "proof of concept" sense):
1) Bypassing production ingestion (direct VectorStore.add_chunks) can create chunks
   without required metadata (e.g., is_active) which makes them invisible to default retrieval.
2) ClinicalDocumentIngestion now delegates to KnowledgeIngestionService (two-phase commit),
   producing chunks that are retrievable by default.
3) RAGEnhancer can return SOURCE-bound context blocks (`[[SOURCE: ...]] ...`) for safe citation.

Run:
  python scripts/poc_rag_grounding_dual_ingestion.py

Notes:
- This will call the configured OpenAI embeddings API to generate vectors.
- It writes to a NEW temp ChromaDB path under tmp/ so it won't touch your main DB.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env so the POC uses the same key config as the app
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    # If python-dotenv isn't installed, we'll rely on the shell env.
    pass

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _new_temp_db_path() -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(PROJECT_ROOT / "tmp" / "poc_rag_dual_ingestion" / stamp / "chroma_db")


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY is not set (and .env did not provide one).")
        print("   This POC requires real embeddings calls (no mocks).")
        print("   Fix: export OPENAI_API_KEY=...  OR put it in .env at the repo root.")
        return 2

    db_path = _new_temp_db_path()
    Path(db_path).mkdir(parents=True, exist_ok=True)

    text = (
        "Fall prevention bundle:\n"
        "- Use bed alarms for high-risk patients.\n"
        "- Non-slip footwear.\n"
        "- Hourly rounding.\n"
        "- Clear clutter and ensure call light is within reach.\n"
    )
    query = "fall prevention bed alarms hourly rounding"

    print("=" * 80)
    print("POC: Dual ingestion vs retrieval")
    print("=" * 80)
    print(f"Temp DB path: {db_path}")
    print()

    # ---------------------------------------------------------------------
    # 1) Bypass production ingestion (direct add_chunks) -> can be invisible
    # ---------------------------------------------------------------------
    print("[1] Direct VectorStore.add_chunks (bypass) → may be invisible due to is_active filter")
    from src.knowledge.vector_store import VectorStoreFactory
    from src.knowledge.document_ingester import ChunkRecord

    VectorStoreFactory.clear_instances()
    store = VectorStoreFactory.get_store("clinical", db_path=db_path, force_new=True)

    # Insert a chunk without is_active metadata (bypass the ingestion service).
    bypass_chunk = ChunkRecord(
        doc_id="poc_bypass_doc",
        chunk_id="poc_bypass_doc_chunk_0001",
        text=text,
        source_path="poc_bypass_source.txt",
        source_type="clinical",
        metadata={},
    )
    store.add_chunks([bypass_chunk])
    stats = store.get_stats()
    print(f"  collection={stats.get('collection_name')} chunk_count={stats.get('chunk_count')}")

    # Default search applies is_active=True filter.
    default_hits = store.search(query=query, limit=5)
    print(f"  default search hits (include_inactive=False): {len(default_hits)}")

    # Show that the data exists if we remove the filter.
    inactive_hits = store.search(query=query, limit=5, include_inactive=True)
    print(f"  search hits when include_inactive=True: {len(inactive_hits)}")
    if inactive_hits:
        meta = inactive_hits[0].metadata or {}
        print(f"  first_hit.has_is_active={'is_active' in meta} is_active={meta.get('is_active')}")
        print(f"  first_hit.source_path={inactive_hits[0].source_path!r}")

    print()

    # ---------------------------------------------------------------------
    # 2) ClinicalDocumentIngestion wrapper -> production-safe ingest
    # ---------------------------------------------------------------------
    print("[2] ClinicalDocumentIngestion (compat wrapper) → KnowledgeIngestionService (two-phase commit)")
    from src.knowledge.clinical_ingestion import ClinicalDocumentIngestion

    VectorStoreFactory.clear_instances()
    wrapper = ClinicalDocumentIngestion(db_path=db_path, default_doc_type="clinical")
    wrap_result = wrapper.ingest_text(text=text, doc_type="clinical", source_name="poc_clinical_ingestion_inline")
    print(f"  ingest_text.success={wrap_result.success} chunk_count={wrap_result.chunk_count}")

    store2 = VectorStoreFactory.get_store("clinical", db_path=db_path, force_new=True)
    default_hits_after = store2.search(query=query, limit=5)
    print(f"  default search hits after production ingest: {len(default_hits_after)}")
    if default_hits_after:
        meta2 = default_hits_after[0].metadata or {}
        print(f"  first_hit.has_is_active={'is_active' in meta2} is_active={meta2.get('is_active')}")
        print(f"  first_hit.doc_key={meta2.get('doc_key')!r}")
        print(f"  first_hit.ingestion_run_id={meta2.get('ingestion_run_id')!r}")

    print()

    # ---------------------------------------------------------------------
    # 3) Demonstrate SOURCE-bound grounded context from RAGEnhancer
    # ---------------------------------------------------------------------
    print("[3] RAGEnhancer.get_grounded_context() returns SOURCE-bound blocks")
    from src.services.rag_enhancement import RAGEnhancer

    enhancer = RAGEnhancer(cache_ttl=0, db_path=db_path)
    grounded = enhancer.get_grounded_context(query=query, agent_hint="nursing_research", n_results=2, use_cache=False)
    rag_results = grounded.get("results", []) or []
    grounding = enhancer.extract_grounding_metadata(rag_results)

    print(f"  rag_results.count={len(rag_results)}")
    if rag_results:
        print("  top result fields:")
        print(f"    source={rag_results[0].source!r}")
        print(f"    citation_id={rag_results[0].citation_id!r}")
        print(f"    source_path={rag_results[0].source_path!r}")

    print(f"  grounding.all_citations={grounding.get('all_citations', [])}")
    ctx = grounded.get("context", "")
    print("  grounded context preview:")
    preview = (ctx or "").replace("\n", " ")
    print(f"    {preview[:220]}...")

    print()
    print("POC complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
