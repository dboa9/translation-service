import sys
from pathlib import Path
from typing import Any, Union

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.credentials import load_credentials
except ImportError:
    def load_credentials():
        return {}

try:
    from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict  # type: ignore
except ImportError:
    Dataset = DatasetDict = IterableDataset = IterableDatasetDict = Any  # type: ignore

try:
    from core.dataset.dataset_wrapper_adapter import DatasetWrapperAdapter  # type: ignore
except ImportError:
    class DatasetWrapperAdapter:  # type: ignore
        def __init__(self, base_dir: str):
            pass
        def load_and_validate_dataset(self, dataset_name: str, subset: str) -> Any:
            pass

DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]

def get_project_root() -> Path:
    return project_root
