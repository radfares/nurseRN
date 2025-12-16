# Knowledge Module Refactor - Migration Notes

**Date:** 2025-12-16
**Phase:** Production-Safe Refactor

## Summary

This refactor addresses 4 critical risks in the original design:
1. **Zombie data on updates** - Fixed with two-phase commit
2. **Ingestion schism** - Fixed with single unified API
3. **Metadata drift** - Fixed with schema enforcement
4. **No caching layer** - Fixed with SQLite-backed cache

## New Module Structure

```
src/knowledge/
├── __init__.py           # Updated exports
├── config.py             # NEW: Pydantic config (YAML + env)
├── metadata.py           # NEW: Schema + validation
├── cache.py              # NEW: SQLite chunk/embedding cache
├── embedders.py          # NEW: Pluggable embedder factory
├── ingestion_service.py  # NEW: Unified ingestion API
├── vector_store.py       # UPDATED: Config-driven + is_active filter
├── chunking_strategies.py
├── document_ingester.py  # LEGACY: Still works, but use service
├── clinical_ingestion.py # LEGACY: Still works, but use service
└── personal_library_tool.py
```

## Breaking Changes

### 1. Use KnowledgeIngestionService for All Ingestion

**Before:**
```python
from src.knowledge.document_ingester import DocumentIngester
ingester = DocumentIngester()
chunks = ingester.ingest_file("/path/to/file.pdf")
store.add_chunks(chunks)
```

**After:**
```python
from src.knowledge import ingest_file
result = ingest_file("/path/to/file.pdf")
# or
from src.knowledge import get_ingestion_service
service = get_ingestion_service()
result = service.ingest_file("/path/to/file.pdf", store_type="clinical")
```

### 2. Search Now Filters Active Chunks by Default

**Before:** Search returned all chunks including inactive/zombie data

**After:** Search defaults to `is_active=true`. Use `include_inactive=True` to see all:
```python
# Default: only active chunks
results = store.search("query")

# Include inactive chunks (for debugging)
results = store.search("query", include_inactive=True)
```

### 3. VectorStoreFactory Reads Config

**Before:**
```python
VectorStoreFactory.get_store("clinical", db_path="data/chroma_db")
```

**After:**
```python
# db_path now comes from config by default
VectorStoreFactory.get_store("clinical")
# Can still override if needed
VectorStoreFactory.get_store("clinical", db_path="/custom/path")
```

## Configuration

### Config File Location
`config/knowledge.yml` (or set `KNOWLEDGE_CONFIG_PATH` env var)

### Environment Variable Overrides
All settings can be overridden with `KNOWLEDGE_` prefix:
- `KNOWLEDGE_DB_PATH` - ChromaDB storage path
- `KNOWLEDGE_EMBEDDER_MODEL` - Embedding model
- `KNOWLEDGE_CACHE_ENABLED` - Enable/disable caching

## Usage Examples

### Ingest a File
```bash
python scripts/ingest_documents.py add /path/to/file.pdf
python scripts/ingest_documents.py add /path/to/file.pdf --doc-type clinical
```

### Ingest a Folder
```bash
python scripts/ingest_documents.py add-folder /path/to/docs/ --recursive
```

### Watch for New Files
```bash
python scripts/watch_and_index.py
```

### Programmatic Ingestion
```python
from src.knowledge import (
    ingest_file,
    ingest_text,
    ingest_folder,
    get_config,
)

# Single file
result = ingest_file("/path/to/doc.pdf", doc_type="clinical")
print(f"Ingested {result.chunk_count} chunks")

# Raw text
result = ingest_text(
    "Clinical guidelines for fall prevention...",
    doc_type="clinical",
    source_name="fall_guidelines"
)

# Folder
results = ingest_folder("/path/to/docs/", recursive=True)
for r in results:
    print(f"{r.doc_key}: {r.chunk_count} chunks")
```

### Query with Active Filtering
```python
from src.knowledge import VectorStoreFactory

store = VectorStoreFactory.get_store("clinical")

# Default: only active chunks
results = store.search("fall prevention protocols", limit=5)

# Debug: include inactive chunks
all_results = store.search("fall prevention", include_inactive=True)
```

## Two-Phase Commit Protocol

When updating a document:
1. **STAGE**: New chunks inserted with `is_active=false`
2. **COMMIT**: Staged chunks activated, old chunks deactivated
3. **CLEANUP** (optional): `service.cleanup_inactive()` removes old chunks

This ensures no zombie data remains after updates.

## Cache Benefits

The SQLite cache (`data/cache/knowledge_cache.db`) stores:
- **Chunk cache**: `(file_hash, chunker_config_hash) -> chunks`
- **Embedding cache**: `(text_hash, embedder_spec_hash) -> embedding`

Benefits:
- Re-ingesting same file skips chunking
- Re-embedding same text skips API calls
- Survives restarts
- Thread-safe

## Metadata Schema (R6)

Required metadata keys on every chunk:
- `doc_key`: Stable logical identifier
- `ingestion_run_id`: Version tracking
- `chunk_id`: Deterministic identifier
- `store_type`, `doc_type`, `source_type`, `source_path`
- `file_hash`
- `embedder_spec_hash`, `chunker_config_hash`
- `is_active`, `ingested_at`

## Running Tests

```bash
python -m pytest tests/unit/test_knowledge_refactor.py -v
```

## Files Changed

### New Files
- `src/knowledge/config.py`
- `src/knowledge/metadata.py`
- `src/knowledge/cache.py`
- `src/knowledge/embedders.py`
- `src/knowledge/ingestion_service.py`
- `config/knowledge.yml`
- `tests/unit/test_knowledge_refactor.py`
- `docs/knowledge_refactor_migration.md`

### Updated Files
- `src/knowledge/__init__.py` - New exports
- `src/knowledge/vector_store.py` - Config-driven + is_active filter
- `scripts/ingest_documents.py` - Uses KnowledgeIngestionService
- `scripts/watch_and_index.py` - Uses KnowledgeIngestionService
