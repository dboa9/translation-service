#!/bin/bash

# Create required directories
mkdir -p cache logs

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dataset_test_deploy_ec2

# Install dependencies
pip install -r requirements.txt

# Set Hugging Face API token from credentials
if [ -f "config/credentials.py" ]; then
    export HUGGINGFACE_API_TOKEN=$(python -c "import sys; sys.path.append('.'); from config.credentials import HUGGINGFACE_TOKEN; print(HUGGINGFACE_TOKEN)")
else
    echo "Error: config/credentials.py not found"
    exit 1
fi

# Print debug information
echo "Environment: dataset_test_deploy_ec2"
echo "HUGGINGFACE_API_TOKEN is set: $(if [ ! -z "$HUGGINGFACE_API_TOKEN" ]; then echo "Yes"; else echo "No"; fi)"
echo "Starting Streamlit app..."

# Run Streamlit app
streamlit run streamlit_app.py
