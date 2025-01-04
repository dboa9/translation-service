#!/bin/bash

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dataset_test_deploy_ec2

# Set environment variables
export TRANSFORMERS_CACHE="./model_cache"
export HF_HOME="./model_cache"
export CUDA_VISIBLE_DEVICES=""  # Disable CUDA for CPU-only inference
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python  # Avoid protobuf warnings

# Create necessary directories
mkdir -p ./model_cache
mkdir -p ./logs

# Function to run tests with proper logging
run_tests() {
    local env=$1
    echo "Running translation tests for $env environment..."
    
    # Run tests and capture both stdout and stderr
    python -m pytest tests/test_all_models_translation.py \
        -v \
        --log-cli-level=INFO \
        --log-file=./logs/translation_test_${env}_$(date +%Y%m%d_%H%M%S).log \
        --capture=tee-sys \
        -k "test_all_models"
        
    return $?
}

# Check if models are available locally
echo "Checking model availability..."
if [ ! -d "./model_cache" ] || [ -z "$(ls -A ./model_cache)" ]; then
    echo "Models not found in cache. Running download script..."
    python download_models.py
    if [ $? -ne 0 ]; then
        echo "Error downloading models. Please check the logs."
        exit 1
    fi
fi

# Run local tests first
echo "Starting local environment tests..."
run_tests "local"
local_status=$?

if [ $local_status -eq 0 ]; then
    echo "✅ Local tests passed successfully"
    
    # Check if we're running on EC2
    if curl -s http://169.254.169.254/latest/meta-data/instance-id > /dev/null; then
        echo "Running on EC2, proceeding with EC2 environment tests..."
        run_tests "ec2"
        ec2_status=$?
        
        if [ $ec2_status -eq 0 ]; then
            echo "✅ EC2 tests passed successfully"
            echo "Comparing results between environments..."
            python -c "
from tests.test_all_models_translation import compare_results
import json
with open('translation_results_local.json') as f:
    local_results = json.load(f)
with open('translation_results_ec2.json') as f:
    ec2_results = json.load(f)
comparison = compare_results(local_results, ec2_results)
"
        else
            echo "❌ EC2 tests failed"
            exit $ec2_status
        fi
    else
        echo "Not running on EC2, skipping EC2 environment tests"
    fi
else
    echo "❌ Local tests failed"
    exit $local_status
fi

echo "All tests completed. Check logs directory for detailed results."
