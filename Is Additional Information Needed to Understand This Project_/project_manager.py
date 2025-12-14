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