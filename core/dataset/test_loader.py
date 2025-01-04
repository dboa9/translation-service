# core/dataset/test_loader.py
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from datasets import Dataset, DatasetDict, load_dataset, load_from_disk

# Keep existing working dataset configurations
DATASET_CONFIGS = {
    "atlasia/darija_english": {
        "subsets": ["web_data", "comments", "stories", "doda", "transliteration"],
        "required_columns": {
            "web_data": ["darija", "english", "source"],
            "comments": ["id", "english", "darija", "source"],
            "stories": ["ChapterName", "darija", "english", "chunk_id"],
            "doda": ["id", "darija", "en"],
            "transliteration": ["darija_arabizi", "darija_arabic"]
        }
    },
    "imomayiz/darija-english": {
        "subsets": ["sentences"],
        "required_columns": {
            "sentences": ["darija", "eng", "darija_ar"]
        }
    },
    "M-A-D/DarijaBridge": {
            "subsets": ["default"],
            "required_columns": {
                "default": ["sentence", "translation", "translated", "corrected", "correction", "quality", "metadata"]
            }
        },
    "BounharAbdelaziz/English-to-Moroccan-Darija": {
            "subsets": ["default"],
            "required_columns": {
                "default": ["english", "darija", "includes_arabizi"]
            }
        }
    }

class EnhancedDatasetTestSuite:
    def __init__(self, base_dir: Path):
        self.logger = logging.getLogger(__name__)
        
        # Setup paths
        self.base_dir = base_dir
        self.test_data_dir = base_dir / "test_data_sample"
        self.cache_dir = base_dir / "datasets_cache"
        
        # Create directories if needed
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_dataset_columns(self, dataset: Union[Dataset, DatasetDict], subset: str) -> List[str]:
        """Existing column getter logic"""
        if isinstance(dataset, DatasetDict):
            if subset in dataset:
                return dataset[subset].column_names
            elif 'train' in dataset:
                return dataset['train'].column_names
            else:
                first_split = next(iter(dataset))
                return dataset[first_split].column_names
        return dataset.column_names

    def get_dataset_splits(self, dataset: Union[Dataset, DatasetDict]) -> List[str]:
        """Existing split getter logic"""
        if isinstance(dataset, DatasetDict):
            return list(dataset.keys())
        return ["train"]

    def validate_dataset(self, 
                      dataset: Union[Dataset, DatasetDict], 
                      config: Dict[str, List[str]],
                      subset: str) -> Dict[str, Any]:
        """Existing validation logic"""
        if isinstance(dataset, DatasetDict):
            split_name = subset if subset in dataset else 'train'
            if split_name not in dataset:
                split_name = next(iter(dataset))
            dataset_to_validate = dataset[split_name]
        else:
            dataset_to_validate = dataset

        results = {
            "num_examples": len(dataset_to_validate),
            "columns_present": dataset_to_validate.column_names,
            "missing_columns": [],
            "empty_rows": 0,
            "valid_examples": 0
        }

        # Check required columns
        if "required_columns" in config:
            results["missing_columns"] = [
                col for col in config["required_columns"] 
                if col not in dataset_to_validate.column_names
            ]

        def is_valid_example(example):
            return any(str(v).strip() if v is not None else False 
                    for v in example.values())

        valid_examples = sum(1 for ex in dataset_to_validate if is_valid_example(ex))
        results["valid_examples"] = valid_examples
        results["empty_rows"] = len(dataset_to_validate) - valid_examples

        return results

    def load_dataset(self, 
                    dataset_name: str,
                    subset: Optional[str] = None,
                    use_test_data: bool = True) -> Dict[str, Any]:
        """Enhanced dataset loading with test/cache support"""
        try:
            # Try test data first if requested
            if use_test_data:
                test_path = self.test_data_dir / dataset_name.replace("/", "_")
                if subset:
                    test_file = test_path / f"{subset}_sample.csv"
                    if test_file.exists():
                        dataset = Dataset.from_csv(str(test_file))
                        self.logger.info(f"Loaded test data from {test_file}")
                        return {
                            "status": "success",
                            "data": dataset,
                            "source": "test_data"
                        }

            # Try cache next
            cache_path = self.cache_dir / dataset_name.replace("/", "___")
            if cache_path.exists():
                try:
                    dataset = load_from_disk(str(cache_path))
                    self.logger.info(f"Loaded from cache: {cache_path}")
                    return {
                        "status": "success",
                        "data": dataset,
                        "source": "cache"
                    }
                except Exception as e:
                    self.logger.warning(f"Cache load failed: {e}")

            # Finally try HuggingFace
            dataset = load_dataset(dataset_name, subset, cache_dir=str(self.cache_dir))
            self.logger.info(f"Downloaded from HuggingFace: {dataset_name}")
            return {
                "status": "success",
                "data": dataset,
                "source": "huggingface"
            }

        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_name}: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }

    def test_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """Main testing function"""
        if dataset_name not in DATASET_CONFIGS:
            return {"status": "error", "error": f"Unknown dataset: {dataset_name}"}

        results = {}
        config = DATASET_CONFIGS[dataset_name]

        for subset in config["subsets"]:
            self.logger.info(f"Testing {dataset_name} - subset: {subset}")
            
            # Try test data first
            result = self.load_dataset(dataset_name, subset, use_test_data=True)
            
            if result["status"] == "success":
                dataset = result["data"]
                validation_results = self.validate_dataset(
                    dataset, 
                    {"required_columns": config["required_columns"][subset]},
                    subset
                )
                
                results[subset] = {
                    "status": "success",
                    "source": result["source"],
                    "validation": validation_results,
                    "splits": self.get_dataset_splits(dataset),
                    "columns": self.get_dataset_columns(dataset, subset)
                }
            else:
                results[subset] = {
                    "status": "error",
                    "error": result["error_message"]
                }

        return results

def main():
    # Use real project path
    base_dir = Path("/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/darija_project")
    
    test_suite = EnhancedDatasetTestSuite(base_dir)
    
    # Test configured datasets
    for dataset_name in DATASET_CONFIGS.keys():
        print(f"\nTesting dataset: {dataset_name}")
        results = test_suite.test_dataset(dataset_name)
        
        # Print results
        for subset_name, subset_results in results.items():
            print(f"\n  {subset_name}:")
            if subset_results["status"] == "success":
                print(f"    Source: {subset_results['source']}")
                print(f"    Splits: {', '.join(subset_results['splits'])}")
                print(f"    Columns: {', '.join(subset_results['columns'])}")
                validation = subset_results["validation"]
                if isinstance(validation, dict):
                    for key, value in validation.items():
                        print(f"    {key}: {value}")
            else:
                print("    Status: Error")
                print(f"    Error: {subset_results['error']}")

if __name__ == "__main__":
    main()