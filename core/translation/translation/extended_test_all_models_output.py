import logging
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from core.translation.translation.unified_translation_service import (
    UnifiedTranslationService,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extended_test_all_models():
    unified_service = UnifiedTranslationService()
    test_text = "Hello, how are you?"
    successful_models = 0
    total_models = len(unified_service.get_available_models())

    logger.info(f"Testing {total_models} models for translation capability.")

    for model_name in unified_service.get_available_models():
        logger.info(f"\nTesting model: {model_name}")
        try:
            result = unified_service.translate(test_text, "English", "Darija", model=model_name)
            if result and not result.startswith("Translation error"):
                logger.info("Translation successful:")
                logger.info(f"Input: {test_text}")
                logger.info(f"Output: {result}")
                successful_models += 1
            else:
                logger.error("Translation failed:")
                logger.error(f"Output: {result}")
        except Exception as e:
            logger.error("An error occurred during translation:")
            logger.error(f"Error: {str(e)}")

    logger.info("\nTest completed.")
    logger.info(f"Number of successfully translating models: {successful_models}")
    logger.info(f"Number of models that failed to translate: {total_models - successful_models}")

if __name__ == '__main__':
    extended_test_all_models()
