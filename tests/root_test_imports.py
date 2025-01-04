import sys
import os
from pathlib import Path

# Set up logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

logger.debug(f"Python version: {sys.version}")
logger.debug(f"Project root: {project_root}")
logger.debug(f"Python path: {sys.path}")
logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(f"Contents of project root: {list(project_root.iterdir())}")
logger.debug(f"Contents of core directory: {list((project_root / 'core').iterdir())}")
logger.debug(f"Contents of core/dataset directory: {list((project_root / 'core' / 'dataset').iterdir())}")

try:
    import core
    logger.debug(f"Successfully imported core module. Contents: {dir(core)}")
except ImportError as e:
    logger.error(f"Error importing core module: {e}")

try:
    import core.dataset
    logger.debug(f"Successfully imported core.dataset module. Contents: {dir(core.dataset)}")
except ImportError as e:
    logger.error(f"Error importing core.dataset module: {e}")

try:
    from core.dataset.dataset_wrapper_adapter import DatasetWrapperAdapter
    logger.debug("Successfully imported DatasetWrapperAdapter")
    logger.debug(f"DatasetWrapperAdapter: {DatasetWrapperAdapter}")
except ImportError as e:
    logger.error(f"Error importing DatasetWrapperAdapter: {e}")

print("Import test completed.")
