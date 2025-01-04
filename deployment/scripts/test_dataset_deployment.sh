#!/bin/bash

# Configuration
LOCAL_KEY="$HOME/key-6-10-24.pem"
EC2_HOST="ubuntu@ec2-34-233-67-166.compute-1.amazonaws.com"
EC2_PROJECT_DIR="/home/ubuntu/darija_project_new"
LOCAL_PROJECT_DIR="$PWD"

# Create test script content
cat > dataset_test_script.py << 'EOL'
import sys
import logging
from pathlib import Path
import psutil
import gc
from datetime import datetime
import os

# Add project root to Python path
sys.path.append("/home/ubuntu/darija_project_new")

# Setup logging
LOG_DIR = Path("/home/ubuntu/darija_project_new/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"dataset_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_system_resources():
    """Check available system resources"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    logger.info(f"Memory Usage: {memory.percent}%")
    logger.info(f"Available Memory: {memory.available / (1024**3):.2f} GB")
    logger.info(f"Disk Usage: {disk.percent}%")
    logger.info(f"Available Disk: {disk.free / (1024**3):.2f} GB")
    
    cache_dir = Path("/home/ubuntu/.cache/huggingface/datasets")
    if cache_dir.exists():
        cache_size = sum(f.stat().st_size for f in cache_dir.glob('**/*') if f.is_file()) / (1024**3)
        logger.info(f"Dataset cache size: {cache_size:.2f} GB")
    
    return memory.available > 2 * (1024**3)  # Require at least 2GB free RAM

def test_dataset_loading():
    """Test dataset loading functionality"""
    try:
        from dataset_loader import load_datasets, clear_datasets_cache
        
        # Clear cache before testing
        logger.info("Clearing dataset cache...")
        clear_datasets_cache()
        
        # Test dataset loading
        logger.info("Loading datasets...")
        dataset = load_datasets()
        
        if dataset is None:
            logger.error("Dataset loading failed - returned None")
            return False
            
        # Log dataset statistics
        logger.info(f"Successfully loaded combined dataset with {len(dataset)} examples")
        logger.info(f"Dataset columns: {dataset.column_names}")
        
        # Sample a few examples
        logger.info("Sample entries from dataset:")
        for i, example in enumerate(dataset.select(range(min(3, len(dataset))))):
            logger.info(f"Example {i+1}:")
            logger.info(f"  English: {example['english']}")
            logger.info(f"  Darija: {example['darija']}")
            
        # Check memory usage after loading
        memory = psutil.Process().memory_info().rss / (1024**3)
        logger.info(f"Memory usage after loading: {memory:.2f} GB")
        
        # Cleanup
        del dataset
        gc.collect()
        
        return True
        
    except Exception as e:
        logger.error(f"Dataset testing failed: {str(e)}")
        logger.exception("Detailed traceback:")
        return False

def main():
    logger.info("Starting dataset validation...")
    
    # Check system resources
    if not check_system_resources():
        logger.error("Insufficient system resources")
        return 1
    
    # Run tests
    success = test_dataset_loading()
    
    if success:
        logger.info("Dataset validation completed successfully")
        return 0
    else:
        logger.error("Dataset validation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOL

# Transfer files to EC2
echo "Transferring test script to EC2..."
scp -i "$LOCAL_KEY" dataset_test_script.py "$EC2_HOST:$EC2_PROJECT_DIR/validation/scripts/"

# Execute test script on EC2
echo "Executing test script on EC2..."
ssh -i "$LOCAL_KEY" "$EC2_HOST" "cd $EC2_PROJECT_DIR && source venv_new_2/bin/activate && PYTHONPATH=$EC2_PROJECT_DIR python validation/scripts/dataset_test_script.py"

# Cleanup local test script
rm dataset_test_script.py

echo "Test deployment completed. Check logs in $EC2_PROJECT_DIR/logs/ for results."
