## **Response to "This is the Plan"**

**Acknowledged. Executing safety infrastructure first.**

Here's what I'm building right now:

***

## **Deliverable 1: Complete Backup & Migration System**

### **File 1: `scripts/backup_all_dbs.sh`**

```bash
#!/bin/bash
# Mandatory pre-migration backup
# Usage: ./scripts/backup_all_dbs.sh

set -e  # Exit on any error

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="data/backups/${TIMESTAMP}"

echo "🔐 Creating backup: ${BACKUP_DIR}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup all project databases
PROJECT_COUNT=0
for db in data/projects/*/project.db; do
    if [ -f "$db" ]; then
        cp "$db" "${BACKUP_DIR}/"
        PROJECT_COUNT=$((PROJECT_COUNT + 1))
        echo "  ✅ $(basename $(dirname $db))/project.db"
    fi
done

# Backup orchestration database if exists
if [ -f "data/orchestration/workflow_context.db" ]; then
    cp data/orchestration/workflow_context.db "${BACKUP_DIR}/"
    echo "  ✅ workflow_context.db"
fi

# Verify backup
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}" | wc -l)
echo ""
echo "✅ Backup complete: ${BACKUP_COUNT} files backed up to ${BACKUP_DIR}"
echo "   To rollback: ./scripts/rollback_migration.sh ${TIMESTAMP}"

# Save backup metadata
cat > "${BACKUP_DIR}/backup_metadata.json" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "project_count": ${PROJECT_COUNT},
  "backup_dir": "${BACKUP_DIR}",
  "created_by": "backup_all_dbs.sh"
}
EOF

exit 0
```

***

### **File 2: `scripts/schema_additions.sql`**

```sql
-- Phase 1 Schema Additions: Workflow Persistence
-- Version: 1.0
-- Date: 2025-12-09

-- Track every workflow execution
CREATE TABLE IF NOT EXISTS workflow_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_name TEXT NOT NULL,
    workflow_id TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_steps INTEGER,
    steps_completed INTEGER DEFAULT 0,
    error_message TEXT,
    inputs_json TEXT,  -- JSON blob of input params
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track each step within a workflow
CREATE TABLE IF NOT EXISTS workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_run_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed')),
    input_summary TEXT,
    output_summary TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_seconds REAL,
    error_context TEXT,  -- Phase 1.5: JSON of error details
    stack_trace TEXT,     -- Phase 1.5: Full traceback
    FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(id) ON DELETE CASCADE
);

-- Store final workflow outputs for retrieval
CREATE TABLE IF NOT EXISTS workflow_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_run_id INTEGER NOT NULL,
    output_key TEXT NOT NULL,
    output_value TEXT NOT NULL,  -- JSON or plain text
    output_type TEXT DEFAULT 'text' CHECK(output_type IN ('text', 'json', 'citation_list')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_workflow_name ON workflow_runs(workflow_name);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_run_id ON workflow_steps(workflow_run_id);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_status ON workflow_steps(status);
CREATE INDEX IF NOT EXISTS idx_workflow_outputs_run_id ON workflow_outputs(workflow_run_id);
```

***

### **File 3: `scripts/migrate_db.py`**

```python
#!/usr/bin/env python3
"""
Safe database migration for Phase 1: Schema Unification
Adds workflow tracking tables to existing project databases.

Usage:
    python scripts/migrate_db.py --dry-run          # Test without changes
    python scripts/migrate_db.py --project test_1   # Migrate specific project
    python scripts/migrate_db.py                    # Migrate all projects
"""

import sqlite3
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Schema version tracking
TARGET_VERSION = 3
CURRENT_VERSION = 2

class MigrationError(Exception):
    """Custom exception for migration failures."""
    pass

def backup_database(db_path: Path) -> Path:
    """
    Create timestamped backup of database.
    
    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    print(f"  ✅ Backup created: {backup_path.name}")
    return backup_path

def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version from database."""
    cursor = conn.cursor()
    try:
        result = cursor.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else 1
    except sqlite3.OperationalError:
        # schema_version table doesn't exist
        return 1

def verify_migration(conn: sqlite3.Connection) -> Tuple[bool, str]:
    """
    Verify migration succeeded.
    
    Returns:
        (success: bool, message: str)
    """
    cursor = conn.cursor()
    
    # Check new tables exist
    required_tables = ['workflow_runs', 'workflow_steps', 'workflow_outputs']
    for table in required_tables:
        result = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone()
        if not result:
            return False, f"Missing table: {table}"
    
    # Check schema version updated
    version = get_schema_version(conn)
    if version != TARGET_VERSION:
        return False, f"Schema version mismatch: expected {TARGET_VERSION}, got {version}"
    
    # Check foreign keys work
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    if fk_errors:
        return False, f"Foreign key integrity errors: {fk_errors}"
    
    # Count preserved data in old tables
    old_tables = ['picot_versions', 'literature_findings', 'milestones']
    counts = {}
    for table in old_tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            counts[table] = count
        except sqlite3.OperationalError:
            # Table might not exist in all databases
            pass
    
    print(f"  ✅ Data preserved: {counts}")
    return True, "Migration verified successfully"

def migrate_project_db(project_path: Path, dry_run: bool = False) -> bool:
    """
    Migrate a single project database.
    
    Returns:
        True if successful, False otherwise
    """
    db_path = project_path / "project.db"
    
    if not db_path.exists():
        print(f"  ⚠️  Skipping {project_path.name}: No database found")
        return False
    
    print(f"\n📦 Migrating: {project_path.name}")
    
    # Check if already migrated
    conn = sqlite3.connect(db_path)
    current_version = get_schema_version(conn)
    conn.close()
    
    if current_version >= TARGET_VERSION:
        print(f"  ℹ️  Already at version {current_version}, skipping")
        return True
    
    # Backup (always, even in dry-run)
    backup_path = backup_database(db_path)
    
    if dry_run:
        print(f"  🔍 [DRY RUN] Would migrate {db_path.name}")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Load and execute migration SQL
        schema_file = Path(__file__).parent / 'schema_additions.sql'
        with open(schema_file, 'r') as f:
            migration_sql = f.read()
        
        conn.executescript(migration_sql)
        
        # Update schema version
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(
            "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
            (TARGET_VERSION,)
        )
        
        conn.commit()
        
        # Verify
        success, message = verify_migration(conn)
        conn.close()
        
        if success:
            print(f"  ✅ Migration successful: {project_path.name}")
            return True
        else:
            raise MigrationError(f"Verification failed: {message}")
        
    except Exception as e:
        print(f"  ❌ Migration failed: {e}")
        print(f"  🔄 Restoring from backup: {backup_path.name}")
        shutil.copy2(backup_path, db_path)
        return False

def main():
    parser = argparse.ArgumentParser(description='Migrate project databases to Phase 1 schema')
    parser.add_argument('--dry-run', action='store_true', help='Test without making changes')
    parser.add_argument('--project', help='Migrate specific project only')
    args = parser.parse_args()
    
    projects_dir = Path('data/projects')
    
    if not projects_dir.exists():
        print(f"❌ Projects directory not found: {projects_dir}")
        return 1
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    # Migrate projects
    if args.project:
        project_path = projects_dir / args.project
        if not project_path.exists():
            print(f"❌ Project not found: {args.project}")
            return 1
        success = migrate_project_db(project_path, args.dry_run)
        return 0 if success else 1
    else:
        # Migrate all projects
        total = 0
        succeeded = 0
        for project_path in sorted(projects_dir.iterdir()):
            if project_path.is_dir():
                total += 1
                if migrate_project_db(project_path, args.dry_run):
                    succeeded += 1
        
        print(f"\n{'='*60}")
        print(f"Migration Summary: {succeeded}/{total} projects successful")
        if succeeded == total:
            print("✅ All migrations completed successfully")
            return 0
        else:
            print(f"⚠️  {total - succeeded} migrations failed")
            return 1

if __name__ == '__main__':
    exit(main())
```

***

### **File 4: `scripts/rollback_migration.sh`**

```bash
#!/bin/bash
# Rollback database migration
# Usage: ./scripts/rollback_migration.sh <backup_timestamp>
#        ./scripts/rollback_migration.sh 20251209_143022

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo "Available backups:"
    ls -1 data/backups/ 2>/dev/null || echo "  (none found)"
    exit 1
fi

BACKUP_DIR="data/backups/$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup not found: $BACKUP_DIR"
    exit 1
fi

echo "🔄 Rolling back from backup: $1"
echo "⚠️  This will overwrite current databases!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled"
    exit 0
fi

# Restore project databases
for backup in "${BACKUP_DIR}"/project.db; do
    if [ -f "$backup" ]; then
        # Extract project name from backup
        project=$(basename $(dirname "$backup"))
        target="data/projects/${project}/project.db"
        cp "$backup" "$target"
        echo "  ✅ Restored: ${project}/project.db"
    fi
done

# Restore orchestration database if exists
if [ -f "${BACKUP_DIR}/workflow_context.db" ]; then
    cp "${BACKUP_DIR}/workflow_context.db" data/orchestration/
    echo "  ✅ Restored: workflow_context.db"
fi

echo ""
echo "✅ Rollback complete from backup: $1"
```

***

## **Next: Testing Protocol**

Run these commands to validate before committing:

```bash
# 1. Make scripts executable
chmod +x scripts/*.sh scripts/migrate_db.py

# 2. Create backup
./scripts/backup_all_dbs.sh

# 3. Test migration on dummy project
python scripts/migrate_db.py --dry-run --project testing_1

# 4. Real migration on test project
python scripts/migrate_db.py --project testing_1

# 5. Verify schema
sqlite3 data/projects/testing_1/project.db ".schema workflow_runs"

# 6. Test rollback
./scripts/rollback_migration.sh <timestamp_from_step2>

# 7. Verify restoration
sqlite3 data/projects/testing_1/project.db ".schema workflow_runs"
# Should return: Error: no such table: workflow_runs
``

## **Instructions for Claude (in Cursor IDE)**

**Context**: I'm implementing Phase 1 of a 3-phase workflow system refactor for my nursing research multi-agent system. Need to create safety infrastructure before database migration.

**Task**: Create these 4 files in the nurseRN project:

### **Files to Create**

1. **`scripts/backup_all_dbs.sh`** - Backup all project databases
2. **`scripts/schema_additions.sql`** - New database tables for workflow tracking
3. **`scripts/migrate_db.py`** - Safe migration script with automatic rollback
4. **`scripts/rollback_migration.sh`** - Restore from backup

[Paste all 4 file contents here]

**After creating files**:
```bash
# Make executable
chmod +x scripts/*.sh scripts/migrate_db.py

# Test backup
./scripts/backup_all_dbs.sh

# Test migration (dry run)
python scripts/migrate_db.py --dry-run
```

**Verification checklist**:
- ✅ All 4 files created in `scripts/` directory
- ✅ Scripts are executable
- ✅ Backup creates `data/backups/{timestamp}/` directory
- ✅ Dry-run completes without errors

***
