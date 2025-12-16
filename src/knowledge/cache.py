"""
SQLite-based Caching Layer for Knowledge Module
Provides disk-backed caching for chunks and embeddings that survives restarts.

Created: 2025-12-16
Phase: Production-Safe Refactor

Cache key schemes:
- Chunk cache: (file_hash, chunker_config_hash) -> List[ChunkResult]
- Embedding cache: (chunk_text_hash, embedder_spec_hash) -> List[float]

This cache is concurrency-safe using SQLite's built-in locking.
"""

import hashlib
import json
import logging
import pickle
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CacheError(Exception):
    """Base exception for cache errors."""
    pass


class KnowledgeCache:
    """
    SQLite-based cache for chunking and embedding results.

    Thread-safe and concurrency-safe using SQLite's WAL mode.
    Supports TTL-based expiration and max entry limits.
    """

    def __init__(
        self,
        db_path: str = "data/cache/knowledge_cache.db",
        max_entries: int = 100000,
        ttl_days: int = 30
    ):
        """
        Initialize the cache.

        Args:
            db_path: Path to SQLite database file
            max_entries: Maximum cache entries before cleanup
            ttl_days: Time-to-live for cache entries in days
        """
        self.db_path = Path(db_path)
        self.max_entries = max_entries
        self.ttl_days = ttl_days
        self._local = threading.local()

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

        logger.info(f"KnowledgeCache initialized: path={db_path}, max_entries={max_entries}, ttl_days={ttl_days}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                check_same_thread=False
            )
            # Enable WAL mode for better concurrency
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    @contextmanager
    def _cursor(self):
        """Get a database cursor with automatic commit/rollback."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def _init_db(self) -> None:
        """Initialize database tables."""
        with self._cursor() as cursor:
            # Chunk cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunk_cache (
                    cache_key TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    chunker_config_hash TEXT NOT NULL,
                    chunks_data BLOB NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 1
                )
            """)

            # Embedding cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embedding_cache (
                    cache_key TEXT PRIMARY KEY,
                    text_hash TEXT NOT NULL,
                    embedder_spec_hash TEXT NOT NULL,
                    embedding_data BLOB NOT NULL,
                    dimensions INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 1
                )
            """)

            # Create indexes for efficient lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunk_expires
                ON chunk_cache(expires_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embedding_expires
                ON embedding_cache(expires_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunk_file_hash
                ON chunk_cache(file_hash)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embedding_text_hash
                ON embedding_cache(text_hash)
            """)

    def _make_chunk_cache_key(self, file_hash: str, chunker_config_hash: str) -> str:
        """Generate cache key for chunk cache."""
        return hashlib.sha256(f"chunk|{file_hash}|{chunker_config_hash}".encode()).hexdigest()

    def _make_embedding_cache_key(self, text_hash: str, embedder_spec_hash: str) -> str:
        """Generate cache key for embedding cache."""
        return hashlib.sha256(f"embed|{text_hash}|{embedder_spec_hash}".encode()).hexdigest()

    @staticmethod
    def compute_text_hash(text: str) -> str:
        """Compute hash of text content for cache key."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # =========================================================================
    # Chunk Cache Operations
    # =========================================================================

    def get_chunks(
        self,
        file_hash: str,
        chunker_config_hash: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached chunks for a file.

        Args:
            file_hash: MD5 hash of the source file
            chunker_config_hash: Hash of chunker configuration

        Returns:
            List of chunk dictionaries if cached, None otherwise
        """
        cache_key = self._make_chunk_cache_key(file_hash, chunker_config_hash)
        now = datetime.utcnow().isoformat()

        with self._cursor() as cursor:
            cursor.execute("""
                SELECT chunks_data, chunk_count
                FROM chunk_cache
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, now))

            row = cursor.fetchone()
            if row is None:
                return None

            # Update access count
            cursor.execute("""
                UPDATE chunk_cache SET access_count = access_count + 1
                WHERE cache_key = ?
            """, (cache_key,))

            try:
                chunks = pickle.loads(row["chunks_data"])
                logger.debug(f"Chunk cache hit: {row['chunk_count']} chunks")
                return chunks
            except Exception as e:
                logger.warning(f"Failed to deserialize cached chunks: {e}")
                return None

    def set_chunks(
        self,
        file_hash: str,
        chunker_config_hash: str,
        chunks: List[Dict[str, Any]]
    ) -> None:
        """
        Cache chunks for a file.

        Args:
            file_hash: MD5 hash of the source file
            chunker_config_hash: Hash of chunker configuration
            chunks: List of chunk dictionaries to cache
        """
        cache_key = self._make_chunk_cache_key(file_hash, chunker_config_hash)
        now = datetime.utcnow()
        expires_at = now + timedelta(days=self.ttl_days)

        chunks_data = pickle.dumps(chunks)

        with self._cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO chunk_cache
                (cache_key, file_hash, chunker_config_hash, chunks_data, chunk_count, created_at, expires_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                cache_key,
                file_hash,
                chunker_config_hash,
                chunks_data,
                len(chunks),
                now.isoformat(),
                expires_at.isoformat()
            ))

        logger.debug(f"Cached {len(chunks)} chunks for file_hash={file_hash[:16]}...")

    def invalidate_chunks(self, file_hash: str) -> int:
        """
        Invalidate all cached chunks for a file.

        Args:
            file_hash: MD5 hash of the source file

        Returns:
            Number of entries invalidated
        """
        with self._cursor() as cursor:
            cursor.execute("DELETE FROM chunk_cache WHERE file_hash = ?", (file_hash,))
            count = cursor.rowcount
            if count > 0:
                logger.debug(f"Invalidated {count} chunk cache entries for file_hash={file_hash[:16]}...")
            return count

    # =========================================================================
    # Embedding Cache Operations
    # =========================================================================

    def get_embedding(
        self,
        text_hash: str,
        embedder_spec_hash: str
    ) -> Optional[List[float]]:
        """
        Retrieve cached embedding for text.

        Args:
            text_hash: Hash of the text content
            embedder_spec_hash: Hash of embedder specification

        Returns:
            Embedding vector if cached, None otherwise
        """
        cache_key = self._make_embedding_cache_key(text_hash, embedder_spec_hash)
        now = datetime.utcnow().isoformat()

        with self._cursor() as cursor:
            cursor.execute("""
                SELECT embedding_data, dimensions
                FROM embedding_cache
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, now))

            row = cursor.fetchone()
            if row is None:
                return None

            # Update access count
            cursor.execute("""
                UPDATE embedding_cache SET access_count = access_count + 1
                WHERE cache_key = ?
            """, (cache_key,))

            try:
                embedding = pickle.loads(row["embedding_data"])
                return embedding
            except Exception as e:
                logger.warning(f"Failed to deserialize cached embedding: {e}")
                return None

    def get_embeddings_batch(
        self,
        text_hashes: List[str],
        embedder_spec_hash: str
    ) -> Dict[str, List[float]]:
        """
        Retrieve cached embeddings for multiple texts.

        Args:
            text_hashes: List of text content hashes
            embedder_spec_hash: Hash of embedder specification

        Returns:
            Dictionary mapping text_hash -> embedding for found entries
        """
        if not text_hashes:
            return {}

        cache_keys = [
            self._make_embedding_cache_key(th, embedder_spec_hash)
            for th in text_hashes
        ]
        now = datetime.utcnow().isoformat()

        results = {}

        with self._cursor() as cursor:
            # Query in batches to avoid parameter limit
            batch_size = 100
            for i in range(0, len(cache_keys), batch_size):
                batch_keys = cache_keys[i:i + batch_size]
                batch_text_hashes = text_hashes[i:i + batch_size]
                placeholders = ",".join(["?"] * len(batch_keys))

                cursor.execute(f"""
                    SELECT cache_key, embedding_data
                    FROM embedding_cache
                    WHERE cache_key IN ({placeholders}) AND expires_at > ?
                """, (*batch_keys, now))

                for row in cursor.fetchall():
                    # Find corresponding text_hash
                    idx = cache_keys.index(row["cache_key"])
                    if idx < len(text_hashes):
                        try:
                            embedding = pickle.loads(row["embedding_data"])
                            results[text_hashes[idx]] = embedding
                        except Exception:
                            pass

        return results

    def set_embedding(
        self,
        text_hash: str,
        embedder_spec_hash: str,
        embedding: List[float]
    ) -> None:
        """
        Cache embedding for text.

        Args:
            text_hash: Hash of the text content
            embedder_spec_hash: Hash of embedder specification
            embedding: Embedding vector to cache
        """
        cache_key = self._make_embedding_cache_key(text_hash, embedder_spec_hash)
        now = datetime.utcnow()
        expires_at = now + timedelta(days=self.ttl_days)

        embedding_data = pickle.dumps(embedding)

        with self._cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO embedding_cache
                (cache_key, text_hash, embedder_spec_hash, embedding_data, dimensions, created_at, expires_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                cache_key,
                text_hash,
                embedder_spec_hash,
                embedding_data,
                len(embedding),
                now.isoformat(),
                expires_at.isoformat()
            ))

    def set_embeddings_batch(
        self,
        embeddings: Dict[str, List[float]],
        embedder_spec_hash: str
    ) -> None:
        """
        Cache multiple embeddings.

        Args:
            embeddings: Dictionary mapping text_hash -> embedding
            embedder_spec_hash: Hash of embedder specification
        """
        if not embeddings:
            return

        now = datetime.utcnow()
        expires_at = now + timedelta(days=self.ttl_days)

        with self._cursor() as cursor:
            for text_hash, embedding in embeddings.items():
                cache_key = self._make_embedding_cache_key(text_hash, embedder_spec_hash)
                embedding_data = pickle.dumps(embedding)

                cursor.execute("""
                    INSERT OR REPLACE INTO embedding_cache
                    (cache_key, text_hash, embedder_spec_hash, embedding_data, dimensions, created_at, expires_at, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    cache_key,
                    text_hash,
                    embedder_spec_hash,
                    embedding_data,
                    len(embedding),
                    now.isoformat(),
                    expires_at.isoformat()
                ))

        logger.debug(f"Cached {len(embeddings)} embeddings")

    # =========================================================================
    # Maintenance Operations
    # =========================================================================

    def cleanup_expired(self) -> Tuple[int, int]:
        """
        Remove expired cache entries.

        Returns:
            Tuple of (chunks_removed, embeddings_removed)
        """
        now = datetime.utcnow().isoformat()

        with self._cursor() as cursor:
            cursor.execute("DELETE FROM chunk_cache WHERE expires_at < ?", (now,))
            chunks_removed = cursor.rowcount

            cursor.execute("DELETE FROM embedding_cache WHERE expires_at < ?", (now,))
            embeddings_removed = cursor.rowcount

        if chunks_removed > 0 or embeddings_removed > 0:
            logger.info(f"Cache cleanup: removed {chunks_removed} chunks, {embeddings_removed} embeddings")

        return chunks_removed, embeddings_removed

    def cleanup_if_needed(self) -> None:
        """Cleanup if cache exceeds max entries."""
        with self._cursor() as cursor:
            # Check total entries
            cursor.execute("SELECT COUNT(*) FROM chunk_cache")
            chunk_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM embedding_cache")
            embedding_count = cursor.fetchone()[0]

            total = chunk_count + embedding_count

            if total > self.max_entries:
                # First, remove expired
                self.cleanup_expired()

                # If still over limit, remove least recently accessed
                overflow = total - self.max_entries
                if overflow > 0:
                    # Remove from both tables proportionally
                    chunk_remove = int(overflow * (chunk_count / total))
                    embedding_remove = overflow - chunk_remove

                    if chunk_remove > 0:
                        cursor.execute("""
                            DELETE FROM chunk_cache
                            WHERE cache_key IN (
                                SELECT cache_key FROM chunk_cache
                                ORDER BY access_count ASC, created_at ASC
                                LIMIT ?
                            )
                        """, (chunk_remove,))

                    if embedding_remove > 0:
                        cursor.execute("""
                            DELETE FROM embedding_cache
                            WHERE cache_key IN (
                                SELECT cache_key FROM embedding_cache
                                ORDER BY access_count ASC, created_at ASC
                                LIMIT ?
                            )
                        """, (embedding_remove,))

                    logger.info(f"Cache LRU cleanup: removed {chunk_remove} chunks, {embedding_remove} embeddings")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*), SUM(chunk_count) FROM chunk_cache")
            row = cursor.fetchone()
            chunk_entries = row[0]
            total_chunks = row[1] or 0

            cursor.execute("SELECT COUNT(*) FROM embedding_cache")
            embedding_entries = cursor.fetchone()[0]

            cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]

        return {
            "chunk_entries": chunk_entries,
            "total_cached_chunks": total_chunks,
            "embedding_entries": embedding_entries,
            "db_size_bytes": db_size,
            "db_path": str(self.db_path),
            "max_entries": self.max_entries,
            "ttl_days": self.ttl_days,
        }

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._cursor() as cursor:
            cursor.execute("DELETE FROM chunk_cache")
            cursor.execute("DELETE FROM embedding_cache")
            cursor.execute("VACUUM")
        logger.info("Cache cleared")

    def close(self) -> None:
        """Close database connection."""
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None


# Singleton cache instance (lazy-loaded)
_cache_instance: Optional[KnowledgeCache] = None


def get_cache(
    db_path: Optional[str] = None,
    max_entries: int = 100000,
    ttl_days: int = 30
) -> KnowledgeCache:
    """Get or create the singleton cache instance."""
    global _cache_instance
    if _cache_instance is None:
        from src.knowledge.config import get_config
        config = get_config()

        if db_path is None:
            db_path = config.cache.db_path

        _cache_instance = KnowledgeCache(
            db_path=db_path,
            max_entries=config.cache.max_entries,
            ttl_days=config.cache.ttl_days
        )
    return _cache_instance


def reset_cache() -> None:
    """Reset the singleton cache instance (for testing)."""
    global _cache_instance
    if _cache_instance is not None:
        _cache_instance.close()
    _cache_instance = None
