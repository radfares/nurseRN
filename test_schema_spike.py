"""
2-Hour Proof of Concept Spike
Tests the project-centric database schema before full implementation.

Run this to validate:
1. Schema creates successfully
2. Foreign keys enforce relationships
3. WAL mode works
4. Agent write/read cycle works
5. Project archival works

Usage:
    python test_schema_spike.py
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, date
import shutil

# ============================================================================
# SCHEMA DEFINITION (Complete DDL)
# ============================================================================

SCHEMA_DDL = """
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) VALUES
    (1, 'Initial schema with 7 core tables');

-- ============================================================================
-- 1. PICOT VERSIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS picot_versions (
    picot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_number INTEGER NOT NULL DEFAULT 1,

    -- PICOT Components
    population TEXT NOT NULL,
    intervention TEXT NOT NULL,
    comparison TEXT,
    outcome TEXT NOT NULL,
    timeframe TEXT,

    -- Full Question
    full_question TEXT NOT NULL,

    -- Approval Tracking
    approved BOOLEAN DEFAULT 0,
    approved_by TEXT,  -- 'CNS', 'Nurse Manager'
    approval_date DATE,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_picot_approved ON picot_versions(approved);

-- ============================================================================
-- 2. LITERATURE FINDINGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS literature_findings (
    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Source Agent
    agent_source TEXT NOT NULL,  -- 'nursing_research', 'medical_research', 'academic_research'

    -- Finding Type
    finding_type TEXT CHECK(finding_type IN ('article', 'standard', 'guideline', 'synthesis', 'best_practice')),

    -- Bibliographic Information
    title TEXT NOT NULL,
    authors TEXT,
    publication_date DATE,
    journal_source TEXT,

    -- Identifiers
    doi TEXT,
    pmid TEXT,
    arxiv_id TEXT,
    url TEXT,

    -- Content
    abstract TEXT,
    key_findings TEXT,  -- JSON array of bullet points
    methodology TEXT,
    clinical_implications TEXT,

    -- Organization
    tags TEXT,  -- JSON array
    relevance_score REAL CHECK(relevance_score BETWEEN 0 AND 1),

    -- User Actions
    selected_for_project BOOLEAN DEFAULT 0,  -- One of 3 required articles
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_findings_type ON literature_findings(finding_type);
CREATE INDEX IF NOT EXISTS idx_findings_selected ON literature_findings(selected_for_project);
CREATE INDEX IF NOT EXISTS idx_findings_agent ON literature_findings(agent_source);

-- ============================================================================
-- 3. ANALYSIS PLANS
-- ============================================================================
CREATE TABLE IF NOT EXISTS analysis_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Task Type
    task_type TEXT CHECK(task_type IN ('test_selection', 'sample_size', 'data_plan', 'interpretation', 'template')),

    -- Statistical Method
    statistical_method TEXT NOT NULL,
    justification TEXT,
    assumptions TEXT,  -- JSON array

    -- Parameters
    parameters TEXT,  -- JSON object: {alpha, power, effect_size, etc.}
    sample_size_required INTEGER,

    -- Data Collection
    data_template TEXT,  -- JSON schema for CSV template

    -- Analysis Steps
    analysis_steps TEXT,  -- JSON array

    -- Code
    r_code TEXT,
    python_code TEXT,

    -- Confidence
    confidence_score REAL CHECK(confidence_score BETWEEN 0 AND 1),

    -- Linking (optional, can be NULL)
    related_finding_ids TEXT,  -- JSON array of finding_ids

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analysis_task ON analysis_plans(task_type);

-- ============================================================================
-- 4. MILESTONES
-- ============================================================================
CREATE TABLE IF NOT EXISTS milestones (
    milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Milestone Info
    milestone_name TEXT NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,

    -- Status
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'overdue')) DEFAULT 'pending',
    completion_date DATE,

    -- Deliverables
    deliverables TEXT,  -- JSON array

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_milestones_status ON milestones(status);
CREATE INDEX IF NOT EXISTS idx_milestones_due ON milestones(due_date);

-- ============================================================================
-- 5. WRITING DRAFTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS writing_drafts (
    draft_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Draft Type
    draft_type TEXT CHECK(draft_type IN ('picot', 'literature_review', 'methodology', 'intervention_plan', 'poster_section', 'abstract', 'synthesis', 'other')),

    -- Content
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    -- Version Control
    version_number INTEGER DEFAULT 1,
    is_final BOOLEAN DEFAULT 0,

    -- Linking
    related_picot_id INTEGER,
    related_finding_ids TEXT,  -- JSON array

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (related_picot_id) REFERENCES picot_versions(picot_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_drafts_type ON writing_drafts(draft_type);
CREATE INDEX IF NOT EXISTS idx_drafts_final ON writing_drafts(is_final);

-- ============================================================================
-- 6. CONVERSATIONS (Tagged by Agent)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Agent Identification
    agent_name TEXT NOT NULL,  -- 'nursing_research', 'medical_research', etc.

    -- Conversation
    user_query TEXT NOT NULL,
    agent_response TEXT NOT NULL,

    -- Importance
    importance_level TEXT CHECK(importance_level IN ('critical', 'important', 'normal')) DEFAULT 'normal',

    -- Linking (what was created/referenced in this conversation)
    created_finding_id INTEGER,
    created_picot_id INTEGER,
    created_plan_id INTEGER,
    created_draft_id INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (created_finding_id) REFERENCES literature_findings(finding_id) ON DELETE SET NULL,
    FOREIGN KEY (created_picot_id) REFERENCES picot_versions(picot_id) ON DELETE SET NULL,
    FOREIGN KEY (created_plan_id) REFERENCES analysis_plans(plan_id) ON DELETE SET NULL,
    FOREIGN KEY (created_draft_id) REFERENCES writing_drafts(draft_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(agent_name);
CREATE INDEX IF NOT EXISTS idx_conversations_importance ON conversations(importance_level);
CREATE INDEX IF NOT EXISTS idx_conversations_date ON conversations(created_at);

-- ============================================================================
-- 7. DOCUMENTS (File Metadata)
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- File Info
    document_type TEXT CHECK(document_type IN ('pdf', 'docx', 'xlsx', 'pptx', 'csv', 'image', 'other')),
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,  -- Relative to project folder
    file_size_bytes INTEGER,

    -- Linking
    associated_finding_id INTEGER,

    -- Organization
    tags TEXT,  -- JSON array

    -- Extraction
    extraction_status TEXT CHECK(extraction_status IN ('pending', 'extracted', 'failed', 'not_applicable')) DEFAULT 'pending',
    extracted_text TEXT,

    -- Metadata
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    FOREIGN KEY (associated_finding_id) REFERENCES literature_findings(finding_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_finding ON documents(associated_finding_id);
"""

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def create_test_project(project_path: Path):
    """Create a test project with schema."""
    project_path.mkdir(parents=True, exist_ok=True)
    db_path = project_path / "project.db"

    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_DDL)
    conn.commit()

    print(f"✅ Created test project: {project_path}")
    print(f"   Database: {db_path}")

    return conn, db_path


def test_schema_creation(conn):
    """Test 1: Verify all 7 tables exist."""
    print("\n" + "="*70)
    print("TEST 1: Schema Creation")
    print("="*70)

    cursor = conn.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)

    tables = [row[0] for row in cursor.fetchall()]
    expected_tables = [
        'schema_version',
        'picot_versions',
        'literature_findings',
        'analysis_plans',
        'milestones',
        'writing_drafts',
        'conversations',
        'documents'
    ]

    print(f"\nExpected {len(expected_tables)} tables, found {len(tables)}")

    for table in expected_tables:
        if table in tables:
            print(f"  ✅ {table}")
        else:
            print(f"  ❌ {table} MISSING")
            return False

    # Check WAL mode
    cursor = conn.execute("PRAGMA journal_mode")
    journal_mode = cursor.fetchone()[0]
    print(f"\n📝 Journal mode: {journal_mode}")

    if journal_mode.lower() != 'wal':
        print("  ⚠️  WAL mode not enabled (may cause issues)")

    return True


def test_foreign_keys(conn):
    """Test 2: Verify foreign key enforcement."""
    print("\n" + "="*70)
    print("TEST 2: Foreign Key Enforcement")
    print("="*70)

    # Check FK is enabled
    cursor = conn.execute("PRAGMA foreign_keys")
    fk_enabled = cursor.fetchone()[0]
    print(f"\nForeign keys enabled: {bool(fk_enabled)}")

    if not fk_enabled:
        print("  ❌ Foreign keys NOT enabled")
        return False

    # Test FK constraint: Try to create draft with non-existent PICOT
    try:
        conn.execute("""
            INSERT INTO writing_drafts
            (draft_type, title, content, related_picot_id)
            VALUES ('picot', 'Test', 'Test content', 999)
        """)
        conn.commit()
        print("  ❌ Foreign key constraint FAILED (allowed invalid reference)")
        return False
    except sqlite3.IntegrityError as e:
        print(f"  ✅ Foreign key constraint WORKING (rejected invalid reference)")
        print(f"     Error: {e}")

    # Test cascade: Create PICOT, create draft, delete PICOT, check draft
    try:
        # Create PICOT
        cursor = conn.execute("""
            INSERT INTO picot_versions
            (population, intervention, outcome, full_question)
            VALUES ('Test pop', 'Test intervention', 'Test outcome', 'Test question?')
        """)
        picot_id = cursor.lastrowid

        # Create draft linked to PICOT
        cursor = conn.execute("""
            INSERT INTO writing_drafts
            (draft_type, title, content, related_picot_id)
            VALUES ('picot', 'PICOT Draft', 'Draft content', ?)
        """, (picot_id,))
        draft_id = cursor.lastrowid

        # Delete PICOT (should SET NULL on draft)
        conn.execute("DELETE FROM picot_versions WHERE picot_id = ?", (picot_id,))

        # Check draft still exists but FK is NULL
        cursor = conn.execute("""
            SELECT related_picot_id FROM writing_drafts WHERE draft_id = ?
        """, (draft_id,))
        result = cursor.fetchone()

        if result and result[0] is None:
            print("  ✅ ON DELETE SET NULL working correctly")
        else:
            print(f"  ❌ ON DELETE SET NULL failed (got {result})")
            return False

        conn.commit()
    except Exception as e:
        print(f"  ❌ FK cascade test failed: {e}")
        return False

    return True


def test_agent_write_cycle(conn):
    """Test 3: Simulate agent writing and reading data."""
    print("\n" + "="*70)
    print("TEST 3: Agent Write/Read Cycle")
    print("="*70)

    try:
        # Simulate Medical Research Agent finding an article
        print("\n1. Medical Research Agent adds finding...")
        cursor = conn.execute("""
            INSERT INTO literature_findings
            (agent_source, finding_type, title, authors, pmid,
             key_findings, tags, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'medical_research',
            'article',
            'Fall Prevention in Hospitalized Elderly Patients',
            'Smith J, Johnson A, et al.',
            '12345678',
            json.dumps([
                'Hourly rounding reduced falls by 30%',
                'Multicomponent intervention most effective',
                'Staff training critical for success'
            ]),
            json.dumps(['fall_prevention', 'elderly', 'hospital']),
            0.92
        ))
        finding_id = cursor.lastrowid
        print(f"   ✅ Finding saved (ID: {finding_id})")

        # Simulate Data Analysis Agent creating plan based on finding
        print("\n2. Data Analysis Agent creates plan...")
        cursor = conn.execute("""
            INSERT INTO analysis_plans
            (task_type, statistical_method, justification,
             parameters, sample_size_required, related_finding_ids, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'sample_size',
            'Two-proportion z-test',
            'Comparing fall rates pre/post intervention',
            json.dumps({
                'alpha': 0.05,
                'power': 0.80,
                'baseline_rate': 0.12,
                'target_rate': 0.08
            }),
            266,
            json.dumps([finding_id]),
            0.85
        ))
        plan_id = cursor.lastrowid
        print(f"   ✅ Analysis plan saved (ID: {plan_id})")

        # Simulate Writing Agent creating draft
        print("\n3. Research Writing Agent creates literature review...")
        cursor = conn.execute("""
            INSERT INTO writing_drafts
            (draft_type, title, content, related_finding_ids)
            VALUES (?, ?, ?, ?)
        """, (
            'literature_review',
            'Literature Review: Fall Prevention',
            'Recent evidence demonstrates that multicomponent fall prevention...',
            json.dumps([finding_id])
        ))
        draft_id = cursor.lastrowid
        print(f"   ✅ Draft saved (ID: {draft_id})")

        # Simulate Nursing Research Agent saving conversation
        print("\n4. Nursing Research Agent logs conversation...")
        conn.execute("""
            INSERT INTO conversations
            (agent_name, user_query, agent_response, importance_level, created_finding_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            'nursing_research',
            'Find recent fall prevention studies',
            'I found 1 relevant study on fall prevention...',
            'important',
            finding_id
        ))
        print(f"   ✅ Conversation logged")

        conn.commit()

        # READ CYCLE: Query cross-agent data
        print("\n5. Cross-agent data retrieval...")
        cursor = conn.execute("""
            SELECT
                lf.title,
                lf.agent_source,
                ap.statistical_method,
                wd.draft_type,
                c.agent_name as conversation_agent
            FROM literature_findings lf
            LEFT JOIN analysis_plans ap ON json_extract(ap.related_finding_ids, '$[0]') = lf.finding_id
            LEFT JOIN writing_drafts wd ON json_extract(wd.related_finding_ids, '$[0]') = lf.finding_id
            LEFT JOIN conversations c ON c.created_finding_id = lf.finding_id
            WHERE lf.finding_id = ?
        """, (finding_id,))

        result = cursor.fetchone()
        if result:
            print(f"   ✅ Successfully retrieved linked data:")
            print(f"      - Finding: {result[0]}")
            print(f"      - Source: {result[1]}")
            print(f"      - Analysis method: {result[2]}")
            print(f"      - Draft type: {result[3]}")
            print(f"      - Conversation: {result[4]}")
        else:
            print("   ❌ Failed to retrieve linked data")
            return False

    except Exception as e:
        print(f"  ❌ Agent write/read cycle failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_json_queries(conn):
    """Test 4: Verify JSON field queries work."""
    print("\n" + "="*70)
    print("TEST 4: JSON Field Queries")
    print("="*70)

    try:
        # Query key findings (JSON array)
        print("\n1. Querying key_findings JSON array...")
        cursor = conn.execute("""
            SELECT title, key_findings
            FROM literature_findings
            WHERE json_array_length(key_findings) > 0
        """)

        for row in cursor.fetchall():
            print(f"   Title: {row[0]}")
            findings = json.loads(row[1])
            print(f"   Key findings ({len(findings)} items):")
            for i, kf in enumerate(findings, 1):
                print(f"     {i}. {kf}")

        # Query tags
        print("\n2. Searching by tag...")
        cursor = conn.execute("""
            SELECT title, tags
            FROM literature_findings
            WHERE tags LIKE '%fall_prevention%'
        """)

        count = 0
        for row in cursor.fetchall():
            count += 1
            tags = json.loads(row[1])
            print(f"   Found: {row[0]}")
            print(f"   Tags: {', '.join(tags)}")

        print(f"\n   ✅ JSON queries working ({count} results)")

    except Exception as e:
        print(f"  ❌ JSON query test failed: {e}")
        return False

    return True


def test_project_archival(test_projects_dir: Path):
    """Test 5: Archive project (move folder)."""
    print("\n" + "="*70)
    print("TEST 5: Project Archival")
    print("="*70)

    try:
        project_name = "fall_prevention_spike"
        archive_dir = test_projects_dir / "archives"
        archive_dir.mkdir(exist_ok=True)

        source = test_projects_dir / project_name
        destination = archive_dir / f"{project_name}_archived_{datetime.now().strftime('%Y%m%d')}"

        print(f"\n1. Archiving project...")
        print(f"   Source: {source}")
        print(f"   Destination: {destination}")

        shutil.move(str(source), str(destination))

        # Verify archive
        if destination.exists():
            db_path = destination / "project.db"
            if db_path.exists():
                # Test can still read from archived DB
                conn = sqlite3.connect(str(db_path))
                cursor = conn.execute("SELECT COUNT(*) FROM literature_findings")
                count = cursor.fetchone()[0]
                conn.close()

                print(f"   ✅ Project archived successfully")
                print(f"   ✅ Database readable ({count} findings)")
                return True
            else:
                print("   ❌ Database file missing in archive")
                return False
        else:
            print("   ❌ Archive directory not created")
            return False

    except Exception as e:
        print(f"  ❌ Archival test failed: {e}")
        return False


# ============================================================================
# MAIN SPIKE EXECUTION
# ============================================================================

def run_spike():
    """Run all validation tests."""
    print("\n" + "="*70)
    print("PROOF OF CONCEPT SPIKE - Project-Centric Database Schema")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Setup
    test_projects_dir = Path("/home/user/nurseRN/test_projects_spike")
    project_name = "fall_prevention_spike"
    project_path = test_projects_dir / project_name

    # Clean up any previous test
    if test_projects_dir.exists():
        shutil.rmtree(test_projects_dir)

    # Create test project
    conn, db_path = create_test_project(project_path)

    # Run tests
    tests = [
        ("Schema Creation", lambda: test_schema_creation(conn)),
        ("Foreign Key Enforcement", lambda: test_foreign_keys(conn)),
        ("Agent Write/Read Cycle", lambda: test_agent_write_cycle(conn)),
        ("JSON Field Queries", lambda: test_json_queries(conn)),
        ("Project Archival", lambda: test_project_archival(test_projects_dir))
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} CRASHED: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nResults: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED - Ready for full implementation!")
        print(f"\nDatabase location: {db_path}")
        print("You can open this in any SQLite browser to inspect the schema.")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Address issues before proceeding")
        return False


if __name__ == "__main__":
    success = run_spike()
    exit(0 if success else 1)
