#!/bin/bash

# Database Restore Script for sogangcomputerclub.org
# Restores database from a backup file

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

BACKUP_DIR="${BACKUP_DIR:-./backups}"
CONTAINER_NAME="${CONTAINER_NAME_PREFIX:-sogangcomputercluborg}-postgres-1"
DB_USER="${POSTGRES_USER:-memo_user}"
DB_PASS="${POSTGRES_PASSWORD:-phoenix}"
DB_NAME="${POSTGRES_DB:-memo_app}"

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh "${BACKUP_DIR}"/memo_app_backup_*.sql* 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Check if file is gzipped
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    echo "Decompressing backup file..."
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "${BACKUP_FILE}" > "${TEMP_FILE}"
    BACKUP_FILE="${TEMP_FILE}"
    CLEANUP_TEMP=true
fi

echo "WARNING: This will replace all data in the ${DB_NAME} database!"
echo "Backup file: ${BACKUP_FILE}"
read -p "Are you sure you want to continue? (yes/no): " confirmation

if [ "${confirmation}" != "yes" ]; then
    echo "Restore cancelled."
    [ "${CLEANUP_TEMP}" = true ] && rm -f "${TEMP_FILE}"
    exit 0
fi

echo "Restoring database from ${BACKUP_FILE}..."

# Restore the backup
cat "${BACKUP_FILE}" | docker exec -i -e PGPASSWORD=${DB_PASS} ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME}

if [ $? -eq 0 ]; then
    echo "Database restored successfully!"
else
    echo "Restore failed!"
    exit 1
fi

# Cleanup temporary file
[ "${CLEANUP_TEMP}" = true ] && rm -f "${TEMP_FILE}"

echo "Restore completed."
