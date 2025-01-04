"""
Translation service implementation with environment-aware model loading.

IMPORTANT: This file contains changes suggested by GitHub Copilot.
The following changes require explicit authorization before modification:

1. Lines 48-71 - TranslationService.__init__:
   - Added environment-aware initialization
   - REQUIRES AUTHORIZATION before modifying initialization logic

2. Lines 171-227 - Local model translation:
   - Added cached model translation functionality
   - REQUIRES AUTHORIZATION before modifying model execution

3. Lines 230-290 - API translation:
   - Added improved API error handling and retry logic
   - REQUIRES AUTHORIZATION before modifying API interaction

4. Lines 292-299 - Fallback model selection:
   - Added language-specific fallback models
   - REQUIRES AUTHORIZATION before modifying fallback logic

5. Lines 301-332 - API status checking:
   - Added environment-aware API status checks
   - REQUIRES AUTHORIZATION before modifying status logic

DO NOT MODIFY THESE SECTIONS WITHOUT EXPLICIT AUTHORIZATION
"""

import os
import time
from pathlib import Path
import logging
from typing import Dict, Any, Optional, Tuple, Union, List, cast
import yaml
import requests
import torch
from transformers import (
    AutoModelForSeq2SeqLM, 
    AutoTokenizer, 
    PreTrainedModel, 
    PreTrainedTokenizerBase,
    GenerationConfig
)
from core.utils.environment import should_use_local_models
from transformers.generation.utils import GenerateOutput
from streamlit.delta_generator import DeltaGenerator
import streamlit as st
from .model_validator import ModelValidator
from .response_handler import ResponseHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("translation_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Type definitions
ModelCache = Dict[str, Tuple[PreTrainedModel, PreTrainedTokenizerBase]]

class TranslationService:
    def __init__(self):
        logger.info("Initializing TranslationService...")
        try:
            # Import here to avoid circular imports
            from config.credentials import HUGGINGFACE_TOKEN
            self.api_url = "https://api-inference.huggingface.co/models/"
            self.headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
            logger.info("HuggingFace token loaded successfully")
            
            # Load configuration
            self._config = self._load_config()
            if not self._config:
                raise ValueError("Failed to load configuration")
            
            # Initialize model cache if running on EC2
            self.use_local_models = should_use_local_models()
            self.cache_dir = Path("model_cache")
            self.cache_dir.mkdir(exist_ok=True)
            
            # Initialize components
            self.model_validator = ModelValidator(self.api_url, self.headers, self.cache_dir)
            self.response_handler = ResponseHandler()
            
            if self.use_local_models:
                logger.info("Running on EC2 - Using local model files")
                self.model_cache: ModelCache = {}
                self._load_cached_models()
            else:
                logger.info("Running locally - Using HuggingFace API")
                self.model_cache = {}
                
            logger.info("TranslationService initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import credentials: {str(e)}")
            st.error("Failed to load HuggingFace token. Please check credentials.py")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize TranslationService: {str(e)}")
            st.error(f"Initialization error: {str(e)}")
            raise

    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML file."""
        try:
            config_path = Path("config/model_config.yaml")
            logger.info(f"Looking for config at: {config_path}")
            
            if not config_path.exists():
                logger.error(f"Config file not found at: {config_path}")
                st.error(f"Configuration file not found at: {config_path}")
                return {}
            
            logger.info("Found config file attempting to load...")
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
            if not isinstance(config, dict):
                logger.error(f"Invalid config format: {type(config)}")
                st.error("Invalid configuration format")
                return {}
                
            if 'translation_models' not in config:
                logger.error("No translation_models section in config")
                st.error("Invalid configuration: missing translation_models")
                return {}
                
            logger.info(f"Successfully loaded {len(config['translation_models'])} models")
            for model in config['translation_models']:
                logger.info(f"Found model: {model}")
                
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            st.error(f"Configuration error: {str(e)}")
            return {}

    def _load_cached_models(self):
        """Load any models that are already cached locally."""
        try:
            for model_name in self._config.get('translation_models', {}):
                model_dir = self.cache_dir / model_name.replace("/", "_")
                if model_dir.exists():
                    try:
                        logger.info(f"Loading cached model: {model_name}")
                        model = AutoModelForSeq2SeqLM.from_pretrained(
                            str(model_dir),
                            torch_dtype=torch.float32,
                            low_cpu_mem_usage=True
                        )
                        tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
                        self.model_cache[model_name] = (model, tokenizer)
                        logger.info(f"Successfully loaded cached model: {model_name}")
                    except Exception as e:
                        logger.error(f"Error loading cached model {model_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading cached models: {str(e)}")

    def is_model_cached(self, model_name: str) -> bool:
        """Check if a model is available in the local cache."""
        return model_name in self.model_cache

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration dictionary."""
        return self._config

    def get_available_models(self) -> List[str]:
        """Get list of available translation models."""
        return list(self._config.get("translation_models", {}).keys())

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        logger.info(f"Getting info for model: {model}")
        if not model:
            return {}
            
        model_info = self._config.get("translation_models", {}).get(model, {})
        logger.info(f"Model info: {model_info}")
        return model_info

    def translate(self, text: str, source_lang: str, target_lang: str, model: str) -> Optional[str]:
        """Translate text using specified model."""
        logger.info(f"Translating text: {text}")
        logger.info(f"Translating text using model: {model}")
        
        try:
            # Validate primary model
            is_valid, message = self.model_validator.validate_model(model)
            if not is_valid:
                logger.warning(f"Primary model validation failed: {message}")
                # Try fallback models
                fallback_models = self.model_validator.get_fallback_chain(model, "translation")
                for fallback in fallback_models:
                    is_valid, message = self.model_validator.validate_model(fallback)
                    if is_valid:
                        logger.info(f"Using fallback model: {fallback}")
                        model = fallback
                        break
                else:
                    error_msg = "No valid models available for translation"
                    logger.error(error_msg)
                    return None
            
            # When running locally, always use API
            # When on EC2, try local model first
            if not self.use_local_models:
                logger.info("Running locally - Using API directly")
                return self._translate_with_api(text, model, target_lang)
            elif self.is_model_cached(model):
                logger.info(f"Running on EC2 - Using cached model: {model}")
                return self._translate_with_local_model(text, model)
            else:
                logger.info(f"Running on EC2 - Model not cached, using API: {model}")
                return self._translate_with_api(text, model, target_lang)
            
        except Exception as e:
            error_context = {
                "text": text[:100],
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model": model
            }
            error_msg = self.response_handler.format_error(e, error_context)
            logger.error(f"Translation error: {error_msg}")
            return None
            
    def _translate_with_local_model(self, text: str, model: str) -> Optional[str]:
        """Translate using a locally cached model."""
        try:
            model_obj, tokenizer = self.model_cache[model]
            
            # Encode input text
            inputs = tokenizer(text, return_tensors="pt", padding=True)
            input_ids = inputs["input_ids"]
            attention_mask = inputs.get("attention_mask", None)
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                max_length=512,
                num_beams=4,
                length_penalty=0.6,
                early_stopping=True
            )
            
            # Generate translation
            outputs = model_obj.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                generation_config=generation_config
            )
            
            # Handle different output types
            if isinstance(outputs, GenerateOutput):
                sequences = outputs.sequences
            elif isinstance(outputs, torch.Tensor):
                sequences = outputs
            else:
                sequences = cast(torch.Tensor, outputs)
            
            # Convert to list for decoding
            if isinstance(sequences, torch.Tensor):
                sequences = sequences.tolist()
            
            # Decode output
            translation = tokenizer.batch_decode(
                sequences,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )[0].strip()
            
            self.response_handler.log_translation_attempt(
                True, model, text, translation
            )
            return translation
            
        except Exception as e:
            self.response_handler.log_translation_attempt(
                False, model, text, None, str(e)
            )
            return None
            
    def _translate_with_api(self, text: str, model: str, target_lang: str) -> Optional[str]:
        """Translate using the HuggingFace API."""
        try:
            logger.info(f"Using API for model: {model}")
            
            # Get model info for language codes
            model_info = self._config.get("translation_models", {}).get(model, {})
            model_type = model_info.get("model_type")
            lang_codes = model_info.get("lang_codes", {})
            
            # Build payload based on model type
            if model_type == "seamless":
                # For seamless models, we need to set the target language token
                payload = {
                    "inputs": text,
                    "parameters": {
                        "max_length": 512,
                        "num_beams": 4,
                        "length_penalty": 0.6,
                        "early_stopping": True,
                        "task": "translation",
                        "source_lang": lang_codes.get("source"),
                        "target_lang": lang_codes.get("target")
                    }
                }
            else:
                # Default payload for other model types
                payload = {
                    "inputs": text,
                    "parameters": {
                        "max_length": 512,
                        "num_beams": 4,
                        "length_penalty": 0.6,
                        "early_stopping": True
                    }
                }
            
            logger.info(f"API request payload: {payload}")
            
            # Get model family for response parsing
            model_family = self._get_model_family(model)
            
            # Make API request with retry
            max_retries = 3
            base_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        f"{self.api_url}{model}",
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 503:
                        if attempt < max_retries - 1:
                            delay = base_delay * (attempt + 1)  # Exponential backoff
                            logger.warning(f"Model is loading, retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        else:
                            error_msg = f"Model failed to load after {max_retries} attempts"
                            logger.error(error_msg)
                            st.error(error_msg)
                            return None
                        
                    if response.status_code != 200:
                        error_msg = f"API error ({response.status_code}): {response.text}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        return None
                        
                    result = response.json()
                    logger.info(f"API response: {result}")
                    success, translation, error = self.response_handler.extract_translation(
                        result, model_family
                    )
                    
                    if success:
                        self.response_handler.log_translation_attempt(
                            True, model, text, translation
                        )
                        return translation
                    else:
                        logger.error(f"Failed to extract translation: {error}")
                        return None
                        
                except requests.exceptions.Timeout:
                    if attempt == 0:
                        continue
                    error_msg = "API request timed out"
                    logger.error(error_msg)
                    st.error(error_msg)
                    return None
                    
            return None
            
        except Exception as e:
            self.response_handler.log_translation_attempt(
                False, model, text, None, str(e)
            )
            return None

    def _get_model_family(self, model: str) -> str:
        """Determine model family for response parsing."""
        model_lower = model.lower()
        if "nllb" in model_lower:
            return "nllb"
        elif "seamless" in model_lower:
            return "seamless"
        else:
            return "marian"  # Default to marian format

    def _get_fallback_model(self, source_lang: str, target_lang: str) -> Optional[str]:
        """Get fallback model based on language direction."""
        if source_lang == "English" and target_lang == "Darija":
            return "AnasAber/nllb-enhanced-darija-eng_v1-1"
        elif source_lang == "Darija" and target_lang == "English":
            return "imomayiz/darija_englishV2.1"
        elif source_lang == "Latin Darija" and target_lang == "English":
            return "lachkarsalim/LatinDarija_English-v2"
        return None

    def _check_api_status(self, model: str, st_status: Optional[DeltaGenerator] = None) -> bool:
        """Check if the HuggingFace API is available for a model."""
        try:
            # If running locally, always use API
            if not self.use_local_models:
                return True
                
            # If running on EC2, check if model is cached
            if self.is_model_cached(model):
                return True
                
            # If model not cached on EC2, check API status
            response = requests.get(
                f"https://api-inference.huggingface.co/status/{model}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Status check failed: {response.text}")
                return False
                
            status = response.json()
            logger.info(f"Model {model} status: {status}")
            return status.get("loaded", False) or status.get("state") == "Loadable"
            
        except Exception as e:
            logger.error(f"Error checking API status: {str(e)}")
            return False

    def check_tokenizer_config(self, model: str):
        """Check the tokenizer configuration for a model."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model)
            logger.info(f"Tokenizer configuration for {model}: {tokenizer}")
        except Exception as e:
            logger.error(f"Error loading tokenizer for {model}: {str(e)}")
