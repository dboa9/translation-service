# LOCATION: core/custom_dataset_loader_extended.py

import logging
from pathlib import Path
from typing import Dict, Optional, Union

from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict, load_dataset

logger = logging.getLogger(__name__)

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

def load_atlasia_darija_english(cache_dir: str, config: str) -> Optional[DatasetType]:
    """Load atlasia/darija_english dataset with specific config"""
    try:
        dataset = load_dataset("atlasia/darija_english", config, cache_dir=cache_dir)
        logger.info(f"Successfully loaded atlasia/darija_english/{config}")
        return dataset
    except Exception as e:
        logger.error(f"Error loading atlasia/darija_english/{config}: {str(e)}")
        return None

def locate_arrow_file(cache_dir: str) -> Optional[Path]:
    """
    Dynamically locate the Arrow file in the dataset cache directory.
    """
    cache_path = Path(cache_dir)
    arrow_files = list(cache_path.glob("**/darija-english-submissions.arrow"))
    if arrow_files:
        return arrow_files[0]
    else:
        raise FileNotFoundError("Arrow file not found in the cache directory.")

def load_imomayiz_darija_english(cache_dir: str, config: str) -> Optional[DatasetType]:
    """Load imomayiz/darija-english dataset with specific config"""
    try:
        if config == "submissions":
            arrow_file_path = locate_arrow_file(cache_dir)
            dataset = load_dataset("imomayiz/darija-english", data_files=str(arrow_file_path), cache_dir=cache_dir)
            logger.info("Successfully loaded submissions dataset from Arrow file")
            return dataset
        else:
            dataset = load_dataset("imomayiz/darija-english", config, cache_dir=cache_dir)
            logger.info(f"Successfully loaded imomayiz/darija-english/{config}")
            return dataset
    except FileNotFoundError as e:
        logger.error(f"Arrow file not found for submissions dataset: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading imomayiz/darija-english/{config}: {str(e)}")
        return None

def load_mad_darija_bridge(cache_dir: str) -> Optional[DatasetType]:
    """Load M-A-D/DarijaBridge dataset"""
    try:
        dataset = load_dataset("M-A-D/DarijaBridge", cache_dir=cache_dir)
        logger.info("Successfully loaded M-A-D/DarijaBridge")
        return dataset
    except Exception as e:
        logger.error(f"Error loading M-A-D/DarijaBridge: {str(e)}")
        return None

def load_bounhar_english_darija(cache_dir: str) -> Optional[DatasetType]:
    """Load BounharAbdelaziz/English-to-Moroccan-Darija dataset"""
    try:
        dataset = load_dataset("BounharAbdelaziz/English-to-Moroccan-Darija", cache_dir=cache_dir)
        logger.info("Successfully loaded BounharAbdelaziz/English-to-Moroccan-Darija")
        return dataset
    except Exception as e:
        logger.error(f"Error loading BounharAbdelaziz/English-to-Moroccan-Darija: {str(e)}")
        return None

def load_datasets(cache_dir: str) -> Dict[str, DatasetType]:
    """
    Load all required datasets with their configurations
    Returns a dictionary mapping dataset names to their loaded instances
    """
    datasets = {}
    
    # Load atlasia/darija_english configurations
    configs = ["web_data", "comments", "stories", "doda", "transliteration"]
    for config in configs:
        dataset = load_atlasia_darija_english(cache_dir, config)
        if dataset is not None:
            datasets[f'atlasia/darija_english/{config}'] = dataset
    
    # Load imomayiz/darija-english configurations
    configs = ["sentences", "submissions"]
    for config in configs:
        dataset = load_imomayiz_darija_english(cache_dir, config)
        if dataset is not None:
            datasets[f'imomayiz/darija-english/{config}'] = dataset
    
    # Load M-A-D/DarijaBridge
    dataset = load_mad_darija_bridge(cache_dir)
    if dataset is not None:
        datasets['M-A-D/DarijaBridge'] = dataset
    
    # Load BounharAbdelaziz/English-to-Moroccan-Darija
    dataset = load_bounhar_english_darija(cache_dir)
    if dataset is not None:
        datasets['BounharAbdelaziz/English-to-Moroccan-Darija'] = dataset
    
    return datasets
