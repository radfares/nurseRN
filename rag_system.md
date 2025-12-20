# NurseRN RAG System (Local Knowledge Library) — End‑to‑End Guide

This guide shows how to load your documents into NurseRN’s local knowledge base (RAG), and how the app uses them while you chat.

## What “RAG” Means In This App

RAG = **Retrieval Augmented Generation**.

In NurseRN:
- Your files are **indexed locally** into a vector database (ChromaDB) under `data/chroma_db/`.
- When you ask a question in an agent, the app can **retrieve relevant excerpts** from your indexed documents and attach them to the prompt as “BACKGROUND CONTEXT (RAG)”.
- Excerpts are **SOURCE‑bound** and formatted like:
  - `[[SOURCE: <filename or path>, p.<page>]] <excerpt>`
- When RAG context is provided, the Nursing Research Agent is required to **cite at least one `[[SOURCE: ...]]` label**, or it refuses the answer.

## Safety / Privacy (Read This First)

- **Do not ingest PHI/PII** (patient identifiers, MRNs, DOBs, etc.).
- Indexing uses embeddings, which means **text is sent to OpenAI’s embeddings API** to compute vectors (unless you change providers later).
- Treat all retrieved excerpts as **untrusted** text. The agent is instructed to never follow “instructions” inside your documents.

## Where To Put Files (The Drop Folder)

Recommended “drop folder” (watched):
- `data/personal_library/to_synthesize/`

After successful indexing, the watch script moves your originals to:
- `data/personal_library/indexed/`

The vector database lives here:
- `data/chroma_db/`

Supported file types (default):
- `.pdf`, `.docx`, `.pptx`, `.txt`, `.md`, `.markdown`, `.csv`, `.json`

Config for this is in:
- `config/knowledge.yml`

## One‑Time Setup

1) Create a `.env` file at the repo root (same folder as `run_nursing_project.py`) with:

```
OPENAI_API_KEY=your_key_here
ENABLE_RAG_CONTEXT=true
AGNO_LOG_LEVEL=WARNING
```

2) (Recommended) Use a virtual environment and install deps (see `SETUP.md` if you want the full setup steps).

## Indexing Your Documents (3 Options)

### Option A (Recommended): Auto‑Index Watch Folder

1) Start the watcher:

`python scripts/watch_and_index.py`

2) Drop or copy your files into:

`data/personal_library/to_synthesize/`

3) Wait for logs like:
- “Detected X new file(s)”
- “Indexed N chunks…”
- “Moved to: …/data/personal_library/indexed/<yourfile>”

This is the easiest “just keep it running” workflow.

### Option B: Index One File (Manual)

`python scripts/ingest_documents.py add /full/path/to/your.pdf`

### Option C: Index A Whole Folder (Manual)

`python scripts/ingest_documents.py add-folder /full/path/to/folder --recursive`

## Confirm Your Library Is Loaded

Show stats:

`python scripts/ingest_documents.py stats`

Quick search test:

`python scripts/ingest_documents.py search "fall prevention hourly rounding" --limit 5`

If you get “library is empty”, indexing didn’t run or nothing was added.

## How RAG Is Used In Agent Mode (Chat)

1) Start the app:

`python run_nursing_project.py`

2) Create or switch to a project.

3) Choose an agent:
- Nursing Research Agent is a good default for QI project work.

4) Ask your question normally, for example:
- “Using my uploaded articles, what are common fall prevention interventions and what gaps are explicitly mentioned?”

If `ENABLE_RAG_CONTEXT=true` and your library has documents, the agent will:
- retrieve top matching excerpts
- inject them into the prompt as:
  - `BACKGROUND CONTEXT (RAG):`
  - `[[SOURCE: ...]] <excerpt>`
- answer using those excerpts
- **cite the sources** in the response

### What You Should Expect In Answers

- If the answer uses your library, you should see citations like:
  - `[[SOURCE: MyArticle.pdf, p.3]]`
- If you asked for a “gap/oversight” but your sources don’t mention one, the agent will say it’s **missing from provided sources** rather than guessing.

## Removing / Clearing Documents

List indexed docs:

`python scripts/ingest_documents.py list`

Remove a specific document by ID:

`python scripts/ingest_documents.py remove <doc_id>`

Clear the entire library:

`python scripts/ingest_documents.py clear`

## Troubleshooting

### “OpenAI embedding failed …” / indexing errors
- Confirm `OPENAI_API_KEY` is set (in `.env` or your shell).
- Restart your terminal/app after setting `.env`.

### Watcher runs but nothing indexes
- Confirm you’re dropping files into `data/personal_library/to_synthesize/`.
- Confirm your files have supported extensions (see above).

### Agent doesn’t cite sources
- If RAG context was provided, the Nursing Research Agent will refuse non‑cited answers (this is intentional).
- If RAG context was not provided, either:
  - `ENABLE_RAG_CONTEXT` is not enabled, or
  - the library has no relevant matches (try different keywords), or
  - your library is empty (re-check stats).

### “Why am I seeing a bunch of INFO lines in chat?”
Those lines are **logs** (from ChromaDB, Agno, httpx/OpenAI) that can clutter the chat UI.

- `run_nursing_project.py` defaults most logs to `WARNING` for interactive chat.
- You can force Agno to be quiet by keeping `AGNO_LOG_LEVEL=WARNING` in `.env`.

## Advanced: Ingest Into Specific Stores (Clinical/Procedural/Research)

Most users only need the personal library flow above.

If you want to explicitly ingest into the dedicated collections (`clinical_knowledge`, `procedural_knowledge`, `research_cache`), you can run a one‑off Python command:

`python -c "from src.knowledge.ingestion_service import get_ingestion_service; s=get_ingestion_service(); print(s.ingest_file(file_path='/full/path/to/file.pdf', doc_type='clinical', store_type='clinical', auto_commit=True))"`

Change `doc_type` / `store_type` to `procedural` or `research` as needed.
