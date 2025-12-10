#!/bin/bash

# cleanup_infrastructure.sh
# This script ensures that all project containers are named with the 'sgcc-' prefix
# and removes any orphaned or unnecessary containers.

set -e

echo "Starting infrastructure cleanup..."

# 1. Stop and remove containers that are part of the project but don't have the 'sgcc-' prefix.
# We look for containers that might have been created by docker-compose before we added container_name.
# Common old names: sogangcomputercluborg-fastapi-1, sogangcomputercluborg-frontend-1, etc.
# Also generic names if they were used: fastapi, frontend, nginx.

OLD_CONTAINERS=(
    "sogangcomputercluborg-fastapi-1"
    "sogangcomputercluborg-frontend-1"
    "sogangcomputercluborg-nginx-1"
    "sogangcomputercluborg-redis-1"
    "sogangcomputercluborg-mariadb-1"
    "sogangcomputercluborg-kafka-1"
    "sogangcomputercluborg-zookeeper-1"
    "sogangcomputercluborg-prometheus-1"
    "sogangcomputercluborg-grafana-1"
    "sogangcomputercluborg-redis-exporter-1"
    "sogangcomputercluborg-postgres-exporter-1"
    "sogangcomputercluborg-nginx-exporter-1"
    "sogangcomputercluborg-certbot-1"
    "fastapi"
    "frontend"
    "nginx"
)

echo "Checking for old containers..."
for container in "${OLD_CONTAINERS[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "Removing old container: $container"
        docker stop "$container" || true
        docker rm "$container" || true
    fi
done

# 2. Prune stopped containers to be safe (optional, maybe too aggressive? Let's stick to explicit removal for now)
# docker container prune -f

# 3. Bring up the stack using docker-compose.prod.yml
# This will create containers with the names defined in the file (sgcc-*)
echo "Starting services with correct names..."
if [ -f "docker-compose.prod.yml" ]; then
    # Ensure GITHUB_REPOSITORY is set if not already
    export GITHUB_REPOSITORY=${GITHUB_REPOSITORY:-sogangcomputerclub/sogangcomputerclub.org}
    
    docker-compose -f docker-compose.prod.yml up -d --remove-orphans
else
    echo "Error: docker-compose.prod.yml not found!"
    exit 1
fi

echo "Infrastructure cleanup complete."
echo "Current running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "sgcc-"
