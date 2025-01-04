import logging
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from datasets import load_dataset

from core.translation.translation.unified_translation_service import (
    UnifiedTranslationService,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ... (keep the existing code)

def test_with_huggingface_dataset():
    service = UnifiedTranslationService()
    try:
        dataset = load_dataset("Helsinki-NLP/tatoeba_mt", "eng-ary", split="test", trust_remote_code=True)
    except ValueError as e:
        logger.error(f"Error loading dataset: {e}")
        logger.info("To load this dataset, you need to allow running remote code. Please run the script again with the appropriate permissions.")
        return None
    
    results = {}
    for model_name in service.get_available_models():
        model_results = []
        for i, example in enumerate(dataset):
            if i >= 10:  # Limit to 10 examples per model
                break
            source_text, target_text = example['source'], example['target']
            try:
                translation = service.translate(source_text, "en", "ary", model_name)
                model_results.append({
                    "source": source_text,
                    "reference": target_text,
                    "translation": translation,
                    "status": "success"
                })
            except Exception as e:
                model_results.append({
                    "source": source_text,
                    "reference": target_text,
                    "status": "error",
                    "error_message": str(e)
                })
        results[model_name] = model_results
    
    return results

if __name__ == "__main__":
    print("Testing all models with predefined test cases:")
    results = test_all_models()
    print_results(results)
    
    print("\nTesting models with Hugging Face dataset:")
    hf_results = test_with_huggingface_dataset()
    if hf_results:
        print_results(hf_results)
    else:
        print("Hugging Face dataset test was not completed due to permission issues.")
