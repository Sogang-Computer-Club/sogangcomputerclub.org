#!/bin/bash

# Staging Kubernetes Deployment Script
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verify kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    print_error "Unable to connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

print_info "=== Staging Deployment Started ==="
print_info "Cluster: $(kubectl config current-context)"
print_info "Environment: Staging"

# Create staging namespace if it doesn't exist
print_step "1. Ensuring staging namespace exists..."
kubectl apply -f namespace-staging.yaml

# Create or update image pull secret
print_step "2. Creating image pull secret..."
if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_ACTOR" ]; then
    kubectl create secret docker-registry ghcr-secret \
        --docker-server=ghcr.io \
        --docker-username="$GITHUB_ACTOR" \
        --docker-password="$GITHUB_TOKEN" \
        --namespace=sgcc-staging \
        --dry-run=client -o yaml | kubectl apply -f -
else
    print_warn "GITHUB_TOKEN or GITHUB_ACTOR not set, skipping image pull secret creation"
fi

# Apply secrets (if they exist)
print_step "3. Applying secrets..."
if [ -f "configmap-secret-staging.yaml" ]; then
    kubectl apply -f configmap-secret-staging.yaml
elif [ -f "configmap-secret.yaml" ]; then
    print_warn "Using production secret for staging (configmap-secret-staging.yaml not found)"
    kubectl apply -f configmap-secret.yaml
else
    print_warn "No secrets found, skipping"
fi

if [ -f "mariadb-secret-staging.yaml" ]; then
    kubectl apply -f mariadb-secret-staging.yaml
elif [ -f "mariadb-secret.yaml" ]; then
    print_warn "Using production secret for staging (mariadb-secret-staging.yaml not found)"
    kubectl apply -f mariadb-secret.yaml
else
    print_warn "No database secrets found, skipping"
fi

# Apply ConfigMaps
print_step "4. Applying ConfigMaps..."
if [ -f "configmap-staging.yaml" ]; then
    kubectl apply -f configmap-staging.yaml
else
    print_warn "configmap-staging.yaml not found, using default configmap.yaml"
    kubectl apply -f configmap.yaml
fi

# Store current deployment for potential rollback
print_step "5. Storing current deployment state..."
CURRENT_BACKEND=$(kubectl get deployment fastapi -n sgcc-staging -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "none")
CURRENT_FRONTEND=$(kubectl get deployment frontend -n sgcc-staging -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "none")

echo "Current Backend: $CURRENT_BACKEND"
echo "Current Frontend: $CURRENT_FRONTEND"

# Deploy application services
print_step "6. Deploying application services..."
kubectl apply -f fastapi-staging.yaml
kubectl apply -f frontend-staging.yaml

# Wait for deployments to complete
print_step "7. Waiting for deployments to complete..."
if ! kubectl rollout status deployment/fastapi -n sgcc-staging --timeout=300s; then
    print_error "Backend deployment failed"

    # Attempt rollback
    if [ "$CURRENT_BACKEND" != "none" ]; then
        print_warn "Initiating rollback for backend..."
        kubectl set image deployment/fastapi fastapi=$CURRENT_BACKEND -n sgcc-staging
        kubectl rollout status deployment/fastapi -n sgcc-staging --timeout=180s || true
    fi
    exit 1
fi

if ! kubectl rollout status deployment/frontend -n sgcc-staging --timeout=300s; then
    print_error "Frontend deployment failed"

    # Attempt rollback
    if [ "$CURRENT_FRONTEND" != "none" ]; then
        print_warn "Initiating rollback for frontend..."
        kubectl set image deployment/frontend frontend=$CURRENT_FRONTEND -n sgcc-staging
        kubectl rollout status deployment/frontend -n sgcc-staging --timeout=180s || true
    fi
    exit 1
fi

# Verify deployment
print_step "8. Verifying deployment..."
echo ""
echo "=== Pod Status ==="
kubectl get pods -n sgcc-staging

echo ""
echo "=== Service Status ==="
kubectl get svc -n sgcc-staging

# Wait for pods to be ready
print_step "9. Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=fastapi -n sgcc-staging --timeout=120s || {
    print_error "Backend pods failed to become ready"
    exit 1
}

kubectl wait --for=condition=ready pod -l app=frontend -n sgcc-staging --timeout=120s || {
    print_error "Frontend pods failed to become ready"
    exit 1
}

# Health check
print_step "10. Running health checks..."
FASTAPI_POD=$(kubectl get pod -n sgcc-staging -l app=fastapi -o jsonpath="{.items[0].metadata.name}")
if [ -n "$FASTAPI_POD" ]; then
    if kubectl exec -n sgcc-staging "$FASTAPI_POD" -- wget -q -O- http://localhost:8000/health &> /dev/null; then
        print_info "Backend health check: PASSED ✓"
    else
        print_warn "Backend health check: FAILED ✗"
        exit 1
    fi
fi

FRONTEND_POD=$(kubectl get pod -n sgcc-staging -l app=frontend -o jsonpath="{.items[0].metadata.name}")
if [ -n "$FRONTEND_POD" ]; then
    if kubectl exec -n sgcc-staging "$FRONTEND_POD" -- wget -q -O- http://localhost:3000 &> /dev/null; then
        print_info "Frontend health check: PASSED ✓"
    else
        print_warn "Frontend health check: FAILED ✗"
        exit 1
    fi
fi

# Check for pod restarts
print_step "11. Checking deployment stability..."
sleep 30
RESTART_COUNT=$(kubectl get pods -n sgcc-staging -l app=fastapi -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}' | awk '{s+=$1} END {print s}')
if [ "$RESTART_COUNT" -gt "0" ]; then
    print_warn "Warning: Detected $RESTART_COUNT pod restarts"
else
    print_info "No pod restarts detected ✓"
fi

echo ""
print_info "=== Staging Deployment Complete ==="
print_info "Application URL: https://staging.sogangcomputerclub.org"
print_info ""
print_info "Useful commands:"
echo "  - View logs: kubectl logs -f deployment/fastapi -n sgcc-staging"
echo "  - Describe pod: kubectl describe pod <pod-name> -n sgcc-staging"
echo "  - Rollback: kubectl rollout undo deployment/fastapi -n sgcc-staging"
echo "  - Scale: kubectl scale deployment/fastapi --replicas=3 -n sgcc-staging"
echo "  - History: kubectl rollout history deployment/fastapi -n sgcc-staging"
