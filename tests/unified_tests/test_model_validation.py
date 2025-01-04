import unittest
import os
import logging
from pathlib import Path
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestModelValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment and load configuration."""
        cls.config_path = Path("config/model_config.yaml")
        cls.cache_dir = Path("model_cache")
        cls.cache_dir.mkdir(exist_ok=True)
        
        # Load model configuration
        with open(cls.config_path) as f:
            cls.config = yaml.safe_load(f)
        
        # Set up test cases
        cls.test_cases = [
            ("Hello, how are you?", "English", "Darija"),
            ("Labas, kif nta?", "Darija", "English"),
            ("Labas, kifach nta?", "Latin Darija", "English")
        ]
        
        # Load HuggingFace token
        from config.credentials import HUGGINGFACE_TOKEN
        cls.token = HUGGINGFACE_TOKEN

    def test_config_structure(self):
        """Test if configuration file has correct structure."""
        self.assertIsInstance(self.config, dict)
        self.assertIn('translation_models', self.config)
        for model_name, model_info in self.config['translation_models'].items():
            self.assertIsInstance(model_info, dict)
            required_fields = ['model_family', 'direction', 'lang_codes']
            for field in required_fields:
                self.assertIn(field, model_info)

    def test_model_availability(self):
        """Test if all models are available and can be loaded."""
        for model_name in self.config['translation_models']:
            with self.subTest(model=model_name):
                try:
                    # Try loading model and tokenizer
                    model = AutoModelForSeq2SeqLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True
                    )
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    # Basic validation
                    self.assertIsNotNone(model)
                    self.assertIsNotNone(tokenizer)
                    
                    # Test model architecture
                    self.assertTrue(hasattr(model, 'generate'))
                    self.assertTrue(hasattr(tokenizer, 'batch_decode'))
                    
                except Exception as e:
                    self.fail(f"Failed to load model {model_name}: {str(e)}")

    def test_basic_translation(self):
        """Test basic translation functionality for each model."""
        for model_name in self.config['translation_models']:
            model_info = self.config['translation_models'][model_name]
            
            with self.subTest(model=model_name):
                try:
                    # Load model and tokenizer
                    model = AutoModelForSeq2SeqLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True
                    )
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    # Test translation
                    for text, source, target in self.test_cases:
                        # Skip if language pair doesn't match model capabilities
                        if not self._is_supported_language_pair(model_info, source, target):
                            continue
                            
                        # Perform translation
                        inputs = tokenizer(text, return_tensors="pt", padding=True)
                        outputs = model.generate(**inputs)
                        translation = tokenizer.batch_decode(
                            outputs,
                            skip_special_tokens=True,
                            clean_up_tokenization_spaces=True
                        )[0].strip()
                        
                        # Basic validation of translation
                        self.assertIsInstance(translation, str)
                        self.assertGreater(len(translation), 0)
                        logger.info(f"Model {model_name} translated '{text}' to '{translation}'")
                        
                except Exception as e:
                    self.fail(f"Translation failed for model {model_name}: {str(e)}")

    def test_model_caching(self):
        """Test if models can be properly cached and loaded from cache."""
        for model_name in self.config['translation_models']:
            with self.subTest(model=model_name):
                try:
                    # Save model to cache
                    cache_path = self.cache_dir / model_name.replace("/", "_")
                    if not cache_path.exists():
                        model = AutoModelForSeq2SeqLM.from_pretrained(
                            model_name,
                            torch_dtype=torch.float32,
                            low_cpu_mem_usage=True
                        )
                        tokenizer = AutoTokenizer.from_pretrained(model_name)
                        model.save_pretrained(str(cache_path))
                        tokenizer.save_pretrained(str(cache_path))
                    
                    # Try loading from cache
                    model = AutoModelForSeq2SeqLM.from_pretrained(str(cache_path))
                    tokenizer = AutoTokenizer.from_pretrained(str(cache_path))
