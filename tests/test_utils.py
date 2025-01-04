import sys
from pathlib import Path
import logging
from typing import Any, Callable, Dict, Union

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from config.credentials import load_credentials
except ImportError as e:
    logger.error(f"Error importing load_credentials: {e}")
    def load_credentials() -> Dict[str, Any]:
        return {}

try:
    from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
except ImportError as e:
    logger.error(f"Error importing datasets: {e}")
    Dataset = DatasetDict = IterableDataset = IterableDatasetDict = Any  # type: ignore

try:
    from core.dataset.dataset_wrapper_adapter import DatasetWrapperAdapter
except ImportError as e:
    logger.error(f"Error importing DatasetWrapperAdapter: {e}")
    class DatasetWrapperAdapter:  # type: ignore
        def __init__(self, base_dir: str):
            pass
        def load_and_validate_dataset(self, dataset_name: str, subset: str) -> Any:
            pass

def get_project_root() -> Path:
    return project_root

# Type aliases
LoadCredentials = Callable[[], Dict[str, Any]]
DatasetType = Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]
