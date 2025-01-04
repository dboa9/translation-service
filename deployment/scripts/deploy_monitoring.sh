#!/bin/bash
# deploy_monitoring.sh
# Location: /home/ubuntu/darija_project_new/deployment/scripts/deploy_monitoring.sh

# EC2 instance details
EC2_USER="ubuntu"
EC2_HOST="ec2-34-233-67-166.compute-1.amazonaws.com"
KEY_PATH="/home/mrdbo/key-6-10-24.pem"
EC2_PROJECT_DIR="/home/ubuntu/darija_project_new"

# Source and destination directories
LOCAL_BASE="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project"
MONITORING_DIR="web/components/monitoring"

# Monitoring files to transfer
declare -a MONITORING_FILES=(
    "consolidated-translation-metrics.tsx"
    "monitoring-types.ts"
    "monitoring_integration_test.py"
)

# Create EC2 directories
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "mkdir -p ${EC2_PROJECT_DIR}/${MONITORING_DIR}/{metrics,types}"

# Transfer monitoring files
for file in "${MONITORING_FILES[@]}"; do
    scp -i "$KEY_PATH" \
        "${LOCAL_BASE}/${MONITORING_DIR}/$file" \
        "${EC2_USER}@${EC2_HOST}:${EC2_PROJECT_DIR}/${MONITORING_DIR}/"
done

# Run integration test
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "cd ${EC2_PROJECT_DIR} && \
    source venv_new_2/bin/activate && \
    python validation/scripts/monitoring_integration_test.py"

echo "Monitoring components deployed and tested"
