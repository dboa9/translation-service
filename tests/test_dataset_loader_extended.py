import sys
import os
from pathlib import Path
import logging
from typing import Optional, Union, Tuple, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from transformers import PreTrainedTokenizerBase
from core.custom_dataset_loader_extended import load_datasets

# Define DatasetType
DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_loader_extended_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def validate_dataset(dataset: Optional[DatasetType], name: str, tokenizer: Optional[PreTrainedTokenizerBase] = None) -> bool:
    """Validate a loaded dataset"""
    if dataset is None:
        logger.error(f"Dataset {name} failed to load")
        return False
        
    try:
        if isinstance(dataset, (DatasetDict, IterableDatasetDict)):
            # Check each split
            for split_name, split_dataset in dataset.items():
                if not validate_split(split_dataset, name, split_name, tokenizer):
                    return False
        else:
            if not validate_split(dataset, name, "main", tokenizer):
                return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating dataset {name}: {str(e)}")
        return False

def validate_split(split_dataset: Union[Dataset, IterableDataset], name: str, split_name: str, tokenizer: Optional[PreTrainedTokenizerBase]) -> bool:
    if isinstance(split_dataset, Dataset):
        if len(split_dataset) == 0:
            logger.error(f"Dataset {name} split {split_name} is empty")
            return False
        logger.info(f"Dataset {name} split {split_name} has {len(split_dataset)} examples")
    elif isinstance(split_dataset, IterableDataset):
        try:
            next(iter(split_dataset))
            logger.info(f"Dataset {name} split {split_name} is not empty")
        except StopIteration:
            logger.error(f"Dataset {name} split {split_name} is empty")
            return False
    else:
        logger.error(f"Dataset {name} split {split_name} has unexpected type: {type(split_dataset)}")
        return False
    
    # Log first example and check input format
    try:
        first_example = next(iter(split_dataset))
        logger.info(f"First example from {name} split {split_name}:")
        logger.info(first_example)
        
        if tokenizer and name == 'doda':
            try:
                # Attempt to encode the input
                encoded = tokenizer(first_example['text'], return_tensors='pt')
                logger.info(f"Successfully encoded input for {name} dataset")
            except Exception as e:
                logger.error(f"Error encoding input for {name} dataset: {str(e)}")
                return False
    except Exception as e:
        logger.error(f"Error processing first example from {name} split {split_name}: {str(e)}")
        return False
    
    return True

def test_extended_loader():
    """Test the extended dataset loader"""
    logger.info("Starting extended dataset loader test")
    
    # Use the cache directory from the environment or default to the standard location
    cache_dir = os.getenv('DATASET_CACHE_DIR', '/home/mrdbo/.cache/huggingface/hub')
    
    try:
        # Load all datasets
        datasets = load_datasets(cache_dir)
        
        if not datasets:
            logger.error("No datasets were loaded")
            return False
            
        logger.info(f"Successfully loaded {len(datasets)} datasets")
        
        # Load the tokenizer for the 'doda' dataset
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("BounharAbdelaziz/Transliteration-Moroccan-Darija")
        
        # Validate each dataset
        all_valid = True
        for name, dataset in datasets.items():
            logger.info(f"Validating dataset: {name}")
            if not validate_dataset(dataset, name, tokenizer if name == 'doda' else None):
                all_valid = False
                
        if all_valid:
            logger.info("All datasets loaded and validated successfully")
            return True
        else:
            logger.error("Some datasets failed validation")
            return False
            
    except Exception as e:
        logger.error(f"Error in extended loader test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_extended_loader()
    sys.exit(0 if success else 1)
