#!/bin/bash
# deployment_utils.sh
# Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project/deployment/scripts/deployment_utils.sh

# Base paths and configurations
LOCAL_BASE="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project"
EC2_USER="ubuntu"
EC2_HOST="ec2-34-233-67-166.compute-1.amazonaws.com"
KEY_PATH="/home/mrdbo/key-6-10-24.pem"
EC2_PROJECT_DIR="/home/ubuntu/darija_project_new"

# Timestamp for versioning
TIMESTAMP=$(date +%d_%m_%y_%H_%M)

# Logging
LOG_DIR="${LOCAL_BASE}/logs/deployment"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/deploy_${TIMESTAMP}.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Deploy monitoring components
deploy_monitoring() {
    log "Deploying monitoring components..."
    
    # Copy test script
    scp -i "$KEY_PATH" \
        "${LOCAL_BASE}/validation/scripts/monitoring_integration_test.py" \
        "${EC2_USER}@${EC2_HOST}:${EC2_PROJECT_DIR}/validation/scripts/"
        
    # Copy monitoring config
    scp -i "$KEY_PATH" \
        "${LOCAL_BASE}/web/components/monitoring/metrics/monitoring_config.json" \
        "${EC2_USER}@${EC2_HOST}:${EC2_PROJECT_DIR}/web/components/monitoring/metrics/"
        
    # Make deployment script executable
    chmod +x "${LOCAL_BASE}/deployment/scripts/deploy_monitoring.sh"
    
    log "Monitoring components deployed successfully"
}

# Deploy configuration files
deploy_configs() {
    log "Deploying configuration files..."
    
    # Create remote directories
    ssh -i "$KEY_PATH" "${EC2_USER}@${EC2_HOST}" "mkdir -p ${EC2_PROJECT_DIR}/configs"
    
    # Copy config files
    scp -i "$KEY_PATH" \
        "${LOCAL_BASE}/configs/"* \
        "${EC2_USER}@${EC2_HOST}:${EC2_PROJECT_DIR}/configs/"
        
    log "Configuration files deployed successfully"
}

# Run integration tests
run_tests() {
    log "Running integration tests..."
    
    ssh -i "$KEY_PATH" "${EC2_USER}@${EC2_HOST}" \
        "cd ${EC2_PROJECT_DIR} && \
         source venv_new_2/bin/activate && \
         python validation/scripts/monitoring_integration_test.py"
         
    local test_status=$?
    if [ $test_status -eq 0 ]; then
        log "Integration tests passed successfully"
    else
        log "Integration tests failed with status $test_status"
        return 1
    fi
}

# Usage function
usage() {
    echo "Usage: $0 [monitoring|configs|tests|all]"
    echo "  monitoring  - Deploy monitoring components"
    echo "  configs     - Deploy configuration files"
    echo "  tests       - Run integration tests"
    echo "  all         - Deploy everything and run tests"
}

# Main execution
main() {
    case "$1" in
        "monitoring")
            deploy_monitoring
            ;;
        "configs")
            deploy_configs
            ;;
        "tests")
            run_tests
            ;;
        "all")
            deploy_monitoring && \
            deploy_configs && \
            run_tests
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# Execute main with arguments
main "$@"