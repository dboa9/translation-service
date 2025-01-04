# File: test_atlasia_imomayiz_darija_english_loading_.py
"""
Unified Test for Atlasia and Imomayiz Darija-English Dataset Loading
Author: dboa9
Date: 10_11_24_01_30
"""
import logging
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Now import DataReader
from core.dataset.import_manager import DataReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dataset_loading(dataset_name: str, configs: list):
    reader = DataReader()
    
    for i, config in enumerate(configs, 1):
        logger.info(f"Testing {dataset_name} - subset: {config} ({i}/{len(configs)})")
        start_time = time.time()
        try:
            # Pass the config as data_files for CSV datasets
            if dataset_name in ["atlasia/darija_english", "imomayiz/darija-english"]:
                dataset = reader.read_dataset(dataset_name, data_files=config)
            else:
                dataset = reader.read_dataset(dataset_name, config=config)
            
            stats = reader.get_dataset_statistics(dataset)
            
            logger.info(f"\n  {config}:")
            logger.info("    Status: Success")
            logger.info(f"    Splits: {', '.join(stats['splits']) if 'splits' in stats else 'N/A'}")
            logger.info(f"    Columns: {', '.join(stats['column_names']) if 'column_names' in stats else 'N/A'}")
            logger.info(f"    num_examples: {stats['num_rows'] if 'num_rows' in stats else 'Unknown'}")
            
        except Exception as e:
            logger.error(f"Error loading {dataset_name} with config {config}: {str(e)}")
            logger.info(f"\n  {config}:")
            logger.info("    Status: Failed")
            logger.info(f"    Error: {str(e)}")
        finally:
            end_time = time.time()
            logger.info(f"Time taken for {dataset_name} - {config}: {end_time - start_time:.2f} seconds")

def main():
    logger.info("Starting dataset loading tests")

    datasets_to_test = [
        ("atlasia/darija_english", ["web_data", "comments", "stories", "doda", "transliteration"]),
        ("imomayiz/darija-english", ["sentences"]),
        ("M-A-D/DarijaBridge", ["default"]),
        ("BounharAbdelaziz/English-to-Moroccan-Darija", ["default"])
    ]

    for dataset_name, configs in datasets_to_test:
        logger.info(f"Testing dataset: {dataset_name}")
        test_dataset_loading(dataset_name, configs)
        logger.info(f"Finished testing dataset: {dataset_name}")

    logger.info("All dataset loading tests completed")

if __name__ == "__main__":
    main()
