#!/bin/bash
# File: copy_translation_files.sh
# Author: dboa9 (danielalchemy9@gmail.com)
# Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/scripts/copy_translation_files.sh

SOURCE_DIR="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project"
TARGET_DIR="/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service"

# Create required directories
mkdir -p "${TARGET_DIR}"/{core/{translation,utils,interfaces},config,frontend/src/components/translation}

# Copy core translation files
echo "Copying core translation files..."
cp -r "${SOURCE_DIR}"/core/translation/translation_service.py "${TARGET_DIR}"/core/translation/
cp -r "${SOURCE_DIR}"/core/translation/model_config.py "${TARGET_DIR}"/core/translation/
cp -r "${SOURCE_DIR}"/core/translation/model_loader.py "${TARGET_DIR}"/core/translation/

# Copy utility files
echo "Copying utility files..."
cp -r "${SOURCE_DIR}"/core/utils/base_utilities_module.py "${TARGET_DIR}"/core/utils/
cp -r "${SOURCE_DIR}"/core/utils/cache_manager.py "${TARGET_DIR}"/core/utils/

# Copy configuration files
echo "Copying configuration files..."
cp -r "${SOURCE_DIR}"/config/column_mapping.yaml "${TARGET_DIR}"/config/
cp -r "${SOURCE_DIR}"/config/column_mapping_extended.yaml "${TARGET_DIR}"/config/
cp -r "${SOURCE_DIR}"/config/project_paths.py "${TARGET_DIR}"/config/

# Copy interface files
echo "Copying interface files..."
cp -r "${SOURCE_DIR}"/core/interfaces/streamlit_interface.py "${TARGET_DIR}"/core/interfaces/
cp -r "${SOURCE_DIR}"/core/interfaces/web_interface.py "${TARGET_DIR}"/core/interfaces/

# Copy frontend components
echo "Copying frontend components..."
cp -r "${SOURCE_DIR}"/frontend/src/components/translation/unified-translation-interface.tsx "${TARGET_DIR}"/frontend/src/components/translation/
cp -r "${SOURCE_DIR}"/frontend/src/components/ui/* "${TARGET_DIR}"/frontend/src/components/ui/

# Copy API routes
echo "Copying API routes..."
mkdir -p "${TARGET_DIR}"/frontend/src/app/api/v2/translate
cp -r "${SOURCE_DIR}"/frontend/src/app/api/v2/translate/route.ts "${TARGET_DIR}"/frontend/src/app/api/v2/translate/

# Set permissions
echo "Setting permissions..."
chmod -R 755 "${TARGET_DIR}"

echo "Copy completed successfully!"
