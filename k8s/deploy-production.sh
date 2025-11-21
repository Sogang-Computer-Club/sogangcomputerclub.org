#!/bin/bash

# Production Kubernetes Deployment Script
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verify kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    print_error "Unable to connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_info "=== Production Deployment Started ==="
print_info "Cluster: $(kubectl config current-context)"

# Create namespace if it doesn't exist
print_info "1. Ensuring namespace exists..."
kubectl apply -f namespace.yaml

# Apply secrets (if they exist)
print_info "2. Applying secrets..."
if [ -f "configmap-secret.yaml" ]; then
    kubectl apply -f configmap-secret.yaml
else
    print_warn "configmap-secret.yaml not found, skipping"
fi

if [ -f "mariadb-secret.yaml" ]; then
    kubectl apply -f mariadb-secret.yaml
else
    print_warn "mariadb-secret.yaml not found, skipping"
fi

# Apply ConfigMaps
print_info "3. Applying ConfigMaps..."
kubectl apply -f configmap.yaml

# Deploy infrastructure components
print_info "4. Deploying infrastructure (MariaDB, Redis, Kafka)..."
kubectl apply -f mariadb.yaml
kubectl apply -f redis.yaml
kubectl apply -f kafka.yaml

# Wait for infrastructure to be ready
print_info "5. Waiting for infrastructure to be ready..."
kubectl wait --for=condition=ready pod -l app=mariadb -n sgcc --timeout=300s || print_warn "MariaDB timeout"
kubectl wait --for=condition=ready pod -l app=redis -n sgcc --timeout=180s || print_warn "Redis timeout"

# Deploy application services (use production manifests if available)
print_info "6. Deploying application services..."
if [ -f "fastapi-production.yaml" ]; then
    kubectl apply -f fastapi-production.yaml
else
    print_warn "fastapi-production.yaml not found, using fastapi.yaml"
    kubectl apply -f fastapi.yaml
fi

if [ -f "frontend-production.yaml" ]; then
    kubectl apply -f frontend-production.yaml
else
    print_warn "frontend-production.yaml not found, using frontend.yaml"
    kubectl apply -f frontend.yaml
fi

# Apply Ingress
print_info "7. Applying Ingress configuration..."
kubectl apply -f ingress.yaml

# Wait for deployments to complete
print_info "8. Waiting for deployments to complete..."
kubectl rollout status deployment/fastapi -n sgcc --timeout=300s
kubectl rollout status deployment/frontend -n sgcc --timeout=300s

# Verify deployment
print_info "9. Verifying deployment..."
echo ""
echo "=== Pod Status ==="
kubectl get pods -n sgcc

echo ""
echo "=== Service Status ==="
kubectl get svc -n sgcc

echo ""
echo "=== Ingress Status ==="
kubectl get ingress -n sgcc

# Health check
print_info "10. Running health checks..."
FASTAPI_POD=$(kubectl get pod -n sgcc -l app=fastapi -o jsonpath="{.items[0].metadata.name}")
if [ -n "$FASTAPI_POD" ]; then
    if kubectl exec -n sgcc "$FASTAPI_POD" -- wget -q -O- http://localhost:8000/health &> /dev/null; then
        print_info "Backend health check: PASSED ✓"
    else
        print_warn "Backend health check: FAILED ✗"
    fi
fi

FRONTEND_POD=$(kubectl get pod -n sgcc -l app=frontend -o jsonpath="{.items[0].metadata.name}")
if [ -n "$FRONTEND_POD" ]; then
    if kubectl exec -n sgcc "$FRONTEND_POD" -- wget -q -O- http://localhost:3000 &> /dev/null; then
        print_info "Frontend health check: PASSED ✓"
    else
        print_warn "Frontend health check: FAILED ✗"
    fi
fi

echo ""
print_info "=== Deployment Complete ==="
print_info "Application URL: https://sogangcomputerclub.org"
print_info ""
print_info "Useful commands:"
echo "  - View logs: kubectl logs -f deployment/fastapi -n sgcc"
echo "  - Describe pod: kubectl describe pod <pod-name> -n sgcc"
echo "  - Rollback: kubectl rollout undo deployment/fastapi -n sgcc"
echo "  - Scale: kubectl scale deployment/fastapi --replicas=5 -n sgcc"
