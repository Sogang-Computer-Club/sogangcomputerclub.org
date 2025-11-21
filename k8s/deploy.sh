#!/bin/bash
# Local/Development Deployment Script
# Uses: sgcc-local namespace
# For: Local KIND cluster or development testing

# Kubernetes 배포 스크립트
set -e

echo "=== Memo App Kubernetes 로컬 배포 시작 ==="
echo "환경: Local Development"
echo "네임스페이스: sgcc-local"
echo ""

# 네임스페이스 생성
echo "1. 네임스페이스 생성..."
kubectl apply -f namespace-local.yaml

# ConfigMap 적용
echo "2. ConfigMap 적용..."
kubectl apply -f configmap.yaml

# 데이터베이스 배포
echo "3. MariaDB 배포..."
kubectl apply -f mariadb.yaml

# Redis 배포
echo "4. Redis 배포..."
kubectl apply -f redis.yaml

# Kafka 배포 (Zookeeper 포함)
echo "5. Kafka 및 Zookeeper 배포..."
kubectl apply -f kafka.yaml

# FastAPI 애플리케이션 배포
echo "6. FastAPI 애플리케이션 배포..."
kubectl apply -f fastapi.yaml

# Ingress 적용
echo "7. Ingress 적용..."
kubectl apply -f ingress.yaml

echo "=== 배포 완료 ==="
echo ""
echo "다음 명령어로 상태를 확인할 수 있습니다:"
echo "kubectl get pods -n sgcc-local"
echo "kubectl get svc -n sgcc-local"
echo "kubectl get ingress -n sgcc-local"
echo ""
echo "로컬 개발 환경 배포 완료"