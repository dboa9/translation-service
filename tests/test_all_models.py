import sys
import os
import logging
from typing import Dict, Any
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.translation.extended_translation_service import ExtendedTranslationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_models():
    service = ExtendedTranslationService()
    test_text = "Hello, how are you?"
    source_lang = "en"
    target_lang = "ary"  # Assuming 'ary' is the code for Darija

    results: Dict[str, Any] = {}

    for model_name in service.get_available_models():
        logger.info(f"Testing model: {model_name}")
        try:
            translation = service.translate(test_text, source_lang, target_lang, model_name)
            results[model_name] = {
                "status": "success",
                "translation": translation
            }
            logger.info(f"Translation successful: {translation}")
        except Exception as e:
            results[model_name] = {
                "status": "error",
                "error_message": str(e)
            }
            logger.error(f"Translation failed: {str(e)}")

    return results

def write_results_to_file(results: Dict[str, Any], file_path: str):
    with open(file_path, 'w') as f:
        json.dump(results, f, indent=4)

def read_results_from_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    results = test_all_models()
    write_results_to_file(results, 'translation_results.json')
    results_from_file = read_results_from_file('translation_results.json')
    print(json.dumps(results_from_file, indent=4))
