#!/bin/bash

# EC2 connection details
EC2_USER="ubuntu"
EC2_HOST="ec2-34-233-67-166.compute-1.amazonaws.com"
KEY_PATH="~/key-6-10-24.pem"
EC2_BASE="/home/ubuntu/darija_project_new"

# Create and setup virtual environment
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
    # Create project directory if it doesn't exist
    mkdir -p $EC2_BASE

    cd $EC2_BASE

    # Create virtual environment if it doesn't exist
    python3 -m venv venv_new_2

    # Activate virtual environment and install requirements
    source venv_new_2/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install required packages
    pip install torch torchvision
    pip install transformers datasets tokenizers sacrebleu
    pip install numpy pandas sentencepiece nltk
    pip install psutil tqdm accelerate safetensors py-cpuinfo memory_profiler
    pip install matplotlib seaborn streamlit plotly
    pip install huggingface_hub evaluate
    pip install ipywidgets Pillow python-dotenv loguru
    pip install fastapi uvicorn requests
    pip install pytest pytest-asyncio
"
