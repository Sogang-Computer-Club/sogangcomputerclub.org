# 데이터베이스 백업 및 복구 가이드

## 백업 스크립트

### 백업을 생성하는 방법

```bash
cd <project-root-directory>
scripts/backup-database.sh
```

이 작업은...
- 타임스탬프가 찍힌 SQL 백업 파일을 생성한 뒤 gzip으로 압축합니다.
- 최근 30개의 백업만 유지합니다. (오래된 백업은 자동으로 삭제됩니다.)

### 백업으로 복구하는 방법

압축된 백업 파일로 복구하는 방법은 아래와 같습니다.
```bash
cd <project-root-directory>
scripts/restore-database.sh backups/memo_app_backup_YYYYMMDD_HHMMSS.sql.gz
```

압축되지 않은 백업 파일로 복구하는 방법은 아래와 같습니다.
```bash
scripts/restore-database.sh backups/memo_app_backup_YYYYMMDD_HHMMSS.sql
```

이 작업은...
- 지정된 백업 파일에서 데이터베이스를 복구합니다.
- 현재 모든 데이터를 백업 데이터로 교체합니다.

## 자동 백업 (권장)

### 일일 백업을 위한 cron 작업 설정:

```bash
# crontab 편집
crontab -e

# 매일 새벽 3시에 백업을 실행하도록 이 줄을 추가 (설치 경로에 맞게 조정)
0 3 * * * /path/to/sogangcomputerclub.org/backup-database.sh >> /path/to/sogangcomputerclub.org/backups/backup.log 2>&1
```

### 또는 시간별 백업 설정:

```bash
# 매시간 백업 (설치 경로에 맞게 조정)
0 * * * * /path/to/sogangcomputerclub.org/backup-database.sh >> /path/to/sogangcomputerclub.org/backups/backup.log 2>&1
```

## 수동으로 데이터베이스 조작하기

### 모든 메모 나열하기:
```bash
# .env 파일에서 자격 증명 로드
source .env
docker exec ${CONTAINER_NAME_PREFIX}-mariadb-1 mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT * FROM memos;"
```

### 메모 수 계산하기:
```bash
# .env 파일에서 자격 증명 로드
source .env
docker exec ${CONTAINER_NAME_PREFIX}-mariadb-1 mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} -e "SELECT COUNT(*) FROM memos;"
```

### 수동 백업 생성하기:
```bash
# .env 파일에서 자격 증명 로드
source .env
docker exec ${CONTAINER_NAME_PREFIX}-mariadb-1 mysqldump -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} > backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 수동 백업 복구하기:
```bash
# .env 파일에서 자격 증명 로드
source .env
docker exec -i ${CONTAINER_NAME_PREFIX}-mariadb-1 mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} < backups/manual_backup_YYYYMMDD_HHMMSS.sql
```

## Docker 볼륨에 백업하기

데이터베이스는 Docker 볼륨인 `sogangcomputercluborg_mariadb_data`에 저장됩니다.

### 전체 볼륨 백업하기:
```bash
docker run --rm -v sogangcomputercluborg_mariadb_data:/data -v $(pwd)/backups:/backup ubuntu tar czf /backup/mariadb_volume_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### 볼륨 복구하기:
```bash
docker run --rm -v sogangcomputercluborg_mariadb_data:/data -v $(pwd)/backups:/backup ubuntu tar xzf /backup/mariadb_volume_YYYYMMDD_HHMMSS.tar.gz -C /data
```

## 복구 옵션

### 데이터가 최근에 손실된 경우

1. **기존 백업 확인**: 이 디렉토리부터 먼저 확인해주세요.
2. **Docker 볼륨 확인**: 컨테이너가 재생성되어도 데이터는 유지됩니다.
3. **애플리케이션 로그 확인**: 메모 내용이 포함된 최근 API 요청이 있을 수 있습니다.

### 백업이 없는 경우:

안타깝게도 백업 없이는 데이터를 복구할 수 없습니다. 향후 데이터 손실을 방지하기 위해서는 아래의 옵션을 고려할 수 있습니다.

1. **자동 백업 설정**
2. **Docker 볼륨 사용**
3. **정기적인 수동 백업**
4. **중요한 메모 내보내기**