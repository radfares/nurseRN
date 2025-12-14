# Personal Knowledge Library - User Guide

**Complete step-by-step instructions for using your personal document library**

Created: 2025-12-13
Version: 1.0

---

## Overview

The Personal Knowledge Library allows the Nursing Research Agent to search your personal documents (PDFs, notes, articles, presentations) alongside external databases like PubMed.

**What it does:**
- Indexes your documents for semantic search
- Agent automatically searches them when you mention "my notes", "my documents", etc.
- Supplements external research with your personal knowledge

**Supported formats:**
`.pdf`, `.pptx`, `.docx`, `.txt`, `.md`, `.csv`, `.json`

---

## Quick Start (3 Steps)

```bash
# 1. Navigate to project
cd /Users/hdz/nurseRN

# 2. Add your documents
python scripts/ingest_documents.py add ~/Downloads/my_notes.pdf

# 3. Ask the agent about them
python run_nursing_project.py
# Then: "What do my notes say about fall prevention?"
```

---

## Step-by-Step Instructions

### Step 1: Prepare Your Documents

**Recommended location (optional but organized):**
```
/Users/hdz/nurseRN/data/personal_library/
```

**Create the folder and copy files:**
```bash
# Create the folder
mkdir -p /Users/hdz/nurseRN/data/personal_library/

# Copy your files
cp ~/Downloads/nursing_notes.pdf /Users/hdz/nurseRN/data/personal_library/
cp ~/Documents/research_article.pdf /Users/hdz/nurseRN/data/personal_library/
```

**Alternative:** Keep files anywhere (Downloads, Documents, etc.) - the system will index them from their current location.

---

### Step 2: Index Your Documents

**Navigate to the project directory:**
```bash
cd /Users/hdz/nurseRN
```

**Add a single file:**
```bash
python scripts/ingest_documents.py add /path/to/your/file.pdf
```

**Examples:**
```bash
# Add from Downloads
python scripts/ingest_documents.py add ~/Downloads/nursing_research.pdf

# Add from personal library folder
python scripts/ingest_documents.py add data/personal_library/my_notes.pdf

# Add from anywhere
python scripts/ingest_documents.py add /Users/hdz/Documents/fall_prevention_study.pdf
```

**Add an entire folder:**
```bash
# Add all supported files from a folder
python scripts/ingest_documents.py add-folder ~/Documents/nursing_school/

# Add recursively (includes subfolders)
python scripts/ingest_documents.py add-folder ~/Documents/nursing_school/ --recursive
```

**Example - Organized approach:**
```bash
# Add entire personal library folder recursively
python scripts/ingest_documents.py add-folder data/personal_library/ --recursive
```

---

### Step 3: Verify Documents Were Added

**List all indexed documents:**
```bash
python scripts/ingest_documents.py list
```

**Expected output:**
```
============================================================
  Indexed Documents
============================================================

  Document ID          Filename                       Chunks   Ingested
  -------------------- ------------------------------ -------- --------------------
  abc123def456         nursing_notes.pdf              12       2025-12-13 16:30:00
  789xyz123abc         fall_prevention.pdf            8        2025-12-13 16:31:00

  ℹ️  Total: 2 documents
```

**View detailed statistics:**
```bash
python scripts/ingest_documents.py stats
```

**Expected output:**
```
============================================================
  Library Statistics
============================================================

  Collection:     personal_docs
  Database Path:  /Users/hdz/nurseRN/data/chroma_db
  Status:         Active

  Total Documents: 2
  Total Chunks:    20
  Embedder:        text-embedding-3-small

  Avg Chunks/Doc:  10.0

  File Types:
    .pdf: 2
```

---

### Step 4: Test Search (Optional)

**Search from command line:**
```bash
python scripts/ingest_documents.py search "fall prevention"
```

**Expected output:**
```
============================================================
  Search: fall prevention
============================================================

  Found 3 results:

  1. [nursing_notes.pdf]
     Page: 5
     Score: 0.892
     "Fall prevention protocols require hourly rounding and environmental assessments..."

  2. [fall_prevention.pdf]
     Page: 1
     Score: 0.845
     "Implementing fall prevention strategies in acute care settings..."
```

**Search with custom limit:**
```bash
python scripts/ingest_documents.py search "medication safety" --limit 10
```

---

### Step 5: Use with the Agent

**Start the Nursing Research Agent:**
```bash
cd /Users/hdz/nurseRN
python run_nursing_project.py
```

**Ask questions about your documents:**

The agent will automatically search your personal library when you use phrases like:
- "my notes"
- "my documents"
- "my files"
- "files I uploaded"
- "what I have saved"

**Example queries:**
```
"What do my notes say about fall prevention?"

"Search my documents for catheter care protocols"

"Check my files about medication safety guidelines"

"What's in my uploaded research about hourly rounding?"

"Do my notes mention anything about CAUTI prevention?"

"Compare PubMed findings with what's in my documents about wound care"
```

---

## Where Do Files Go?

### Your Original Files
**Files stay exactly where they are.** The system does NOT move or copy your files.

Example:
- Original location: `/Users/hdz/Downloads/research.pdf`
- After ingestion: **Still at** `/Users/hdz/Downloads/research.pdf`
- ✅ Nothing moved, nothing copied

### The Search Index
The system creates a **searchable index** (not file copies) at:
```
/Users/hdz/nurseRN/data/chroma_db/
```

This contains:
- **Embeddings** (vector representations for semantic search)
- **Text chunks** (your documents split into searchable pieces)
- **Metadata** (file paths, page numbers, timestamps)

**Important:** The index is NOT a backup of your files. It's a database that points back to your original files.

---

## Recommended File Organization

```
/Users/hdz/nurseRN/data/personal_library/
├── class_notes/
│   ├── med_surg_week1.pdf
│   ├── med_surg_week2.pdf
│   └── pharmacology_notes.docx
├── research_articles/
│   ├── fall_prevention_2024.pdf
│   ├── catheter_care_review.pdf
│   └── wound_healing_study.pdf
├── protocols/
│   ├── hospital_fall_protocol.pdf
│   ├── infection_control_policy.pdf
│   └── medication_admin_guidelines.pdf
├── my_projects/
│   ├── capstone_research.docx
│   └── picot_question_draft.pdf
└── presentations/
    ├── fall_prevention_presentation.pptx
    └── evidence_based_practice.pptx
```

**Then ingest everything at once:**
```bash
python scripts/ingest_documents.py add-folder data/personal_library/ --recursive
```

---

## Complete Example Workflow

```bash
# 1. Navigate to project
cd /Users/hdz/nurseRN

# 2. Create organized folder structure
mkdir -p data/personal_library/class_notes
mkdir -p data/personal_library/research_articles
mkdir -p data/personal_library/protocols

# 3. Copy files to organized locations
cp ~/Downloads/nursing_notes.pdf data/personal_library/class_notes/
cp ~/Documents/fall_prevention_study.pdf data/personal_library/research_articles/
cp ~/Desktop/hospital_protocol.pdf data/personal_library/protocols/

# 4. Index everything
python scripts/ingest_documents.py add-folder data/personal_library/ --recursive

# 5. Verify
python scripts/ingest_documents.py list

# 6. Test search
python scripts/ingest_documents.py search "fall prevention"

# 7. Use with agent
python run_nursing_project.py
# Then ask: "What do my notes say about fall prevention protocols?"
```

---

## Command Reference

### Add Commands

| Command | Description |
|---------|-------------|
| `python scripts/ingest_documents.py add <file>` | Add a single file |
| `python scripts/ingest_documents.py add <file> --chunk-size 3000` | Add with custom chunk size |
| `python scripts/ingest_documents.py add-folder <folder>` | Add all files in folder |
| `python scripts/ingest_documents.py add-folder <folder> -r` | Add folder recursively |

### View Commands

| Command | Description |
|---------|-------------|
| `python scripts/ingest_documents.py list` | List all indexed documents |
| `python scripts/ingest_documents.py stats` | Show library statistics |
| `python scripts/ingest_documents.py search "query"` | Search the library |
| `python scripts/ingest_documents.py search "query" -n 10` | Search with more results |

### Manage Commands

| Command | Description |
|---------|-------------|
| `python scripts/ingest_documents.py remove <doc_id>` | Remove a document by ID |
| `python scripts/ingest_documents.py clear --force` | Clear entire library |

### Get Help

| Command | Description |
|---------|-------------|
| `python scripts/ingest_documents.py --help` | Show all commands |
| `python scripts/ingest_documents.py add --help` | Help for add command |

---

## Advanced Options

### Custom Chunk Size and Overlap

```bash
# Larger chunks (better for narrative documents)
python scripts/ingest_documents.py add document.pdf --chunk-size 3000 --overlap 300

# Smaller chunks (better for reference material)
python scripts/ingest_documents.py add protocol.pdf --chunk-size 1000 --overlap 100
```

**Defaults:**
- Chunk size: 2000 characters
- Overlap: 200 characters

### Custom Database Location

```bash
# Use a different database location
python scripts/ingest_documents.py add file.pdf --db-path /path/to/custom/db
```

---

## Troubleshooting

### "No documents indexed yet"
**Cause:** Library is empty
**Solution:** Run `add` or `add-folder` command first

### "File not found"
**Cause:** Incorrect file path
**Solution:** Use full path or check current directory
```bash
# Use full path
python scripts/ingest_documents.py add /Users/hdz/Downloads/file.pdf

# Or navigate to the directory first
cd ~/Downloads
python /Users/hdz/nurseRN/scripts/ingest_documents.py add file.pdf
```

### "Unsupported format"
**Cause:** File type not supported
**Solution:** Convert to PDF or use supported formats (`.pdf`, `.pptx`, `.docx`, `.txt`, `.md`, `.csv`, `.json`)

### "Your personal library is empty" (from agent)
**Cause:** No documents indexed yet
**Solution:** Index documents first
```bash
python scripts/ingest_documents.py add-folder data/personal_library/ -r
```

### Agent doesn't search personal library
**Cause:** Query didn't trigger personal library keywords
**Solution:** Use explicit phrases:
- ✅ "Check **my notes** about fall prevention"
- ✅ "Search **my documents** for wound care"
- ❌ "Find information about fall prevention" (will use PubMed only)

---

## Best Practices

### 1. Organize Before Indexing
Create a clear folder structure before adding documents:
```
personal_library/
├── by_topic/
├── by_course/
└── by_project/
```

### 2. Use Descriptive Filenames
- ✅ `fall_prevention_protocol_2024.pdf`
- ❌ `document1.pdf`

### 3. Re-index When Files Change
If you update a file, remove the old version and add the new one:
```bash
# Get the doc_id
python scripts/ingest_documents.py list

# Remove old version
python scripts/ingest_documents.py remove abc123def456

# Add new version
python scripts/ingest_documents.py add updated_file.pdf
```

### 4. Regular Maintenance
Periodically review what's indexed:
```bash
python scripts/ingest_documents.py list
python scripts/ingest_documents.py stats
```

### 5. Keep Originals Safe
The library only stores an index. Keep your original files backed up elsewhere.

---

## Integration with Agent

### Tool Priority

When you ask the agent a question, it searches in this order:

1. **PubMed** - Peer-reviewed clinical research (PRIMARY)
2. **ClinicalTrials.gov** - Clinical trials
3. **medRxiv** - Medical preprints
4. **Other external sources** - Semantic Scholar, CORE, DOAJ, etc.
5. **Personal Library** - Your documents (SUPPLEMENT)

### Trigger Phrases

The agent automatically uses personal library when it detects:
- "my notes"
- "my documents"
- "my files"
- "files I uploaded"
- "what I saved"
- "my personal"

### Example Agent Responses

**Query:** "What do my notes say about fall prevention?"

**Agent Response:**
```
Found 2 relevant sections from your personal library:

1. [nursing_notes.pdf, p.12] (Score: 0.92)
   "The fall prevention protocol requires hourly rounding and
   environmental safety assessments. High-risk patients should..."

2. [fall_prevention_protocol.pdf, p.3] (Score: 0.87)
   "Risk factors include age >65, history of falls, medications
   affecting balance, and cognitive impairment..."
```

---

## FAQs

**Q: Can I index files from multiple locations?**
A: Yes! Files can be anywhere. The index stores their paths.

**Q: What happens if I move a file after indexing?**
A: The index will have the old path. Remove and re-add the file.

**Q: How much disk space does the index use?**
A: Much less than your files. Roughly 10-20% of original file sizes.

**Q: Can I search without using the agent?**
A: Yes, use `python scripts/ingest_documents.py search "query"`

**Q: Will this work offline?**
A: Searching indexed documents works offline. Adding new documents requires OpenAI API (for embeddings).

**Q: How many documents can I index?**
A: Thousands. ChromaDB is designed to scale.

**Q: Can I have multiple libraries?**
A: Yes, use `--db-path` to specify different database locations.

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Run `python scripts/ingest_documents.py --help`
3. Check project documentation in `/Users/hdz/nurseRN/docs/`

---

**Happy searching! 📚**
