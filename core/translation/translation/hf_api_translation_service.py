"""
Translation service using Hugging Face's Inference API
"""
import logging
import requests
import time
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class HFAPITranslationService:
    """
    Translation service that uses Hugging Face's Inference API
    """
    
    def __init__(self):
        """Initialize the service"""
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        self.max_retries = 5
        self.retry_delay = 10  # seconds
        
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model_name: str
    ) -> str:
        """
        Translate text using Hugging Face's API with improved error handling
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            model_name: Name of the model to use
            
        Returns:
            Translated text
        """
        try:
            # Construct API URL
            api_url = f"https://api-inference.huggingface.co/models/{model_name}"
            
            # Prepare payload based on model type
            if "seamless" in model_name.lower():
                payload = {
                    "inputs": text,
                    "parameters": {
                        "src_lang": source_lang,
                        "tgt_lang": target_lang,
                        "task": "translation",
                        "max_length": 128,
                        "wait_for_model": True
                    }
                }
            elif "nllb" in model_name.lower():
                # NLLB models use specific language codes
                src_code = f"{source_lang}_Latn" if source_lang == "eng" else f"{source_lang}_Arab"
                tgt_code = f"{target_lang}_Latn" if target_lang == "eng" else f"{target_lang}_Arab"
                payload = {
                    "inputs": text,
                    "parameters": {
                        "src_lang": src_code,
                        "tgt_lang": tgt_code,
                        "task": "translation",
                        "max_length": 128,
                        "wait_for_model": True
                    }
                }
            elif "marian" in model_name.lower() or "helsinki" in model_name.lower():
                # Marian models don't need language codes in the payload
                payload = {
                    "inputs": text,
                    "parameters": {
                        "task": "translation",
                        "max_length": 128,
                        "wait_for_model": True
                    }
                }
            elif "llama" in model_name.lower() or "chat" in model_name.lower():
                # LLM models need a prompt format
                payload = {
                    "inputs": f"Translate from {source_lang} to {target_lang}: {text}",
                    "parameters": {
                        "max_length": 128,
                        "temperature": 0.7,
                        "task": "text-generation",
                        "wait_for_model": True,
                        "return_full_text": False
                    }
                }
            elif "bert" in model_name.lower():
                # BERT models for text processing
                payload = {
                    "inputs": text,
                    "parameters": {
                        "task": "feature-extraction",
                        "wait_for_model": True
                    }
                }
            else:
                # Default translation payload
                payload = {
                    "inputs": text,
                    "parameters": {
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "task": "translation",
                        "max_length": 128,
                        "wait_for_model": True
                    }
                }
            
            # Make API request with retries
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(api_url, headers=self.headers, json=payload, timeout=30)
                    
                    if response.status_code == 503:
                        logger.warning(f"Model {model_name} is loading (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(self.retry_delay)
                        continue
                        
                    response.raise_for_status()
                    result = response.json()
                    
                    # Parse response based on model type
                    translation = self._parse_response(result, model_name)
                    if translation:
                        return translation
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"Request timeout for {model_name} (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    raise
                    
                except requests.exceptions.RequestException as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Request failed for {model_name} (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                        time.sleep(self.retry_delay)
                        continue
                    raise
                    
            return f"Translation failed after {self.max_retries} attempts"
            
        except Exception as e:
            logger.error(f"Translation error with model {model_name}: {str(e)}")
            return f"Error translating text: {str(e)}"
            
    def _parse_response(
        self,
        response: Any,
        model_name: str
    ) -> str:
        """Parse API response based on model type"""
        try:
            if isinstance(response, list):
                if len(response) > 0:
                    if isinstance(response[0], dict):
                        # Handle response format: [{"translation_text": "..."}]
                        if "generated_text" in response[0]:
                            return response[0]["generated_text"]
                        return response[0].get("translation_text", "")
                    elif isinstance(response[0], str):
                        # Handle response format: ["..."]
                        return response[0]
            elif isinstance(response, dict):
                # Handle response format: {"translation_text": "..."}
                if "generated_text" in response:
                    return response["generated_text"]
                return response.get("translation_text", "")
            
            # If we can't parse the response, return it as a string
            return str(response)
            
        except Exception as e:
            logger.error(f"Error parsing response from {model_name}: {str(e)}")
            return f"Error parsing translation: {str(e)}"
