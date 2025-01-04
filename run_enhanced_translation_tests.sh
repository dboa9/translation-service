#!/bin/bash

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dataset_test_deploy_ec2

# Set PYTHONPATH to include project root
export PYTHONPATH=$PYTHONPATH:/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service

# Set Hugging Face API token from credentials
export HUGGINGFACE_API_TOKEN=$(python -c "from config.credentials import HUGGINGFACE_TOKEN; print(HUGGINGFACE_TOKEN)")

# Run tests
python -m pytest tests/test_enhanced_unified_translation.py -v
