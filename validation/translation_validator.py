import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationValidator:
    """Validator class to ensure translation parameters and responses are valid"""
    
    def __init__(self):
        self.supported_languages = {
            "english": "eng",
            "darija": "ary"
        }
        
    def validate_request_params(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Validate translation request parameters and return formatted parameters"""
        if not text:
            logger.warning("Empty text provided for translation")
            raise ValueError("Text cannot be empty")
            
        source_lang = source_lang.lower()
        target_lang = target_lang.lower()
        
        if target_lang not in self.supported_languages:
            raise ValueError(f"Unsupported target language: {target_lang}")
            
        tgt_lang_code = self.supported_languages[target_lang]
        
        return {
            "inputs": text,
            "parameters": {
                "tgt_lang": tgt_lang_code,
                "max_length": 128,
                "num_beams": 5,
                "temperature": 0.7,
                "do_sample": True,
                "top_k": 50,
                "top_p": 0.95
            }
        }
        
    def validate_api_response(self, response: Any) -> Optional[str]:
        """Validate and extract translation from API response"""
        if not isinstance(response, list):
            logger.error(f"Invalid response format: {response}")
            return None
            
        if not response:
            logger.error("Empty response received")
            return None
            
        translation = response[0].get('generated_text', '').strip()
        if not translation:
            logger.warning("Empty translation in response")
            return None
            
        return translation
        
    def validate_batch_inputs(self, texts: list, source_lang: str, target_lang: str) -> bool:
        """Validate batch translation inputs"""
        if not texts:
            logger.warning("Empty text list provided for batch translation")
            return False
            
        if not all(isinstance(text, str) for text in texts):
            logger.error("All batch inputs must be strings")
            return False
            
        if not all(text.strip() for text in texts):
            logger.warning("Some batch inputs are empty strings")
            return False
            
        return True

    def get_language_code(self, language: str) -> str:
        """Get standardized language code"""
        language = language.lower()
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        return self.supported_languages[language]
