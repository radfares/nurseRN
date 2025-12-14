"""
Document Ingester for Personal Knowledge Library
Extracts and chunks text from documents for vector storage.

Created: 2025-12-13
Phase: B1

Tracer IDs: TRACE-B1-001 through TRACE-B1-006
"""

import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import agno document and chunking infrastructure
from agno.knowledge.document.base import Document
from agno.knowledge.chunking.recursive import RecursiveChunking

logger = logging.getLogger(__name__)


@dataclass
class ChunkRecord:
    """
    Structured record for a document chunk, future-proofed for Phase C.

    Attributes:
        doc_id: Unique document identifier (hash of file path + content)
        chunk_id: Unique chunk identifier (doc_id_chunk_XXX)
        text: The actual chunk text content
        source_path: Original file path
        source_type: Type of source ("personal", "pubmed", "arxiv" for Phase C)
        page_num: Page number if applicable (None for non-paginated docs)
        version: Document version for tracking changes (Phase C)
        ingested_at: ISO timestamp of ingestion
        citation_info: APA citation string (Phase C)
        file_hash: MD5 hash of file for version detection
        chunk_index: Index of this chunk within the document
        total_chunks: Total number of chunks in the document
        char_count: Character count of this chunk
    """
    doc_id: str
    chunk_id: str
    text: str
    source_path: str
    source_type: str = "personal"
    page_num: Optional[int] = None
    version: int = 1
    ingested_at: str = ""
    citation_info: Optional[str] = None
    file_hash: str = ""
    chunk_index: int = 0
    total_chunks: int = 0
    char_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.ingested_at:
            self.ingested_at = datetime.now().isoformat()
        if not self.char_count:
            self.char_count = len(self.text)

    def to_document(self) -> Document:
        """Convert ChunkRecord to agno Document for vector storage."""
        meta_data = {
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "source_path": self.source_path,
            "source_type": self.source_type,
            "page_num": self.page_num,
            "version": self.version,
            "ingested_at": self.ingested_at,
            "file_hash": self.file_hash,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "char_count": self.char_count,
            **self.metadata
        }
        return Document(
            id=self.chunk_id,
            name=Path(self.source_path).name,
            content=self.text,
            meta_data=meta_data,
            content_id=self.doc_id
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source_path": self.source_path,
            "source_type": self.source_type,
            "page_num": self.page_num,
            "version": self.version,
            "ingested_at": self.ingested_at,
            "citation_info": self.citation_info,
            "file_hash": self.file_hash,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "char_count": self.char_count,
            "metadata": self.metadata
        }


class DocumentIngesterError(Exception):
    """Base exception for document ingestion errors."""
    pass


class FileNotFoundError(DocumentIngesterError):
    """Raised when file is not found."""
    pass


class UnsupportedFormatError(DocumentIngesterError):
    """Raised when file format is not supported."""
    pass


class ReadError(DocumentIngesterError):
    """Raised when file cannot be read."""
    pass


class DocumentIngester:
    """
    Ingests documents by extracting text and chunking for vector storage.

    Supports: PDF, PPTX, DOCX, CSV, JSON, TXT, MD

    Uses agno readers for extraction and RecursiveChunking for splitting.

    Example:
        ingester = DocumentIngester(chunk_size=2000, overlap=200)
        chunks = ingester.ingest_file("/path/to/document.pdf")
        for chunk in chunks:
            print(f"Chunk {chunk.chunk_index}: {len(chunk.text)} chars")
    """

    # Supported file extensions and their reader types
    SUPPORTED_FORMATS = {
        ".pdf": "pdf",
        ".pptx": "pptx",
        ".docx": "docx",
        ".csv": "csv",
        ".json": "json",
        ".txt": "text",
        ".md": "markdown",
        ".markdown": "markdown",
    }

    def __init__(
        self,
        chunk_size: int = 2000,
        overlap: int = 200,
        source_type: str = "personal",
    ):
        """
        Initialize the document ingester.

        Args:
            chunk_size: Target size of each chunk in characters (default: 2000)
            overlap: Overlap between chunks in characters (default: 200)
            source_type: Default source type for metadata (default: "personal")
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.source_type = source_type

        # Initialize chunking strategy
        self.chunker = RecursiveChunking(chunk_size=chunk_size, overlap=overlap)

        # Lazy-loaded readers (initialized on first use)
        self._readers: Dict[str, Any] = {}

        logger.info(
            f"DocumentIngester initialized: chunk_size={chunk_size}, "
            f"overlap={overlap}, source_type={source_type}"
        )

    def _trace(self, trace_id: str, **kwargs) -> None:
        """Log a trace point for debugging."""
        msg = f"[{trace_id}] " + " | ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.debug(msg)

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for version detection."""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _generate_doc_id(self, file_path: Path, file_hash: str) -> str:
        """Generate unique document ID from path and hash."""
        unique_str = f"{file_path.absolute()}:{file_hash}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]

    def _get_reader(self, file_type: str):
        """Get or initialize a reader for the given file type."""
        if file_type in self._readers:
            return self._readers[file_type]

        reader = None

        try:
            if file_type == "pdf":
                from agno.knowledge.reader.pdf_reader import PDFReader
                reader = PDFReader()
            elif file_type == "pptx":
                from agno.knowledge.reader.pptx_reader import PPTXReader
                reader = PPTXReader()
            elif file_type == "docx":
                from agno.knowledge.reader.docx_reader import DocxReader
                reader = DocxReader()
            elif file_type == "csv":
                from agno.knowledge.reader.csv_reader import CSVReader
                reader = CSVReader()
            elif file_type == "json":
                from agno.knowledge.reader.json_reader import JSONReader
                reader = JSONReader()
            elif file_type == "text":
                from agno.knowledge.reader.text_reader import TextReader
                reader = TextReader()
            elif file_type == "markdown":
                from agno.knowledge.reader.markdown_reader import MarkdownReader
                reader = MarkdownReader()
        except ImportError as e:
            logger.warning(f"Reader for {file_type} not available: {e}")
            return None

        if reader:
            self._readers[file_type] = reader
        return reader

    def _read_text_file(self, file_path: Path) -> str:
        """Fallback reader for plain text files."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    def _extract_content(self, file_path: Path, file_type: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text content from a file.

        Returns:
            Tuple of (content_text, extraction_metadata)
        """
        self._trace("TRACE-B1-002", reader_type=file_type, file_extension=file_path.suffix)

        reader = self._get_reader(file_type)
        extraction_metadata: Dict[str, Any] = {}

        if reader:
            try:
                documents = reader.read(str(file_path))
                if documents:
                    # Combine all document content
                    content = "\n\n".join([doc.content for doc in documents if doc.content])

                    # Extract page info if available
                    if documents[0].meta_data:
                        extraction_metadata = documents[0].meta_data.copy()

                    self._trace("TRACE-B1-003", char_count=len(content))
                    return content, extraction_metadata
            except Exception as e:
                logger.warning(f"Reader failed for {file_path}: {e}, trying fallback")

        # Fallback for text-based files
        if file_type in ("text", "markdown") or file_path.suffix in (".txt", ".md", ".markdown"):
            content = self._read_text_file(file_path)
            self._trace("TRACE-B1-003", char_count=len(content))
            return content, extraction_metadata

        raise ReadError(f"Could not extract content from {file_path}")

    def ingest_file(
        self,
        file_path: str,
        source_type: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ChunkRecord]:
        """
        Ingest a single file and return chunked records.

        Args:
            file_path: Path to the file to ingest
            source_type: Override default source type (optional)
            extra_metadata: Additional metadata to include (optional)

        Returns:
            List of ChunkRecord objects ready for vector storage

        Raises:
            FileNotFoundError: If file does not exist
            UnsupportedFormatError: If file format is not supported
            ReadError: If file cannot be read
        """
        path = Path(file_path)
        self._trace("TRACE-B1-001", path=str(path))

        # Validate file exists
        if not path.exists():
            self._trace("TRACE-B1-006", error_type="FileNotFoundError", error_message=f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            self._trace("TRACE-B1-006", error_type="NotAFileError", error_message=f"Not a file: {path}")
            raise FileNotFoundError(f"Not a file: {path}")

        # Check file format
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            self._trace("TRACE-B1-006", error_type="UnsupportedFormatError", error_message=f"Unsupported format: {suffix}")
            raise UnsupportedFormatError(
                f"Unsupported file format: {suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS.keys())}"
            )

        file_type = self.SUPPORTED_FORMATS[suffix]

        # Calculate file hash for version detection
        try:
            file_hash = self._get_file_hash(path)
        except Exception as e:
            self._trace("TRACE-B1-006", error_type="HashError", error_message=str(e))
            raise ReadError(f"Could not read file for hashing: {e}")

        # Generate document ID
        doc_id = self._generate_doc_id(path, file_hash)

        # Extract content
        try:
            content, extraction_metadata = self._extract_content(path, file_type)
        except Exception as e:
            self._trace("TRACE-B1-006", error_type=type(e).__name__, error_message=str(e))
            raise ReadError(f"Failed to extract content: {e}")

        if not content or not content.strip():
            self._trace("TRACE-B1-006", error_type="EmptyContent", error_message="No content extracted")
            raise ReadError(f"No content extracted from {path}")

        # Create a Document for chunking
        doc = Document(
            id=doc_id,
            name=path.name,
            content=content,
            meta_data=extraction_metadata
        )

        # Chunk the document
        try:
            chunked_docs = self.chunker.chunk(doc)
        except Exception as e:
            self._trace("TRACE-B1-006", error_type="ChunkingError", error_message=str(e))
            raise ReadError(f"Failed to chunk document: {e}")

        total_chunks = len(chunked_docs)
        avg_size = sum(len(d.content) for d in chunked_docs) / total_chunks if total_chunks > 0 else 0
        self._trace("TRACE-B1-004", chunk_count=total_chunks, avg_size=int(avg_size))

        # Create ChunkRecords
        chunks: List[ChunkRecord] = []
        effective_source_type = source_type or self.source_type

        for idx, chunk_doc in enumerate(chunked_docs):
            # Build metadata
            metadata = {
                "filename": path.name,
                "file_extension": suffix,
                "file_size_bytes": path.stat().st_size,
                **(extraction_metadata or {}),
                **(extra_metadata or {})
            }

            # Extract page number if available
            page_num = chunk_doc.meta_data.get("page") or chunk_doc.meta_data.get("page_num")

            chunk_record = ChunkRecord(
                doc_id=doc_id,
                chunk_id=f"{doc_id}_chunk_{idx:04d}",
                text=chunk_doc.content,
                source_path=str(path.absolute()),
                source_type=effective_source_type,
                page_num=page_num,
                version=1,
                file_hash=file_hash,
                chunk_index=idx,
                total_chunks=total_chunks,
                metadata=metadata
            )
            chunks.append(chunk_record)

        self._trace("TRACE-B1-005", metadata_keys=list(metadata.keys()) if chunks else [])

        logger.info(
            f"Ingested {path.name}: {total_chunks} chunks, "
            f"{len(content)} chars total, avg chunk size {int(avg_size)} chars"
        )

        return chunks

    def ingest_folder(
        self,
        folder_path: str,
        recursive: bool = True,
        source_type: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ChunkRecord], List[Tuple[str, str]]]:
        """
        Ingest all supported files in a folder.

        Args:
            folder_path: Path to the folder
            recursive: Whether to process subdirectories (default: True)
            source_type: Override default source type (optional)
            extra_metadata: Additional metadata to include (optional)

        Returns:
            Tuple of (successful_chunks, failed_files)
            - successful_chunks: List of all ChunkRecords from successful files
            - failed_files: List of (file_path, error_message) tuples
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder}")
        if not folder.is_dir():
            raise FileNotFoundError(f"Not a directory: {folder}")

        all_chunks: List[ChunkRecord] = []
        failed_files: List[Tuple[str, str]] = []

        # Get all files
        if recursive:
            files = list(folder.rglob("*"))
        else:
            files = list(folder.glob("*"))

        # Filter to supported files
        supported_files = [
            f for f in files
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_FORMATS
        ]

        logger.info(f"Found {len(supported_files)} supported files in {folder}")

        for file_path in supported_files:
            try:
                chunks = self.ingest_file(
                    str(file_path),
                    source_type=source_type,
                    extra_metadata=extra_metadata
                )
                all_chunks.extend(chunks)
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                failed_files.append((str(file_path), error_msg))
                logger.warning(f"Failed to ingest {file_path}: {error_msg}")

        logger.info(
            f"Folder ingestion complete: {len(all_chunks)} chunks from "
            f"{len(supported_files) - len(failed_files)} files, "
            f"{len(failed_files)} failures"
        )

        return all_chunks, failed_files

    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions."""
        return list(self.SUPPORTED_FORMATS.keys())


# Convenience function for quick ingestion
def ingest_document(
    file_path: str,
    chunk_size: int = 2000,
    overlap: int = 200
) -> List[ChunkRecord]:
    """
    Convenience function to ingest a single document.

    Args:
        file_path: Path to the document
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks

    Returns:
        List of ChunkRecord objects
    """
    ingester = DocumentIngester(chunk_size=chunk_size, overlap=overlap)
    return ingester.ingest_file(file_path)
