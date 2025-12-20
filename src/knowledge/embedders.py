"""
Embedder Factory for Knowledge Module
Provides pluggable embedding providers with a stable interface.

Created: 2025-12-16
Phase: Production-Safe Refactor

Supports:
- OpenAI (default)
- Extensible for future providers (Cohere, local models, etc.)

Important: Never mix embedding models in the same active collection.
If embedder spec changes, a new collection version is required.
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from src.knowledge.config import EmbedderConfig, get_config
from src.knowledge.cache import get_cache, KnowledgeCache

logger = logging.getLogger(__name__)


class EmbedderError(Exception):
    """Base exception for embedder errors."""
    pass


class EmbedderSpec:
    """
    Immutable specification for an embedder.

    Used to generate deterministic hashes and verify embedder compatibility.
    """

    def __init__(self, provider: str, model: str, dimensions: int):
        self.provider = provider
        self.model = model
        self.dimensions = dimensions
        self._hash: Optional[str] = None

    def get_hash(self) -> str:
        """Get deterministic hash for this embedder specification."""
        if self._hash is None:
            spec_str = f"{self.provider}|{self.model}|{self.dimensions}"
            self._hash = hashlib.sha256(spec_str.encode()).hexdigest()[:16]
        return self._hash

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EmbedderSpec):
            return False
        return (self.provider == other.provider and
                self.model == other.model and
                self.dimensions == other.dimensions)

    def __hash__(self) -> int:
        return hash((self.provider, self.model, self.dimensions))

    def __repr__(self) -> str:
        return f"EmbedderSpec({self.provider}/{self.model}, dim={self.dimensions})"

    @classmethod
    def from_config(cls, config: EmbedderConfig) -> "EmbedderSpec":
        """Create from EmbedderConfig."""
        return cls(
            provider=config.provider,
            model=config.model,
            dimensions=config.dimensions
        )


class BaseEmbedder(ABC):
    """Abstract base class for embedders."""

    def __init__(self, spec: EmbedderSpec, batch_size: int = 100):
        self.spec = spec
        self.batch_size = batch_size
        self._call_count = 0

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        pass

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        results = self.embed_texts([text])
        return results[0] if results else []

    def get_call_count(self) -> int:
        """Get number of API calls made (for testing/monitoring)."""
        return self._call_count

    def reset_call_count(self) -> None:
        """Reset call counter."""
        self._call_count = 0


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embedder using agno's OpenAIEmbedder wrapper."""

    def __init__(
        self,
        spec: EmbedderSpec,
        batch_size: int = 100,
        api_key: Optional[str] = None
    ):
        super().__init__(spec, batch_size)
        self.api_key = api_key
        self._embedder = None

    def _get_embedder(self):
        """Lazy-load the agno OpenAI embedder."""
        if self._embedder is None:
            try:
                from agno.knowledge.embedder.openai import OpenAIEmbedder as AgnoOpenAIEmbedder
                self._embedder = AgnoOpenAIEmbedder(
                    id=self.spec.model,
                    dimensions=self.spec.dimensions if self.spec.dimensions != 1536 else None
                )
            except ImportError as e:
                raise EmbedderError(f"Failed to import agno OpenAI embedder: {e}")
        return self._embedder

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using OpenAI API."""
        if not texts:
            return []

        embedder = self._get_embedder()
        all_embeddings: List[List[float]] = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]

            try:
                if hasattr(embedder, "get_embeddings"):
                    embeddings = embedder.get_embeddings(batch)
                elif hasattr(embedder, "client"):
                    req: Dict[str, Any] = {
                        "input": batch,
                        "model": getattr(embedder, "id", self.spec.model),
                        "encoding_format": getattr(embedder, "encoding_format", "float"),
                    }
                    user = getattr(embedder, "user", None)
                    if user is not None:
                        req["user"] = user

                    model_id = req["model"]
                    if isinstance(model_id, str) and model_id.startswith("text-embedding-3"):
                        dims = getattr(embedder, "dimensions", None)
                        if dims is not None:
                            req["dimensions"] = dims

                    request_params = getattr(embedder, "request_params", None)
                    if isinstance(request_params, dict) and request_params:
                        req.update(request_params)

                    response = embedder.client.embeddings.create(**req)
                    embeddings = [item.embedding for item in response.data]
                else:
                    embeddings = [embedder.get_embedding(text) for text in batch]

                all_embeddings.extend(embeddings)
                self._call_count += 1
            except Exception as e:
                logger.error(f"OpenAI embedding failed: {e}")
                raise EmbedderError(f"Embedding failed: {e}")

        return all_embeddings


class CachedEmbedder(BaseEmbedder):
    """
    Embedder wrapper that caches results.

    Checks cache before calling underlying embedder, reducing API calls.
    """

    def __init__(
        self,
        underlying: BaseEmbedder,
        cache: Optional[KnowledgeCache] = None
    ):
        super().__init__(underlying.spec, underlying.batch_size)
        self.underlying = underlying
        self._cache = cache

    @property
    def cache(self) -> KnowledgeCache:
        if self._cache is None:
            self._cache = get_cache()
        return self._cache

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts, using cache where possible."""
        if not texts:
            return []

        spec_hash = self.spec.get_hash()

        # Compute text hashes
        text_hashes = [self.cache.compute_text_hash(t) for t in texts]

        # Check cache for existing embeddings
        cached = self.cache.get_embeddings_batch(text_hashes, spec_hash)

        # Determine which texts need embedding
        results: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        for i, (text, text_hash) in enumerate(zip(texts, text_hashes)):
            if text_hash in cached:
                results[i] = cached[text_hash]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        cache_hits = len(texts) - len(uncached_texts)
        if cache_hits > 0:
            logger.debug(f"Embedding cache: {cache_hits}/{len(texts)} hits")

        # Embed uncached texts
        if uncached_texts:
            new_embeddings = self.underlying.embed_texts(uncached_texts)

            # Store results and cache them
            new_cache_entries: Dict[str, List[float]] = {}
            for i, (idx, embedding) in enumerate(zip(uncached_indices, new_embeddings)):
                results[idx] = embedding
                new_cache_entries[text_hashes[idx]] = embedding

            # Cache new embeddings
            self.cache.set_embeddings_batch(new_cache_entries, spec_hash)

        return [r for r in results if r is not None]

    def get_call_count(self) -> int:
        """Get underlying embedder call count."""
        return self.underlying.get_call_count()


class EmbedderFactory:
    """
    Factory for creating embedder instances.

    Supports multiple providers and ensures consistency within collections.
    """

    # Registry of available providers
    _providers: Dict[str, Type[BaseEmbedder]] = {
        "openai": OpenAIEmbedder,
    }

    @classmethod
    def register_provider(cls, name: str, embedder_class: Type[BaseEmbedder]) -> None:
        """Register a new embedder provider."""
        cls._providers[name] = embedder_class
        logger.info(f"Registered embedder provider: {name} -> {embedder_class.__name__}")

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())

    @classmethod
    def create(
        cls,
        config: Optional[EmbedderConfig] = None,
        use_cache: bool = True
    ) -> BaseEmbedder:
        """
        Create an embedder instance from configuration.

        Args:
            config: Embedder configuration (uses global config if None)
            use_cache: Whether to wrap with caching layer

        Returns:
            Configured embedder instance
        """
        if config is None:
            config = get_config().embedder

        spec = EmbedderSpec.from_config(config)

        # Get provider class
        provider_class = cls._providers.get(config.provider)
        if provider_class is None:
            available = cls.get_available_providers()
            raise EmbedderError(
                f"Unknown embedder provider: {config.provider}. "
                f"Available: {available}"
            )

        # Create base embedder
        embedder = provider_class(
            spec=spec,
            batch_size=config.batch_size
        )

        # Wrap with cache if enabled
        if use_cache:
            cache_config = get_config().cache
            if cache_config.enabled and cache_config.embedding_cache_enabled:
                embedder = CachedEmbedder(embedder)
                logger.debug("Created cached embedder")

        logger.info(f"Created embedder: {spec}")
        return embedder

    @classmethod
    def create_from_spec(
        cls,
        spec: EmbedderSpec,
        batch_size: int = 100,
        use_cache: bool = True
    ) -> BaseEmbedder:
        """
        Create an embedder from a specification.

        Args:
            spec: Embedder specification
            batch_size: Batch size for API calls
            use_cache: Whether to wrap with caching layer

        Returns:
            Configured embedder instance
        """
        config = EmbedderConfig(
            provider=spec.provider,
            model=spec.model,
            dimensions=spec.dimensions,
            batch_size=batch_size
        )
        return cls.create(config, use_cache)


def get_embedder(use_cache: bool = True) -> BaseEmbedder:
    """
    Get a configured embedder using global configuration.

    Args:
        use_cache: Whether to enable caching

    Returns:
        Configured embedder instance
    """
    return EmbedderFactory.create(use_cache=use_cache)


def get_current_embedder_spec() -> EmbedderSpec:
    """Get the embedder specification from current configuration."""
    config = get_config().embedder
    return EmbedderSpec.from_config(config)
