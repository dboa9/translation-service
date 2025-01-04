"""
Test translation using locally cached models
"""
import unittest
import logging
import os
import sys
from pathlib import Path
import torch
import gc
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('translation_cached_test.log')
    ]
)
logger = logging.getLogger(__name__)

class TestCachedModels(unittest.TestCase):
    """Test cases using locally cached models"""
    
    def setUp(self):
        """Set up test environment"""
        self.cache_dir = os.path.join(project_root, "dataset_cache")
        self.models = {
            "seamless": {
                "name": "AnasAber/seamless-darija-eng",
                "lang_codes": {"english": "eng", "darija": "ary"}
            }
        }
        
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
        
        # Load model
        model_name = self.models["seamless"]["name"]
        logger.info(f"Loading model {model_name} from cache...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                use_fast=True,
                model_max_length=128
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            )
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
            self.tokenizer = None
    
    def tearDown(self):
        """Clean up after test"""
        del self.model
        del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate text using cached model"""
        if self.model is None or self.tokenizer is None:
            self.skipTest("Model not loaded")
        
        try:
            # Get language code
            tgt_lang_code = "eng" if target_lang.lower() == "english" else "ary"
            
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128
            )
            
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=128,
                    num_beams=4,
                    temperature=0.7,
                    do_sample=False,
                    tgt_lang=tgt_lang_code
                )
            
            # Decode output
            translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            # Clear memory
            del inputs, outputs
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return None
    
    def test_translations(self):
        """Test translations in both directions"""
        test_cases = [
            ("Hello", "english", "darija"),
            ("Good morning", "english", "darija"),
            ("كيف حالك", "darija", "english"),
            ("صباح الخير", "darija", "english")
        ]
        
        for text, source_lang, target_lang in test_cases:
            logger.info(f"\nTranslating: '{text}' from {source_lang} to {target_lang}")
            translation = self.translate_text(text, source_lang, target_lang)
            
            self.assertIsNotNone(translation, f"Translation failed for '{text}'")
            if translation:
                logger.info(f"Translation: '{translation}'")
                self.assertNotEqual(translation, text)
            
            # Clear memory between translations
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()

if __name__ == "__main__":
    unittest.main(verbosity=2)
