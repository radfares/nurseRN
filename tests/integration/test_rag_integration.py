"""
Integration test for RAG Pipeline.
Verifies actual connection between RAGPipeline and VectorStore (no mocks).
"""

import pytest
import shutil
import os
from src.services.rag_pipeline import RAGPipeline
from src.knowledge.vector_store import VectorStoreFactory, ChunkRecord

@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary path for the vector DB."""
    path = tmp_path / "integration_db"
    yield str(path)
    # Cleanup (shutil.rmtree handled by tmp_path usually, but good to be explicit if needed)

def test_rag_vector_store_integration(temp_db_path):
    """
    Test the full flow:
    1. Initialize Vector Store (Phase 1)
    2. Add real data
    3. Initialize RAG Pipeline (Phase 2)
    4. Retrieve data (checking connection)
    """
    # 1. Setup Phase 1 Store
    store = VectorStoreFactory.get_store("clinical", db_path=temp_db_path, force_new=True)
    
    # 2. Add Data
    chunk = ChunkRecord(
        chunk_id="test_c1",
        doc_id="test_d1",
        text="The patient protocol for falling requires immediate vitals check.",
        source_path="/test/fall_protocol.pdf",
        metadata={"source": "protocol", "title": "Fall Protocol"}
    )
    store.add_chunks([chunk])
    
    # 3. Setup Phase 2 Pipeline (pointing to same DB)
    # RAGPipeline usually gets store from Factory. 
    # We must ensure Factory uses our temp path.
    # Since RAGPipeline calls VectorStoreFactory.get_store("clinical"), 
    # we need to ensure the factory yields the instance we just created or uses defaults.
    # IN CODE: RAGPipeline._search_local_stores calls get_store(s_type).
    # It relies on default path or cached instance.
    
    # For this test, we must inject our specific store instance into the Factory cache
    # to ensure the Pipeline uses our temporary DB, not the production one.
    VectorStoreFactory._instances[f"clinical:{temp_db_path}"] = store  # Pre-cache it if path matched
    
    # BUT wait, the pipeline in `_search_local_stores` calls `get_store(s_type)`.
    # It doesn't pass a custom db_path. So it will look for `get_store("clinical", db_path="data/chroma_db")`.
    # WE NEED TO PATCH THE PIPELINE OR THE FACTORY TO USE OUR TEMP DB.
    
    # Let's perform a patch on the Factory just to redirect the path for this test process
    with pytest.MonkeyPatch.context() as m:
        # We wrap the get_store to always return our temp store if "clinical" is asked
        original_get_store = VectorStoreFactory.get_store
        
        def side_effect_get_store(store_type, **kwargs):
             if store_type == "clinical":
                 return store
             return original_get_store(store_type, **kwargs)
             
        m.setattr(VectorStoreFactory, "get_store", side_effect_get_store)
        
        # 4. Run Pipeline
        pipeline = RAGPipeline()
        results = pipeline.retrieve("falling protocol", agent_hint="clinical", limit=1)
        
        # 5. Verify
        assert len(results) >= 1, f"Expected at least 1 result, got {len(results)}"
        # Find our test data in the results
        clinical_results = [r for r in results if "immediate vitals check" in r.content]
        assert len(clinical_results) >= 1, "Clinical test data not found in results"
        assert clinical_results[0].source == "Local Store (Clinical)"
