#!/bin/bash

# Define variables
EC2_USER="ubuntu"
EC2_HOST="ec2-34-233-67-166.compute-1.amazonaws.com"
EC2_KEY_PATH="~/key-6-10-24.pem"
REMOTE_DIR="darija_project_new"

# Transfer files to EC2 instance
scp -i "$EC2_KEY_PATH" core/dataset/data_reader.py "$EC2_USER@$EC2_HOST:$REMOTE_DIR"
scp -i "$EC2_KEY_PATH" core/dataset/data_preprocessor.py "$EC2_USER@$EC2_HOST:$REMOTE_DIR"
scp -i "$EC2_KEY_PATH" core/dataset/utils.py "$EC2_USER@$EC2_HOST:$REMOTE_DIR"
scp -i "$EC2_KEY_PATH" core/dataset/config.py "$EC2_USER@$EC2_HOST:$REMOTE_DIR"
scp -i "$EC2_KEY_PATH" requirements.txt "$EC2_USER@$EC2_HOST:$REMOTE_DIR"

# SSH into EC2 instance and run compatibility checks
ssh -i "$EC2_KEY_PATH" "$EC2_USER@$EC2_HOST" << EOF
  cd $REMOTE_DIR
  source venv_new_2/bin/activate
  # List files and their timestamps
  echo "Listing files and their timestamps on EC2:"
  ls -l
  # Run your compatibility checks or tests here
  echo "Running compatibility checks..."
  # Example: python3 test_compatibility.py
EOF
