# Database Backup & Restore Guide

## Current Database Status

The database currently contains **4 memos**:
1. Test Memo
2. Test from nginx
3. Updated: Memo Service Works
4. 10/6 (repository cleanup note)

## Backup Scripts

### Create a Backup

```bash
cd <project-root-directory>
./backup-database.sh
```

This will:
- Create a timestamped SQL backup file
- Compress it with gzip
- Keep only the last 30 backups (older ones are automatically deleted)

### Restore from Backup

```bash
cd <project-root-directory>
./restore-database.sh backups/memo_app_backup_YYYYMMDD_HHMMSS.sql.gz
```

Or with an uncompressed file:
```bash
./restore-database.sh backups/memo_app_backup_YYYYMMDD_HHMMSS.sql
```

This will:
- Show a confirmation prompt
- Restore the database from the specified backup file
- Replace all current data with backup data

## Automated Backups (Recommended)

### Set up a daily cron job:

```bash
# Edit crontab
crontab -e

# Add this line to run backup daily at 3 AM (adjust path to your installation)
0 3 * * * /path/to/sogangcomputerclub.org/backup-database.sh >> /path/to/sogangcomputerclub.org/backups/backup.log 2>&1
```

### Or set up hourly backups:

```bash
# Backup every hour (adjust path to your installation)
0 * * * * /path/to/sogangcomputerclub.org/backup-database.sh >> /path/to/sogangcomputerclub.org/backups/backup.log 2>&1
```

## Manual Database Operations

### List all memos:
```bash
# Load credentials from .env file
source .env
docker exec ${CONTAINER_NAME_PREFIX}-mariadb-1 mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT * FROM memos;"
```

### Count memos:
```bash
# Load credentials from .env file
source .env
docker exec ${CONTAINER_NAME_PREFIX}-mariadb-1 mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT COUNT(*) FROM memos;"
```

### Create manual backup:
```bash
# Load credentials from .env file
source .env
docker exec ${CONTAINER_NAME_PREFIX}-mariadb-1 mysqldump -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} > backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore manual backup:
```bash
# Load credentials from .env file
source .env
docker exec -i ${CONTAINER_NAME_PREFIX}-mariadb-1 mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} < backups/manual_backup_YYYYMMDD_HHMMSS.sql
```

## Docker Volume Backup

The database is stored in a Docker volume: `sogangcomputercluborg_mariadb_data`

### Backup the entire volume:
```bash
docker run --rm -v sogangcomputercluborg_mariadb_data:/data -v $(pwd)/backups:/backup ubuntu tar czf /backup/mariadb_volume_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### Restore volume:
```bash
docker run --rm -v sogangcomputercluborg_mariadb_data:/data -v $(pwd)/backups:/backup ubuntu tar xzf /backup/mariadb_volume_YYYYMMDD_HHMMSS.tar.gz -C /data
```

## Recovery Options

### If data was recently lost:

1. **Check existing backups** in this directory
2. **Check Docker volume** - data persists even if containers are recreated
3. **Check application logs** - may contain recent API requests with memo content

### If no backups exist:

Unfortunately, without backups, data cannot be recovered. The current 4 memos are all that remain in the database.

## Prevention

To prevent future data loss:

1. ✅ **Set up automated backups** (cron job recommended)
2. ✅ **Use Docker volumes** (already configured)
3. ✅ **Regular manual backups** before major changes
4. 📝 **Export important memos** to files
5. 🔄 **Version control** - commit exported data to git

## First Backup Created

- Date: 2025-10-06 02:51:25
- File: `memo_app_backup_20251006_025125.sql`
- Contains: 4 memos (all current data)
