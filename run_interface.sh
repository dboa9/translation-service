#!/bin/bash

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dataset_test_deploy_ec2

# Set environment variables
export TRANSFORMERS_CACHE="./model_cache"
export HF_HOME="./model_cache"
export CUDA_VISIBLE_DEVICES=""  # Disable CUDA for CPU-only inference
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python  # Avoid protobuf warnings

# Create cache directory if it doesn't exist
mkdir -p ./model_cache

# Kill any existing streamlit processes
pkill -f streamlit || true

# Wait a moment for ports to be freed
sleep 2

# Check if HuggingFace token is set
if [ ! -f "config/credentials.py" ]; then
    echo "Error: HuggingFace token not found in config/credentials.py"
    echo "Please create the file with your token:"
    echo 'HUGGINGFACE_TOKEN = "your_token_here"'
    exit 1
fi

# Download models first
echo "Checking and downloading models..."
python download_models.py

# Check if models were downloaded successfully
if [ $? -eq 0 ]; then
    echo "Models ready"
    echo "Starting translation interface..."
    streamlit run translation_interface.py --server.port 8505 --server.address localhost
else
    echo "Error preparing models"
    exit 1
fi
