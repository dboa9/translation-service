#!/bin/bash
# Local Deployment Test Script
# LOCATION: deployment/scripts/local_deployment_test.sh

# Configuration
PROJECT_NAME="darija_project"
VERSION="1.0.8"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Local paths
LOCAL_BASE="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project"
BACKUP_DIR="${LOCAL_BASE}/backups"
LOG_FILE="${LOCAL_BASE}/logs/deployment_test_${TIMESTAMP}.log"

# Required directories
REQUIRED_DIRS=(
    "data/raw"
    "data/processed"
    "models/configs"
    "logs"
    "validation/results"
    "monitoring/metrics"
    "dataset_cache"
)

# Logging function
log() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Validate environment
validate_environment() {
    log "INFO" "Starting environment validation"
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ ! -d "${LOCAL_BASE}/${dir}" ]]; then
            log "WARN" "Creating missing directory: ${dir}"
            mkdir -p "${LOCAL_BASE}/${dir}"
        fi
    done
    log "INFO" "Environment validation completed"
}

# Create backups
create_backups() {
    log "INFO" "Creating backups"
    
    local backup_path="${BACKUP_DIR}/${TIMESTAMP}"
    mkdir -p "$backup_path"
    cp -R "${LOCAL_BASE}"/* "$backup_path/" 2>/dev/null || true
    rm -rf "${backup_path}/dataset_cache" "${backup_path}/backups"
    
    if [[ -d "$backup_path" ]]; then
        log "INFO" "Backup created successfully at $backup_path"
    else
        log "ERROR" "Failed to create backup"
    fi
}

# Check dataset cache
check_dataset_cache() {
    log "INFO" "Checking dataset cache"
    
    python3 -c "
from pathlib import Path
import os

cache_dir = Path('${LOCAL_BASE}/dataset_cache')
required_datasets = [
    ('imomayiz___darija-english', 'submissions'),
    ('atlasia___darija_english', 'web_data'),
    ('atlasia___darija_english', 'comments'),
    ('atlasia___darija_english', 'stories'),
    ('atlasia___darija_english', 'doda'),
    ('atlasia___darija_english', 'transliteration'),
    ('imomayiz___darija-english', 'sentences'),
    ('M-A-D___darija_bridge', None),
    ('BounharAbdelaziz___english-to-moroccan-darija', None)
]

missing_datasets = []
for dataset, config in required_datasets:
    dataset_path = cache_dir / dataset
    if config:
        dataset_path = dataset_path / config
    if not dataset_path.exists():
        print(f'Missing dataset: {dataset} (config: {config})')
        missing_datasets.append((dataset, config))

if missing_datasets:
    print('Some datasets are missing from cache')
    exit(1)
else:
    print('All required datasets found in cache')
"
    
    if [[ $? -eq 0 ]]; then
        log "INFO" "Dataset cache check completed successfully"
    else
        log "ERROR" "Dataset cache check failed"
        exit 1
    fi
}

# Setup datasets
setup_datasets() {
    log "INFO" "Setting up and validating datasets"
    
    python3 -c "
from pathlib import Path
from core.custom_dataset_loader_extended import load_datasets
import os

cache_dir = Path('${LOCAL_BASE}/dataset_cache')
datasets = load_datasets(str(cache_dir))

if not datasets:
    print('Dataset loading failed')
    exit(1)

print(f'Successfully loaded datasets')
"
    
    if [[ $? -eq 0 ]]; then
        log "INFO" "Dataset setup and validation completed successfully"
    else
        log "ERROR" "Dataset setup and validation failed"
        exit 1
    fi
}

# Run tests
run_tests() {
    log "INFO" "Running validation tests"
    
    python3 tests/test_dataset_loader_extended.py
    
    if [[ $? -eq 0 ]]; then
        log "INFO" "Extended dataset loader tests completed successfully"
    else
        log "ERROR" "Extended dataset loader tests failed"
        exit 1
    fi

    python3 -m unittest tests/unified_tests/test_column_mapping_analyzer_extended.py
    
    if [[ $? -eq 0 ]]; then
        log "INFO" "Extended column mapping tests completed successfully"
    else
        log "ERROR" "Extended column mapping tests failed"
        exit 1
    fi
}

# Main execution
main() {
    log "INFO" "Starting local deployment test v${VERSION}"
    
    validate_environment
    create_backups
    check_dataset_cache
    setup_datasets
    run_tests
    
    log "INFO" "Local deployment test completed successfully"
}

main
