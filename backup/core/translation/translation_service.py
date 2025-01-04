# """
# Enhanced Translation Service for English-Darija Bidirectional Translation
# Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service/core/translation/translation_service.py
# Author: dboa9 (danielalchemy9@gmail.com)
# """

# import logging
# import os
# import sys
# from typing import Any, Dict, Optional, Tuple, List

# # Add the project root to the Python path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# sys.path.insert(0, project_root)

# # Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     filename='translation_service.log',
#     filemode='a'
# )
# logger = logging.getLogger(__name__)

# # Also log to console
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# logger.addHandler(console_handler)

# logger.info(f"Python path: {sys.path}")
# logger.info(f"Python version: {sys.version}")

# try:
#     import tensorflow as tf  # type: ignore
#     from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TFAutoModelForSeq2SeqLM, pipeline  # type: ignore
#     logger.info(f"TensorFlow version: {tf.__version__}")
# except ImportError as e:
#     logger.error(f"Error importing required libraries: {str(e)}")
#     logger.error(f"Python executable: {sys.executable}")
#     logger.error(f"Python path: {sys.path}")
#     raise

# # Import configurations
# from core.translation.model_config import MODEL_CONFIG

# class TranslationService:
#     def __init__(self):
#         self.models: Dict[str, Any] = {}
#         self.tokenizers: Dict[str, Any] = {}
#         self.pipelines: Dict[str, Any] = {}
#         self.model_configs: Dict[str, Dict[str, Any]] = MODEL_CONFIG["generation_config"]
#         self.max_input_length: int = 512
#         self.device: str = "cuda" if tf.test.is_built_with_cuda() else "cpu"
#         logger.info(f"TranslationService initialized on device: {self.device}")

#     def load_model(self, model_name: str) -> None:
#         """Load model and tokenizer"""
#         try:
#             if model_name not in self.models:
#                 logger.info(f"Loading model: {model_name}")
#                 config = self.model_configs.get(model_name, {})
#                 model_family = config.get("model_family", "marian")
#                 load_config = MODEL_CONFIG["model_load_config"].get(model_family, {})
                
#                 tokenizer = AutoTokenizer.from_pretrained(model_name, **load_config)
#                 model = AutoModelForSeq2SeqLM.from_pretrained(model_name, **load_config)
                
#                 self.models[model_name] = model
#                 self.tokenizers[model_name] = tokenizer
                
#                 pipeline_task = "text2text-generation" if config.get("use_case") == ["transliteration"] else "translation"
#                 self.pipelines[model_name] = pipeline(pipeline_task, model=model, tokenizer=tokenizer, device=self.device)
                
#                 logger.info(f"Model {model_name} loaded successfully")
#         except Exception as e:
#             logger.error(f"Error loading model {model_name}: {str(e)}")
#             raise

#     def translate(self, text: str, source_lang: str, target_lang: str) -> str:
#         """Translate text between English and Darija"""
#         try:
#             if not text:
#                 logger.warning("Empty text provided for translation")
#                 return ""

#             model_name = self.select_model(source_lang, target_lang)
            
#             if model_name not in self.models:
#                 self.load_model(model_name)

#             logger.info(f"Translating from {source_lang} to {target_lang} using model: {model_name}")
#             result = self.pipelines[model_name](text, max_length=self.max_input_length)
#             translation = result[0]['generated_text']
            
#             logger.info(f"Translation completed: '{text}' -> '{translation}'")
#             return translation.strip()

#         except Exception as e:
#             logger.error(f"Error in translate method: {str(e)}")
#             return ""

#     def transliterate(self, text: str, source_script: str, target_script: str) -> str:
#         """Transliterate text between Latin and Arabic scripts for Darija"""
#         try:
#             model_name = "atlasia/Transliteration-Moroccan-Darija"
#             if model_name not in self.models:
#                 self.load_model(model_name)

#             logger.info(f"Transliterating from {source_script} to {target_script}")
#             result = self.pipelines[model_name](text, max_length=self.max_input_length)
#             transliterated = result[0]['generated_text']
            
#             logger.info(f"Transliteration completed: '{text}' -> '{transliterated}'")
#             return transliterated.strip()
#         except Exception as e:
#             logger.error(f"Error in transliterate method: {str(e)}")
#             return text

#     def select_model(self, source_lang: str, target_lang: str) -> str:
#         """Select appropriate model based on language pair"""
#         if source_lang.lower() == "english" and target_lang.lower() == "darija":
#             return "lachkarsalim/LatinDarija_English-v2"
#         elif source_lang.lower() == "darija" and target_lang.lower() == "english":
#             return "ychafiqui/darija-to-english-2"
#         else:
#             logger.warning(f"Unsupported language pair: {source_lang} to {target_lang}")
#             return MODEL_CONFIG["fallback_models"][1]  # Use the fallback model

# # Example usage
# if __name__ == "__main__":
#     service = TranslationService()
#     print(service.translate("Hello, how are you?", "English", "Darija"))
#     print(service.translate("كيف داير؟", "Darija", "English"))
#     print(service.transliterate("Kifash rak?", "Latin", "Arabic"))
"""
Enhanced Translation Service for English-Darija Bidirectional Translation
Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/ec2/translation-service/core/translation/translation_service_24_11_24_1432.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import gc
import logging
import os
import sys
from typing import Any, Dict, Optional, Tuple

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print(f"Python path: {sys.path}")
print(f"Python version: {sys.version}")

try:
    import torch
    from transformers import (
        AutoConfig,
        AutoModelForCausalLM,
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        M2M100ForConditionalGeneration,
    )
    print(f"PyTorch version: {torch.__version__}")
except ImportError as e:
    logger.error(f"Error importing required libraries: {str(e)}")
    logger.error(f"Python executable: {sys.executable}")
    logger.error(f"Python path: {sys.path}")
    raise

# Import configurations
from core.translation.model_config import MODEL_CONFIG


class TranslationService:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        self.model_paths: Dict[str, str] = MODEL_CONFIG["translation_models"]
        self.max_input_length: int = 512
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"TranslationService initialized on device: {self.device}")

        # Initialize supported models mapping
        self.supported_models = {
            "SI2M-Lab/DarijaBERT": {"family": "seq2seq", "direction": "both"},
            "hananeChab/darija_englishV2.1": {"family": "seq2seq", "direction": "both"},
            "Anassk/MoroccanDarija-Llama-3.1-8B": {"family": "llama", "direction": "both"},
            "centino00/darija-to-english": {"family": "seq2seq", "direction": "ar-en"},
            "lachkarsalim/LatinDarija_English-v2": {"family": "seq2seq", "direction": "both"},
            "ychafiqui/darija-to-english-2": {"family": "seq2seq", "direction": "ar-en"},
            "atlasia/Transliteration-Moroccan-Darija": {"family": "seq2seq", "direction": "both"},
            "Helsinki-NLP/opus-mt-ar-en": {"family": "marian", "direction": "ar-en"},
            "lachkarsalim/Helsinki-translation-English_Moroccan-Arabic": {"family": "seq2seq", "direction": "both"}
        }

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between English and Darija"""
        try:
            if not text:
                logger.warning("Empty text provided for translation")
                return ""

            model_name = self.select_model(source_lang, target_lang)
            logger.info(f"Starting translation with model: {model_name}")

            model, tokenizer = self.load_model(model_name)
            if not model or not tokenizer:
                return ""

            # Prepare input for tokenization
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=self.max_input_length)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model.generate(**inputs)
                
            translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info("Translation completed successfully")
            return translation.strip()

        except Exception as e:
            logger.error(f"Error in translate method: {str(e)}")
            return ""

    def select_model(self, source_lang: str, target_lang: str) -> str:
        """Select appropriate model based on language pair"""
        direction = "ar-en" if source_lang == "Darija" else "en-ar"
        
        for model_name, config in self.supported_models.items():
            if config["direction"] == "both" or config["direction"] == direction:
                logger.info(f"Selected model {model_name} for {source_lang} to {target_lang} translation")
                return model_name
                
        logger.warning(f"No suitable model found for {source_lang} to {target_lang}")
        return self.model_paths["default_model"]

    def load_model(self, model_name: str) -> Tuple[Optional[Any], Optional[Any]]:
        """Load and cache model with error handling"""
        try:
            if model_name not in self.models:
                logger.info(f"Loading model: {model_name}")
                
                model_info = self.supported_models[model_name]
                model_family = model_info["family"]
                
                # Get model-specific configurations
                generation_config = MODEL_CONFIG["generation_config"][model_family]
                load_config = MODEL_CONFIG["model_load_config"][model_family]

                # Select appropriate model class
                if model_family == "llama":
                    ModelClass = AutoModelForCausalLM
                elif model_family in ["mbart", "nllb"]:
                    ModelClass = M2M100ForConditionalGeneration
                else:
                    ModelClass = AutoModelForSeq2SeqLM

                # Load tokenizer and model
                tokenizer = AutoTokenizer.from_pretrained(model_name, **load_config)
                model = ModelClass.from_pretrained(model_name, **load_config).to(self.device)
                model.eval()

                self.models[model_name] = model
                self.tokenizers[model_name] = tokenizer
                
                logger.info(f"Successfully loaded model: {model_name}")
                
            return self.models[model_name], self.tokenizers[model_name]
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            return None, None

    def transliterate(self, text: str, source_script: str, target_script: str) -> str:
        """Transliterate text between Latin and Arabic scripts for Darija"""
        try:
            model_name = "atlasia/Transliteration-Moroccan-Darija"
            logger.info(f"Starting transliteration with model: {model_name}")
            
            model, tokenizer = self.load_model(model_name)
            if not model or not tokenizer:
                return text

            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=self.max_input_length)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model.generate(**inputs)
                
            transliteration = tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info("Transliteration completed successfully")
            return transliteration.strip()
            
        except Exception as e:
            logger.error(f"Error in transliterate method: {str(e)}")
            return text

    def cleanup(self):
        """Clean up resources and free memory"""
        try:
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Clear model caches
            self.models.clear()
            self.tokenizers.clear()
            
            # Run garbage collection
            gc.collect()
            
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

# Example usage
if __name__ == "__main__":
    service = TranslationService()
    try:
        print(service.translate("Hello, how are you?", "English", "Darija"))
        print(service.translate("كيف داير؟", "Darija", "English"))
        print(service.translate("Kifash rak?", "Latin Darija", "English"))
        print(service.transliterate("Kifash rak?", "Latin", "Arabic"))
    finally:
        service.cleanup()