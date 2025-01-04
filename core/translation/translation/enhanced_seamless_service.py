import logging
import requests
from typing import List, Optional
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from validation.translation_validator import TranslationValidator
from core.translation.translation.seamless_darija_translation_service import SeamlessDarijaTranslationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSeamlessService(SeamlessDarijaTranslationService):
    """Enhanced translation service with validation"""
    
    def __init__(self):
        super().__init__()
        self.validator = TranslationValidator()
        
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            # Validate and format request parameters
            payload = self.validator.validate_request_params(text, source_lang, target_lang)
            
            logger.info(f"Sending validated request with payload: {payload}")
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            response.raise_for_status()
            result = response.json()
            
            # Validate and extract translation from response
            translation = self.validator.validate_api_response(result)
            if translation:
                logger.info(f"Translation completed successfully: '{text}' -> '{translation}'")
                return translation
                
            return "Translation error: Invalid response format"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return f"Translation error: {str(e)}"
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return f"Translation error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Translation error: {str(e)}"
            
    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        if not self.validator.validate_batch_inputs(texts, source_lang, target_lang):
            return ["Translation error: Invalid batch input"] * len(texts)
            
        return [self.translate(text, source_lang, target_lang) for text in texts]

# Example usage
if __name__ == "__main__":
    service = EnhancedSeamlessService()
    try:
        print("\nTesting English to Darija translation:")
        result = service.translate("Hello, how are you?", "English", "Darija")
        print(f"Input: Hello, how are you?\nOutput: {result}")
        
        print("\nTesting Darija to English translation:")
        result = service.translate("كيف داير؟", "Darija", "English")
        print(f"Input: كيف داير؟\nOutput: {result}")
        
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
