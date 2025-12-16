# RAG Implementation Plan - 5 Phase Execution Guide

> **Document Version:** 1.0
> **Created:** 2025-12-15
> **Author:** Senior Software Architect
> **Project:** nurseRN Multi-Agent Research System

---

## Executive Summary

This document provides a **5-phase implementation plan** for integrating Retrieval-Augmented Generation (RAG) capabilities into the nurseRN project. Each phase includes:

- Step-by-step instructions
- Checklists
- Dependencies and prerequisites
- Validation gates
- Test procedures

**CRITICAL RULE**: Per `CLAUDE.md` - DO NOT proceed to the next phase without explicit user approval.

---

## Current State Analysis

### Existing Infrastructure (Verified 2025-12-15)

| Component | File | Status |
|-----------|------|--------|
| Vector Store | `src/knowledge/vector_store.py` | EXISTS - PersonalLibraryVectorStore (ChromaDB) |
| Document Ingester | `src/knowledge/document_ingester.py` | EXISTS - DocumentIngester with RecursiveChunking |
| Orchestrator | `src/orchestration/orchestrator.py` | EXISTS - WorkflowOrchestrator with MCP |
| Context Manager | `src/orchestration/context_manager.py` | EXISTS - State management |
| Embedder | agno.knowledge.embedder.openai | EXISTS - OpenAIEmbedder |

### Existing Collections (Defined in vector_store.py)

```python
COLLECTION_PERSONAL = "personal_docs"     # ACTIVE
COLLECTION_PUBMED_CACHE = "pubmed_cache"  # Phase C (placeholder)
COLLECTION_ARXIV_CACHE = "arxiv_cache"    # Phase C (placeholder)
COLLECTION_COMBINED = "combined_index"     # Phase C (placeholder)
```

### Key Dependencies (from requirements.txt)

- `openai>=1.0.0` - LLM and embeddings
- `tenacity>=8.0.0` - Retry logic
- `sentence-transformers>=2.2.0` - Embedding models
- `biopython>=1.80` - PubMed search
- agno framework (vendored in `libs/agno`)

---

## Phase Overview

| Phase | Name | Focus | Risk Level |
|-------|------|-------|------------|
| 1 | Foundation Enhancement | Extend vector store, add chunking strategies | Low |
| 2 | RAG Pipeline Core | Create retrieval + generation pipeline | Medium |
| 3 | Agent RAG Integration | Integrate RAG into specialized agents | Medium |
| 4 | Orchestrator & Coordination | Wire up complete workflow | Medium-High |
| 5 | Validation & Optimization | End-to-end testing, performance tuning | Low |

---

# PHASE 1: Foundation Enhancement

## Objective
Enhance the existing vector store infrastructure and add flexible chunking strategies to support multiple knowledge domains (clinical, procedural, research).

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] OpenAI API key configured in `.env`
- [ ] ChromaDB storage directory exists: `data/chroma_db/`

## Dependencies

```bash
# Verify existing dependencies
pip install openai tiktoken tenacity

# Verify agno framework is accessible
python -c "from agno.vectordb.chroma.chromadb import ChromaDb; print('OK')"
```

## Tasks

### Task 1.1: Create Chunking Strategies Module

**File:** `src/knowledge/chunking_strategies.py`

**Purpose:** Provide multiple chunking strategies optimized for different document types.

**Implementation Steps:**

1. [ ] Create file at `src/knowledge/chunking_strategies.py`
2. [ ] Implement `SemanticChunker` class (for clinical documents)
3. [ ] Implement `TokenBasedChunker` class (for precise token control)
4. [ ] Implement `SentenceChunker` class (for procedural documents)
5. [ ] Add `ChunkingFactory` to select strategy based on document type
6. [ ] Add unit tests

**Code Specification:**

```python
# chunking_strategies.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import tiktoken

@dataclass
class ChunkResult:
    """Result of chunking operation."""
    text: str
    start_idx: int
    end_idx: int
    token_count: int
    metadata: Dict[str, Any]

class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """Chunk text into smaller pieces."""
        pass

class SemanticChunker(ChunkingStrategy):
    """Chunk based on semantic boundaries (paragraphs, sections)."""
    # Implementation here

class TokenBasedChunker(ChunkingStrategy):
    """Chunk based on token count with overlap."""
    # Implementation here

class SentenceChunker(ChunkingStrategy):
    """Chunk based on sentence boundaries."""
    # Implementation here

class ChunkingFactory:
    """Factory to create appropriate chunker based on document type."""

    @staticmethod
    def get_chunker(doc_type: str) -> ChunkingStrategy:
        strategies = {
            "clinical": SemanticChunker(chunk_size=500, overlap=50),
            "procedural": SentenceChunker(sentences_per_chunk=5),
            "research": TokenBasedChunker(token_limit=400, overlap=50),
            "default": TokenBasedChunker(token_limit=400, overlap=50),
        }
        return strategies.get(doc_type, strategies["default"])
```

**Validation Gate 1.1:**
- [ ] File exists at `src/knowledge/chunking_strategies.py`
- [ ] All classes are importable
- [ ] Unit test passes: `pytest tests/unit/test_chunking_strategies.py -v`

---

### Task 1.2: Enhance Vector Store with Multiple Collections

**File:** `src/knowledge/vector_store.py`

**Purpose:** Add support for clinical knowledge, procedural knowledge, and research collections.

**Implementation Steps:**

1. [ ] Add new collection constants
2. [ ] Create `ClinicalKnowledgeStore` class (extends PersonalLibraryVectorStore)
3. [ ] Create `ProceduralKnowledgeStore` class
4. [ ] Create `ResearchCacheStore` class
5. [ ] Add `VectorStoreFactory` to manage multiple stores
6. [ ] Add namespace/collection switching methods

**Code Specification (additions to vector_store.py):**

```python
# New collection constants
COLLECTION_CLINICAL = "clinical_knowledge"
COLLECTION_PROCEDURAL = "procedural_knowledge"
COLLECTION_RESEARCH = "research_cache"

class ClinicalKnowledgeStore(PersonalLibraryVectorStore):
    """Vector store for clinical knowledge (facts, guidelines)."""

    def __init__(self, db_path: str = "data/chroma_db"):
        super().__init__(
            collection_name=COLLECTION_CLINICAL,
            db_path=db_path
        )

class ProceduralKnowledgeStore(PersonalLibraryVectorStore):
    """Vector store for procedural knowledge (protocols, workflows)."""

    def __init__(self, db_path: str = "data/chroma_db"):
        super().__init__(
            collection_name=COLLECTION_PROCEDURAL,
            db_path=db_path
        )

class VectorStoreFactory:
    """Factory to create and manage multiple vector stores."""

    _instances: Dict[str, PersonalLibraryVectorStore] = {}

    @classmethod
    def get_store(cls, store_type: str, db_path: str = "data/chroma_db"):
        """Get or create a vector store instance."""
        pass  # Implementation
```

**Validation Gate 1.2:**
- [ ] New classes are defined and importable
- [ ] Each store creates separate ChromaDB collection
- [ ] Unit test passes: `pytest tests/unit/test_vector_store_enhanced.py -v`

---

### Task 1.3: Create Data Ingestion Enhancements

**File:** `src/knowledge/clinical_ingestion.py`

**Purpose:** Specialized ingestion pipeline for clinical data sources.

**Implementation Steps:**

1. [ ] Create `ClinicalDataIngester` class
2. [ ] Implement metadata extraction for clinical documents
3. [ ] Add citation extraction helpers
4. [ ] Implement batch ingestion with progress tracking

**Validation Gate 1.3:**
- [ ] File exists and is importable
- [ ] Can ingest a sample clinical document
- [ ] Metadata is properly extracted and stored

---

## Phase 1 Testing Protocol

### Test File: `tests/unit/test_phase1.py`

```python
"""Phase 1 Validation Tests"""
import pytest

class TestPhase1Foundation:

    def test_chunking_strategies_import(self):
        """Verify chunking strategies module is importable."""
        from src.knowledge.chunking_strategies import (
            ChunkingStrategy,
            SemanticChunker,
            TokenBasedChunker,
            SentenceChunker,
            ChunkingFactory
        )
        assert ChunkingFactory is not None

    def test_semantic_chunker_basic(self):
        """Test semantic chunker produces valid chunks."""
        from src.knowledge.chunking_strategies import SemanticChunker
        chunker = SemanticChunker(chunk_size=100, overlap=20)
        text = "This is a test paragraph.\n\nThis is another paragraph with more content."
        chunks = chunker.chunk(text)
        assert len(chunks) > 0
        assert all(c.token_count > 0 for c in chunks)

    def test_vector_store_factory(self):
        """Test vector store factory creates correct store types."""
        from src.knowledge.vector_store import VectorStoreFactory, ClinicalKnowledgeStore
        store = VectorStoreFactory.get_store("clinical")
        assert isinstance(store, ClinicalKnowledgeStore)

    def test_collections_exist(self):
        """Verify all required collections can be created."""
        from src.knowledge.vector_store import (
            ClinicalKnowledgeStore,
            ProceduralKnowledgeStore,
            PersonalLibraryVectorStore
        )
        # Test instantiation (not actual DB operations)
        clinical = ClinicalKnowledgeStore(db_path="data/test_chroma")
        procedural = ProceduralKnowledgeStore(db_path="data/test_chroma")
        personal = PersonalLibraryVectorStore(db_path="data/test_chroma")
        assert clinical.collection_name == "clinical_knowledge"
        assert procedural.collection_name == "procedural_knowledge"
```

### Run Tests

```bash
# Run Phase 1 tests
pytest tests/unit/test_phase1.py -v --tb=short

# Run with coverage
pytest tests/unit/test_phase1.py -v --cov=src/knowledge --cov-report=term-missing
```

## Phase 1 Completion Checklist

- [ ] `chunking_strategies.py` created and tested
- [ ] Vector store enhanced with new collection classes
- [ ] `clinical_ingestion.py` created
- [ ] All unit tests pass
- [ ] Code coverage > 80% for new code
- [ ] No linting errors: `ruff check src/knowledge/`

**STOP: Wait for user approval before proceeding to Phase 2**

---

# PHASE 2: RAG Pipeline Core

## Objective
Create the core RAG pipeline that combines retrieval and generation into a unified interface.

## Prerequisites Checklist

- [ ] Phase 1 completed and approved
- [ ] All Phase 1 tests passing
- [ ] OpenAI API key valid and working

## Dependencies

```bash
# Verify OpenAI is working
python -c "from openai import OpenAI; print('OK')"
```

## Tasks

### Task 2.1: Create RAG Pipeline Module

**File:** `src/rag/rag_pipeline.py`

**Purpose:** Core RAG pipeline combining retrieval and generation.

**Implementation Steps:**

1. [ ] Create directory: `src/rag/`
2. [ ] Create `__init__.py`
3. [ ] Create `rag_pipeline.py`
4. [ ] Implement `RAGPipeline` class with retrieve/generate methods
5. [ ] Add context window management
6. [ ] Implement result ranking and filtering

**Code Specification:**

```python
# src/rag/rag_pipeline.py

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

from src.knowledge.vector_store import PersonalLibraryVectorStore, SearchResult

logger = logging.getLogger(__name__)

@dataclass
class RAGResponse:
    """Response from RAG pipeline."""
    answer: str
    sources: List[SearchResult]
    confidence: float
    metadata: Dict[str, Any]

class RAGPipeline:
    """
    Retrieval-Augmented Generation Pipeline.

    Combines vector store retrieval with LLM generation.
    """

    def __init__(
        self,
        vector_store: PersonalLibraryVectorStore,
        llm_model: str = "gpt-4o-mini",
        top_k: int = 5,
        min_relevance_score: float = 0.3
    ):
        self.vector_store = vector_store
        self.llm_model = llm_model
        self.top_k = top_k
        self.min_relevance_score = min_relevance_score
        self._client = None

    def retrieve(self, query: str, filters: Optional[Dict] = None) -> List[SearchResult]:
        """Retrieve relevant documents from vector store."""
        results = self.vector_store.search(
            query=query,
            limit=self.top_k,
            filters=filters
        )
        # Filter by minimum relevance
        return [r for r in results if r.score >= self.min_relevance_score]

    def generate(
        self,
        query: str,
        context: List[SearchResult],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using LLM with retrieved context."""
        # Build context string
        context_text = "\n\n".join([
            f"[Source: {r.filename}, Page: {r.page_num}]\n{r.text}"
            for r in context
        ])

        # Default system prompt for clinical assistant
        if system_prompt is None:
            system_prompt = """You are a clinical research assistant.
            Answer questions based on the provided context.
            Cite sources when making claims.
            If the context doesn't contain relevant information, say so."""

        # Call LLM
        # Implementation using OpenAI client
        pass

    def query(self, query: str, **kwargs) -> RAGResponse:
        """
        Full RAG query: retrieve context and generate response.

        Args:
            query: User question
            **kwargs: Additional parameters for retrieval/generation

        Returns:
            RAGResponse with answer, sources, and metadata
        """
        # 1. Retrieve
        sources = self.retrieve(query, filters=kwargs.get("filters"))

        # 2. Generate
        answer = self.generate(
            query=query,
            context=sources,
            system_prompt=kwargs.get("system_prompt")
        )

        # 3. Calculate confidence based on source relevance
        avg_score = sum(s.score for s in sources) / len(sources) if sources else 0

        return RAGResponse(
            answer=answer,
            sources=sources,
            confidence=avg_score,
            metadata={
                "model": self.llm_model,
                "num_sources": len(sources),
                "query": query
            }
        )
```

**Validation Gate 2.1:**
- [ ] `src/rag/` directory exists
- [ ] `RAGPipeline` class is importable
- [ ] `retrieve()` method returns `List[SearchResult]`
- [ ] `generate()` method returns string
- [ ] `query()` method returns `RAGResponse`

---

### Task 2.2: Create LLM Wrapper Module

**File:** `src/rag/llm_wrapper.py`

**Purpose:** Unified interface for LLM interactions with retry logic and error handling.

**Implementation Steps:**

1. [ ] Create `LLMWrapper` class
2. [ ] Add OpenAI integration
3. [ ] Implement retry logic with tenacity
4. [ ] Add token counting and context window management
5. [ ] Add response caching (optional)

**Code Specification:**

```python
# src/rag/llm_wrapper.py

from typing import List, Dict, Optional
from dataclasses import dataclass
import tiktoken
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    finish_reason: str

class LLMWrapper:
    """Wrapper for LLM interactions with retry logic."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        max_tokens: int = 4096
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=api_key)
        self._tokenizer = tiktoken.encoding_for_model(model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._tokenizer.encode(text))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response from LLM."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=self.max_tokens
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason
        )
```

**Validation Gate 2.2:**
- [ ] `LLMWrapper` class is importable
- [ ] `count_tokens()` returns accurate count
- [ ] `generate()` successfully calls OpenAI API (mock in tests)
- [ ] Retry logic works on transient failures

---

### Task 2.3: Create Embedding Manager

**File:** `src/rag/embedding_manager.py`

**Purpose:** Centralized embedding management with caching.

**Implementation Steps:**

1. [ ] Create `EmbeddingManager` class
2. [ ] Integrate with agno's OpenAIEmbedder
3. [ ] Add embedding caching
4. [ ] Add batch embedding support

**Validation Gate 2.3:**
- [ ] Can generate embeddings for text
- [ ] Batch embedding works efficiently
- [ ] Caching reduces redundant API calls

---

## Phase 2 Testing Protocol

### Test File: `tests/unit/test_phase2.py`

```python
"""Phase 2 Validation Tests"""
import pytest
from unittest.mock import Mock, patch

class TestPhase2RAGPipeline:

    def test_rag_pipeline_import(self):
        """Verify RAG pipeline is importable."""
        from src.rag.rag_pipeline import RAGPipeline, RAGResponse
        assert RAGPipeline is not None
        assert RAGResponse is not None

    def test_retrieve_returns_search_results(self):
        """Test retrieve method returns proper results."""
        from src.rag.rag_pipeline import RAGPipeline
        from src.knowledge.vector_store import PersonalLibraryVectorStore

        # Mock vector store
        mock_store = Mock(spec=PersonalLibraryVectorStore)
        mock_store.search.return_value = []

        pipeline = RAGPipeline(vector_store=mock_store)
        results = pipeline.retrieve("test query")

        assert isinstance(results, list)
        mock_store.search.assert_called_once()

    @patch('src.rag.llm_wrapper.OpenAI')
    def test_llm_wrapper_generate(self, mock_openai):
        """Test LLM wrapper generates response."""
        from src.rag.llm_wrapper import LLMWrapper, LLMResponse

        # Setup mock
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.total_tokens = 100

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        wrapper = LLMWrapper()
        response = wrapper.generate("system", "user")

        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
```

### Run Tests

```bash
# Run Phase 2 tests
pytest tests/unit/test_phase2.py -v --tb=short

# Run integration test with real API (requires API key)
pytest tests/integration/test_rag_integration.py -v --tb=short -m "not slow"
```

## Phase 2 Completion Checklist

- [ ] `src/rag/rag_pipeline.py` created and tested
- [ ] `src/rag/llm_wrapper.py` created and tested
- [ ] `src/rag/embedding_manager.py` created and tested
- [ ] All unit tests pass
- [ ] Integration test with mock API passes
- [ ] RAG query returns properly formatted response

**STOP: Wait for user approval before proceeding to Phase 3**

---

# PHASE 3: Agent RAG Integration

## Objective
Integrate RAG capabilities into specialized agents (Researcher, Validator, Clinician).

## Prerequisites Checklist

- [ ] Phase 2 completed and approved
- [ ] All Phase 2 tests passing
- [ ] RAG pipeline functioning correctly

## Tasks

### Task 3.1: Create RAG-Enhanced Researcher Agent

**File:** `src/agents/rag_researcher.py`

**Purpose:** Researcher agent that uses RAG to retrieve factual knowledge.

**Implementation Steps:**

1. [ ] Create `RAGResearcherAgent` class
2. [ ] Integrate with RAG pipeline
3. [ ] Implement `retrieve_facts()` method
4. [ ] Add source attribution tracking
5. [ ] Implement confidence scoring

**Code Specification:**

```python
# src/agents/rag_researcher.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from src.rag.rag_pipeline import RAGPipeline, RAGResponse
from src.knowledge.vector_store import VectorStoreFactory

logger = logging.getLogger(__name__)

@dataclass
class ResearchFinding:
    """A research finding with source attribution."""
    claim: str
    evidence: str
    source: str
    confidence: float
    page_reference: Optional[int] = None

class RAGResearcherAgent:
    """
    Researcher agent with RAG capabilities.

    Retrieves factual knowledge from clinical databases
    and provides source-attributed findings.
    """

    agent_name = "RAGResearcher"

    def __init__(
        self,
        rag_pipeline: Optional[RAGPipeline] = None,
        knowledge_store_type: str = "clinical"
    ):
        if rag_pipeline is None:
            store = VectorStoreFactory.get_store(knowledge_store_type)
            self.rag_pipeline = RAGPipeline(vector_store=store)
        else:
            self.rag_pipeline = rag_pipeline

    def retrieve_facts(
        self,
        query: str,
        min_confidence: float = 0.5
    ) -> List[ResearchFinding]:
        """
        Retrieve factual findings for a query.

        Args:
            query: Research question
            min_confidence: Minimum confidence threshold

        Returns:
            List of ResearchFinding objects with source attribution
        """
        response = self.rag_pipeline.query(query)

        findings = []
        for source in response.sources:
            if source.score >= min_confidence:
                finding = ResearchFinding(
                    claim=query,
                    evidence=source.text,
                    source=source.filename,
                    confidence=source.score,
                    page_reference=source.page_num
                )
                findings.append(finding)

        return findings

    def run(self, query: str, **kwargs) -> str:
        """
        Execute agent and return formatted response.

        This method is called by the WorkflowOrchestrator.
        """
        findings = self.retrieve_facts(query)

        if not findings:
            return f"No relevant findings for: {query}"

        # Format response
        response_parts = [f"Research findings for: {query}\n"]
        for i, f in enumerate(findings, 1):
            response_parts.append(
                f"\n{i}. [Confidence: {f.confidence:.2f}]\n"
                f"   Source: {f.source} (p. {f.page_reference})\n"
                f"   Evidence: {f.evidence[:200]}..."
            )

        return "\n".join(response_parts)
```

**Validation Gate 3.1:**
- [ ] `RAGResearcherAgent` is importable
- [ ] `retrieve_facts()` returns `List[ResearchFinding]`
- [ ] `run()` method works with WorkflowOrchestrator
- [ ] Source attribution is accurate

---

### Task 3.2: Create RAG-Enhanced Validator Agent

**File:** `src/agents/rag_validator.py`

**Purpose:** Validator agent that fact-checks claims against evidence.

**Implementation Steps:**

1. [ ] Create `RAGValidatorAgent` class
2. [ ] Implement `validate_claim()` method
3. [ ] Add evidence scoring logic
4. [ ] Implement contradiction detection

**Code Specification:**

```python
# src/agents/rag_validator.py

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from src.rag.rag_pipeline import RAGPipeline

class ValidationResult(Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    PARTIALLY_SUPPORTED = "partially_supported"

@dataclass
class ClaimValidation:
    """Result of claim validation."""
    claim: str
    result: ValidationResult
    confidence: float
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    explanation: str

class RAGValidatorAgent:
    """
    Validator agent that fact-checks claims against evidence.
    """

    agent_name = "RAGValidator"

    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        # Initialize with clinical knowledge store
        pass

    def validate_claim(
        self,
        claim: str,
        min_evidence_count: int = 2
    ) -> ClaimValidation:
        """
        Validate a claim against retrieved evidence.

        Args:
            claim: The claim to validate
            min_evidence_count: Minimum sources needed for validation

        Returns:
            ClaimValidation with result and evidence
        """
        # Implementation
        pass

    def run(self, claim: str, **kwargs) -> str:
        """Execute agent for orchestrator integration."""
        validation = self.validate_claim(claim)
        return f"Validation: {validation.result.value} (confidence: {validation.confidence:.2f})"
```

**Validation Gate 3.2:**
- [ ] `RAGValidatorAgent` is importable
- [ ] `validate_claim()` returns `ClaimValidation`
- [ ] Correctly identifies supported vs contradicted claims
- [ ] Works with WorkflowOrchestrator

---

### Task 3.3: Create RAG-Enhanced Clinician Agent

**File:** `src/agents/rag_clinician.py`

**Purpose:** Clinician agent that retrieves procedural knowledge (protocols, guidelines).

**Implementation Steps:**

1. [ ] Create `RAGClinicianAgent` class
2. [ ] Implement `retrieve_protocols()` method
3. [ ] Add step-by-step extraction logic
4. [ ] Implement safety warning detection

**Code Specification:**

```python
# src/agents/rag_clinician.py

from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ClinicalProtocol:
    """A clinical protocol or procedure."""
    name: str
    steps: List[str]
    warnings: List[str]
    source: str
    confidence: float

class RAGClinicianAgent:
    """
    Clinician agent that retrieves procedural knowledge.
    """

    agent_name = "RAGClinician"

    def retrieve_protocols(
        self,
        query: str,
        include_warnings: bool = True
    ) -> List[ClinicalProtocol]:
        """Retrieve clinical protocols for a procedure."""
        pass

    def run(self, query: str, **kwargs) -> str:
        """Execute agent for orchestrator integration."""
        pass
```

**Validation Gate 3.3:**
- [ ] `RAGClinicianAgent` is importable
- [ ] `retrieve_protocols()` returns `List[ClinicalProtocol]`
- [ ] Safety warnings are properly extracted
- [ ] Works with WorkflowOrchestrator

---

## Phase 3 Testing Protocol

### Test File: `tests/unit/test_phase3.py`

```python
"""Phase 3 Validation Tests"""
import pytest
from unittest.mock import Mock, patch

class TestPhase3AgentIntegration:

    def test_researcher_agent_import(self):
        """Verify RAG researcher agent is importable."""
        from src.agents.rag_researcher import RAGResearcherAgent, ResearchFinding
        assert RAGResearcherAgent is not None

    def test_researcher_retrieve_facts(self):
        """Test researcher retrieves facts with attribution."""
        from src.agents.rag_researcher import RAGResearcherAgent

        # Mock RAG pipeline
        mock_pipeline = Mock()
        mock_pipeline.query.return_value = Mock(
            sources=[Mock(text="Test evidence", filename="test.pdf", score=0.9, page_num=5)]
        )

        agent = RAGResearcherAgent(rag_pipeline=mock_pipeline)
        findings = agent.retrieve_facts("test query")

        assert len(findings) > 0
        assert findings[0].source == "test.pdf"

    def test_validator_agent_validation(self):
        """Test validator validates claims correctly."""
        from src.agents.rag_validator import RAGValidatorAgent, ValidationResult

        # Test with mock
        # Implementation
        pass

    def test_clinician_agent_protocols(self):
        """Test clinician retrieves protocols."""
        from src.agents.rag_clinician import RAGClinicianAgent

        # Test with mock
        # Implementation
        pass

    def test_agents_work_with_orchestrator(self):
        """Test all agents integrate with WorkflowOrchestrator."""
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.orchestration.context_manager import ContextManager
        from src.agents.rag_researcher import RAGResearcherAgent

        # Verify run() method signature compatibility
        agent = RAGResearcherAgent()
        assert callable(getattr(agent, 'run', None))
        assert hasattr(agent, 'agent_name')
```

### Run Tests

```bash
# Run Phase 3 tests
pytest tests/unit/test_phase3.py -v --tb=short
```

## Phase 3 Completion Checklist

- [ ] `rag_researcher.py` created and tested
- [ ] `rag_validator.py` created and tested
- [ ] `rag_clinician.py` created and tested
- [ ] All agents have compatible `run()` method
- [ ] All agents have `agent_name` attribute
- [ ] All unit tests pass

**STOP: Wait for user approval before proceeding to Phase 4**

---

# PHASE 4: Orchestrator & Coordination

## Objective
Wire up the complete RAG workflow with orchestrator coordination and MCP integration.

## Prerequisites Checklist

- [ ] Phase 3 completed and approved
- [ ] All RAG agents functioning correctly
- [ ] WorkflowOrchestrator tested

## Tasks

### Task 4.1: Create RAG Orchestrator

**File:** `src/orchestration/rag_orchestrator.py`

**Purpose:** Specialized orchestrator for RAG workflows.

**Implementation Steps:**

1. [ ] Create `RAGOrchestrator` class
2. [ ] Implement multi-agent RAG workflow
3. [ ] Add result aggregation with source deduplication
4. [ ] Implement confidence-based ranking

**Code Specification:**

```python
# src/orchestration/rag_orchestrator.py

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.context_manager import ContextManager
from src.agents.rag_researcher import RAGResearcherAgent
from src.agents.rag_validator import RAGValidatorAgent
from src.agents.rag_clinician import RAGClinicianAgent
from src.rag.rag_pipeline import RAGPipeline
from src.rag.llm_wrapper import LLMWrapper

logger = logging.getLogger(__name__)

@dataclass
class RAGWorkflowResult:
    """Result of a complete RAG workflow."""
    query: str
    answer: str
    research_findings: List[Any]
    validation_results: List[Any]
    protocols: List[Any]
    overall_confidence: float
    sources: List[str]

class RAGOrchestrator:
    """
    Orchestrator for RAG-enhanced multi-agent workflows.

    Coordinates:
    1. RAGResearcherAgent - retrieves facts
    2. RAGValidatorAgent - validates claims
    3. RAGClinicianAgent - retrieves protocols
    4. LLM synthesis - generates final answer
    """

    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        llm_model: str = "gpt-4o-mini"
    ):
        self.context_manager = context_manager or ContextManager()
        self.base_orchestrator = WorkflowOrchestrator(self.context_manager)
        self.llm = LLMWrapper(model=llm_model)

        # Initialize agents
        self.researcher = RAGResearcherAgent()
        self.validator = RAGValidatorAgent()
        self.clinician = RAGClinicianAgent()

    def orchestrate(self, query: str, workflow_id: Optional[str] = None) -> RAGWorkflowResult:
        """
        Execute complete RAG workflow.

        Flow:
        1. Researcher retrieves relevant facts
        2. Validator checks fact accuracy
        3. Clinician retrieves relevant protocols
        4. LLM synthesizes final answer

        Args:
            query: User question
            workflow_id: Optional workflow tracking ID

        Returns:
            RAGWorkflowResult with comprehensive response
        """
        workflow_id = workflow_id or f"rag_{int(time.time())}"

        logger.info(f"Starting RAG workflow: {workflow_id}")

        # 1. Research phase (parallel-safe)
        research_result = self.base_orchestrator.execute_single_agent(
            agent=self.researcher,
            query=query,
            workflow_id=workflow_id
        )
        findings = self.researcher.retrieve_facts(query)

        # 2. Validation phase
        validation_results = []
        for finding in findings[:3]:  # Validate top 3 findings
            validation = self.validator.validate_claim(finding.evidence)
            validation_results.append(validation)

        # 3. Protocol retrieval phase
        protocols = self.clinician.retrieve_protocols(query)

        # 4. Synthesis phase
        synthesis_prompt = self._build_synthesis_prompt(
            query=query,
            findings=findings,
            validations=validation_results,
            protocols=protocols
        )

        final_response = self.llm.generate(
            system_prompt="You are a clinical research assistant. Synthesize the provided information into a clear, accurate response.",
            user_prompt=synthesis_prompt
        )

        # Calculate overall confidence
        avg_confidence = self._calculate_confidence(findings, validation_results)

        # Collect unique sources
        all_sources = list(set(
            [f.source for f in findings] +
            [p.source for p in protocols]
        ))

        return RAGWorkflowResult(
            query=query,
            answer=final_response.content,
            research_findings=findings,
            validation_results=validation_results,
            protocols=protocols,
            overall_confidence=avg_confidence,
            sources=all_sources
        )

    def _build_synthesis_prompt(self, query, findings, validations, protocols) -> str:
        """Build prompt for final synthesis."""
        # Implementation
        pass

    def _calculate_confidence(self, findings, validations) -> float:
        """Calculate overall confidence score."""
        # Implementation
        pass
```

**Validation Gate 4.1:**
- [ ] `RAGOrchestrator` is importable
- [ ] `orchestrate()` returns `RAGWorkflowResult`
- [ ] All agent results are properly aggregated
- [ ] Sources are deduplicated

---

### Task 4.2: Create Integration Tests

**File:** `tests/integration/test_rag_workflow.py`

**Purpose:** End-to-end integration tests for RAG workflow.

**Implementation Steps:**

1. [ ] Create test fixtures for sample clinical data
2. [ ] Implement workflow integration tests
3. [ ] Add performance benchmarks
4. [ ] Create mock API tests

**Validation Gate 4.2:**
- [ ] Integration tests pass with mock data
- [ ] Workflow completes within acceptable time
- [ ] Error handling works correctly

---

### Task 4.3: Add MCP Message Enhancements

**File:** `src/orchestration/mcp_rag.py`

**Purpose:** RAG-specific MCP message types and handlers.

**Implementation Steps:**

1. [ ] Create RAG-specific message types
2. [ ] Add source attribution to MCP messages
3. [ ] Implement confidence propagation

**Validation Gate 4.3:**
- [ ] MCP messages include RAG metadata
- [ ] Source attribution preserved through workflow
- [ ] Compatible with existing MCP infrastructure

---

## Phase 4 Testing Protocol

### Test File: `tests/integration/test_phase4.py`

```python
"""Phase 4 Integration Tests"""
import pytest
from unittest.mock import Mock, patch

class TestPhase4Orchestration:

    def test_rag_orchestrator_import(self):
        """Verify RAG orchestrator is importable."""
        from src.orchestration.rag_orchestrator import RAGOrchestrator, RAGWorkflowResult
        assert RAGOrchestrator is not None

    @patch('src.rag.llm_wrapper.OpenAI')
    def test_full_workflow(self, mock_openai):
        """Test complete RAG workflow execution."""
        from src.orchestration.rag_orchestrator import RAGOrchestrator

        # Setup mocks
        # ...

        orchestrator = RAGOrchestrator()
        result = orchestrator.orchestrate("What is the treatment for diabetes?")

        assert result.answer is not None
        assert result.overall_confidence >= 0

    def test_workflow_error_handling(self):
        """Test workflow handles agent failures gracefully."""
        from src.orchestration.rag_orchestrator import RAGOrchestrator

        # Test with failing agent
        # Implementation
        pass
```

### Run Tests

```bash
# Run Phase 4 integration tests
pytest tests/integration/test_phase4.py -v --tb=short

# Run with real API (requires key)
pytest tests/integration/test_phase4.py -v --tb=short -m "integration"
```

## Phase 4 Completion Checklist

- [ ] `rag_orchestrator.py` created and tested
- [ ] Integration tests pass
- [ ] MCP enhancements added
- [ ] Full workflow executes successfully
- [ ] Error handling verified
- [ ] Performance acceptable (< 30s for typical query)

**STOP: Wait for user approval before proceeding to Phase 5**

---

# PHASE 5: Validation & Optimization

## Objective
Comprehensive testing, performance optimization, and production readiness validation.

## Prerequisites Checklist

- [ ] Phase 4 completed and approved
- [ ] All integration tests passing
- [ ] Sample clinical data available for testing

## Tasks

### Task 5.1: Create Comprehensive Test Suite

**Directory:** `RAG_plans/rag_testing/`

**Files to Create:**
- `test_e2e_rag.py` - End-to-end tests
- `test_performance.py` - Performance benchmarks
- `fixtures/` - Test data and mocks
- `conftest.py` - Shared fixtures

**Implementation Steps:**

1. [ ] Create test fixtures with sample clinical documents
2. [ ] Implement E2E tests for common use cases
3. [ ] Add performance benchmarks
4. [ ] Create regression test suite

**Test Scenarios:**

```python
# RAG_plans/rag_testing/test_e2e_rag.py

"""End-to-end RAG tests with clinical scenarios."""
import pytest
import time

class TestE2EClinicalRAG:
    """End-to-end tests for clinical RAG scenarios."""

    def test_clinical_query_returns_sourced_answer(self):
        """Query returns answer with source citations."""
        pass

    def test_protocol_retrieval_includes_steps(self):
        """Protocol queries return step-by-step procedures."""
        pass

    def test_validation_detects_contradictions(self):
        """Validator correctly identifies contradicting evidence."""
        pass

    def test_low_confidence_queries_handled(self):
        """System appropriately handles low-confidence scenarios."""
        pass

    def test_multi_source_aggregation(self):
        """Multiple sources are properly aggregated and deduplicated."""
        pass


class TestPerformance:
    """Performance benchmarks."""

    def test_query_latency_under_threshold(self):
        """Typical query completes in < 10 seconds."""
        start = time.time()
        # Execute query
        elapsed = time.time() - start
        assert elapsed < 10.0

    def test_batch_ingestion_performance(self):
        """Batch ingestion maintains acceptable throughput."""
        pass

    def test_concurrent_queries(self):
        """System handles concurrent queries."""
        pass
```

**Validation Gate 5.1:**
- [ ] E2E test suite created
- [ ] All E2E tests pass
- [ ] Performance benchmarks documented
- [ ] Test coverage > 80%

---

### Task 5.2: Performance Optimization

**Focus Areas:**
- Embedding caching
- Query result caching
- Batch processing
- Connection pooling

**Implementation Steps:**

1. [ ] Profile current performance
2. [ ] Implement embedding cache
3. [ ] Add query result caching (TTL-based)
4. [ ] Optimize batch ingestion
5. [ ] Document performance characteristics

**Validation Gate 5.2:**
- [ ] Query latency reduced by 30%+
- [ ] Caching reduces API calls
- [ ] No memory leaks in extended runs

---

### Task 5.3: Documentation & Cleanup

**Files to Create/Update:**
- `RAG_plans/rag_testing/TESTING_GUIDE.md`
- `docs/RAG_API.md`
- `docs/DEPLOYMENT.md`

**Implementation Steps:**

1. [ ] Create API documentation
2. [ ] Document configuration options
3. [ ] Create deployment guide
4. [ ] Update CLAUDE.md with RAG capabilities
5. [ ] Clean up unused code

**Validation Gate 5.3:**
- [ ] All new modules documented
- [ ] Configuration documented
- [ ] Deployment steps verified
- [ ] No dead code remaining

---

## Phase 5 Testing Protocol

### Final Validation Script

```bash
#!/bin/bash
# RAG_plans/rag_testing/run_final_validation.sh

echo "=== RAG System Final Validation ==="

# 1. Unit tests
echo "Running unit tests..."
pytest tests/unit/ -v --tb=short -q
if [ $? -ne 0 ]; then echo "FAIL: Unit tests"; exit 1; fi

# 2. Integration tests
echo "Running integration tests..."
pytest tests/integration/ -v --tb=short -q
if [ $? -ne 0 ]; then echo "FAIL: Integration tests"; exit 1; fi

# 3. E2E tests
echo "Running E2E tests..."
pytest RAG_plans/rag_testing/test_e2e_rag.py -v --tb=short -q
if [ $? -ne 0 ]; then echo "FAIL: E2E tests"; exit 1; fi

# 4. Performance tests
echo "Running performance tests..."
pytest RAG_plans/rag_testing/test_performance.py -v --tb=short -q
if [ $? -ne 0 ]; then echo "FAIL: Performance tests"; exit 1; fi

# 5. Linting
echo "Running linter..."
ruff check src/rag/ src/agents/rag_*.py src/knowledge/
if [ $? -ne 0 ]; then echo "FAIL: Linting"; exit 1; fi

# 6. Type checking (optional)
echo "Running type checker..."
mypy src/rag/ --ignore-missing-imports || true

echo "=== ALL VALIDATIONS PASSED ==="
```

### Run Final Validation

```bash
chmod +x RAG_plans/rag_testing/run_final_validation.sh
./RAG_plans/rag_testing/run_final_validation.sh
```

## Phase 5 Completion Checklist

- [ ] E2E test suite passes
- [ ] Performance benchmarks meet targets
- [ ] Documentation complete
- [ ] Code cleanup done
- [ ] Final validation script passes
- [ ] No critical issues in linting

---

# Summary: Quick Reference

## Files to Create (By Phase)

### Phase 1
- `src/knowledge/chunking_strategies.py`
- `src/knowledge/clinical_ingestion.py`
- `tests/unit/test_phase1.py`

### Phase 2
- `src/rag/__init__.py`
- `src/rag/rag_pipeline.py`
- `src/rag/llm_wrapper.py`
- `src/rag/embedding_manager.py`
- `tests/unit/test_phase2.py`

### Phase 3
- `src/agents/rag_researcher.py`
- `src/agents/rag_validator.py`
- `src/agents/rag_clinician.py`
- `tests/unit/test_phase3.py`

### Phase 4
- `src/orchestration/rag_orchestrator.py`
- `src/orchestration/mcp_rag.py`
- `tests/integration/test_phase4.py`

### Phase 5
- `RAG_plans/rag_testing/test_e2e_rag.py`
- `RAG_plans/rag_testing/test_performance.py`
- `RAG_plans/rag_testing/run_final_validation.sh`
- `docs/RAG_API.md`

## Dependencies Summary

```bash
# All required packages (already in requirements.txt)
openai>=1.0.0
tiktoken
tenacity>=8.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

## Commands Summary

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests for specific phase
pytest tests/unit/test_phase{N}.py -v

# Run all tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Linting
ruff check src/

# Final validation
./RAG_plans/rag_testing/run_final_validation.sh
```

---

**Document End**

> **REMINDER**: Do not proceed to the next phase without explicit user approval.
