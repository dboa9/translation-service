#!/bin/bash

# Local to EC2 deployment script
# This script handles local testing, file transfer, and EC2 setup

# Exit on error
set -e

# Load conda environment
echo "Activating conda environment..."
source conda activate /mnt/c/conda_envs/myenv

# Stage 1: Local Testing
echo "Stage 1: Running local tests..."

# Create test directories if they don't exist
mkdir -p tests/test_results
mkdir -p logs

# Run dataset handler tests
echo "Running dataset handler tests..."
python -m unittest tests/test_dataset_handlers.py -v

# Run lightweight data loading test
echo "Running data loading tests..."
python tests/lightweight_data_load_test.py

# Run dataset validation
echo "Running dataset validation..."
python validation/scripts/dataset-cache-validator.py

# Stage 2: Prepare for EC2 Transfer
echo "Stage 2: Preparing files for EC2 transfer..."

# Create deployment package directory
DEPLOY_DIR="deployment_package"
mkdir -p $DEPLOY_DIR

# Copy required files and directories
cp -r core $DEPLOY_DIR/
cp -r config $DEPLOY_DIR/
cp -r models $DEPLOY_DIR/
cp -r data $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp darija_english_model_claud_deep_seek_gpt_ec2.py $DEPLOY_DIR/

# Create EC2 setup script
cat > $DEPLOY_DIR/setup_ec2.sh << 'EOF'
#!/bin/bash
set -e

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
sudo apt-get install -y python3-pip python3-dev

# Install Python requirements
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p datasets_cache
mkdir -p model_output
mkdir -p checkpoints
mkdir -p logs

# Set up environment variables
export PYTHONPATH="${PYTHONPATH}:${PWD}"
EOF

chmod +x $DEPLOY_DIR/setup_ec2.sh

# Stage 3: Transfer to EC2
echo "Stage 3: Transferring files to EC2..."

# Note: Replace these variables with your EC2 instance details
read -p "Enter your EC2 instance IP: " EC2_IP
read -p "Enter path to your EC2 key file: " KEY_FILE

# Validate EC2 connection
if ! ssh -i "$KEY_FILE" ubuntu@$EC2_IP "echo 'Connection successful'"; then
    echo "Failed to connect to EC2 instance"
    exit 1
fi

# Create remote directory and transfer files
ssh -i "$KEY_FILE" ubuntu@$EC2_IP "mkdir -p ~/darija_project"
scp -i "$KEY_FILE" -r $DEPLOY_DIR/* ubuntu@$EC2_IP:~/darija_project/

# Stage 4: EC2 Setup and Initial Test
echo "Stage 4: Setting up EC2 environment..."

ssh -i "$KEY_FILE" ubuntu@$EC2_IP << 'ENDSSH'
cd ~/darija_project
chmod +x setup_ec2.sh
./setup_ec2.sh

# Run a small test to verify setup
python3 -c "
from core.dataset.handlers.dataset_handler_factory import DatasetHandlerFactory
from pathlib import Path
factory = DatasetHandlerFactory(Path('./datasets_cache'), Path('./config'))
print('Setup verification successful')
"
ENDSSH

# Cleanup
echo "Cleaning up local deployment package..."
rm -rf $DEPLOY_DIR

echo "Deployment completed successfully!"
echo "To start model training on EC2, run:"
echo "ssh -i $KEY_FILE ubuntu@$EC2_IP"
echo "cd ~/darija_project"
echo "python3 darija_english_model_claud_deep_seek_gpt_ec2.py --mode train"
