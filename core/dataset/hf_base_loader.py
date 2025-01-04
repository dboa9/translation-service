import yaml
from pathlib import Path
from datasets import load_dataset, Dataset, DatasetDict, IterableDataset, IterableDatasetDict
from typing import Optional, Union, List, Dict, Any
import logging
import pandas as pd
import json
import requests

logger = logging.getLogger(__name__)

# Define DatasetType
DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

def get_dataset_columns(dataset: DatasetType) -> List[str]:
    if isinstance(dataset, (Dataset, IterableDataset)):
        return dataset.column_names or []
    elif isinstance(dataset, (DatasetDict, IterableDatasetDict)):
        first_split = next(iter(dataset.values()), None)
        return first_split.column_names if first_split else []
    else:
        raise ValueError(f"Unsupported dataset type: {type(dataset)}")

class HFBaseLoader:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        config_files = [
            Path(self.base_dir) / "config" / "column_mapping_extended.yaml",
            Path(self.base_dir) / "config" / "column_mapping.yaml",
            Path(self.base_dir) / "config" / "dataset_loader_debug.yaml"
        ]
        
        for config_path in config_files:
            try:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Error loading configuration from {config_path}: {e}")
        
        raise FileNotFoundError(f"No valid config file found in {self.base_dir}/config/")

    def load_dataset(self, dataset_name: str, subset: str) -> DatasetType:
        try:
            if dataset_name == "imomayiz/darija-english" and subset == "submissions":
                dataset = self._load_imomayiz_submissions()
            else:
                dataset = load_dataset(dataset_name, subset)
            return dataset
        except Exception as e:
            logger.error(f"Error loading dataset {dataset_name}/{subset}: {e}")
            raise

    def _load_imomayiz_submissions(self) -> Dataset:
        try:
            file_path = Path.home() / ".cache/huggingface/datasets/imomayiz/darija-english/submissions/submissions.json"
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}. Attempting to download...")
                self._download_imomayiz_submissions(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            dataset = Dataset.from_pandas(df)
            
            return dataset
        except Exception as e:
            logger.error(f"Error loading imomayiz/darija-english submissions: {e}")
            raise

    def _download_imomayiz_submissions(self, file_path: Path):
        url = "https://huggingface.co/datasets/imomayiz/darija-english/resolve/main/submissions.json"
        response = requests.get(url)
        response.raise_for_status()
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(response.content)

    def get_column_mapping(self, dataset_name: str, subset: str) -> Dict[str, str]:
        return {col: col for col in self.config[dataset_name]["required_columns"][subset]}

# Usage example:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        base_dir = "/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project"
        loader = HFBaseLoader(base_dir)
        dataset = loader.load_dataset("atlasia/darija_english", "web_data")
        print(f"Successfully loaded dataset: atlasia/darija_english/web_data")
        print(f"Columns: {get_dataset_columns(dataset)}")
        column_mapping = loader.get_column_mapping("atlasia/darija_english", "web_data")
        print(f"Column mapping: {column_mapping}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
