import logging
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from core.translation.translation import UnifiedTranslationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_unified_translation():
    service = UnifiedTranslationService()

    test_texts = [
        "Hello, how are you?",
        "Good morning",
        "What's your name?",
        "Nice to meet you",
        "Goodbye"
    ]

    for model in service.get_available_models():
        print(f"\nTesting {model.capitalize()} model:")
        for text in test_texts:
            try:
                result = service.translate(text, "English", "Darija", model=model)
                print(f"Input: {text}")
                print(f"Output: {result}")
            except Exception as e:
                logger.error(f"Error with {model} model: {str(e)}")

    print("\nTesting batch translation with seamless model:")
    results = service.batch_translate(test_texts, "English", "Darija")
    for input_text, output_text in zip(test_texts, results):
        print(f"Input: {input_text}")
        print(f"Output: {output_text}")

if __name__ == "__main__":
    test_unified_translation()
