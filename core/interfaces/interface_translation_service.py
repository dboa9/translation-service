import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("interface_translation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InterfaceTranslationService:
    def __init__(self):
        self.config = self._load_config()
        self.api_url = "https://api-inference.huggingface.co/models/"
        # Import here to avoid circular imports
        from config.credentials import HUGGINGFACE_TOKEN
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
        logger.info("InterfaceTranslationService initialized with HuggingFace token")

    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML file."""
        # Use absolute path from current working directory
        config_path = Path('/mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service/config/model_config.yaml')
        logger.info(f"Loading config from absolute path: {config_path}")
        if not config_path.exists():
            logger.error(f"Config file not found at: {config_path}")
            return {}
        logger.info("Config file found")
        
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config: {config}")
                if 'translation_models' in config:
                    logger.info(f"Found {len(config['translation_models'])} translation models")
                    for model in config['translation_models']:
                        logger.info(f"Model: {model}")
                else:
                    logger.error("No translation_models found in config")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            logger.error(f"Current working directory: {os.getcwd()}")
            return {}

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        logger.info(f"Getting info for model: {model}")
        if not model:
            return {}
            
        model_info = self.config.get("translation_models", {}).get(model, {})
        logger.info(f"Model info: {model_info}")
        return model_info

    def translate(self, text: str, source_lang: str, target_lang: str, model: str) -> Optional[str]:
        """Translate text using specified model."""
        logger.info(f"Translating text using model: {model}")
        if not text or not model:
            return None

        try:
            api_url = self.api_url + model
            response = requests.post(api_url, headers=self.headers, json={"inputs": text})
            response.raise_for_status()

            result = response.json()
            if isinstance(result, list) and result:
                translation = result[0].get("translation_text")
                logger.info(f"Translation successful: {translation}")
                return translation
            
            logger.warning("Translation API returned unexpected response format")
            return None
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None
