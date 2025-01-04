import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import yaml
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logger = logging.getLogger(__name__)

class ModelDownloader:
    def __init__(self, cache_dir: str = "model_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def load_model_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML file."""
        try:
            config_path = Path("config/model_config.yaml")
            if not config_path.exists():
                logger.error(f"Config file not found at: {config_path}")
                return {}
                
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
            if not isinstance(config, dict) or 'translation_models' not in config:
                logger.error("Invalid config format or missing translation_models section")
                return {}
                
            return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
            
    def download_models(self) -> bool:
        """
        Download all models specified in the configuration.
        Returns True if all models were downloaded successfully.
        """
        config = self.load_model_config()
        if not config:
            return False
            
        success = True
        models = config.get('translation_models', {})
        
        for model_name in models:
            model_dir = self.cache_dir / model_name.replace("/", "_")
            if model_dir.exists():
                logger.info(f"Model {model_name} already cached at {model_dir}")
                continue
                
            try:
                logger.info(f"Downloading model: {model_name}")
                
                # Download and save model
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # Save to cache directory
                model.save_pretrained(str(model_dir))
                tokenizer.save_pretrained(str(model_dir))
                
                logger.info(f"Successfully downloaded model: {model_name}")
                
            except Exception as e:
                logger.error(f"Error downloading model {model_name}: {str(e)}")
                success = False
                
        return success

def download_models_if_needed():
    """
    Download models if running on EC2 and models are not already cached.
    """
    from .environment import should_use_local_models
    
    if should_use_local_models():
        logger.info("Running on EC2 - Checking if models need to be downloaded")
        downloader = ModelDownloader()
        if downloader.download_models():
            logger.info("All models downloaded successfully")
        else:
            logger.warning("Some models failed to download")
    else:
        logger.info("Running locally - Skipping model downloads")
