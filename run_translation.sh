#!/bin/bash

# Source conda initialization
source ~/miniconda3/etc/profile.d/conda.sh

# Activate the conda environment
conda activate dataset_test_deploy_ec2

# Set Python path to include project root
export PYTHONPATH="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service:$PYTHONPATH"

# Run the streamlit interface
streamlit run translation_interface.py
