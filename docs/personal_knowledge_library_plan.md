# Personal Knowledge Library Implementation Plan

## Overview

**Goal:** Build a personal document library that agents can search, designed to scale from Phase B (basic vector search) to Phase C (full RAG pipeline).

**Architecture:** B builds foundation → C adds features on top

---

## Phase B: Vector Search Foundation (1-2 Days)

### B1: Document Processor (4 hours)

**Purpose:** Extract and chunk text from your documents

**File:** `src/knowledge/document_ingester.py`

**Components:**
1. `DocumentIngester` class
2. Uses existing `DocumentReaderTools` for PDF/PPTX extraction
3. Chunks text into ~500 token pieces with overlap
4. Returns structured records ready for embedding

**Schema (future-proofed for C):**
```
{
    "doc_id": "unique_document_identifier",
    "chunk_id": "doc_id_chunk_003",
    "text": "The fall prevention protocol states...",
    "source_path": "/docs/fall_prevention.pdf",
    "source_type": "personal",      # C: "pubmed", "arxiv"
    "page_num": 12,
    "version": 1,                   # C: track versions
    "ingested_at": "2024-12-13",
    "citation_info": null           # C: APA citation
}
```

**Deliverables:**
- [ ] `DocumentIngester` class with `ingest_file()` method
- [ ] Text chunking with configurable size/overlap
- [ ] Metadata extraction (filename, path, date)
- [ ] Error handling for corrupt/unreadable files

---

### B2: Vector Database (4 hours)

**Purpose:** Store embeddings and enable similarity search

**File:** `src/knowledge/vector_store.py`

**Technology:** ChromaDB (free, local, Python-native)

**Components:**
1. `VectorStore` class wrapping ChromaDB
2. Collection management (create, delete, list)
3. Embedding generation using OpenAI embeddings
4. Similarity search with configurable N results

**Collections (designed for C expansion):**
```
personal_docs      # Your PDFs, notes, articles
pubmed_cache       # C: Cached PubMed results
arxiv_cache        # C: Cached ArXiv results
combined_index     # C: Unified search across all
```

**Deliverables:**
- [ ] `VectorStore` class with CRUD operations
- [ ] `add_documents()` method
- [ ] `search()` method returning ranked results
- [ ] `delete_document()` for re-indexing
- [ ] Metadata filtering support

---

### B3: Search Tool (2 hours)

**Purpose:** Agent-callable tool for searching personal library

**File:** `src/knowledge/personal_library_tool.py`

**Components:**
1. `PersonalLibraryTools` class (extends Toolkit)
2. `search_personal_library(query, n_results)` method
3. Returns formatted results with source attribution

**Tool Response Format:**
```
Found 3 relevant sections from your personal library:

1. [fall_prevention.pdf, p.12] (Score: 0.92)
   "The fall prevention protocol requires hourly rounding..."

2. [joint_commission_2024.pdf, p.45] (Score: 0.87)
   "National Patient Safety Goal 9 addresses..."

3. [my_notes.docx, p.3] (Score: 0.81)
   "Key takeaways from the fall prevention workshop..."
```

**Deliverables:**
- [ ] `PersonalLibraryTools` Toolkit class
- [ ] `search_personal_library()` registered tool
- [ ] Formatted output with source/page/score
- [ ] Error handling for empty results

---

### B4: Agent Integration (2 hours)

**Purpose:** Add personal library search to Nursing Research Agent

**File:** Modify `agents/nursing_research_agent.py`

**Changes:**
1. Import `PersonalLibraryTools`
2. Add to toolkit list (after external sources)
3. Update system prompt with usage guidance

**Prompt Addition:**
```
PERSONAL LIBRARY TOOL:
- Use search_personal_library() when user mentions "my notes", 
  "my documents", "files I uploaded", or similar phrases
- Also use when external sources lack relevant results
- Personal library may contain unpublished work, class notes,
  project documents, and saved articles
- Always cite source path and page number from results
```

**Deliverables:**
- [ ] PersonalLibraryTools added to agent
- [ ] System prompt updated
- [ ] Tool priority documented

---

### B5: Ingestion CLI (2 hours)

**Purpose:** Command-line tool to add documents to library

**File:** `scripts/ingest_documents.py`

**Commands:**
```bash
# Ingest single file
python scripts/ingest_documents.py add /path/to/file.pdf

# Ingest entire folder
python scripts/ingest_documents.py add-folder /path/to/docs/

# List indexed documents
python scripts/ingest_documents.py list

# Remove document from index
python scripts/ingest_documents.py remove doc_id

# Show statistics
python scripts/ingest_documents.py stats
```

**Deliverables:**
- [ ] CLI tool with add/remove/list commands
- [ ] Progress bar for bulk ingestion
- [ ] Summary statistics output

---

## Phase B Complete Checklist

- [ ] B1: Document Processor
- [ ] B2: Vector Database
- [ ] B3: Search Tool
- [ ] B4: Agent Integration
- [ ] B5: Ingestion CLI
- [ ] Integration test: Ingest 10 PDFs, search works
- [ ] End-to-end test: Agent uses personal library in response

---

## Phase C: Full RAG Pipeline (Add After B Works)

### C1: Document Versioning (+2 hours)

**Purpose:** Track document changes over time

**Additions:**
- `detect_changes()` - Compare file hash to stored version
- `version` field incremented on re-index
- Option to keep old versions or replace

**Files:**
- Add to `document_ingester.py`
- Add `doc_versions` table/collection

---

### C2: Folder Watcher (+2 hours)

**Purpose:** Auto-index when files change

**Technology:** `watchdog` library

**Components:**
- Background service watching document folder
- Triggers ingestion on file add/modify
- Triggers removal on file delete

**File:** `src/knowledge/folder_watcher.py`

---

### C3: Combined Search (+4 hours)

**Purpose:** Search personal + external sources in one query

**Components:**
- `CombinedSearchTool` merging results from:
  - Personal library (ChromaDB)
  - PubMed (API call or cache)
  - ArXiv (API call or cache)
- Unified ranking by relevance score
- Source type included in results

**File:** `src/knowledge/combined_search.py`

---

### C4: Citation Tracker (+3 hours)

**Purpose:** Track sources used in agent responses

**Components:**
- Log which chunks were retrieved per query
- Generate APA citations for personal docs
- Link back to exact page/paragraph

**File:** `src/knowledge/citation_tracker.py`

---

### C5: External Cache (+4 hours)

**Purpose:** Cache PubMed/ArXiv results locally

**Components:**
- Save successful search results to vector store
- Search cache before hitting API
- TTL-based expiration (e.g., 30 days)

**Benefit:** Faster repeated searches, offline capability

---

## Phase C Complete Checklist

- [ ] C1: Document Versioning
- [ ] C2: Folder Watcher
- [ ] C3: Combined Search
- [ ] C4: Citation Tracker
- [ ] C5: External Cache
- [ ] Integration test: Auto-updates on file change
- [ ] End-to-end test: Combined search returns ranked results

---

## File Structure

```
src/
  knowledge/
    __init__.py
    document_ingester.py       # B1
    vector_store.py            # B2
    personal_library_tool.py   # B3
    folder_watcher.py          # C2
    combined_search.py         # C3
    citation_tracker.py        # C4

scripts/
    ingest_documents.py        # B5

data/
    personal_library/          # Default document folder
    chroma_db/                 # Vector database storage
```

---

## Dependencies

**Phase B:**
```
chromadb>=0.4.0           # Vector database
openai>=1.0.0             # Already have - for embeddings
tiktoken>=0.5.0           # Token counting for chunking
```

**Phase C additions:**
```
watchdog>=3.0.0           # Folder watching
```

---

## Timeline Summary

| Phase | Components | Time | Outcome |
|-------|------------|------|---------|
| **B1** | Document Processor | 4 hrs | Parse PDFs into chunks |
| **B2** | Vector Database | 4 hrs | Store and search embeddings |
| **B3** | Search Tool | 2 hrs | Agent-callable search |
| **B4** | Agent Integration | 2 hrs | Tool in Nursing Agent |
| **B5** | Ingestion CLI | 2 hrs | Easy document management |
| **Total B** | | **14 hrs** | **Working personal library** |
| | | | |
| **C1** | Versioning | 2 hrs | Track document changes |
| **C2** | Folder Watcher | 2 hrs | Auto-sync documents |
| **C3** | Combined Search | 4 hrs | Unified search |
| **C4** | Citation Tracker | 3 hrs | Source attribution |
| **C5** | External Cache | 4 hrs | Faster searches |
| **Total C** | | **15 hrs** | **Full RAG pipeline** |

---

## Getting Started

**Step 1:** Install dependencies
```bash
pip install chromadb tiktoken
```

**Step 2:** Create folder structure
```bash
mkdir -p src/knowledge data/personal_library data/chroma_db
```

**Step 3:** Start with B1 (Document Processor)

---

## Notes

- All Phase B code includes fields/structures needed for Phase C
- No rewrites required when upgrading B → C
- Each C component is independent (add in any order)
- ChromaDB stores data locally (no cloud dependency)
