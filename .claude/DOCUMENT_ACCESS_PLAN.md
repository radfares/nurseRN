# Document Access Implementation Plan

**Status:** 🔄 In Planning
**Created:** 2025-11-26
**Priority:** High
**Complexity:** Medium

---

## 📋 Executive Summary

Enable all 6 nursing research agents to access, search, and cite documents stored in a project-specific knowledge base. This allows residents to drop research papers, notes, and literature into a folder and have all agents automatically reference this content when answering queries.

---

## 🎯 Goals

### Primary Goals
1. **Document Ingestion** - Import MD/PDF/DOCX/CSV files into project knowledge base
2. **Semantic Search** - Agents find relevant content even with different wording
3. **Auto-Citation** - Agents cite which document information came from
4. **Project-Scoped** - Each project maintains its own knowledge base
5. **Agent Storage** - Agents can save their outputs back to the knowledge base

### Secondary Goals
- Incremental document addition (add files anytime)
- Multi-format support (prioritize MD, PDF, DOCX)
- Persistent storage (survives restarts)
- Version tracking (know when documents were added/updated)

---

## 🏗️ Architecture Overview

```
User's Research Folder
        │
        ▼
  Document Manager ──────► Project Database (metadata)
        │                        │
        │                        └─► documents table
        ▼                              (file_path, extracted_text, tags)
  Vector Knowledge Base
  (LanceDB or ChromaDB)
        │
        └──► Embeddings (OpenAI)
                │
                ▼
        Shared Across All 6 Agents
        (via BaseAgent.knowledge parameter)
```

---

## 📂 Current State Analysis

### ✅ What Already Exists
- **Database Schema:** `documents` table with text extraction fields (lines 267-291 in project_manager.py)
- **Directory Structure:** Each project has `data/projects/{name}/documents/` folder
- **Agno Framework:** Full knowledge base support with readers for PDF, DOCX, CSV, MD, JSON, PPTX
- **Vector DB Options:** ChromaDB, LanceDB, Pinecone, Qdrant (all supported by Agno)
- **Embedders:** OpenAI, HuggingFace, Jina (OpenAI already configured)

### ❌ What's Missing
- Document ingestion logic
- Knowledge base initialization per project
- Integration with BaseAgent
- CLI commands for document management
- Text extraction from PDFs/DOCX
- Agent output storage mechanism

---

## 🚀 Implementation Plan

### Phase 1: Core Document Management (Priority: HIGH)

#### 1.1 Create `document_manager.py` Module

**Location:** `/Users/hdz_agents/Documents/nurseRN/document_manager.py`

**Core Functions:**
```python
class DocumentManager:
    """Manage documents and knowledge base for nursing projects."""

    def __init__(self, project_name: Optional[str] = None):
        """Initialize document manager for project."""

    def ingest_documents(self, source_path: str, copy_files: bool = True) -> Dict:
        """
        Ingest documents from folder into project.

        Args:
            source_path: Path to folder with documents
            copy_files: If True, copy files to project documents/ folder
                       If False, just reference original location

        Returns:
            {
                "ingested": 10,
                "failed": 0,
                "total_size_mb": 1.4,
                "file_types": {"md": 10, "pdf": 0}
            }
        """

    def create_knowledge_base(self) -> Knowledge:
        """
        Create or load vector knowledge base for project.
        Uses LanceDB + OpenAI embeddings.

        Returns:
            Agno Knowledge instance ready for agent use
        """

    def search_documents(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search across all project documents.

        Returns:
            [
                {
                    "content": "extracted text chunk",
                    "source": "falls-ref.md",
                    "relevance": 0.89,
                    "metadata": {...}
                }
            ]
        """

    def list_documents(self) -> List[Dict]:
        """List all documents with metadata."""

    def add_agent_output(self, agent_name: str, content: str,
                        output_type: str, metadata: Dict = None) -> int:
        """
        Save agent output to knowledge base.

        Args:
            agent_name: Which agent created this
            content: The output content
            output_type: "picot", "literature_review", "analysis_plan", etc.
            metadata: Additional context

        Returns:
            document_id of stored output
        """

    def refresh_knowledge_base(self) -> Dict:
        """Re-index all documents (useful after updates)."""
```

**Database Integration:**
- Store file metadata in existing `documents` table
- Track extraction status: pending → extracted → indexed
- Link documents to literature_findings if applicable

**File Handling:**
```python
# Supported formats (Phase 1)
SUPPORTED_FORMATS = {
    'md': 'MarkdownReader',    # Priority 1 (user has 10 MD files)
    'pdf': 'PDFReader',        # Priority 2 (common for research papers)
    'docx': 'DOCXReader',      # Priority 3 (Word documents)
    'txt': 'TextReader',       # Priority 4 (plain text)
    'csv': 'CSVReader',        # Priority 5 (data files)
}

# Phase 2 (if needed)
FUTURE_FORMATS = {
    'pptx': 'PPTXReader',
    'json': 'JSONReader',
    'xlsx': 'ExcelReader'  # Would need custom implementation
}
```

---

#### 1.2 Update `BaseAgent` Class

**File:** `agents/base_agent.py`

**Changes:**
```python
class BaseAgent(ABC):
    def __init__(self, agent_name: str, agent_key: str,
                 tools: list = None, knowledge: Knowledge = None):
        """
        Initialize the base agent.

        Args:
            agent_name: Display name for the agent
            agent_key: Key for database path (e.g., 'medical_research')
            tools: List of tools for the agent (can be None or empty)
            knowledge: Agno Knowledge instance for document search (NEW)
        """
        self.agent_name = agent_name
        self.agent_key = agent_key
        self.tools = tools or []
        self.knowledge = knowledge  # NEW: Store knowledge base reference

        # Setup logging
        self.logger = setup_agent_logging(agent_name)

        # Create the agent (now with knowledge parameter)
        self.agent = self._create_agent()

        # Log initialization
        db_path = get_db_path(agent_key)
        self.logger.info(f"{agent_name} initialized: {db_path}")
        if knowledge:
            self.logger.info(f"  Knowledge base: ENABLED")
```

**Agent Creation Update:**
```python
def _create_agent(self) -> Agent:
    """Create agent with knowledge base if available."""
    return Agent(
        model=OpenAIChat(id=get_model_id(self.agent_key)),
        tools=self.tools,
        knowledge=self.knowledge,  # NEW: Pass knowledge to agent
        search_knowledge=True,     # NEW: Enable automatic search
        db=SqliteDb(db_file=get_db_path(self.agent_key)),
        # ... existing parameters
    )
```

---

#### 1.3 Update Agent Initialization

**File:** `run_nursing_project.py`

**Add Knowledge Base Loading:**
```python
from document_manager import get_document_manager

def load_agents_for_project():
    """Load all agents with shared knowledge base."""

    # Get active project
    pm = get_project_manager()
    active_project = pm.get_active_project()

    if not active_project:
        print("⚠️ No active project. Agents will run without knowledge base.")
        return load_agents_without_knowledge()

    # Load or create knowledge base for project
    dm = get_document_manager(active_project)

    try:
        kb = dm.create_knowledge_base()
        print(f"✅ Knowledge base loaded: {dm.get_document_count()} documents")
    except Exception as e:
        print(f"⚠️ Knowledge base unavailable: {e}")
        print("   Agents will run without document access.")
        kb = None

    # Initialize all agents with shared knowledge base
    nursing_research = NursingResearchAgent(knowledge=kb)
    medical_research = MedicalResearchAgent(knowledge=kb)
    academic_research = AcademicResearchAgent(knowledge=kb)
    writing = ResearchWritingAgent(knowledge=kb)
    timeline = ProjectTimelineAgent(knowledge=kb)
    data_analysis = DataAnalysisAgent(knowledge=kb)

    return {
        'nursing_research': nursing_research,
        'medical_research': medical_research,
        'academic_research': academic_research,
        'writing': writing,
        'timeline': timeline,
        'data_analysis': data_analysis,
    }
```

---

#### 1.4 CLI Commands

**Add to `run_nursing_project.py` main loop:**

```python
# New commands for document management
DOCUMENT_COMMANDS = {
    'ingest': cli_ingest_documents,
    'docs': cli_document_operations,
    'kb': cli_knowledge_base_operations,
}

def cli_ingest_documents(args):
    """
    Ingest documents from a folder.

    Usage:
        ingest /path/to/folder
        ingest /path/to/folder --no-copy  # Reference files, don't copy
    """

def cli_document_operations(args):
    """
    Document management operations.

    Usage:
        docs list                    # List all documents
        docs search "query"          # Search documents
        docs refresh                 # Re-index all documents
        docs remove <file_name>      # Remove document
        docs stats                   # Show statistics
    """

def cli_knowledge_base_operations(args):
    """
    Knowledge base operations.

    Usage:
        kb status                    # Show KB status
        kb rebuild                   # Rebuild from scratch
        kb test "query"              # Test search
    """
```

---

### Phase 2: Agent Output Storage (Priority: MEDIUM)

Enable agents to save their outputs back to the knowledge base.

#### 2.1 Extend Agent Instructions

**Add to each agent's instructions:**
```python
instructions=dedent("""
    ...existing instructions...

    DOCUMENT ACCESS:
    - You have access to project documents via your knowledge base
    - When relevant information exists in documents, cite the source
    - Format citations: "According to falls-ref.md (Section 3.2)..."

    OUTPUT STORAGE (NEW):
    - When you create substantial content (PICOT questions, literature reviews,
      analysis plans), you can save it to the project knowledge base
    - Use the save_output tool to store your work
    - This makes your outputs searchable by other agents
""")
```

#### 2.2 Create Save Output Tool

```python
from agno.tools import Toolkit

class ProjectOutputTool(Toolkit):
    """Tool for agents to save their outputs to project knowledge base."""

    def save_output(self, content: str, output_type: str,
                   title: str, tags: List[str] = None) -> str:
        """
        Save agent output to project knowledge base.

        Args:
            content: The content to save
            output_type: "picot", "literature_review", "analysis_plan", etc.
            title: Descriptive title
            tags: Optional tags for organization

        Returns:
            Confirmation message with document ID
        """
        dm = get_document_manager()
        doc_id = dm.add_agent_output(
            agent_name=self.agent_name,
            content=content,
            output_type=output_type,
            metadata={"title": title, "tags": tags or []}
        )
        return f"✅ Saved to knowledge base (ID: {doc_id}). Other agents can now reference this."
```

---

### Phase 3: Advanced Features (Priority: LOW)

#### 3.1 Document Version Tracking
- Track when documents are updated
- Re-extract and re-index automatically
- Notify user of changed documents

#### 3.2 Selective Knowledge Access
- Allow agents to have different knowledge scopes
- E.g., Data Analysis agent only sees statistical documents
- Implement via filtered knowledge bases

#### 3.3 Web-Based Document Viewer
- Add route to view documents in browser
- Highlight relevant passages from search
- Show citation graph (which agents used which docs)

#### 3.4 Collaborative Features
- Multiple residents share a knowledge base
- Track who added which documents
- Commenting on documents

---

## 🎨 Technical Design Decisions

### Vector Database: LanceDB vs ChromaDB

#### Recommendation: **LanceDB** ⭐

**Why LanceDB:**
- ✅ **Lightweight** - Embedded, no server process
- ✅ **Fast** - Built on Apache Arrow, optimized for analytics
- ✅ **Storage Efficient** - Uses disk efficiently with compression
- ✅ **SQL-Like Queries** - Familiar query interface
- ✅ **Production Ready** - Used by major companies
- ✅ **Already in Agno** - Native support, well-tested
- ✅ **Cost** - Free, no API calls

**Why Not ChromaDB:**
- ⚠️ Slightly heavier (more dependencies)
- ⚠️ More complex for simple use cases
- ✅ Better for very large datasets (100k+ docs)
- ✅ Better for multi-tenancy

**Storage Location:**
```
data/projects/{project_name}/
├── project.db              # SQLite (metadata)
├── .lancedb/               # Vector DB (NEW)
│   ├── index.lance
│   └── embeddings.lance
└── documents/              # Original files
    ├── falls-ref.md
    └── ...
```

---

### Embeddings: OpenAI vs HuggingFace

#### Recommendation: **OpenAI text-embedding-3-small** ⭐

**Why OpenAI:**
- ✅ **Already Configured** - OPENAI_API_KEY set
- ✅ **High Quality** - State-of-the-art embeddings
- ✅ **Fast** - API-based, no local compute
- ✅ **Cost-Effective** - $0.00002 per 1K tokens (~$0.02 for 10 files)
- ✅ **Consistent** - Same model agents use for reasoning
- ✅ **Dimensions** - 1536 dims (good balance)

**Why Not HuggingFace:**
- ⚠️ Requires local compute (slower on laptop)
- ⚠️ Model download and storage (~500MB)
- ✅ Free (no API cost)
- ✅ Better for offline use

**Cost Estimate:**
- Initial embedding: ~100K tokens = $0.02 (one-time)
- Query cost: ~500 tokens per search = $0.00001 (negligible)
- Monthly cost: ~$0.10 (assuming 100 queries)

---

### File Handling: Copy vs Reference

#### Recommendation: **Copy Files** ⭐

**Why Copy:**
- ✅ **Portability** - Project is self-contained
- ✅ **Archival** - Original files stay with project
- ✅ **Safety** - User can delete source folder without breaking project
- ✅ **Consistency** - Files don't change unexpectedly

**Why Reference (Optional Mode):**
- ✅ **Storage** - Saves disk space
- ✅ **Sync** - Changes to original files propagate
- ⚠️ **Fragile** - Breaks if source files move

**Implementation:**
```python
def ingest_documents(self, source_path: str, copy_files: bool = True):
    if copy_files:
        # Copy to data/projects/{name}/documents/
        shutil.copy2(source_file, dest_file)
    else:
        # Just store reference path
        # Add warning: "Files are referenced, not copied"
```

---

### Text Extraction: Strategy

#### Markdown Files (Priority 1)
- **Method:** Direct read (no extraction needed)
- **Library:** Built-in Python `open()`
- **Speed:** Instant

#### PDF Files (Priority 2)
- **Method:** PyPDF2 or pdfplumber
- **Library:** Agno's `PDFReader` (uses PyMuPDF)
- **Challenges:**
  - Scanned PDFs need OCR (not Phase 1)
  - Complex layouts may lose formatting
  - Tables difficult to preserve
- **Fallback:** Store as reference only if extraction fails

#### DOCX Files (Priority 3)
- **Method:** python-docx
- **Library:** Agno's `DOCXReader`
- **Speed:** Fast

#### CSV Files (Priority 4)
- **Method:** pandas
- **Library:** Agno's `CSVReader`
- **Use Case:** Statistical data, results tables

---

## 💰 Cost Analysis

### One-Time Costs
| Item | Cost | Notes |
|------|------|-------|
| Embedding 10 files (1.4MB) | $0.02 | OpenAI API |
| LanceDB setup | $0.00 | Free, local |
| Development time | N/A | Implementation effort |

### Recurring Costs
| Item | Monthly Cost | Notes |
|------|--------------|-------|
| Knowledge base queries | $0.01 - $0.10 | ~100-1000 searches |
| New document embeddings | $0.01 - $0.05 | ~5-10 new files/month |
| Storage | $0.00 | Local disk (~50MB/project) |

### Scaling
- **10 documents:** $0.02 one-time + $0.10/month
- **100 documents:** $0.20 one-time + $1.00/month
- **1000 documents:** $2.00 one-time + $10.00/month

**Conclusion:** Very affordable. Even heavy usage stays under $20/month.

---

## ⚡ Performance Considerations

### Embedding Time
- **Markdown (10 files, 1.4MB):** ~30 seconds
- **PDF (100 pages):** ~2-3 minutes
- **Large document (10MB):** ~5-10 minutes

**Optimization:**
- Batch embeddings (all at once)
- Cache embeddings (don't re-embed unchanged files)
- Background processing (don't block CLI)

### Search Time
- **Query:** < 100ms (LanceDB local search)
- **Embedding query:** ~200ms (OpenAI API)
- **Total:** ~300ms per search

**User Experience:**
- Agents respond within 1-2 seconds
- Comparable to API-based search tools
- Much faster than manual document search

### Storage
- **Vectors:** ~4KB per 1K token chunk
- **10 files (1.4MB):** ~500 chunks = ~2MB vectors
- **100 files:** ~20MB vectors
- **1000 files:** ~200MB vectors

**Disk Space:**
```
data/projects/fall_prevention/
├── project.db (500KB)           # Metadata
├── .lancedb/ (2MB)              # Vectors
└── documents/ (1.4MB)           # Original files
Total: ~4MB
```

---

## 🔒 Security & Privacy

### Data Protection
- ✅ **Local Storage** - All data stays on user's machine
- ✅ **No Cloud Upload** - Documents never leave local environment
- ✅ **API Privacy** - Only embeddings sent to OpenAI (not full documents)
- ✅ **Project Isolation** - Each project has separate knowledge base

### Sensitive Documents
- **PHI/PII Handling:**
  - System does NOT automatically redact PHI
  - User responsible for de-identifying documents before ingestion
  - Add warning in CLI: "⚠️ Ensure documents are de-identified"

- **API Considerations:**
  - OpenAI embeddings API: Text sent for embedding
  - OpenAI states: Not used for training (as of 2024)
  - User should review OpenAI terms of service

### Access Control
- **Current:** No access control (single-user system)
- **Future:** Add user authentication if multi-user needed

---

## 🧪 Testing Strategy

### Unit Tests
```python
def test_document_ingestion():
    """Test ingesting markdown files."""

def test_knowledge_base_creation():
    """Test creating LanceDB knowledge base."""

def test_document_search():
    """Test semantic search across documents."""

def test_agent_with_knowledge():
    """Test agent using knowledge base."""
```

### Integration Tests
```python
def test_end_to_end_workflow():
    """
    1. Create project
    2. Ingest documents
    3. Create knowledge base
    4. Query agent
    5. Verify response cites documents
    """
```

### Manual Testing
- [ ] Ingest user's actual 10 MD files
- [ ] Test each agent with document queries
- [ ] Verify citations are correct
- [ ] Check performance (< 2 sec response)
- [ ] Test edge cases (empty folder, large files, etc.)

---

## 📊 Success Metrics

### Phase 1 (Core Implementation)
- [ ] Can ingest 10 MD files in < 60 seconds
- [ ] All 6 agents can search documents
- [ ] Agents cite sources correctly
- [ ] CLI commands work intuitively
- [ ] No crashes or data loss

### Phase 2 (Agent Output Storage)
- [ ] Agents can save outputs
- [ ] Saved outputs searchable by other agents
- [ ] Outputs linked to original documents

### User Satisfaction
- [ ] User reports faster research workflow
- [ ] Agents provide more relevant answers
- [ ] Document management feels seamless

---

## 🚧 Known Limitations & Future Work

### Current Limitations
1. **No OCR:** Scanned PDFs won't extract text
2. **No Table Preservation:** Tables in PDFs may lose structure
3. **No Multi-Tenancy:** Single user per project
4. **No Real-Time Sync:** Must manually refresh after adding docs
5. **English Only:** Embeddings optimized for English

### Future Enhancements
1. **OCR Support:** Add Tesseract for scanned documents
2. **Table Extraction:** Use specialized tools (Camelot, Tabula)
3. **Multi-Language:** Support Spanish, Chinese, etc.
4. **Auto-Sync:** Watch folder for new documents
5. **Web UI:** Drag-and-drop document upload
6. **Export:** Export knowledge base for sharing
7. **Version Control:** Track document changes over time
8. **Collaborative:** Multiple users, shared knowledge bases

---

## 🤔 Questions for User

### Critical Decisions (Please Answer)

#### 1. Vector Database Choice
**Options:**
- **A. LanceDB** (Recommended) - Lightweight, fast, embedded
- **B. ChromaDB** - Heavier but more features

**My Recommendation:** LanceDB for simplicity and performance

**Your Choice:** _______

---

#### 2. File Handling Strategy
**Options:**
- **A. Copy Files** (Recommended) - Copy documents into project folder
  - ✅ Self-contained, portable
  - ⚠️ Uses more disk space
- **B. Reference Files** - Just store path to original files
  - ✅ Saves disk space
  - ⚠️ Breaks if files move
- **C. Hybrid** - Let user choose per ingestion

**My Recommendation:** Copy files (Option A) for reliability

**Your Choice:** _______

---

#### 3. Document Update Strategy
**Options:**
- **A. Manual Refresh** (Recommended) - User runs `docs refresh` command
  - ✅ Explicit control
  - ✅ No surprises
- **B. Auto-Detect** - System checks for changes on startup
  - ✅ Convenient
  - ⚠️ Slower startup
- **C. Watch Folder** - Real-time monitoring (complex)

**My Recommendation:** Manual refresh (Option A) for Phase 1

**Your Choice:** _______

---

#### 4. Document Scope
**Options:**
- **A. Single Ingestion** - User manually adds documents
- **B. Watch Folder** - Auto-ingest from `New_Grad_project/` folder
- **C. Both** - Watch folder + manual adds

**My Recommendation:** Start with Option A, add B later if needed

**Your Choice:** _______

---

#### 5. Agent Output Storage
**Options:**
- **A. Phase 2** (Recommended) - Implement after core features work
- **B. Phase 1** - Include in initial implementation
- **C. Skip** - Don't implement for now

**My Recommendation:** Phase 2 (Option A) - get core working first

**Your Choice:** _______

---

### Additional Questions

#### 6. Document Organization
Should documents be organized by type/category, or all in one folder?

**Options:**
- **A. Flat Structure** (Recommended) - All in `documents/`
- **B. Categorized** - `documents/research/`, `documents/notes/`, etc.

**Your Choice:** _______

---

#### 7. Citation Format
How should agents cite documents?

**Options:**
- **A. Simple** - "According to falls-ref.md..."
- **B. Academic** - "(Johnson, 2023, falls-ref.md)"
- **C. Detailed** - "Source: falls-ref.md, Section 3, Page 12"

**My Recommendation:** Option A for simplicity

**Your Choice:** _______

---

#### 8. Error Handling
What should happen if a document fails to ingest?

**Options:**
- **A. Skip & Warn** (Recommended) - Continue with other files, log warning
- **B. Fail Fast** - Stop entire ingestion
- **C. Retry** - Try multiple extraction methods

**My Recommendation:** Option A with detailed error log

**Your Choice:** _______

---

## 💡 My Top Recommendations

Based on analysis of your use case (nursing resident with 10 MD research files):

### ✅ Recommended Approach

1. **Start Simple:**
   - LanceDB + OpenAI embeddings
   - Copy files to project folder
   - Manual refresh workflow
   - Flat document structure

2. **Phase 1 Goals:**
   - Ingest your 10 MD files
   - All agents can search and cite
   - Basic CLI commands work
   - Solid foundation for expansion

3. **Phase 2 (After Testing):**
   - Agent output storage
   - Auto-watch folder (if needed)
   - PDF support (when you get PDFs)
   - Advanced search features

4. **Keep It Maintainable:**
   - Clear error messages
   - Good logging
   - Easy to troubleshoot
   - Well-documented

### 🎯 Quick Start After Implementation

```bash
# 1. Ingest your research
> ingest /Users/hdz_agents/Documents/nurseRN/New_Grad_project
✅ Ingested 10 documents (1.4MB, 512 chunks)

# 2. Check status
> kb status
📚 Knowledge Base: 10 documents, 512 chunks, 2MB vectors

# 3. Test search
> kb test "fall prevention interventions"
Found 5 relevant passages:
  1. falls-ref.md (relevance: 0.91)
  2. systematic_reviews_falls.md (relevance: 0.87)
  ...

# 4. Use with agents
> agents
[All agents now have access to your research!]
```

---

## 📅 Implementation Timeline

### Estimated Effort

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| **Phase 1A** | DocumentManager class | 4-6 hours |
| **Phase 1B** | BaseAgent integration | 2-3 hours |
| **Phase 1C** | CLI commands | 2-3 hours |
| **Phase 1D** | Testing & debugging | 3-4 hours |
| **Total Phase 1** | Core implementation | **11-16 hours** |
| | |
| **Phase 2** | Agent output storage | 4-6 hours |
| **Phase 3** | Advanced features | 8-12 hours |

### Recommended Schedule

**Week 1: Core Implementation**
- Day 1-2: DocumentManager + knowledge base setup
- Day 3: BaseAgent integration
- Day 4: CLI commands + testing
- Day 5: User testing & refinements

**Week 2: Enhancement** (Optional)
- Day 1-2: Agent output storage
- Day 3: PDF support testing
- Day 4-5: Advanced features as needed

---

## ✅ Next Steps

### For User (You)
1. **Review this plan**
2. **Answer the 8 questions above**
3. **Provide feedback on recommendations**
4. **Approve Phase 1 implementation** (or request changes)

### For Implementation (After Approval)
1. Install dependencies: `pip install lancedb pyarrow`
2. Create `document_manager.py`
3. Update `BaseAgent` class
4. Add CLI commands
5. Test with your 10 MD files
6. Iterate based on feedback

---

## 📝 Notes & Considerations

### User's Requirements (From Conversation)
- ✅ "Drop anything in there for them to read" - Covered by document ingestion
- ✅ "Have them store information they make" - Covered by Phase 2 (agent output storage)
- ✅ "All agents have access" - Covered by BaseAgent integration
- ✅ "Put in your plan" - This document
- ✅ "Give me your suggestions" - Recommendations section above

### Additional Ideas to Consider
1. **Document Metadata Tags:** Allow tagging documents (e.g., "falls", "statistics", "intervention")
2. **Search Filters:** Filter by document type, date added, relevance
3. **Export Knowledge Base:** Export as JSON or Markdown for sharing/backup
4. **Document Summaries:** Auto-generate TL;DR for each document
5. **Citation Graph:** Visualize which agents use which documents most
6. **Duplicate Detection:** Warn if similar documents already exist

### Open Questions for Future
- Should system support image/diagram extraction from PDFs?
- Should there be a maximum document size limit?
- Should older/unused documents auto-archive?
- Should knowledge base be backed up separately?

---

## 🔗 Related Documentation

- **Project Architecture:** See CLAUDE.md (main project documentation)
- **Database Schema:** See project_manager.py lines 267-291 (documents table)
- **Agno Knowledge:** See libs/agno/agno/knowledge/knowledge.py
- **Vector DB Comparison:** See libs/agno/agno/vectordb/

---

## 📞 Support & Feedback

If you have questions or suggestions:
1. Update this document with your answers to questions
2. Add your feedback in "User Feedback" section below
3. Flag any concerns or blockers

---

## 📝 User Feedback Section

**Date:** _______
**Reviewed By:** _______

### Approved Changes
- [ ] Phase 1 Core Implementation - Approved
- [ ] Vector DB Choice: _______
- [ ] File Handling: _______
- [ ] Other decisions: _______

### Requested Changes
_[Add any changes or concerns here]_

### Additional Ideas
_[Add any ideas not covered in this plan]_

### Priority Adjustments
_[Any changes to implementation priority?]_

---

**Status:** ⏳ Awaiting User Review
**Next Action:** User to review and provide answers to questions above
