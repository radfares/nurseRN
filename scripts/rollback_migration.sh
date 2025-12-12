#!/bin/bash
# Rollback database migration
# Usage: ./scripts/rollback_migration.sh <backup_timestamp>

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

for project_dir in "${BACKUP_DIR}"/*/; do
    if [ -d "$project_dir" ]; then
        project=$(basename "$project_dir")
        backup="${project_dir}project.db"
        if [ -f "$backup" ]; then
            target="data/projects/${project}/project.db"
            cp "$backup" "$target"
            echo "  ✅ Restored: ${project}/project.db"
        fi
    fi
done

if [ -f "${BACKUP_DIR}/workflow_context.db" ]; then
    cp "${BACKUP_DIR}/workflow_context.db" data/orchestration/
    echo "  ✅ Restored: workflow_context.db"
fi

echo ""
echo "✅ Rollback complete from backup: $1"
