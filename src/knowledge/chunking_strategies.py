"""
Chunking Strategies for RAG Pipeline
Provides multiple chunking strategies optimized for different document types.

Created: 2025-12-15
Phase: 1 - Foundation Enhancement
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import re

import tiktoken

logger = logging.getLogger(__name__)


@dataclass
class ChunkResult:
    """Result of a chunking operation."""
    text: str
    start_idx: int
    end_idx: int
    token_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.metadata:
            self.metadata = {}


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """
        Chunk text into smaller pieces.

        Args:
            text: The text to chunk
            **kwargs: Strategy-specific parameters

        Returns:
            List of ChunkResult objects
        """
        pass


class TokenBasedChunker(ChunkingStrategy):
    """
    Chunk based on token count with overlap.

    Best for: Research documents, general text where precise token limits matter.
    """

    def __init__(
        self,
        token_limit: int = 400,
        overlap: int = 50,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize token-based chunker.

        Args:
            token_limit: Maximum tokens per chunk
            overlap: Token overlap between chunks
            model: Model name for tokenizer selection
        """
        self.token_limit = token_limit
        self.overlap = overlap
        try:
            self._tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self._tokenizer = tiktoken.get_encoding("cl100k_base")
        logger.debug(f"TokenBasedChunker initialized: limit={token_limit}, overlap={overlap}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._tokenizer.encode(text))

    def chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """Chunk text based on token count."""
        if not text or not text.strip():
            return []

        tokens = self._tokenizer.encode(text)
        total_tokens = len(tokens)

        if total_tokens <= self.token_limit:
            return [ChunkResult(
                text=text,
                start_idx=0,
                end_idx=len(text),
                token_count=total_tokens,
                metadata={"chunk_index": 0, "total_chunks": 1}
            )]

        chunks = []
        start_token = 0
        chunk_index = 0

        while start_token < total_tokens:
            end_token = min(start_token + self.token_limit, total_tokens)
            chunk_tokens = tokens[start_token:end_token]
            chunk_text = self._tokenizer.decode(chunk_tokens)

            # Calculate character positions (approximate)
            prefix_text = self._tokenizer.decode(tokens[:start_token])
            start_char = len(prefix_text)
            end_char = start_char + len(chunk_text)

            chunks.append(ChunkResult(
                text=chunk_text,
                start_idx=start_char,
                end_idx=end_char,
                token_count=len(chunk_tokens),
                metadata={"chunk_index": chunk_index}
            ))

            # Move forward, accounting for overlap
            start_token = end_token - self.overlap if end_token < total_tokens else total_tokens
            chunk_index += 1

        # Update total_chunks in metadata
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)

        logger.debug(f"TokenBasedChunker produced {len(chunks)} chunks from {total_tokens} tokens")
        return chunks


class SemanticChunker(ChunkingStrategy):
    """
    Chunk based on semantic boundaries (paragraphs, sections).

    Best for: Clinical documents, structured text with clear sections.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize semantic chunker.

        Args:
            chunk_size: Target token size per chunk
            overlap: Token overlap between chunks
            model: Model name for tokenizer selection
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        try:
            self._tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self._tokenizer = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._tokenizer.encode(text))

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split on double newlines or multiple newlines
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """Chunk text based on semantic boundaries."""
        if not text or not text.strip():
            return []

        paragraphs = self._split_into_paragraphs(text)

        if not paragraphs:
            return []

        chunks = []
        current_chunk_parts = []
        current_tokens = 0
        current_start = 0
        chunk_index = 0

        for para in paragraphs:
            para_tokens = self._count_tokens(para)

            # If single paragraph exceeds chunk_size, use token-based splitting
            if para_tokens > self.chunk_size:
                # Flush current chunk first
                if current_chunk_parts:
                    chunk_text = "\n\n".join(current_chunk_parts)
                    chunks.append(ChunkResult(
                        text=chunk_text,
                        start_idx=current_start,
                        end_idx=current_start + len(chunk_text),
                        token_count=current_tokens,
                        metadata={"chunk_index": chunk_index}
                    ))
                    current_start += len(chunk_text) + 2
                    chunk_index += 1
                    current_chunk_parts = []
                    current_tokens = 0

                # Split large paragraph with token chunker
                token_chunker = TokenBasedChunker(
                    token_limit=self.chunk_size,
                    overlap=self.overlap
                )
                sub_chunks = token_chunker.chunk(para)
                for sc in sub_chunks:
                    sc.start_idx += current_start
                    sc.end_idx += current_start
                    sc.metadata["chunk_index"] = chunk_index
                    chunks.append(sc)
                    chunk_index += 1
                current_start += len(para) + 2
                continue

            # Check if adding this paragraph exceeds limit
            if current_tokens + para_tokens > self.chunk_size and current_chunk_parts:
                # Flush current chunk
                chunk_text = "\n\n".join(current_chunk_parts)
                chunks.append(ChunkResult(
                    text=chunk_text,
                    start_idx=current_start,
                    end_idx=current_start + len(chunk_text),
                    token_count=current_tokens,
                    metadata={"chunk_index": chunk_index}
                ))
                current_start += len(chunk_text) + 2
                chunk_index += 1
                current_chunk_parts = []
                current_tokens = 0

            current_chunk_parts.append(para)
            current_tokens += para_tokens

        # Flush remaining content
        if current_chunk_parts:
            chunk_text = "\n\n".join(current_chunk_parts)
            chunks.append(ChunkResult(
                text=chunk_text,
                start_idx=current_start,
                end_idx=current_start + len(chunk_text),
                token_count=current_tokens,
                metadata={"chunk_index": chunk_index}
            ))

        # Update total_chunks
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)

        logger.debug(f"SemanticChunker produced {len(chunks)} chunks from {len(paragraphs)} paragraphs")
        return chunks


class SentenceChunker(ChunkingStrategy):
    """
    Chunk based on sentence boundaries.

    Best for: Procedural documents, step-by-step instructions.
    """

    def __init__(
        self,
        sentences_per_chunk: int = 5,
        overlap_sentences: int = 1,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize sentence-based chunker.

        Args:
            sentences_per_chunk: Number of sentences per chunk
            overlap_sentences: Sentence overlap between chunks
            model: Model name for tokenizer selection
        """
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences
        try:
            self._tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self._tokenizer = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._tokenizer.encode(text))

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (handles common cases)
        # Splits on . ! ? followed by space or newline
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """Chunk text based on sentence boundaries."""
        if not text or not text.strip():
            return []

        sentences = self._split_into_sentences(text)

        if not sentences:
            return []

        if len(sentences) <= self.sentences_per_chunk:
            full_text = " ".join(sentences)
            return [ChunkResult(
                text=full_text,
                start_idx=0,
                end_idx=len(full_text),
                token_count=self._count_tokens(full_text),
                metadata={"chunk_index": 0, "total_chunks": 1}
            )]

        chunks = []
        chunk_index = 0
        current_pos = 0
        i = 0

        while i < len(sentences):
            end_idx = min(i + self.sentences_per_chunk, len(sentences))
            chunk_sentences = sentences[i:end_idx]
            chunk_text = " ".join(chunk_sentences)

            chunks.append(ChunkResult(
                text=chunk_text,
                start_idx=current_pos,
                end_idx=current_pos + len(chunk_text),
                token_count=self._count_tokens(chunk_text),
                metadata={"chunk_index": chunk_index}
            ))

            current_pos += len(chunk_text) + 1
            chunk_index += 1

            # Move forward with overlap
            i = end_idx - self.overlap_sentences if end_idx < len(sentences) else len(sentences)

        # Update total_chunks
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)

        logger.debug(f"SentenceChunker produced {len(chunks)} chunks from {len(sentences)} sentences")
        return chunks


class ChunkingFactory:
    """Factory to create appropriate chunker based on document type."""

    _default_configs = {
        "clinical": {"class": SemanticChunker, "chunk_size": 500, "overlap": 50},
        "procedural": {"class": SentenceChunker, "sentences_per_chunk": 5, "overlap_sentences": 1},
        "research": {"class": TokenBasedChunker, "token_limit": 400, "overlap": 50},
        "default": {"class": TokenBasedChunker, "token_limit": 400, "overlap": 50},
    }

    @classmethod
    def get_chunker(cls, doc_type: str, **override_params) -> ChunkingStrategy:
        """
        Get a chunker instance for the specified document type.

        Args:
            doc_type: Type of document ("clinical", "procedural", "research", "default")
            **override_params: Override default parameters

        Returns:
            Configured ChunkingStrategy instance
        """
        config = cls._default_configs.get(doc_type, cls._default_configs["default"]).copy()
        chunker_class = config.pop("class")

        # Apply overrides
        config.update(override_params)

        logger.info(f"Creating {chunker_class.__name__} for doc_type={doc_type}")
        return chunker_class(**config)

    @classmethod
    def register_strategy(cls, doc_type: str, chunker_class: type, **default_params) -> None:
        """
        Register a custom chunking strategy.

        Args:
            doc_type: Document type identifier
            chunker_class: ChunkingStrategy subclass
            **default_params: Default parameters for the chunker
        """
        cls._default_configs[doc_type] = {"class": chunker_class, **default_params}
        logger.info(f"Registered chunking strategy: {doc_type} -> {chunker_class.__name__}")
