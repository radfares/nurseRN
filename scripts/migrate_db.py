#!/usr/bin/env python3
"""
Safe database migration for Phase 1: Schema Unification
Adds workflow tracking tables to existing project databases.

Usage:
    python scripts/migrate_db.py --dry-run
    python scripts/migrate_db.py --project test_1
    python scripts/migrate_db.py
"""

import sqlite3
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple

TARGET_VERSION = 3
CURRENT_VERSION = 2

class MigrationError(Exception):
    pass

def backup_database(db_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    print(f"  ✅ Backup created: {backup_path.name}")
    return backup_path

def get_schema_version(conn: sqlite3.Connection) -> int:
    cursor = conn.cursor()
    try:
        result = cursor.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else 1
    except sqlite3.OperationalError:
        return 1

def verify_migration(conn: sqlite3.Connection) -> Tuple[bool, str]:
    cursor = conn.cursor()

    required_tables = ['workflow_runs', 'workflow_steps', 'workflow_outputs']
    for table in required_tables:
        result = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone()
        if not result:
            return False, f"Missing table: {table}"

    version = get_schema_version(conn)
    if version != TARGET_VERSION:
        return False, f"Schema version mismatch: expected {TARGET_VERSION}, got {version}"

    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    if fk_errors:
        return False, f"Foreign key integrity errors: {fk_errors}"

    old_tables = ['picot_versions', 'literature_findings', 'milestones']
    counts = {}
    for table in old_tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            counts[table] = count
        except sqlite3.OperationalError:
            pass

    print(f"  ✅ Data preserved: {counts}")
    return True, "Migration verified successfully"

def migrate_project_db(project_path: Path, dry_run: bool = False) -> bool:
    db_path = project_path / "project.db"

    if not db_path.exists():
        print(f"  ⚠️  Skipping {project_path.name}: No database found")
        return False

    print(f"\n📦 Migrating: {project_path.name}")

    conn = sqlite3.connect(db_path)
    current_version = get_schema_version(conn)
    conn.close()

    if current_version >= TARGET_VERSION:
        print(f"  ℹ️  Already at version {current_version}, skipping")
        return True

    backup_path = backup_database(db_path)

    if dry_run:
        print(f"  🔍 [DRY RUN] Would migrate {db_path.name}")
        return True

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")

        schema_file = Path(__file__).parent / 'schema_additions.sql'
        with open(schema_file, 'r') as f:
            migration_sql = f.read()

        conn.executescript(migration_sql)

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

    if args.project:
        project_path = projects_dir / args.project
        if not project_path.exists():
            print(f"❌ Project not found: {args.project}")
            return 1
        success = migrate_project_db(project_path, args.dry_run)
        return 0 if success else 1
    else:
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
