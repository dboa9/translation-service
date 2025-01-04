"""
Model validator for translation service.
Handles model availability checks and fallback chain management.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelValidator:
    def __init__(self, api_url: str, headers: Dict[str, str], cache_dir: Path):
        self.api_url = api_url
        self.headers = headers
        self.cache_dir = cache_dir
        self.model_status_cache: Dict[str, Dict[str, Any]] = {}
        
    def validate_model(self, model_name: str) -> Tuple[bool, str]:
        """
        Validate model availability and status.
        Returns (is_valid, message)
        """
        logger.info(f"Validating model: {model_name}")
        
        # Check if model is cached locally
        model_dir = self.cache_dir / model_name.replace("/", "_")
        if model_dir.exists():
            logger.info(f"Model {model_name} found in local cache")
            if self._verify_local_model(model_dir):
                return True, "Model available locally"
            else:
                logger.warning(f"Local model {model_name} appears corrupted")
                
        # Check API availability
        try:
            status = self._check_api_status(model_name)
            if status.get("loaded", False):
                logger.info(f"Model {model_name} is loaded and ready via API")
                return True, "Model available via API"
            elif status.get("state") == "Loadable":
                logger.info(f"Model {model_name} is loadable via API")
                return True, "Model loadable via API"
            else:
                logger.error(f"Model {model_name} is not available: {status.get('state', 'unknown state')}")
                return False, f"Model not available: {status.get('state', 'unknown state')}"
                
        except Exception as e:
            logger.error(f"Error validating model {model_name}: {str(e)}")
            return False, f"Validation error: {str(e)}"
            
    def get_fallback_chain(self, primary_model: str, task_type: str) -> List[str]:
        """
        Get ordered list of fallback models for a given primary model and task.
        """
        fallback_models = {
            "translation": {
                "AnasAber/seamless-darija-eng": [
                    "BAKKALIAYOUB/DarijaTranslation-V1",
                    "lachkarsalim/LatinDarija_English-v2",
                    "hananeChab/darija_englishV2.1"
                ],
                "BAKKALIAYOUB/DarijaTranslation-V1": [
                    "AnasAber/seamless-darija-eng",
                    "lachkarsalim/LatinDarija_English-v2"
                ],
                "lachkarsalim/LatinDarija_English-v2": [
                    "AnasAber/seamless-darija-eng",
                    "BAKKALIAYOUB/DarijaTranslation-V1"
                ]
            }
        }
        
        chain = fallback_models.get(task_type, {}).get(primary_model, [])
        logger.info(f"Fallback chain for {primary_model}: {chain}")
        return chain
        
    def _verify_local_model(self, model_dir: Path) -> bool:
        """Verify local model files are complete and valid."""
        required_files = ["config.json", "tokenizer_config.json"]
        model_files = ["pytorch_model.bin", "model.safetensors"]
        
        # Check for required configuration files
        for req_file in required_files:
            if not (model_dir / req_file).exists():
                logger.error(f"Missing required file {req_file} in {model_dir}")
                return False
                
        # Check for at least one model file format
        has_model_file = any((model_dir / mf).exists() for mf in model_files)
        if not has_model_file:
            logger.error(f"No model file found in {model_dir}")
            return False
            
        return True
        
    def _check_api_status(self, model_name: str) -> Dict[str, Any]:
        """Check model status via HuggingFace API."""
        # Use cached status if available and recent
        if model_name in self.model_status_cache:
            return self.model_status_cache[model_name]
            
        try:
            response = requests.get(
                f"https://api-inference.huggingface.co/status/{model_name}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                status = response.json()
                self.model_status_cache[model_name] = status
                return status
            else:
                logger.error(f"API status check failed: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error checking API status: {str(e)}")
            return {"error": str(e)}
