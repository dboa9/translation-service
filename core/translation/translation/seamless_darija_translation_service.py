import logging
import requests
import sys
import os
from typing import List, Dict

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from core.translation.translation.services import UnifiedTranslationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeamlessDarijaTranslationService(UnifiedTranslationService):
    def __init__(self):
        super().__init__()
        self.model_name = "AnasAber/seamless-darija-eng"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.language_codes = {
            "english": "eng",
            "darija": "ary"
        }
        from config.credentials import HUGGINGFACE_TOKEN
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
        logger.info(f"SeamlessDarijaTranslationService initialized with model: {self.model_name}")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"Headers: {self.headers}")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            if not text:
                logger.warning("Empty text provided for translation")
                return ""

            logger.info(f"Translating from {source_lang} to {target_lang}")
            logger.info(f"Input text: {text}")

            tgt_lang_code = self.language_codes.get(target_lang.lower(), "ary")

            payload = {
                "inputs": text,
                "parameters": {
                    "tgt_lang": tgt_lang_code
                }
            }

            logger.info(f"Sending request to API with payload: {payload}")
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")
            logger.info(f"Response content: {response.text}")

            response.raise_for_status()
            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                translation = result[0].get('generated_text', '').strip()
                if translation:
                    logger.info(f"Translation completed: '{text}' ({source_lang}) -> '{translation}' ({target_lang})")
                    return translation
                else:
                    logger.warning("Empty translation received from API")
            else:
                logger.error(f"Unexpected API response format: {result}")

            return f"Translation error: Unexpected response format"

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return f"Translation error: {str(e)}"
        except Exception as e:
            logger.error(f"Error in translate method: {str(e)}")
            return f"Translation error: {str(e)}"

    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        return [self.translate(text, source_lang, target_lang) for text in texts]

# Example usage
if __name__ == "__main__":
    service = SeamlessDarijaTranslationService()
    try:
        print("English to Darija:")
        result = service.translate("Hello, how are you?", "English", "Darija")
        print(f"Input: Hello, how are you?\nOutput: {result}\n")

        print("Darija to English:")
        result = service.translate("كيف داير؟", "Darija", "English")
        print(f"Input: كيف داير؟\nOutput: {result}\n")

    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
