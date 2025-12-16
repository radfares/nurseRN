"""
Metadata Schema and Validation for Knowledge Module
Defines canonical metadata keys and enforces consistency at ingestion time.

Created: 2025-12-16
Phase: Production-Safe Refactor

Required metadata keys (minimum):
- doc_key: Stable logical identifier (normalized absolute source_path)
- doc_version or ingestion_run_id: Version tracking
- chunk_id: Stable, deterministic identifier
- store_type, doc_type, source_type, source_path
- file_hash
- embedder_spec_hash, chunker_config_hash
- is_active, ingested_at
"""

import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


# Canonical metadata keys (R6 requirement)
REQUIRED_METADATA_KEYS: Set[str] = {
    "doc_key",
    "ingestion_run_id",
    "chunk_id",
    "store_type",
    "doc_type",
    "source_type",
    "source_path",
    "file_hash",
    "embedder_spec_hash",
    "chunker_config_hash",
    "is_active",
    "ingested_at",
}

# Optional but recommended keys
OPTIONAL_METADATA_KEYS: Set[str] = {
    "chunk_index",
    "total_chunks",
    "char_count",
    "token_count",
    "page_num",
    "filename",
    "file_extension",
    "file_size_bytes",
    "version",
    "citation_info",
}

# All canonical keys
CANONICAL_METADATA_KEYS: Set[str] = REQUIRED_METADATA_KEYS | OPTIONAL_METADATA_KEYS


class ChunkMetadata(BaseModel):
    """
    Validated metadata for a document chunk.

    Enforces the canonical schema and normalizes values.
    """

    # Required keys (R6)
    doc_key: str = Field(..., description="Stable logical identifier (normalized absolute source_path)")
    ingestion_run_id: str = Field(..., description="Unique ID for this ingestion run")
    chunk_id: str = Field(..., description="Deterministic chunk identifier")
    store_type: str = Field(..., description="Target store type (personal, clinical, etc.)")
    doc_type: str = Field(..., description="Document type (clinical, procedural, research, etc.)")
    source_type: str = Field(..., description="Source type (personal, pubmed, arxiv, etc.)")
    source_path: str = Field(..., description="Original file path")
    file_hash: str = Field(..., description="MD5 hash of source file")
    embedder_spec_hash: str = Field(..., description="Hash of embedder configuration")
    chunker_config_hash: str = Field(..., description="Hash of chunker configuration")
    is_active: bool = Field(default=False, description="Whether this chunk is active (visible in searches)")
    ingested_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO timestamp")

    # Optional keys
    chunk_index: int = Field(default=0, description="Position within document")
    total_chunks: int = Field(default=1, description="Total chunks in document")
    char_count: int = Field(default=0, description="Character count of chunk text")
    token_count: Optional[int] = Field(default=None, description="Token count if computed")
    page_num: Optional[int] = Field(default=None, description="Page number if applicable")
    filename: Optional[str] = Field(default=None, description="Original filename")
    file_extension: Optional[str] = Field(default=None, description="File extension")
    file_size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    version: int = Field(default=1, description="Document version number")
    citation_info: Optional[str] = Field(default=None, description="Citation string if available")

    @field_validator("doc_key")
    @classmethod
    def normalize_doc_key(cls, v: str) -> str:
        """Normalize doc_key to absolute path format."""
        if not v:
            raise ValueError("doc_key cannot be empty")
        # Normalize path separators and resolve relative paths
        return str(Path(v).resolve()) if os.path.exists(v) else v

    @field_validator("source_path")
    @classmethod
    def normalize_source_path(cls, v: str) -> str:
        """Normalize source_path."""
        if not v:
            return "inline"
        return str(Path(v).resolve()) if os.path.exists(v) else v

    @field_validator("is_active")
    @classmethod
    def ensure_bool(cls, v: Any) -> bool:
        """Ensure is_active is boolean."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Chroma metadata."""
        result = {}
        for key in CANONICAL_METADATA_KEYS:
            if hasattr(self, key):
                value = getattr(self, key)
                if value is not None:
                    result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkMetadata":
        """Create from dictionary, normalizing and validating."""
        # Filter to known keys only
        filtered = {k: v for k, v in data.items() if k in CANONICAL_METADATA_KEYS}
        return cls(**filtered)


class MetadataValidationError(Exception):
    """Raised when metadata validation fails."""

    def __init__(self, message: str, missing_keys: Optional[List[str]] = None,
                 invalid_keys: Optional[Dict[str, str]] = None):
        super().__init__(message)
        self.missing_keys = missing_keys or []
        self.invalid_keys = invalid_keys or {}


def generate_doc_key(source_path: str) -> str:
    """
    Generate a stable doc_key from source path.

    Uses normalized absolute path as the logical document identifier.
    This ensures the same file always gets the same doc_key regardless
    of how the path is specified.
    """
    if not source_path or source_path == "inline":
        return f"inline_{hashlib.md5(str(datetime.utcnow().timestamp()).encode()).hexdigest()[:8]}"

    path = Path(source_path)
    if path.exists():
        return str(path.resolve())
    return str(path.absolute())


def generate_chunk_id(doc_key: str, ingestion_run_id: str, chunk_index: int) -> str:
    """
    Generate a deterministic chunk_id.

    Format: sha256(doc_key + ingestion_run_id + chunk_index)[:16]

    This ensures:
    - Same chunk in same ingestion run always gets same ID
    - Different ingestion runs get different IDs (enabling two-phase commit)
    """
    input_str = f"{doc_key}|{ingestion_run_id}|{chunk_index}"
    return hashlib.sha256(input_str.encode()).hexdigest()[:16]


def generate_ingestion_run_id() -> str:
    """
    Generate a unique ingestion run ID.

    Format: ing_{timestamp}_{random}
    """
    import uuid
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = uuid.uuid4().hex[:8]
    return f"ing_{timestamp}_{random_suffix}"


def validate_metadata(metadata: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
    """
    Validate and normalize metadata dictionary.

    Args:
        metadata: Raw metadata dictionary
        strict: If True, raise on missing required keys; if False, add defaults

    Returns:
        Validated and normalized metadata dictionary

    Raises:
        MetadataValidationError: If validation fails in strict mode
    """
    missing_keys = []
    normalized = dict(metadata)

    # Check required keys
    for key in REQUIRED_METADATA_KEYS:
        if key not in normalized or normalized[key] is None:
            if strict:
                missing_keys.append(key)
            else:
                # Add sensible defaults
                if key == "is_active":
                    normalized[key] = False
                elif key == "ingested_at":
                    normalized[key] = datetime.utcnow().isoformat()
                elif key in ("ingestion_run_id", "chunk_id", "doc_key"):
                    # These really should be provided
                    if strict:
                        missing_keys.append(key)

    if missing_keys:
        raise MetadataValidationError(
            f"Missing required metadata keys: {missing_keys}",
            missing_keys=missing_keys
        )

    # Normalize boolean fields
    if "is_active" in normalized:
        val = normalized["is_active"]
        if isinstance(val, str):
            normalized["is_active"] = val.lower() in ("true", "1", "yes")
        else:
            normalized["is_active"] = bool(val)

    # Normalize paths
    if "source_path" in normalized and normalized["source_path"]:
        path_str = normalized["source_path"]
        if path_str != "inline":
            path = Path(path_str)
            if path.exists():
                normalized["source_path"] = str(path.resolve())

    return normalized


def normalize_for_chroma(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize metadata for ChromaDB storage.

    ChromaDB has restrictions on metadata values:
    - Only str, int, float, bool allowed
    - No None values
    - No nested structures
    """
    result = {}

    for key, value in metadata.items():
        if value is None:
            continue

        # Convert to supported types
        if isinstance(value, (str, int, float, bool)):
            result[key] = value
        elif isinstance(value, (list, dict)):
            # Serialize complex types to JSON string
            import json
            result[key] = json.dumps(value)
        else:
            result[key] = str(value)

    return result


def extract_doc_key_from_metadata(metadata: Dict[str, Any]) -> Optional[str]:
    """Extract doc_key from metadata, with fallbacks."""
    if "doc_key" in metadata:
        return metadata["doc_key"]
    if "source_path" in metadata and metadata["source_path"] != "inline":
        return generate_doc_key(metadata["source_path"])
    return None
