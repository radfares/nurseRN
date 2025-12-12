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
        project_name=$(basename $(dirname "$db"))
        mkdir -p "${BACKUP_DIR}/${project_name}"
        cp "$db" "${BACKUP_DIR}/${project_name}/"
        PROJECT_COUNT=$((PROJECT_COUNT + 1))
        echo "  ✅ ${project_name}/project.db"
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
