"""
Knowledge Module Configuration
Pydantic-based configuration with YAML file + environment variable override.

Created: 2025-12-16
Phase: Production-Safe Refactor

Environment variables override YAML values with prefix KNOWLEDGE_
Example: KNOWLEDGE_DB_PATH overrides stores.db_path
"""

import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

# Default config file location
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "knowledge.yml"


class EmbedderConfig(BaseModel):
    """Configuration for embedding model."""
    provider: str = Field(default="openai", description="Embedding provider (openai, etc.)")
    model: str = Field(default="text-embedding-3-small", description="Model identifier")
    dimensions: int = Field(default=1536, description="Embedding dimensions")
    batch_size: int = Field(default=100, description="Batch size for embedding calls")

    def get_spec_hash(self) -> str:
        """Generate deterministic hash for this embedder specification."""
        spec_str = f"{self.provider}|{self.model}|{self.dimensions}"
        return hashlib.sha256(spec_str.encode()).hexdigest()[:16]


class ChunkerConfig(BaseModel):
    """Configuration for a specific chunking strategy."""
    strategy: str = Field(default="token", description="Chunking strategy (token, semantic, sentence)")
    chunk_size: int = Field(default=400, description="Target chunk size (tokens or chars)")
    overlap: int = Field(default=50, description="Overlap between chunks")
    # Strategy-specific params
    sentences_per_chunk: Optional[int] = Field(default=None, description="For sentence chunker")
    overlap_sentences: Optional[int] = Field(default=None, description="For sentence chunker")

    def get_config_hash(self) -> str:
        """Generate deterministic hash for this chunker configuration."""
        spec_str = f"{self.strategy}|{self.chunk_size}|{self.overlap}"
        if self.sentences_per_chunk is not None:
            spec_str += f"|{self.sentences_per_chunk}|{self.overlap_sentences}"
        return hashlib.sha256(spec_str.encode()).hexdigest()[:16]


class StoreConfig(BaseModel):
    """Configuration for a vector store collection."""
    collection_name: str = Field(..., description="ChromaDB collection name")
    store_type: str = Field(..., description="Logical store type (clinical, procedural, etc.)")


class CacheConfig(BaseModel):
    """Configuration for caching layer."""
    enabled: bool = Field(default=True, description="Enable caching")
    db_path: str = Field(default="data/cache/knowledge_cache.db", description="SQLite cache database path")
    chunk_cache_enabled: bool = Field(default=True, description="Cache chunking results")
    embedding_cache_enabled: bool = Field(default=True, description="Cache embeddings")
    max_entries: int = Field(default=100000, description="Maximum cache entries before cleanup")
    ttl_days: int = Field(default=30, description="Cache entry TTL in days")


# Default search limit (used when config unavailable)
DEFAULT_MAX_RESULTS = 20


class PersonalLibraryConfig(BaseModel):
    """Configuration for personal library search defaults."""
    max_results: int = Field(default=DEFAULT_MAX_RESULTS, description="Default max results for personal library search")
    min_score: float = Field(default=0.1, description="Minimum relevance score threshold")


class RAGConfig(BaseModel):
    """Configuration for RAG enhancement service."""
    default_k: int = Field(default=10, description="Default number of results to retrieve")
    max_k: int = Field(default=50, description="Hard cap on retrieval count")
    score_threshold: float = Field(default=0.1, description="Minimum relevance score")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")


class KnowledgeConfig(BaseModel):
    """
    Root configuration for the knowledge module.

    Load order:
    1. Default values
    2. YAML file (config/knowledge.yml)
    3. Environment variables (KNOWLEDGE_ prefix)
    """

    # Database/Store settings
    db_path: str = Field(default="data/chroma_db", description="ChromaDB storage path")

    # Embedder configuration
    embedder: EmbedderConfig = Field(default_factory=EmbedderConfig)

    # Chunking strategies per doc_type
    chunking: Dict[str, ChunkerConfig] = Field(
        default_factory=lambda: {
            "clinical": ChunkerConfig(strategy="semantic", chunk_size=500, overlap=50),
            "procedural": ChunkerConfig(strategy="sentence", chunk_size=400, overlap=50,
                                        sentences_per_chunk=5, overlap_sentences=1),
            "research": ChunkerConfig(strategy="token", chunk_size=400, overlap=50),
            "default": ChunkerConfig(strategy="token", chunk_size=400, overlap=50),
        }
    )

    # Store routing: store_type -> collection_name
    stores: Dict[str, StoreConfig] = Field(
        default_factory=lambda: {
            "personal": StoreConfig(collection_name="personal_docs", store_type="personal"),
            "clinical": StoreConfig(collection_name="clinical_knowledge", store_type="clinical"),
            "procedural": StoreConfig(collection_name="procedural_knowledge", store_type="procedural"),
            "research": StoreConfig(collection_name="research_cache", store_type="research"),
        }
    )

    # Cache configuration
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # Personal library search defaults
    personal_library: PersonalLibraryConfig = Field(default_factory=PersonalLibraryConfig)

    # RAG enhancement settings
    rag: RAGConfig = Field(default_factory=RAGConfig)

    # Ingestion settings
    supported_extensions: List[str] = Field(
        default=[".pdf", ".docx", ".pptx", ".txt", ".md", ".markdown", ".csv", ".json"],
        description="Supported file extensions for ingestion"
    )

    @field_validator("db_path")
    @classmethod
    def validate_db_path(cls, v: str) -> str:
        """Ensure db_path is a valid path string."""
        if not v:
            return "data/chroma_db"
        return str(Path(v))

    def get_store_config(self, store_type: str) -> StoreConfig:
        """Get store configuration by type, with fallback to personal."""
        return self.stores.get(store_type, self.stores.get("personal",
            StoreConfig(collection_name="personal_docs", store_type="personal")))

    def get_chunker_config(self, doc_type: str) -> ChunkerConfig:
        """Get chunker configuration by doc type, with fallback to default."""
        return self.chunking.get(doc_type, self.chunking.get("default",
            ChunkerConfig(strategy="token", chunk_size=400, overlap=50)))


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_env_overrides(config_dict: Dict[str, Any], prefix: str = "KNOWLEDGE") -> Dict[str, Any]:
    """
    Apply environment variable overrides to config dictionary.

    Environment variable naming convention:
    - KNOWLEDGE_DB_PATH -> db_path
    - KNOWLEDGE_EMBEDDER_MODEL -> embedder.model
    - KNOWLEDGE_CACHE_ENABLED -> cache.enabled
    """
    result = config_dict.copy()

    # Simple top-level overrides
    env_mappings = {
        f"{prefix}_DB_PATH": "db_path",
        f"{prefix}_EMBEDDER_PROVIDER": ("embedder", "provider"),
        f"{prefix}_EMBEDDER_MODEL": ("embedder", "model"),
        f"{prefix}_EMBEDDER_DIMENSIONS": ("embedder", "dimensions"),
        f"{prefix}_EMBEDDER_BATCH_SIZE": ("embedder", "batch_size"),
        f"{prefix}_CACHE_ENABLED": ("cache", "enabled"),
        f"{prefix}_CACHE_DB_PATH": ("cache", "db_path"),
        f"{prefix}_CACHE_TTL_DAYS": ("cache", "ttl_days"),
        f"{prefix}_PERSONAL_LIBRARY_MAX_RESULTS": ("personal_library", "max_results"),
        f"{prefix}_PERSONAL_LIBRARY_MIN_SCORE": ("personal_library", "min_score"),
        f"{prefix}_RAG_DEFAULT_K": ("rag", "default_k"),
        f"{prefix}_RAG_MAX_K": ("rag", "max_k"),
        f"{prefix}_RAG_SCORE_THRESHOLD": ("rag", "score_threshold"),
        f"{prefix}_RAG_CACHE_TTL_SECONDS": ("rag", "cache_ttl_seconds"),
    }

    for env_var, path in env_mappings.items():
        value = os.environ.get(env_var)
        if value is not None:
            # Convert types appropriately
            if isinstance(path, tuple):
                # Nested path
                if path[0] not in result:
                    result[path[0]] = {}

                # Type conversion based on field name
                if path[1] in ("dimensions", "batch_size", "ttl_days", "max_entries", "default_k", "max_k", "cache_ttl_seconds"):
                    value = int(value)
                elif path[1] == "enabled":
                    value = value.lower() in ("true", "1", "yes")
                elif path[1] == "max_results":
                    value = int(value)
                elif path[1] in ("min_score", "score_threshold"):
                    value = float(value)

                result[path[0]][path[1]] = value
            else:
                result[path] = value

            logger.debug(f"Applied env override: {env_var} -> {path}")

    return result


def load_config(
    config_path: Optional[Union[str, Path]] = None,
    env_prefix: str = "KNOWLEDGE"
) -> KnowledgeConfig:
    """
    Load configuration from YAML file with environment variable overrides.

    Args:
        config_path: Path to YAML config file (default: config/knowledge.yml)
        env_prefix: Prefix for environment variables (default: KNOWLEDGE)

    Returns:
        KnowledgeConfig instance

    Load order:
        1. Default values from Pydantic models
        2. YAML file values (if file exists)
        3. Environment variable overrides
    """
    config_dict: Dict[str, Any] = {}

    # Determine config path
    if config_path is None:
        config_path = os.environ.get(f"{env_prefix}_CONFIG_PATH", str(DEFAULT_CONFIG_PATH))

    config_path = Path(config_path)

    # Load YAML if exists
    if config_path.exists():
        try:
            import yaml
            with open(config_path, "r") as f:
                yaml_config = yaml.safe_load(f) or {}
            config_dict = _deep_merge(config_dict, yaml_config)
            logger.info(f"Loaded config from {config_path}")
        except ImportError:
            logger.warning("PyYAML not installed, skipping YAML config loading")
        except Exception as e:
            logger.warning(f"Failed to load YAML config from {config_path}: {e}")
    else:
        logger.debug(f"Config file not found: {config_path}, using defaults")

    # Apply environment variable overrides
    config_dict = _apply_env_overrides(config_dict, env_prefix)

    # Create and return config object
    return KnowledgeConfig(**config_dict)


# Singleton config instance (lazy-loaded)
_config_instance: Optional[KnowledgeConfig] = None


def get_config() -> KnowledgeConfig:
    """Get the singleton configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance


def reset_config() -> None:
    """Reset the singleton config instance (for testing)."""
    global _config_instance
    _config_instance = None


def set_config(config: KnowledgeConfig) -> None:
    """Set a specific config instance (for testing)."""
    global _config_instance
    _config_instance = config
