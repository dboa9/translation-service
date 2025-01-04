"""
Environment detection utilities for the translation service.
Handles detection of running environment (local vs EC2) and related settings.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

def is_running_on_ec2() -> bool:
    """
    Check if the application is running on an EC2 instance by attempting to
    access the EC2 metadata service.
    """
    try:
        response = requests.get(
            'http://169.254.169.254/latest/meta-data/instance-id',
            timeout=1  # Short timeout since metadata service should be fast
        )
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_environment() -> str:
    """
    Get the current environment (local or ec2).
    Can be overridden by setting DEPLOYMENT_ENV environment variable.
    """
    # Allow manual override through environment variable
    env = os.getenv('DEPLOYMENT_ENV')
    if env:
        return env.lower()
        
    # Auto-detect environment
    if is_running_on_ec2():
        return 'ec2'
    return 'local'

def should_use_local_models() -> bool:
    """
    Determine if we should use local model files based on environment.
    Returns True if running on EC2, False if running locally.
    """
    return get_environment() == 'ec2'
