#!/bin/bash

# Database Backup Script for sogangcomputerclub.org
# Creates timestamped backups of the memo_app database

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/memo_app_backup_${TIMESTAMP}.sql"
CONTAINER_NAME="${CONTAINER_NAME_PREFIX:-sogangcomputercluborg}-mariadb-1"
DB_USER="${MYSQL_USER:-memo_user}"
DB_PASS="${MYSQL_PASSWORD:-changeme}"
DB_NAME="${MYSQL_DATABASE:-memo_app}"

# Keep only the last 30 backups
KEEP_BACKUPS=30

echo "Creating backup: ${BACKUP_FILE}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create backup
docker exec ${CONTAINER_NAME} mysqldump -u${DB_USER} -p${DB_PASS} ${DB_NAME} > "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "Backup created successfully: ${BACKUP_FILE}"

    # Compress the backup
    gzip "${BACKUP_FILE}"
    echo "Backup compressed: ${BACKUP_FILE}.gz"

    # Remove old backups (keep only the last N)
    cd "${BACKUP_DIR}"
    ls -t memo_app_backup_*.sql.gz | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm

    echo "Cleanup completed. Kept last ${KEEP_BACKUPS} backups."
else
    echo "Backup failed!"
    exit 1
fi
