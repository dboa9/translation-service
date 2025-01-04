import logging
import requests
import time
import os

logger = logging.getLogger(__name__)

class SimLabDarijaBertService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/sim-lab/darijabert"
        self.headers = {"Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_TOKEN')}"}
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        payload = {
            "inputs": f"Translate from {source_lang} to {target_lang}: {text}"
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['generated_text']
                else:
                    logger.error(f"Unexpected API response format: {result}")
                    return "[SimLabDarijaBert] Unexpected API response format"
            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    return f"[SimLabDarijaBert] API request failed after {self.max_retries} attempts: {str(e)}"
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                return f"[SimLabDarijaBert] Translation error: {str(e)}"
        
        return "[SimLabDarijaBert] Translation failed after all retries"

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    service = SimLabDarijaBertService()
    
    # Darija to English
    darija_text = "كيفاش نقدر نتعلم الإنجليزية بسرعة؟"
    english_translation = service.translate(darija_text, source_lang="Darija", target_lang="English")
    print(f"Darija to English: {english_translation}")
    
    # English to Darija
    english_text = "How can I learn English quickly?"
    darija_translation = service.translate(english_text, source_lang="English", target_lang="Darija")
    print(f"English to Darija: {darija_translation}")
