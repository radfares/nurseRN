"""
Unit Tests for Enhanced Vector Store
Phase 1 - Task 1.2 Validation

Created: 2025-12-15
"""

import pytest
from src.knowledge.vector_store import (
    # Constants
    COLLECTION_PERSONAL,
    COLLECTION_CLINICAL,
    COLLECTION_PROCEDURAL,
    COLLECTION_RESEARCH,
    # Classes
    PersonalLibraryVectorStore,
    ClinicalKnowledgeStore,
    ProceduralKnowledgeStore,
    ResearchCacheStore,
    VectorStoreFactory,
)


class TestCollectionConstants:
    """Tests for collection name constants."""

    def test_clinical_constant_exists(self):
        """Verify COLLECTION_CLINICAL constant exists."""
        assert COLLECTION_CLINICAL == "clinical_knowledge"

    def test_procedural_constant_exists(self):
        """Verify COLLECTION_PROCEDURAL constant exists."""
        assert COLLECTION_PROCEDURAL == "procedural_knowledge"

    def test_research_constant_exists(self):
        """Verify COLLECTION_RESEARCH constant exists."""
        assert COLLECTION_RESEARCH == "research_cache"

    def test_personal_constant_unchanged(self):
        """Verify existing COLLECTION_PERSONAL is unchanged."""
        assert COLLECTION_PERSONAL == "personal_docs"


class TestClinicalKnowledgeStore:
    """Tests for ClinicalKnowledgeStore class."""

    def test_instantiation(self):
        """Test ClinicalKnowledgeStore can be instantiated."""
        store = ClinicalKnowledgeStore(db_path="data/test_chroma")
        assert store is not None
        assert store.collection_name == COLLECTION_CLINICAL

    def test_inherits_from_personal_library(self):
        """Test ClinicalKnowledgeStore inherits from PersonalLibraryVectorStore."""
        store = ClinicalKnowledgeStore(db_path="data/test_chroma")
        assert isinstance(store, PersonalLibraryVectorStore)

    def test_has_search_method(self):
        """Test ClinicalKnowledgeStore has search method from parent."""
        store = ClinicalKnowledgeStore(db_path="data/test_chroma")
        assert callable(getattr(store, 'search', None))

    def test_has_add_chunks_method(self):
        """Test ClinicalKnowledgeStore has add_chunks method from parent."""
        store = ClinicalKnowledgeStore(db_path="data/test_chroma")
        assert callable(getattr(store, 'add_chunks', None))


class TestProceduralKnowledgeStore:
    """Tests for ProceduralKnowledgeStore class."""

    def test_instantiation(self):
        """Test ProceduralKnowledgeStore can be instantiated."""
        store = ProceduralKnowledgeStore(db_path="data/test_chroma")
        assert store is not None
        assert store.collection_name == COLLECTION_PROCEDURAL

    def test_inherits_from_personal_library(self):
        """Test ProceduralKnowledgeStore inherits from PersonalLibraryVectorStore."""
        store = ProceduralKnowledgeStore(db_path="data/test_chroma")
        assert isinstance(store, PersonalLibraryVectorStore)


class TestResearchCacheStore:
    """Tests for ResearchCacheStore class."""

    def test_instantiation(self):
        """Test ResearchCacheStore can be instantiated."""
        store = ResearchCacheStore(db_path="data/test_chroma")
        assert store is not None
        assert store.collection_name == COLLECTION_RESEARCH

    def test_inherits_from_personal_library(self):
        """Test ResearchCacheStore inherits from PersonalLibraryVectorStore."""
        store = ResearchCacheStore(db_path="data/test_chroma")
        assert isinstance(store, PersonalLibraryVectorStore)


class TestVectorStoreFactory:
    """Tests for VectorStoreFactory class."""

    def setup_method(self):
        """Clear factory cache before each test."""
        VectorStoreFactory.clear_instances()

    def test_get_clinical_store(self):
        """Test factory returns ClinicalKnowledgeStore for 'clinical' type."""
        store = VectorStoreFactory.get_store("clinical", db_path="data/test_chroma")
        assert isinstance(store, ClinicalKnowledgeStore)
        assert store.collection_name == COLLECTION_CLINICAL

    def test_get_procedural_store(self):
        """Test factory returns ProceduralKnowledgeStore for 'procedural' type."""
        store = VectorStoreFactory.get_store("procedural", db_path="data/test_chroma")
        assert isinstance(store, ProceduralKnowledgeStore)
        assert store.collection_name == COLLECTION_PROCEDURAL

    def test_get_research_store(self):
        """Test factory returns ResearchCacheStore for 'research' type."""
        store = VectorStoreFactory.get_store("research", db_path="data/test_chroma")
        assert isinstance(store, ResearchCacheStore)
        assert store.collection_name == COLLECTION_RESEARCH

    def test_get_personal_store(self):
        """Test factory returns PersonalLibraryVectorStore for 'personal' type."""
        store = VectorStoreFactory.get_store("personal", db_path="data/test_chroma")
        assert isinstance(store, PersonalLibraryVectorStore)
        assert store.collection_name == COLLECTION_PERSONAL

    def test_invalid_store_type_raises(self):
        """Test factory raises ValueError for unknown store type."""
        with pytest.raises(ValueError) as exc_info:
            VectorStoreFactory.get_store("invalid_type")
        assert "Unknown store type" in str(exc_info.value)

    def test_caching_returns_same_instance(self):
        """Test factory returns cached instance on second call."""
        store1 = VectorStoreFactory.get_store("clinical", db_path="data/test_chroma")
        store2 = VectorStoreFactory.get_store("clinical", db_path="data/test_chroma")
        assert store1 is store2

    def test_force_new_creates_new_instance(self):
        """Test force_new=True creates new instance."""
        store1 = VectorStoreFactory.get_store("clinical", db_path="data/test_chroma")
        store2 = VectorStoreFactory.get_store("clinical", db_path="data/test_chroma", force_new=True)
        assert store1 is not store2

    def test_get_available_types(self):
        """Test get_available_types returns all registered types."""
        types = VectorStoreFactory.get_available_types()
        assert "personal" in types
        assert "clinical" in types
        assert "procedural" in types
        assert "research" in types

    def test_clear_instances(self):
        """Test clear_instances removes all cached stores."""
        VectorStoreFactory.get_store("clinical", db_path="data/test_chroma")
        VectorStoreFactory.get_store("procedural", db_path="data/test_chroma")

        VectorStoreFactory.clear_instances()

        # After clearing, getting store should create new instance
        # We can verify by checking the internal _instances dict is empty
        assert len(VectorStoreFactory._instances) == 0
