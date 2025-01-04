#!/bin/bash

# Set the PYTHONPATH
export PYTHONPATH="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service:$PYTHONPATH"

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

# Run the all models test script
echo "Running all models test..."
python tests/test_all_models.py

# Deactivate the Conda environment
conda deactivate
