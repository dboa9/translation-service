import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def log_error(message: str) -> Dict[str, Any]:
    logger.error(message)
    return {"status": False, "error": message}
