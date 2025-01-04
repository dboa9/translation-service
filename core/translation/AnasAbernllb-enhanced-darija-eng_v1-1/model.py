import logging
import requests
from config.credentials import load_credentials

logger = logging.getLogger(__name__)

class AnasAberNllbEnhancedTranslationService:
    def __init__(self):
        self.model_name = "AnasAber/nllb-enhanced-darija-eng"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        credentials = load_credentials()
        self.headers = {"Authorization": f"Bearer {credentials['tokens']['huggingface']}"}
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        payload = {
            "inputs": text,
            "parameters": {
                "src_lang": source_lang,
                "tgt_lang": target_lang,
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
                    return result[0]['generated_text']
                else:
                    logger.error(f"Unexpected API response format: {result}")
                    return f"[AnasAberNllbEnhanced] Unexpected API response format"
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    continue
                return f"[AnasAberNllbEnhanced] API request failed: {str(e)}"
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                return f"[AnasAberNllbEnhanced] Translation error: {str(e)}"
        
        return "[AnasAberNllbEnhanced] Translation failed after all retries"

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    service = AnasAberNllbEnhancedTranslationService()
    
    # Darija to English
    darija_text = "كيفاش نقدر نتعلم الإنجليزية بسرعة؟"
    english_translation = service.translate(darija_text, source_lang="ary_Arab", target_lang="eng_Latn")
    print(f"Darija to English: {english_translation}")
    
    # English to Darija
    english_text = "How can I learn English quickly?"
    darija_translation = service.translate(english_text, source_lang="eng_Latn", target_lang="ary_Arab")
    print(f"English to Darija: {darija_translation}")
