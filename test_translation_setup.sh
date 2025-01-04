#!/bin/bash
# File: test_translation_setup.sh
# Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service/test_translation_setup.sh
# Author: dboa9 (danielalchemy9@gmail.com)

# Activate conda environment
conda activate dataset_test_deploy_ec2

# Test Python imports
python3 << EOF
try:
    import torch
    import transformers
    import streamlit
    print("Python dependencies verified successfully")
except ImportError as e:
    print(f"Missing dependency: {e}")
    exit(1)
EOF

# Test configuration files
if [ -f "config/column_mapping.yaml" ] && [ -f "config/project_paths.py" ]; then
    echo "Configuration files present"
else
    echo "Missing configuration files"
    exit 1
fi

# Test core modules
if [ -f "core/translation/translation_service.py" ] && [ -f "core/utils/base_utilities_module.py" ]; then
    echo "Core modules present"
else
    echo "Missing core modules"
    exit 1
fi

# Test frontend setup
if [ -d "frontend/src/components/ui" ] && [ -f "frontend/src/app/api/v2/translate/route.ts" ]; then
    echo "Frontend setup verified"
else
    echo "Frontend setup incomplete"
    exit 1
fi

echo "Setup verification completed successfully"