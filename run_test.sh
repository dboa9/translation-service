#!/bin/bash

# Source the Conda initialization script
source ~/miniconda3/etc/profile.d/conda.sh

# Activate the Conda environment
conda activate dataset_test_deploy_ec2

# Run the debug test script
echo "Running debug test..."
python debug_test.py

# Run the main Python test script
echo "Running main test..."
python test_translation.py

# Deactivate the Conda environment
conda deactivate
