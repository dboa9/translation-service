# File: dataset_preprocessor.py
from typing import Dict, Any, Callable, Union, List, Optional
from .dataset_types import DatasetType, get_dataset_columns
import yaml
from pathlib import Path
import logging
from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

logger = logging.getLogger(__name__)

class DatasetPreprocessor:
    def __init__(self, config_path: str = 'config/column_mapping.yaml'):
        self.config = self._load_config(config_path)

    @staticmethod
    def _load_config(config_path: str) -> Dict[str, Any]:
        try:
            with open(Path(config_path), 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            raise

    def preprocess_dataset(self, dataset: Union[DatasetType, List[Dict[str, Any]]], dataset_name: str, subset: str) -> Union[DatasetType, List[Dict[str, Any]]]:
        if dataset_name not in self.config['datasets']:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        if subset not in self.config['datasets'][dataset_name]['required_columns']:
            raise ValueError(f"Unknown subset {subset} for dataset {dataset_name}")

        required_columns = self.config['datasets'][dataset_name]['required_columns'][subset]
        
        def preprocess_func(example: Dict[str, Any]) -> Dict[str, Any]:
            processed = {}
            for col in required_columns:
                if col in example:
                    processed[col] = example[col]
                else:
                    raise ValueError(f"Required column {col} not found in example for {dataset_name}/{subset}")
            
            # Add source information
            processed['source'] = f"{dataset_name}/{subset}"
            
            return processed

        if isinstance(dataset, (Dataset, DatasetDict)):
            return dataset.map(preprocess_func)
        elif isinstance(dataset, (IterableDataset, IterableDatasetDict)):
            return dataset.map(preprocess_func)
        elif isinstance(dataset, dict):
            return {k: preprocess_func(v) for k, v in dataset.items()}
        elif isinstance(dataset, list):
            return [preprocess_func(item) for item in dataset]
        else:
            raise ValueError(f"Unsupported dataset type: {type(dataset)}")

    def validate_columns(self, dataset: Union[DatasetType, List[Dict[str, Any]]], dataset_name: str, subset: str) -> None:
        if dataset is None:
            raise ValueError("Dataset is None")
        
        required_columns = set(self.config['datasets'][dataset_name]['required_columns'][subset])
        
        if isinstance(dataset, (Dataset, DatasetDict, IterableDataset, IterableDatasetDict)):
            actual_columns = set(get_dataset_columns(dataset))
        elif isinstance(dataset, dict):
            actual_columns = set(dataset.keys())
        elif isinstance(dataset, list) and len(dataset) > 0:
            actual_columns = set(dataset[0].keys())
        else:
            raise ValueError(f"Unsupported dataset type: {type(dataset)}")
        
        missing_columns = required_columns - actual_columns
        if missing_columns:
            raise ValueError(f"Missing required columns for {dataset_name}/{subset}: {missing_columns}")

        extra_columns = actual_columns - required_columns
        if extra_columns:
            logger.warning(f"Extra columns found in {dataset_name}/{subset}: {extra_columns}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        from datasets import load_dataset

        preprocessor = DatasetPreprocessor()

        # Load and preprocess web_data dataset
        web_data = load_dataset("atlasia/darija_english", "web_data")
        if isinstance(web_data, (Dataset, DatasetDict)):
            preprocessor.validate_columns(web_data["train"], "atlasia/darija_english", "web_data")
            preprocessed_web_data = preprocessor.preprocess_dataset(
                web_data["train"], "atlasia/darija_english", "web_data"
            )
            if isinstance(preprocessed_web_data, Dataset):
                print(preprocessed_web_data[0])
            elif isinstance(preprocessed_web_data, DatasetDict):
                print(next(iter(preprocessed_web_data.values()))[0])

        # Load and preprocess comments dataset
        comments = load_dataset("atlasia/darija_english", "comments")
        if isinstance(comments, (Dataset, DatasetDict)):
            preprocessor.validate_columns(comments["train"], "atlasia/darija_english", "comments")
            preprocessed_comments = preprocessor.preprocess_dataset(
                comments["train"], "atlasia/darija_english", "comments"
            )
            if isinstance(preprocessed_comments, Dataset):
                print(preprocessed_comments[0])
            elif isinstance(preprocessed_comments, DatasetDict):
                print(next(iter(preprocessed_comments.values()))[0])

        # Add similar examples for other dataset types
    except ImportError:
        logger.error("Error: Unable to import 'datasets' library. "
                     "Please install it using 'pip install datasets'.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
