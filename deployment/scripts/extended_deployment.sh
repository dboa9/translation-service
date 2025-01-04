#!/bin/bash
# Extended Deployment Script
# LOCATION: deployment/scripts/extended_deployment.sh

source deployment/scripts/local_deployment_test.sh

# Additional steps for extended deployment
run_extended_tests() {
    log "INFO" "Running extended tests"
    
    python3 -m unittest tests/unified_tests/test_column_mapping_analyzer_extended.py
    
    if [[ $? -eq 0 ]]; then
        log "INFO" "Extended tests completed successfully"
    else
        log "ERROR" "Extended tests failed"
        exit 1
    fi
}

# Override the main function
main() {
    log "INFO" "Starting extended deployment test"
    
    validate_environment
    create_backups
    check_dataset_cache
    setup_datasets
    run_tests
    run_extended_tests
    
    log "INFO" "Extended deployment test completed successfully"
}

# Run the extended main function
main
