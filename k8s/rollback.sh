#!/bin/bash

# Kubernetes Rollback Script
# Usage: ./rollback.sh [environment] [type] [options]

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Display usage
usage() {
    cat << EOF
Usage: $0 [ENVIRONMENT] [TYPE] [OPTIONS]

ENVIRONMENT:
    production      Rollback production environment
    staging         Rollback staging environment

TYPE:
    previous        Rollback to previous revision
    revision N      Rollback to specific revision N
    image           Rollback to specific image(s)

OPTIONS (for 'image' type):
    --backend IMAGE     Specify backend image
    --frontend IMAGE    Specify frontend image

Examples:
    $0 production previous
    $0 staging revision 3
    $0 production image --backend ghcr.io/owner/repo/backend:v1.2.3
    $0 staging image --backend ghcr.io/owner/repo/backend:abc123 --frontend ghcr.io/owner/repo/frontend:abc123

EOF
    exit 1
}

# Parse arguments
ENVIRONMENT=${1:-}
ROLLBACK_TYPE=${2:-}
BACKEND_IMAGE=""
FRONTEND_IMAGE=""
REVISION=""

if [ -z "$ENVIRONMENT" ] || [ -z "$ROLLBACK_TYPE" ]; then
    usage
fi

# Set namespace based on environment
if [ "$ENVIRONMENT" == "production" ]; then
    NAMESPACE="sgcc"
elif [ "$ENVIRONMENT" == "staging" ]; then
    NAMESPACE="sgcc-staging"
else
    print_error "Invalid environment: $ENVIRONMENT"
    usage
fi

# Parse rollback type and options
case "$ROLLBACK_TYPE" in
    previous)
        MODE="previous"
        ;;
    revision)
        MODE="revision"
        REVISION=${3:-}
        if [ -z "$REVISION" ]; then
            print_error "Revision number required for revision rollback"
            usage
        fi
        ;;
    image)
        MODE="image"
        shift 2
        while [ $# -gt 0 ]; do
            case "$1" in
                --backend)
                    BACKEND_IMAGE="$2"
                    shift 2
                    ;;
                --frontend)
                    FRONTEND_IMAGE="$2"
                    shift 2
                    ;;
                *)
                    print_error "Unknown option: $1"
                    usage
                    ;;
            esac
        done
        if [ -z "$BACKEND_IMAGE" ] && [ -z "$FRONTEND_IMAGE" ]; then
            print_error "At least one image must be specified for image rollback"
            usage
        fi
        ;;
    *)
        print_error "Invalid rollback type: $ROLLBACK_TYPE"
        usage
        ;;
esac

# Verify kubectl connection
if ! kubectl cluster-info &> /dev/null; then
    print_error "Unable to connect to Kubernetes cluster. Check your kubeconfig."
    exit 1
fi

print_info "=== Kubernetes Rollback Started ==="
print_info "Environment: $ENVIRONMENT"
print_info "Namespace: $NAMESPACE"
print_info "Rollback Type: $ROLLBACK_TYPE"
echo ""

# Show current deployment status
print_step "1. Current deployment status"
echo ""
echo "Backend Image:"
CURRENT_BACKEND=$(kubectl get deployment fastapi -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "  $CURRENT_BACKEND"
echo ""
echo "Frontend Image:"
CURRENT_FRONTEND=$(kubectl get deployment frontend -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "  $CURRENT_FRONTEND"
echo ""

# Show rollout history
print_step "2. Deployment history"
echo ""
echo "Backend History:"
kubectl rollout history deployment/fastapi -n $NAMESPACE
echo ""
echo "Frontend History:"
kubectl rollout history deployment/frontend -n $NAMESPACE
echo ""

# Confirmation prompt
print_warn "You are about to rollback the $ENVIRONMENT environment"
read -p "Do you want to continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    print_info "Rollback cancelled"
    exit 0
fi

# Perform rollback
print_step "3. Initiating rollback"
echo ""

case "$MODE" in
    previous)
        print_info "Rolling back to previous revision..."
        kubectl rollout undo deployment/fastapi -n $NAMESPACE
        kubectl rollout undo deployment/frontend -n $NAMESPACE
        ;;
    revision)
        print_info "Rolling back to revision $REVISION..."
        kubectl rollout undo deployment/fastapi -n $NAMESPACE --to-revision=$REVISION
        kubectl rollout undo deployment/frontend -n $NAMESPACE --to-revision=$REVISION
        ;;
    image)
        if [ -n "$BACKEND_IMAGE" ]; then
            print_info "Rolling back backend to: $BACKEND_IMAGE"
            kubectl set image deployment/fastapi fastapi=$BACKEND_IMAGE -n $NAMESPACE --record
        fi
        if [ -n "$FRONTEND_IMAGE" ]; then
            print_info "Rolling back frontend to: $FRONTEND_IMAGE"
            kubectl set image deployment/frontend frontend=$FRONTEND_IMAGE -n $NAMESPACE --record
        fi
        ;;
esac

# Wait for rollback
print_step "4. Waiting for rollback to complete"
kubectl rollout status deployment/fastapi -n $NAMESPACE --timeout=5m || {
    print_error "Backend rollback failed"
    exit 1
}
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=5m || {
    print_error "Frontend rollback failed"
    exit 1
}

# Verify health
print_step "5. Verifying rollback health"
kubectl wait --for=condition=ready pod -l app=fastapi -n $NAMESPACE --timeout=3m || {
    print_error "Backend pods not ready after rollback"
    exit 1
}
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=3m || {
    print_error "Frontend pods not ready after rollback"
    exit 1
}

# Health check
print_step "6. Running health checks"
FASTAPI_POD=$(kubectl get pod -n $NAMESPACE -l app=fastapi -o jsonpath="{.items[0].metadata.name}")
if kubectl exec -n $NAMESPACE "$FASTAPI_POD" -- wget -q -O- http://localhost:8000/health &> /dev/null; then
    print_info "Backend health check: PASSED ✓"
else
    print_warn "Backend health check: FAILED ✗"
    exit 1
fi

# Monitor stability
print_step "7. Monitoring stability (60 seconds)"
sleep 60

RESTART_COUNT=$(kubectl get pods -n $NAMESPACE -l app=fastapi -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}' | awk '{s+=$1} END {print s}')
if [ "$RESTART_COUNT" -gt "0" ]; then
    print_warn "Warning: Detected $RESTART_COUNT pod restarts"
else
    print_info "No pod restarts detected ✓"
fi

# Show final status
print_step "8. Final deployment status"
echo ""
echo "Backend Image:"
kubectl get deployment fastapi -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}'
echo ""
echo "Frontend Image:"
kubectl get deployment frontend -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}'
echo ""
echo ""
kubectl get pods -n $NAMESPACE

echo ""
print_info "=== Rollback Completed Successfully ==="
if [ "$ENVIRONMENT" == "production" ]; then
    print_info "Application URL: https://sogangcomputerclub.org"
else
    print_info "Application URL: https://staging.sogangcomputerclub.org"
fi
