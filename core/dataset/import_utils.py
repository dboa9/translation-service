# File: import_utils.py
import sys
import logging
import site
from typing import Tuple, Any

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"sys.path: {sys.path}")


def import_datasets() -> Tuple[Any, ...]:
    try:
        from datasets import (
            load_dataset, Dataset, IterableDataset,
            DatasetDict, IterableDatasetDict
        )
        logger.debug("Successfully imported datasets module")
        return (
            load_dataset, Dataset, IterableDataset,
            DatasetDict, IterableDatasetDict
        )
    except ImportError as e:
        logger.error(f"Failed to import datasets module: {e}")
        user_site = site.getusersitepackages()
        sys.path.append(user_site)
        logger.debug(f"Added user site-packages to sys.path: {user_site}")
        try:
            from datasets import (
                load_dataset, Dataset, IterableDataset,
                DatasetDict, IterableDatasetDict
            )
            logger.debug(
                "Successfully imported datasets module after path modification"
            )
            return (
                load_dataset, Dataset, IterableDataset,
                DatasetDict, IterableDatasetDict
            )
        except ImportError as e:
            logger.error(f"Still failed to import datasets module: {e}")
            raise
