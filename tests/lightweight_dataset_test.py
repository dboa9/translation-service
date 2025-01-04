#tests/lightweight_dataset_test.py

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import logging

from datasets import (
    Dataset,
    DatasetDict,
    IterableDataset,
    IterableDatasetDict,
    load_dataset,
)

from core.custom_dataset_loader import load_imomayiz_darija_english_submissions

# Set up logging to write to both console and file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("dataset_test.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

logger = logging.getLogger(__name__)

def test_dataset_loading(dataset_name, config=None):
    try:
        logger.info(f"Attempting to load dataset: {dataset_name} (config: {config})")
        if dataset_name == "imomayiz/darija-english" and config == "submissions":
            dataset = load_imomayiz_darija_english_submissions("/home/mrdbo/.cache/huggingface/hub")
        elif config:
            dataset = load_dataset(dataset_name, config)
        else:
            dataset = load_dataset(dataset_name)
        
        if dataset is None:
            logger.error(f"Failed to load dataset: {dataset_name}")
            return False
        
        logger.info(f"Successfully loaded {dataset_name}")
        logger.info(f"Dataset structure: {dataset}")
        
        # Print first example from each split
        if isinstance(dataset, (Dataset, DatasetDict)):
            if isinstance(dataset, DatasetDict):
                for split in dataset.keys():
                    logger.info(f"First example from {split} split:")
                    logger.info(dataset[split][0])
                    logger.info("---")
            else:
                logger.info("First example:")
                logger.info(dataset[0])
                logger.info("---")
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            if isinstance(dataset, IterableDatasetDict):
                for split in dataset.keys():
                    logger.info(f"First example from {split} split:")
                    logger.info(next(iter(dataset[split])))
                    logger.info("---")
            else:
                logger.info("First example:")
                logger.info(next(iter(dataset)))
                logger.info("---")
        else:
            logger.warning(f"Unexpected dataset type: {type(dataset)}")
        
        return True
    except Exception as e:
        logger.error(f"Error loading {dataset_name}: {str(e)}", exc_info=True)
        return False

def main():
    datasets_to_test = [
        ("atlasia/darija_english", "web_data"),
        ("atlasia/darija_english", "comments"),
        ("atlasia/darija_english", "stories"),
        ("atlasia/darija_english", "doda"),
        ("atlasia/darija_english", "transliteration"),
        ("imomayiz/darija-english", "sentences"),
        ("imomayiz/darija-english", "submissions"),
        ("M-A-D/DarijaBridge", None),
        ("BounharAbdelaziz/English-to-Moroccan-Darija", None)
    ]

    logger.info("Starting lightweight dataset test")
    for dataset_name, config in datasets_to_test:
        logger.info(f"Testing dataset: {dataset_name} (config: {config})")
        success = test_dataset_loading(dataset_name, config)
        if success:
            logger.info(f"Dataset {dataset_name} loaded successfully")
        else:
            logger.error(f"Failed to load dataset {dataset_name}")
        logger.info("=" * 50)
    logger.info("Lightweight dataset test completed")

if __name__ == "__main__":
    main()
