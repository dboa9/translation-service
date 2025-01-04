#!/bin/bash
# Enhanced Integrated Deployment Script for Darija Translation Project
# Location: deployment/scripts/enhanced-integrated-deployment_2_11_24_8_41.sh

# Configuration
PROJECT_NAME="darija_project"
VERSION="2.0.0"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Environment paths
LOCAL_BASE="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project"
EC2_USER="ubuntu"
EC2_HOST="ec2-34-233-67-166.compute-1.amazonaws.com"
EC2_BASE="/home/ubuntu/darija_project_new"
KEY_PATH="~/key-6-10-24.pem"

# Backup and version paths
BACKUP_ROOT="${EC2_BASE}/backups"
VERSION_BACKUP="${EC2_BASE}/versions/backup"
SYNC_BACKUP="${BACKUP_ROOT}/sync/${TIMESTAMP}"

# Configuration paths
MONITOR_CONFIG="${EC2_BASE}/monitoring/monitoring_config.json"
VERSION_FILE="${EC2_BASE}/VERSION"

# Dataset configuration
DATASET_NAMES=(
    "BounharAbdelaziz/english-to-moroccan-darija"
    "atlasia/darija_english"
    "imomayiz/darija-english"
)

# Required directories that must exist and be populated
REQUIRED_DIRS=(
    "data/raw"
    "data/processed"
    "models/configs"
    "logs"
    "validation/results"
    "monitoring/metrics"
    "dataset_cache"
)

# Directory descriptions for logging
declare -A DIR_DESCRIPTIONS=(
    ["data/raw"]="Raw dataset files"
    ["data/processed"]="Processed dataset files"
    ["models/configs"]="Model configuration files"
    ["logs"]="Application and system logs"
    ["validation/results"]="Validation test outputs"
    ["monitoring/metrics"]="Monitoring metrics data"
    ["dataset_cache"]="Dataset cache storage"
)

# Logging function
log() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Enhanced error handling
handle_error() {
    local stage=$1
    local error_msg=$2
    log "ERROR" "Failed at stage '${stage}': ${error_msg}"
    
    if [[ "$stage" != "validate" ]]; then
        initiate_rollback "$stage"
    fi
    
    exit 1
}

# Enhanced rollback function
initiate_rollback() {
    local failed_stage=$1
    log "WARN" "Initiating rollback from stage: ${failed_stage}"
    
    case $failed_stage in
        "sync")
            if [[ -d "$SYNC_BACKUP" ]]; then
                log "INFO" "Rolling back synced files from ${SYNC_BACKUP}"
                rsync -avz --delete -e "ssh -i $KEY_PATH" \
                    "${SYNC_BACKUP}/" "${EC2_USER}@${EC2_HOST}:${EC2_BASE}/"
            fi
            ;;
        "setup")
            if [[ -d "${VERSION_BACKUP}/latest" ]]; then
                log "INFO" "Rolling back to last known good version"
                rsync -avz --delete -e "ssh -i $KEY_PATH" \
                    "${VERSION_BACKUP}/latest/" "${EC2_USER}@${EC2_HOST}:${EC2_BASE}/"
            fi
            ;;
    esac
}

# Stage 1: Enhanced Validation
validate_environment() {
    log "INFO" "Starting environment validation"
    
    # Check SSH access
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "echo 'SSH connection successful'" || \
        handle_error "validate" "SSH connection failed"
        
    # Check disk space
    local disk_space=$(ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "df -h / | awk 'NR==2 {print \$5}' | sed 's/%//'")
    if (( disk_space > 90 )); then
        handle_error "validate" "Low disk space: ${disk_space}%"
    fi
    
    # Validate required directories exist locally
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ ! -d "${LOCAL_BASE}/${dir}" ]]; then
            log "WARN" "Creating missing local directory: ${dir} (${DIR_DESCRIPTIONS[$dir]})"
            mkdir -p "${LOCAL_BASE}/${dir}"
        fi
    done
}

# Stage 2: Enhanced Backup
create_backups() {
    log "INFO" "Creating backups"
    
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        mkdir -p ${SYNC_BACKUP} ${VERSION_BACKUP}/latest
        
        if [ -d ${EC2_BASE} ]; then
            rsync -a ${EC2_BASE}/ ${SYNC_BACKUP}/ --exclude 'dataset_cache' --exclude 'backups' --exclude 'versions/backup'
            rsync -a ${EC2_BASE}/ ${VERSION_BACKUP}/latest/ --exclude 'dataset_cache' --exclude 'backups' --exclude 'versions/backup'
        fi
    "
}

# Stage 3: Enhanced Environment Setup
setup_environment() {
    log "INFO" "Setting up/updating project structure"
    
    # Create all required directories on EC2
    local dir_list
    dir_list=$(printf "%s\n" "${REQUIRED_DIRS[@]}" | paste -sd " ")
    
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        for dir in $dir_list; do
            mkdir -p ${EC2_BASE}/\$dir
            chmod -R 755 ${EC2_BASE}/\$dir
        done
        
        find ${EC2_BASE} -type f -name '*.sh' -exec chmod +x {} \;
    "
}

# Stage 4: Dataset Validation and Cache Setup
setup_datasets() {
    log "INFO" "Setting up and validating datasets"
    
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        cd ${EC2_BASE}
        source venv_new_2/bin/activate
        
        # Initialize cache manager
        python3 -c \"
from pathlib import Path
from core.dataset_management.cache_manager import CacheManager
cache_dir = Path('${EC2_BASE}/dataset_cache')
manager = CacheManager(cache_dir)
manager.verify_cache_integrity()
\"

        # Validate datasets
        for dataset in ${DATASET_NAMES[@]}; do
            python3 -c \"
from pathlib import Path
from core.dataset_management.dataset_validator import DatasetValidator
validator = DatasetValidator(Path('${EC2_BASE}/dataset_cache'))
success, issues, stats = validator.load_and_validate_dataset('\$dataset')
if not success:
    print(f'Dataset validation failed for \$dataset: {issues}')
    exit(1)
\"
        done
    " || handle_error "datasets" "Dataset validation failed"
}

# Stage 5: Enhanced File Sync
sync_files() {
    log "INFO" "Synchronizing files"
    
    # Sync entire project structure while preserving permissions
    rsync -avz --progress -e "ssh -i $KEY_PATH" \
        --exclude 'dataset_cache' \
        --exclude 'backups' \
        --exclude 'versions/backup' \
        --exclude '*.pyc' \
        --exclude '__pycache__' \
        --exclude '.git' \
        --exclude '.env' \
        --exclude 'venv' \
        --exclude 'venv_new_2' \
        "${LOCAL_BASE}/" "${EC2_USER}@${EC2_HOST}:${EC2_BASE}/" || \
        handle_error "sync" "Failed to sync project files"
    
    # Verify critical files exist after sync
    local dir_list
    dir_list=$(printf "%s\n" "${REQUIRED_DIRS[@]}" | paste -sd " ")
    
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        for dir in $dir_list; do
            if [ ! -d \"${EC2_BASE}/\$dir\" ]; then
                echo \"ERROR: Required directory \$dir missing after sync\"
                exit 1
            fi
        done
    " || handle_error "sync" "Failed to verify directory structure"
}

# Stage 6: Run Tests
run_tests() {
    log "INFO" "Running validation tests"
    
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        cd ${EC2_BASE}
        source venv_new_2/bin/activate
        
        # Run dataset cache validation
        python3 validation/scripts/dataset-cache-validator.py || exit 1
        
        # Run monitoring tests
        python3 validation/scripts/monitoring-test.py || exit 1
        
        # Verify directory structure and permissions
        for dir in data/raw data/processed models/configs logs validation/results monitoring/metrics; do
            if [ ! -d \"\$dir\" ]; then
                echo \"ERROR: Required directory \$dir missing\"
                exit 1
            fi
        done
        
        # Verify dataset cache integrity
        python3 -c \"
from pathlib import Path
from core.dataset_management.cache_manager import CacheManager
cache_dir = Path('${EC2_BASE}/dataset_cache')
manager = CacheManager(cache_dir)
if not manager.verify_cache_integrity():
    print('Dataset cache integrity check failed')
    exit(1)
\"
    " || handle_error "test" "Validation tests failed"
}

# Main execution
main() {
    log "INFO" "Starting enhanced deployment pipeline v${VERSION}"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                ;;
            --help)
                echo "Usage: $0 [--skip-tests]"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done
    
    # Execute stages
    validate_environment
    create_backups
    setup_environment
    setup_datasets
    sync_files
    
    if [[ "$SKIP_TESTS" != true ]]; then
        run_tests
    fi
    
    log "INFO" "Enhanced deployment pipeline completed successfully"
    
    # Print directory structure verification
    log "INFO" "Verifying final directory structure:"
    ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
        echo 'EC2 Directory Structure:'
        find ${EC2_BASE} -type d -maxdepth 2 -not -path '*/\.*' | sort
    "
}

main "$@"
