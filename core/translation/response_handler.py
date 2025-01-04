"""
Response handler for translation service.
Handles different API response formats and provides detailed error reporting.
"""

import logging
from typing import Dict, Any, Optional, Union, List, Tuple
import json
import requests

logger = logging.getLogger(__name__)

class ResponseHandler:
    def __init__(self):
        # Known response formats for different model types
        self.response_formats = {
            "marian": {
                "translation_key": "translation_text",
                "fallback_keys": ["generated_text"]
            },
            "nllb": {
                "translation_key": "generated_text",
                "fallback_keys": ["translation_text"]
            },
            "seamless": {
                "translation_key": "generated_text",
                "fallback_keys": ["translation_text", "text"]
            }
        }
        
    def extract_translation(
        self,
        response: Union[str, Dict, List],
        model_family: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract translation from API response.
        Returns (success, translation, error_message)
        """
        try:
            # Handle string responses
            if isinstance(response, str):
                return True, response, None
                
            # Handle list responses
            if isinstance(response, list):
                if not response:
                    return False, None, "Empty response list"
                response = response[0]
                
            # Handle dict responses
            if isinstance(response, dict):
                # Get format keys for model family
                format_info = self.response_formats.get(
                    model_family,
                    self.response_formats["marian"]  # Default to marian format
                )
                
                # Try primary translation key
                translation = response.get(format_info["translation_key"])
                if translation:
                    return True, translation, None
                    
                # Try fallback keys
                for key in format_info["fallback_keys"]:
                    translation = response.get(key)
                    if translation:
                        logger.info(f"Used fallback key: {key}")
                        return True, translation, None
                        
                # No valid translation found
                error_msg = f"No translation found in keys: {[format_info['translation_key']] + format_info['fallback_keys']}"
                logger.error(error_msg)
                return False, None, error_msg
                
            error_msg = f"Unexpected response type: {type(response)}"
            logger.error(error_msg)
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Error extracting translation: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
            
    def format_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """
        Format error message with context for better debugging.
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        try:
            # Add response status and content for request errors
            if isinstance(error, requests.RequestException) and error.response is not None:
                error_info.update({
                    "status_code": error.response.status_code,
                    "response_text": error.response.text[:500]  # Limit response text length
                })
        except Exception as e:
            logger.warning(f"Could not add response details to error: {e}")
            
        return json.dumps(error_info, indent=2)
        
    def log_translation_attempt(
        self,
        success: bool,
        model: str,
        source_text: str,
        translation: Optional[str],
        error: Optional[str] = None
    ):
        """
        Log translation attempt with detailed information.
        """
        log_data = {
            "success": success,
            "model": model,
            "source_text": source_text[:100],  # Limit text length in logs
            "translation": translation[:100] if translation else None,
            "error": error
        }
        
        if success:
            logger.info(f"Translation successful: {json.dumps(log_data, indent=2)}")
        else:
            logger.error(f"Translation failed: {json.dumps(log_data, indent=2)}")
