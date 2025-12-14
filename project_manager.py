"""
Project Manager for Nursing Research Projects
Handles project creation, switching, archival, and database initialization.

Created: 2025-11-23
Part of 4-day implementation (Day 1)
"""

import json
import logging
import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ============================================================================
# PROJECT DIRECTORY STRUCTURE
# ============================================================================

# Base directory for all projects
PROJECTS_BASE_DIR = Path(__file__).parent / "data" / "projects"
ARCHIVES_DIR = Path(__file__).parent / "data" / "archives"

# Active project tracking file
ACTIVE_PROJECT_FILE = Path(__file__).parent / "data" / ".active_project"

# ============================================================================
# SCHEMA DEFINITION (Same as PoC)
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
    (1, 'Initial schema with 7 core tables for project-centric architecture'),
    (2, 'Phase 1, Task 3: Added is_current flag to picot_versions table');

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
    approved_by TEXT,
    approval_date DATE,
    is_current BOOLEAN DEFAULT 0,  -- Phase 1, Task 3: Track which PICOT version is active

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_picot_approved ON picot_versions(approved);
CREATE INDEX IF NOT EXISTS idx_picot_current ON picot_versions(is_current);  -- Phase 1, Task 3

-- ============================================================================
-- 2. LITERATURE FINDINGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS literature_findings (
    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Source Agent
    agent_source TEXT NOT NULL,

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
    key_findings TEXT,  -- JSON array
    methodology TEXT,
    clinical_implications TEXT,

    -- Organization
    tags TEXT,  -- JSON array
    relevance_score REAL CHECK(relevance_score BETWEEN 0 AND 1),

    -- User Actions
    selected_for_project BOOLEAN DEFAULT 0,
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
    parameters TEXT,  -- JSON object
    sample_size_required INTEGER,

    -- Data Collection
    data_template TEXT,  -- JSON schema

    -- Analysis Steps
    analysis_steps TEXT,  -- JSON array

    -- Code
    r_code TEXT,
    python_code TEXT,

    -- Confidence
    confidence_score REAL CHECK(confidence_score BETWEEN 0 AND 1),

    -- Linking
    related_finding_ids TEXT,  -- JSON array

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
    agent_name TEXT NOT NULL,

    -- Conversation
    user_query TEXT NOT NULL,
    agent_response TEXT NOT NULL,

    -- Importance
    importance_level TEXT CHECK(importance_level IN ('critical', 'important', 'normal')) DEFAULT 'normal',

    -- Linking
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
    file_path TEXT NOT NULL,
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

# Default milestones for nursing residency project (Nov 2025 - June 2026)
DEFAULT_MILESTONES = [
    {
        "name": "PICOT Development",
        "description": "Develop and refine PICOT question",
        "due_date": "2025-12-17",
        "deliverables": ["Approved PICOT statement", "NM confirmation form"],
    },
    {
        "name": "Literature Search",
        "description": "Find and analyze 3 research articles",
        "due_date": "2026-01-21",
        "deliverables": ["3 peer-reviewed articles", "Article summaries"],
    },
    {
        "name": "Intervention Planning",
        "description": "Design intervention and data collection plan",
        "due_date": "2026-03-18",
        "deliverables": [
            "Intervention steps",
            "Data collection template",
            "Stakeholder list",
        ],
    },
    {
        "name": "Poster Completion",
        "description": "Complete poster board and PowerPoint",
        "due_date": "2026-04-22",
        "deliverables": ["Poster board", "PowerPoint file"],
    },
    {
        "name": "Practice Presentation",
        "description": "Practice presentation day",
        "due_date": "2026-05-20",
        "deliverables": ["Practiced presentation"],
    },
    {
        "name": "Final Presentation",
        "description": "Final presentation and graduation",
        "due_date": "2026-06-17",
        "deliverables": ["Completed presentation"],
    },
]


# ============================================================================
# PROJECT MANAGER CLASS
# ============================================================================


class ProjectManager:
    """Manages nursing research projects."""

    def __init__(self):
        """Initialize project manager."""
        # Ensure directories exist
        PROJECTS_BASE_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
        ACTIVE_PROJECT_FILE.parent.mkdir(parents=True, exist_ok=True)

        logger.info("ProjectManager initialized")

    def create_project(
        self, project_name: str, add_default_milestones: bool = True
    ) -> Path:
        """
        Create a new project with initialized database.

        Args:
            project_name: Name of the project (will be sanitized)
            add_default_milestones: Add default nursing residency milestones

        Returns:
            Path to project directory

        Raises:
            ValueError: If project already exists
        """
        # Sanitize project name
        safe_name = self._sanitize_project_name(project_name)
        project_path = PROJECTS_BASE_DIR / safe_name

        if project_path.exists():
            raise ValueError(f"Project '{safe_name}' already exists at {project_path}")

        # Create project directory structure
        project_path.mkdir(parents=True)
        documents_dir = project_path / "documents"
        documents_dir.mkdir()

        # Initialize database
        db_path = project_path / "project.db"
        conn = sqlite3.connect(str(db_path))
        conn.executescript(SCHEMA_DDL)

        # Add default milestones if requested
        if add_default_milestones:
            for milestone in DEFAULT_MILESTONES:
                conn.execute(
                    """
                    INSERT INTO milestones (milestone_name, description, due_date, deliverables)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        milestone["name"],
                        milestone["description"],
                        milestone["due_date"],
                        json.dumps(milestone["deliverables"]),
                    ),
                )

        conn.commit()
        conn.close()

        logger.info(f"Created project: {safe_name} at {project_path}")

        # Set as active project
        self.set_active_project(safe_name)

        return project_path

    def list_projects(self) -> List[Dict[str, str]]:
        """
        List all available projects.

        Returns:
            List of project info dictionaries
        """
        projects = []

        if not PROJECTS_BASE_DIR.exists():
            return projects

        for project_dir in sorted(PROJECTS_BASE_DIR.iterdir()):
            if project_dir.is_dir():
                db_path = project_dir / "project.db"

                if db_path.exists():
                    # Get project stats
                    try:
                        conn = sqlite3.connect(str(db_path))
                        cursor = conn.execute("""
                            SELECT
                                (SELECT COUNT(*) FROM literature_findings) as findings_count,
                                (SELECT COUNT(*) FROM picot_versions) as picot_count,
                                (SELECT COUNT(*) FROM milestones WHERE status = 'completed') as completed_milestones,
                                (SELECT COUNT(*) FROM milestones) as total_milestones
                        """)
                        stats = cursor.fetchone()
                        conn.close()

                        projects.append(
                            {
                                "name": project_dir.name,
                                "path": str(project_dir),
                                "findings": stats[0],
                                "picots": stats[1],
                                "progress": f"{stats[2]}/{stats[3]} milestones",
                                "modified": datetime.fromtimestamp(
                                    db_path.stat().st_mtime
                                ).strftime("%Y-%m-%d %H:%M"),
                            }
                        )
                    except Exception as e:
                        logger.error(f"Error reading project {project_dir.name}: {e}")
                        projects.append(
                            {
                                "name": project_dir.name,
                                "path": str(project_dir),
                                "error": str(e),
                            }
                        )

        return projects

    def get_active_project(self) -> Optional[str]:
        """
        Get the currently active project name.

        Returns:
            Project name or None if no active project
        """
        if ACTIVE_PROJECT_FILE.exists():
            return ACTIVE_PROJECT_FILE.read_text().strip()
        return None

    def set_active_project(self, project_name: str):
        """
        Set the active project.

        Args:
            project_name: Name of project to activate

        Raises:
            ValueError: If project doesn't exist
        """
        safe_name = self._sanitize_project_name(project_name)
        project_path = PROJECTS_BASE_DIR / safe_name

        if not project_path.exists():
            raise ValueError(f"Project '{safe_name}' does not exist")

        ACTIVE_PROJECT_FILE.write_text(safe_name)
        logger.info(f"Set active project: {safe_name}")

    def get_active_project_path(self) -> Optional[Path]:
        """
        Get the path to the active project.

        Returns:
            Path to active project or None
        """
        active_project = self.get_active_project()
        if active_project:
            return PROJECTS_BASE_DIR / active_project
        return None

    def archive_project(self, project_name: str) -> Path:
        """
        Archive a project (move to archives folder).

        Args:
            project_name: Name of project to archive

        Returns:
            Path to archived project

        Raises:
            ValueError: If project doesn't exist or is currently active
        """
        safe_name = self._sanitize_project_name(project_name)
        source_path = PROJECTS_BASE_DIR / safe_name

        if not source_path.exists():
            raise ValueError(f"Project '{safe_name}' does not exist")

        # Check if it's the active project
        if self.get_active_project() == safe_name:
            raise ValueError(
                f"Cannot archive active project. Switch to another project first."
            )

        # Create archive name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{safe_name}_archived_{timestamp}"
        archive_path = ARCHIVES_DIR / archive_name

        # Move to archives
        shutil.move(str(source_path), str(archive_path))

        logger.info(f"Archived project: {safe_name} -> {archive_path}")

        return archive_path

    def get_project_db_path(self, project_name: Optional[str] = None) -> Path:
        """
        Get the database path for a project.

        Args:
            project_name: Project name, or None to use active project

        Returns:
            Path to project.db

        Raises:
            ValueError: If project doesn't exist or no active project
        """
        if project_name is None:
            project_name = self.get_active_project()
            if project_name is None:
                raise ValueError(
                    "No active project. Create or switch to a project first."
                )

        safe_name = self._sanitize_project_name(project_name)
        db_path = PROJECTS_BASE_DIR / safe_name / "project.db"

        if not db_path.exists():
            raise FileNotFoundError(f"Project database not found: {db_path}")

        return db_path

    def get_project_connection(
        self, project_name: Optional[str] = None
    ) -> sqlite3.Connection:
        """
        Get a database connection for a project.

        Args:
            project_name: Project name, or None to use active project

        Returns:
            SQLite connection with foreign keys enabled

        Raises:
            ValueError/FileNotFoundError: If project issues
        """
        db_path = self.get_project_db_path(project_name)
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def _sanitize_project_name(self, name: str) -> str:
        """
        Sanitize project name for filesystem.

        Args:
            name: Raw project name

        Returns:
            Safe filesystem name
        """
        # Replace spaces with underscores, remove special chars
        safe_name = name.lower().strip()
        safe_name = safe_name.replace(" ", "_")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in "_-")

        # Limit length
        if len(safe_name) > 50:
            safe_name = safe_name[:50]

        return safe_name


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_project_manager = None


def get_project_manager() -> ProjectManager:
    """Get or create global ProjectManager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager


# ============================================================================
# CLI HELPER FUNCTIONS
# ============================================================================


def cli_create_project(project_name: str, add_milestones: bool = True):
    """CLI command: Create new project."""
    pm = get_project_manager()
    try:
        project_path = pm.create_project(project_name, add_milestones)
        print(f"\n✅ Created project: {project_name}")
        print(f"   Location: {project_path}")
        print(f"   Database: {project_path / 'project.db'}")
        if add_milestones:
            print(f"   Added {len(DEFAULT_MILESTONES)} default milestones")
        print(f"\n   ✨ This is now your active project")
        return True
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return False


def cli_list_projects():
    """CLI command: List all projects."""
    pm = get_project_manager()
    projects = pm.list_projects()
    active_project = pm.get_active_project()

    if not projects:
        print("\n📁 No projects found. Create one with: new project <name>")
        return

    print(f"\n📁 Available Projects ({len(projects)}):")
    print("=" * 80)

    for project in projects:
        is_active = "★ ACTIVE" if project["name"] == active_project else ""

        if "error" in project:
            print(f"  ❌ {project['name']} - Error: {project['error']}")
        else:
            print(f"  {'★' if is_active else ' '} {project['name']} {is_active}")
            print(
                f"     Findings: {project['findings']} | PICOTs: {project['picots']} | Progress: {project['progress']}"
            )
            print(f"     Modified: {project['modified']}")
            print()


def cli_switch_project(project_name: str):
    """CLI command: Switch active project."""
    pm = get_project_manager()
    try:
        pm.set_active_project(project_name)
        print(f"\n✅ Switched to project: {project_name}")
        return True
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Available projects:")
        cli_list_projects()
        return False


def cli_archive_project(project_name: str):
    """CLI command: Archive a project."""
    pm = get_project_manager()
    try:
        archive_path = pm.archive_project(project_name)
        print(f"\n✅ Archived project: {project_name}")
        print(f"   Location: {archive_path}")
        return True
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Test module
    print("Project Manager Module")
    print("=" * 70)
    print("\nFunctions available:")
    print("  - create_project(name)")
    print("  - list_projects()")
    print("  - get_active_project()")
    print("  - set_active_project(name)")
    print("  - archive_project(name)")
    print("  - get_project_db_path()")
    print("  - get_project_connection()")
