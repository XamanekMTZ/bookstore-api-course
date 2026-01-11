#!/bin/bash

# BookStore API Kubernetes Deployment Script
# This script deploys the complete BookStore API stack to Kubernetes

set -e

# Configuration
NAMESPACE="bookstore-api"
KUBECTL_CMD="kubectl"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if cert-manager is installed (for SSL certificates)
    if ! kubectl get crd certificates.cert-manager.io &> /dev/null; then
        log_warning "cert-manager is not installed. SSL certificates will need to be managed manually."
    fi
    
    log_success "Prerequisites check completed"
}

# Create namespace
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl apply -f namespace.yaml
        log_success "Namespace created"
    fi
}

# Deploy secrets and config
deploy_config() {
    log_info "Deploying configuration and secrets..."
    
    log_warning "IMPORTANT: Please update secrets.yaml with your actual base64-encoded values before deployment!"
    read -p "Have you updated the secrets? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Please update secrets.yaml with your production values and run again"
        exit 1
    fi
    
    kubectl apply -f configmap.yaml
    kubectl apply -f secrets.yaml
    
    log_success "Configuration deployed"
}

# Deploy database
deploy_database() {
    log_info "Deploying PostgreSQL database..."
    
    kubectl apply -f postgresql.yaml
    
    # Wait for database to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgresql -n $NAMESPACE --timeout=300s
    
    log_success "PostgreSQL deployed and ready"
}

# Deploy Redis
deploy_redis() {
    log_info "Deploying Redis cache..."
    
    kubectl apply -f redis.yaml
    
    # Wait for Redis to be ready
    log_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    
    log_success "Redis deployed and ready"
}

# Deploy API
deploy_api() {
    log_info "Deploying BookStore API..."
    
    kubectl apply -f api-deployment.yaml
    
    # Wait for API to be ready
    log_info "Waiting for API to be ready..."
    kubectl wait --for=condition=ready pod -l app=bookstore-api -n $NAMESPACE --timeout=300s
    
    log_success "BookStore API deployed and ready"
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring stack (Prometheus & Grafana)..."
    
    kubectl apply -f monitoring.yaml
    
    # Wait for monitoring to be ready
    log_info "Waiting for monitoring stack to be ready..."
    kubectl wait --for=condition=ready pod -l app=prometheus -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=grafana -n $NAMESPACE --timeout=300s
    
    log_success "Monitoring stack deployed and ready"
}

# Deploy ingress
deploy_ingress() {
    log_info "Deploying ingress configuration..."
    
    log_warning "Please update ingress.yaml with your actual domain names before deployment!"
    read -p "Have you updated the domain names in ingress.yaml? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Please update ingress.yaml with your domain names and run again"
        exit 1
    fi
    
    kubectl apply -f ingress.yaml
    
    log_success "Ingress deployed"
}

# Check deployment status
check_status() {
    log_info "Checking deployment status..."
    
    echo
    log_info "Pods status:"
    kubectl get pods -n $NAMESPACE
    
    echo
    log_info "Services status:"
    kubectl get services -n $NAMESPACE
    
    echo
    log_info "Ingress status:"
    kubectl get ingress -n $NAMESPACE
    
    echo
    log_info "HPA status:"
    kubectl get hpa -n $NAMESPACE
}

# Get access information
get_access_info() {
    log_info "Getting access information..."
    
    # Get ingress IP
    INGRESS_IP=$(kubectl get ingress bookstore-api-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending")
    
    echo
    log_success "Deployment completed successfully!"
    echo
    echo "Access Information:"
    echo "=================="
    echo "API URL: https://api.yourdomain.com"
    echo "Monitoring: https://monitoring.yourdomain.com"
    echo "Ingress IP: $INGRESS_IP"
    echo
    echo "Health Check:"
    echo "curl -k https://api.yourdomain.com/health"
    echo
    echo "Grafana Login:"
    echo "Username: admin"
    echo "Password: (from GRAFANA_PASSWORD secret)"
    echo
    echo "To get logs:"
    echo "kubectl logs -f deployment/bookstore-api -n $NAMESPACE"
    echo
    echo "To scale the API:"
    echo "kubectl scale deployment bookstore-api --replicas=5 -n $NAMESPACE"
}

# Main deployment function
main() {
    log_info "Starting BookStore API Kubernetes deployment..."
    
    check_prerequisites
    create_namespace
    deploy_config
    deploy_database
    deploy_redis
    deploy_api
    deploy_monitoring
    deploy_ingress
    
    # Wait a bit for everything to settle
    sleep 10
    
    check_status
    get_access_info
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "status")
        check_status
        ;;
    "delete")
        log_warning "This will delete the entire BookStore API deployment!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deleting deployment..."
            kubectl delete namespace $NAMESPACE
            log_success "Deployment deleted"
        fi
        ;;
    "update")
        log_info "Updating API deployment..."
        kubectl rollout restart deployment/bookstore-api -n $NAMESPACE
        kubectl rollout status deployment/bookstore-api -n $NAMESPACE
        log_success "API updated"
        ;;
    *)
        echo "Usage: $0 {deploy|status|delete|update}"
        echo
        echo "Commands:"
        echo "  deploy  - Deploy the complete stack (default)"
        echo "  status  - Check deployment status"
        echo "  delete  - Delete the entire deployment"
        echo "  update  - Update the API deployment"
        exit 1
        ;;
esac