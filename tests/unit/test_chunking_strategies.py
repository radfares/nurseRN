"""
Unit Tests for Chunking Strategies
Phase 1 - Task 1.1 Validation

Created: 2025-12-15
"""

import pytest
from src.knowledge.chunking_strategies import (
    ChunkResult,
    ChunkingStrategy,
    TokenBasedChunker,
    SemanticChunker,
    SentenceChunker,
    ChunkingFactory,
)


# Sample texts for testing
SAMPLE_SHORT_TEXT = "This is a short text for testing."

SAMPLE_PARAGRAPH_TEXT = """First paragraph with some content about clinical procedures.

Second paragraph discusses patient care protocols and safety measures.

Third paragraph covers documentation requirements and compliance standards."""

SAMPLE_MULTI_SENTENCE_TEXT = (
    "Step one: Assess the patient. "
    "Step two: Check vital signs. "
    "Step three: Document findings. "
    "Step four: Notify the physician. "
    "Step five: Administer medication. "
    "Step six: Monitor response. "
    "Step seven: Update records. "
    "Step eight: Discharge planning."
)


class TestChunkResult:
    """Tests for ChunkResult dataclass."""

    def test_chunk_result_creation(self):
        """Test ChunkResult can be instantiated with required fields."""
        chunk = ChunkResult(
            text="test text",
            start_idx=0,
            end_idx=9,
            token_count=2,
            metadata={"chunk_index": 0}
        )
        assert chunk.text == "test text"
        assert chunk.start_idx == 0
        assert chunk.end_idx == 9
        assert chunk.token_count == 2
        assert chunk.metadata["chunk_index"] == 0

    def test_chunk_result_default_metadata(self):
        """Test ChunkResult initializes empty metadata dict by default."""
        chunk = ChunkResult(
            text="test",
            start_idx=0,
            end_idx=4,
            token_count=1
        )
        assert chunk.metadata == {}


class TestTokenBasedChunker:
    """Tests for TokenBasedChunker."""

    def test_instantiation(self):
        """Test TokenBasedChunker can be instantiated."""
        chunker = TokenBasedChunker(token_limit=100, overlap=10)
        assert chunker.token_limit == 100
        assert chunker.overlap == 10

    def test_short_text_single_chunk(self):
        """Test short text returns single chunk."""
        chunker = TokenBasedChunker(token_limit=100, overlap=10)
        chunks = chunker.chunk(SAMPLE_SHORT_TEXT)

        assert len(chunks) == 1
        assert chunks[0].text == SAMPLE_SHORT_TEXT
        assert chunks[0].token_count > 0
        assert chunks[0].metadata["chunk_index"] == 0
        assert chunks[0].metadata["total_chunks"] == 1

    def test_long_text_multiple_chunks(self):
        """Test long text produces multiple chunks."""
        chunker = TokenBasedChunker(token_limit=20, overlap=5)
        chunks = chunker.chunk(SAMPLE_PARAGRAPH_TEXT)

        assert len(chunks) > 1
        # Verify metadata
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["chunk_index"] == i
            assert chunk.metadata["total_chunks"] == len(chunks)
            assert chunk.token_count > 0
            assert chunk.text  # Non-empty text

    def test_empty_text_returns_empty_list(self):
        """Test empty text returns empty list."""
        chunker = TokenBasedChunker()
        assert chunker.chunk("") == []
        assert chunker.chunk("   ") == []

    def test_token_count_positive(self):
        """Test all chunks have positive token counts."""
        chunker = TokenBasedChunker(token_limit=30, overlap=5)
        chunks = chunker.chunk(SAMPLE_PARAGRAPH_TEXT)

        for chunk in chunks:
            assert chunk.token_count > 0


class TestSemanticChunker:
    """Tests for SemanticChunker."""

    def test_instantiation(self):
        """Test SemanticChunker can be instantiated."""
        chunker = SemanticChunker(chunk_size=200, overlap=20)
        assert chunker.chunk_size == 200
        assert chunker.overlap == 20

    def test_paragraph_text_chunking(self):
        """Test paragraph-based text is chunked on semantic boundaries."""
        chunker = SemanticChunker(chunk_size=50, overlap=10)
        chunks = chunker.chunk(SAMPLE_PARAGRAPH_TEXT)

        assert len(chunks) >= 1
        # Verify metadata structure
        for i, chunk in enumerate(chunks):
            assert "chunk_index" in chunk.metadata
            assert "total_chunks" in chunk.metadata
            assert chunk.token_count > 0

    def test_short_text_single_chunk(self):
        """Test short text returns single chunk."""
        chunker = SemanticChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(SAMPLE_SHORT_TEXT)

        assert len(chunks) == 1
        assert chunks[0].metadata["total_chunks"] == 1

    def test_empty_text_returns_empty_list(self):
        """Test empty text returns empty list."""
        chunker = SemanticChunker()
        assert chunker.chunk("") == []


class TestSentenceChunker:
    """Tests for SentenceChunker."""

    def test_instantiation(self):
        """Test SentenceChunker can be instantiated."""
        chunker = SentenceChunker(sentences_per_chunk=3, overlap_sentences=1)
        assert chunker.sentences_per_chunk == 3
        assert chunker.overlap_sentences == 1

    def test_multi_sentence_chunking(self):
        """Test multi-sentence text is chunked correctly."""
        chunker = SentenceChunker(sentences_per_chunk=3, overlap_sentences=1)
        chunks = chunker.chunk(SAMPLE_MULTI_SENTENCE_TEXT)

        assert len(chunks) > 1
        # Verify metadata
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["chunk_index"] == i
            assert chunk.metadata["total_chunks"] == len(chunks)
            assert chunk.token_count > 0

    def test_short_text_single_chunk(self):
        """Test text with few sentences returns single chunk."""
        chunker = SentenceChunker(sentences_per_chunk=10, overlap_sentences=1)
        short_text = "First sentence. Second sentence."
        chunks = chunker.chunk(short_text)

        assert len(chunks) == 1
        assert chunks[0].metadata["total_chunks"] == 1

    def test_empty_text_returns_empty_list(self):
        """Test empty text returns empty list."""
        chunker = SentenceChunker()
        assert chunker.chunk("") == []


class TestChunkingFactory:
    """Tests for ChunkingFactory."""

    def test_get_clinical_chunker(self):
        """Test factory returns SemanticChunker for clinical docs."""
        chunker = ChunkingFactory.get_chunker("clinical")
        assert isinstance(chunker, SemanticChunker)

    def test_get_procedural_chunker(self):
        """Test factory returns SentenceChunker for procedural docs."""
        chunker = ChunkingFactory.get_chunker("procedural")
        assert isinstance(chunker, SentenceChunker)

    def test_get_research_chunker(self):
        """Test factory returns TokenBasedChunker for research docs."""
        chunker = ChunkingFactory.get_chunker("research")
        assert isinstance(chunker, TokenBasedChunker)

    def test_get_default_chunker(self):
        """Test factory returns TokenBasedChunker for unknown doc type."""
        chunker = ChunkingFactory.get_chunker("unknown_type")
        assert isinstance(chunker, TokenBasedChunker)

    def test_override_params(self):
        """Test factory accepts override parameters."""
        chunker = ChunkingFactory.get_chunker("research", token_limit=200)
        assert isinstance(chunker, TokenBasedChunker)
        assert chunker.token_limit == 200

    def test_all_chunkers_produce_valid_output(self):
        """Test all factory-created chunkers produce valid chunks."""
        doc_types = ["clinical", "procedural", "research", "default"]

        for doc_type in doc_types:
            chunker = ChunkingFactory.get_chunker(doc_type)
            chunks = chunker.chunk(SAMPLE_PARAGRAPH_TEXT)

            assert len(chunks) >= 1, f"{doc_type} chunker produced no chunks"
            for chunk in chunks:
                assert chunk.text, f"{doc_type} chunker produced empty text"
                assert chunk.token_count > 0, f"{doc_type} chunker produced zero tokens"
                assert "chunk_index" in chunk.metadata
                assert "total_chunks" in chunk.metadata
