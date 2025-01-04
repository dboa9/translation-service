#!/bin/bash

# EC2 connection details
EC2_USER="ubuntu"
EC2_HOST="ec2-34-233-67-166.compute-1.amazonaws.com"
KEY_PATH="~/key-6-10-24.pem"

# Connect to EC2 and clean up system files only (not project files)
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
    echo 'Cleaning up EC2 instance system files and caches...'
    
    echo 'Step 1: Cleaning package manager cache...'
    sudo apt-get clean
    sudo apt-get autoremove -y
    
    echo 'Step 2: Clearing pip cache...'
    rm -rf ~/.cache/pip
    
    echo 'Step 3: Truncating (not deleting) system log files...'
    sudo find /var/log -type f -name '*.log' -exec truncate -s 0 {} \;
    
    echo 'Step 4: Cleaning old systemd journals...'
    sudo journalctl --vacuum-time=1d
    
    echo 'Step 5: Clearing temporary files...'
    sudo rm -rf /tmp/*
    
    echo 'Cleanup complete. Current disk usage:'
    df -h /
"
