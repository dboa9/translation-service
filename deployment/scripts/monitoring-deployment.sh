#!/bin/bash
# deploy_monitoring.sh
# Location: /home/ubuntu/darija_project_new/deployment/scripts/deploy_monitoring.sh

# Configuration
EC2_USER="ubuntu"
EC2_HOST="ec2-34-233-67-166.compute-1.amazonaws.com"
KEY_PATH="/home/mrdbo/key-6-10-24.pem"
EC2_PROJECT_DIR="/home/ubuntu/darija_project_new"
LOCAL_BASE="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project"
MONITORING_DIR="web/components/monitoring"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Setup logging
LOG_DIR="${EC2_PROJECT_DIR}/logs/monitoring"
LOG_FILE="${LOG_DIR}/deploy_${TIMESTAMP}.log"

# Monitoring files to transfer
declare -a MONITORING_FILES=(
    "consolidated-translation-metrics.tsx"
    "monitoring-types.ts"
    "monitoring_integration_test.py"
)

# Logging function
log() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    local error_msg=$1
    log "ERROR" "$error_msg"
    exit 1
}

# Create EC2 directories
setup_directories() {
    log "INFO" "Creating monitoring directories..."
    
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        mkdir -p ${EC2_PROJECT_DIR}/${MONITORING_DIR}/{metrics,types}
        mkdir -p ${LOG_DIR}
    " || handle_error "Failed to create directories"
}

# Transfer monitoring files
transfer_files() {
    log "INFO" "Transferring monitoring files..."
    
    for file in "${MONITORING_FILES[@]}"; do
        log "INFO" "Transferring $file..."
        scp -i "$KEY_PATH" \
            "${LOCAL_BASE}/${MONITORING_DIR}/$file" \
            "${EC2_USER@$EC2_HOST}:${EC2_PROJECT_DIR}/${MONITORING_DIR}/" || \
            handle_error "Failed to transfer $file"
    done
}

# Run integration test
run_tests() {
    log "INFO" "Running integration tests..."
    
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        cd ${EC2_PROJECT_DIR} && \
        source venv_new_2/bin/activate && \
        python validation/scripts/monitoring_integration_test.py
    " || handle_error "Integration tests failed"
}

# Main execution
main() {
    log "INFO" "Starting monitoring deployment"
    
    setup_directories
    transfer_files
    run_tests
    
    log "INFO" "Monitoring components deployed and tested successfully"
}

# Execute main with error handling
main "$@" || handle_error "Deployment failed"