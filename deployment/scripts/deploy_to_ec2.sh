#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# EC2 instance details (replace with your actual values)
EC2_USER="ec2-user"
EC2_HOST="your-ec2-instance-ip"
EC2_KEY="path/to/your/ec2-key.pem"

# Local project directory
LOCAL_PROJECT_DIR="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project"

# EC2 project directory
EC2_PROJECT_DIR="/home/ec2-user/daija_dataset_tests_project"

echo "Syncing project files to EC2..."
rsync -avz -e "ssh -i $EC2_KEY" --exclude '.git' --exclude 'venv' --exclude '__pycache__' \
    $LOCAL_PROJECT_DIR/ $EC2_USER@$EC2_HOST:$EC2_PROJECT_DIR/

echo "Setting up environment and running tests on EC2..."
ssh -i $EC2_KEY $EC2_USER@$EC2_HOST << EOF
    cd $EC2_PROJECT_DIR
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python tests/unified_tests/test_working_datasets.py
    TEST_EXIT_CODE=$?
    deactivate
    exit $TEST_EXIT_CODE
EOF

if [ $? -eq 0 ]; then
    echo "Deployment and testing completed successfully!"
else
    echo "Deployment completed, but tests failed. Check the output for details."
    exit 1
fi

# Note: Before running this script, make sure to replace the placeholder values
# for EC2_USER, EC2_HOST, and EC2_KEY with your actual EC2 instance details.
