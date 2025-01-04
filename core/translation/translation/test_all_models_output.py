import logging
from core.translation.translation.all_models_translation_service import *
from core.translation.translation.unified_translation_service import UnifiedTranslationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_models():
    unified_service = UnifiedTranslationService()
    test_text = "Hello, how are you?"
    successful_models = 0

    for model_name, model_service in unified_service.services.items():
        try:
            result = model_service.translate(test_text, "English", "Darija")
            if result and not result.startswith("Translation error"):
                logger.info(f"\n{model_name} translation:")
                logger.info(f"Input: {test_text}")
                logger.info(f"Output: {result}")
                successful_models += 1
            else:
                logger.error(f"\n{model_name} failed to translate:")
                logger.error(f"Output: {result}")
        except Exception as e:
            logger.error(f"\n{model_name} failed to translate:")
            logger.error(f"Error: {str(e)}")

    logger.info(f"\nNumber of successfully translating models: {successful_models}")

if __name__ == '__main__':
    test_all_models()
