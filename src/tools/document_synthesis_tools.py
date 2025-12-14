"""
Document Synthesis Tools for Literature Synthesis Agent
Provides tools for loading files and retrieving library content for synthesis.

Created: 2025-12-13
Purpose: Enable file-based literature synthesis with any number of documents
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit

from src.knowledge.document_ingester import DocumentIngester, DocumentIngesterError
from src.knowledge.vector_store import (
    PersonalLibraryVectorStore,
    COLLECTION_PERSONAL,
)

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_DB_PATH = "data/chroma_db"
DEFAULT_CHUNK_SIZE = 4000  # Larger chunks for synthesis context
DEFAULT_OVERLAP = 400
MAX_DOCUMENTS = 20  # Safety limit


class DocumentSynthesisTools(Toolkit):
    """
    Toolkit for loading and preparing documents for synthesis.

    Provides two main capabilities:
    1. Load files directly from file paths
    2. Search and retrieve full documents from indexed library

    Example Agent Usage:
        - "Synthesize /path/to/doc1.pdf, /path/to/doc2.pdf"
        - "Synthesize articles about fall prevention from my library"
        - "Compare these files: study1.pdf, study2.docx, notes.txt"
    """

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
        **kwargs,
    ):
        """
        Initialize Document Synthesis Tools.

        Args:
            db_path: Path to ChromaDB storage
            chunk_size: Size of text chunks for processing
            overlap: Overlap between chunks
        """
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.overlap = overlap

        # Initialize ingester for file loading
        self._ingester = DocumentIngester(
            chunk_size=chunk_size,
            overlap=overlap
        )

        # Lazy-loaded vector store
        self._store: Optional[PersonalLibraryVectorStore] = None

        # Register tools
        super().__init__(
            name="document_synthesis_tools",
            tools=[
                self.load_files_for_synthesis,
                self.search_library_for_synthesis,
                self.get_library_document_list,
            ],
            **kwargs,
        )

        logger.info("DocumentSynthesisTools initialized")

    @property
    def store(self) -> PersonalLibraryVectorStore:
        """Lazy-load vector store."""
        if self._store is None:
            self._store = PersonalLibraryVectorStore(
                collection_name=COLLECTION_PERSONAL,
                db_path=self.db_path,
            )
        return self._store

    def load_files_for_synthesis(self, file_paths: str) -> str:
        """
        Load multiple files for synthesis analysis.

        Accepts file paths separated by commas, newlines, or semicolons.
        Supports: PDF, DOCX, TXT, MD, PPTX, CSV, JSON

        Args:
            file_paths: Comma/newline/semicolon separated file paths.
                       Can also be a single folder path to load all files.

        Returns:
            JSON string with document content and metadata for each file.

        Example:
            load_files_for_synthesis("/docs/study1.pdf, /docs/study2.pdf")
            load_files_for_synthesis("/docs/research_folder/")
        """
        try:
            # Parse paths - handle various separators
            paths_raw = file_paths.replace("\n", ",").replace(";", ",")
            paths = [p.strip() for p in paths_raw.split(",") if p.strip()]

            if not paths:
                return json.dumps({
                    "error": "No file paths provided",
                    "documents": []
                })

            documents = []
            errors = []

            for path in paths[:MAX_DOCUMENTS]:  # Safety limit
                path_obj = Path(path).expanduser()

                # Handle folder paths
                if path_obj.is_dir():
                    folder_docs, folder_errors = self._load_folder(path_obj)
                    documents.extend(folder_docs)
                    errors.extend(folder_errors)
                    continue

                # Handle single file
                if not path_obj.exists():
                    errors.append(f"File not found: {path}")
                    continue

                try:
                    doc_data = self._load_single_file(path_obj)
                    documents.append(doc_data)
                except Exception as e:
                    errors.append(f"Error loading {path}: {str(e)}")

            result = {
                "documents": documents,
                "total_loaded": len(documents),
                "errors": errors if errors else None,
            }

            logger.info(f"Loaded {len(documents)} documents for synthesis")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error in load_files_for_synthesis: {e}")
            return json.dumps({
                "error": str(e),
                "documents": []
            })

    def _load_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a single file and extract content."""
        try:
            # Use ingester to extract and chunk content
            chunks = self._ingester.ingest_file(str(file_path))

            if not chunks:
                return {
                    "filename": file_path.name,
                    "file_type": file_path.suffix.lower(),
                    "error": "No content extracted",
                    "content": "",
                }

            # Combine all chunks into full content
            full_content = "\n\n".join([chunk.text for chunk in chunks])

            # Calculate metadata
            word_count = len(full_content.split())
            page_count = max(
                (chunk.page_num or 0 for chunk in chunks),
                default=len(chunks)
            )

            return {
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix.lower().lstrip("."),
                "page_count": page_count if page_count > 0 else len(chunks),
                "word_count": word_count,
                "chunk_count": len(chunks),
                "content": full_content,
            }

        except DocumentIngesterError as e:
            raise Exception(f"Ingestion error: {str(e)}")

    def _load_folder(self, folder_path: Path) -> tuple:
        """Load all supported files from a folder."""
        documents = []
        errors = []

        supported_extensions = {".pdf", ".docx", ".txt", ".md", ".pptx", ".csv", ".json"}

        for file_path in folder_path.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    doc_data = self._load_single_file(file_path)
                    documents.append(doc_data)
                except Exception as e:
                    errors.append(f"Error loading {file_path.name}: {str(e)}")

            if len(documents) >= MAX_DOCUMENTS:
                errors.append(f"Reached maximum document limit ({MAX_DOCUMENTS})")
                break

        return documents, errors

    def search_library_for_synthesis(
        self,
        query: str,
        n_results: int = 10
    ) -> str:
        """
        Search the indexed personal library and retrieve full document content.

        Unlike regular search which returns snippets, this retrieves ALL chunks
        for each matching document to enable complete synthesis.

        Args:
            query: Search query to find relevant documents
            n_results: Maximum number of documents to retrieve (default: 10)

        Returns:
            JSON string with full document content for synthesis.

        Example:
            search_library_for_synthesis("fall prevention nursing")
            search_library_for_synthesis("medication administration safety", n_results=5)
        """
        try:
            if not query or not query.strip():
                return json.dumps({
                    "error": "Empty query provided",
                    "documents": []
                })

            # Clamp n_results
            n_results = max(1, min(n_results, MAX_DOCUMENTS))

            # Search for relevant documents
            search_results = self.store.search(query, limit=n_results * 3)  # Over-fetch to dedupe

            if not search_results:
                return json.dumps({
                    "message": "No matching documents found in library",
                    "query": query,
                    "documents": []
                })

            # Group results by document ID and get unique docs
            doc_ids_seen = set()
            unique_docs = []

            for result in search_results:
                doc_id = result.doc_id
                if doc_id not in doc_ids_seen and len(unique_docs) < n_results:
                    doc_ids_seen.add(doc_id)
                    unique_docs.append(result)

            # For each unique document, retrieve ALL its chunks
            documents = []
            for doc_result in unique_docs:
                doc_data = self._get_full_document_content(doc_result.doc_id)
                if doc_data:
                    doc_data["relevance_score"] = doc_result.score
                    documents.append(doc_data)

            result = {
                "query": query,
                "documents": documents,
                "total_found": len(documents),
            }

            logger.info(f"Retrieved {len(documents)} documents from library for synthesis")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error in search_library_for_synthesis: {e}")
            return json.dumps({
                "error": str(e),
                "documents": []
            })

    def _get_full_document_content(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve all chunks for a document and reconstruct full content."""
        try:
            # Get all chunks for this document from the store
            all_chunks = self.store.get_chunks_by_doc_id(doc_id)

            if not all_chunks:
                return None

            # Sort by chunk index
            all_chunks.sort(key=lambda x: x.get("chunk_index", 0))

            # Combine content
            full_content = "\n\n".join([
                chunk.get("text", "") for chunk in all_chunks
            ])

            # Get metadata from first chunk
            first_chunk = all_chunks[0]
            source_path = first_chunk.get("source_path", "")
            filename = Path(source_path).name if source_path else f"doc_{doc_id[:8]}"

            # Calculate stats
            word_count = len(full_content.split())
            page_nums = [c.get("page_num") for c in all_chunks if c.get("page_num")]
            page_count = max(page_nums) if page_nums else len(all_chunks)

            return {
                "filename": filename,
                "doc_id": doc_id,
                "file_type": Path(source_path).suffix.lower().lstrip(".") if source_path else "unknown",
                "page_count": page_count,
                "word_count": word_count,
                "chunk_count": len(all_chunks),
                "content": full_content,
            }

        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
            return None

    def get_library_document_list(self) -> str:
        """
        List all documents currently indexed in the personal library.

        Returns:
            JSON string with list of all indexed documents and their metadata.

        Example:
            get_library_document_list()
        """
        try:
            docs = self.store.list_documents()

            if not docs:
                return json.dumps({
                    "message": "No documents in library. Use the CLI to add documents.",
                    "documents": [],
                    "total": 0
                })

            result = {
                "documents": docs,
                "total": len(docs),
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error listing library documents: {e}")
            return json.dumps({
                "error": str(e),
                "documents": []
            })


def create_document_synthesis_tools_safe() -> Optional[DocumentSynthesisTools]:
    """
    Safely create DocumentSynthesisTools with error handling.

    Returns:
        DocumentSynthesisTools instance or None if initialization fails.
    """
    try:
        return DocumentSynthesisTools()
    except Exception as e:
        logger.warning(f"DocumentSynthesisTools unavailable: {e}")
        return None
