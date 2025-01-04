"""
Tests for translation service setup and configuration
"""
import unittest
import logging
import torch
from pathlib import Path
import yaml
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from core.translation.translation_service import TranslationService

# Load model configuration
CONFIG_PATH = project_root / "config" / "model_config.yaml"
with open(CONFIG_PATH) as f:
    MODEL_CONFIG = yaml.safe_load(f)

class TestTranslationServiceSetup(unittest.TestCase):
    """Test cases for translation service setup"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        logging.info("Testing CUDA availability")
        if not torch.cuda.is_available():
            logging.warning("No CUDA devices found, using CPU")
        cls.service = TranslationService()
        
    def test_imports(self):
        """Test required imports"""
        self.assertIsNotNone(torch)
        self.assertIsNotNone(yaml)
        
    def test_model_configurations(self):
        """Test all model configurations are properly defined"""
        for model_name in [
            "AnasAber/seamless-darija-eng",
            "Anassk/MoroccanDarija-Llama-3.1-8B",
            "hananeChab/darija_englishV2.1"
        ]:
            self.assertIn(
                model_name,
                MODEL_CONFIG["translation_models"],
                f"Missing configuration for {model_name}"
            )
            
    def test_language_codes(self):
        """Test language code configurations"""
        codes = MODEL_CONFIG.get("language_codes", {})
        self.assertIsNotNone(codes)
        self.assertIn("darija", codes)
        self.assertIn("english", codes)
        
    def test_model_loading_validation(self):
        """Test model loading configurations"""
        for model_family in ["marian", "nllb", "llama", "seamless", "bert"]:
            self.assertIn(
                model_family,
                MODEL_CONFIG["model_load_config"]
            )
            
    def test_generation_configs(self):
        """Test generation configurations for each model family"""
        for model_family in ["marian", "nllb", "llama", "seamless", "bert"]:
            self.assertIn(
                model_family,
                MODEL_CONFIG["generation_config"]
            )
            
    def test_service_initialization(self):
        """Test service initialization and model paths"""
        self.assertIsInstance(self.service, TranslationService)
        
        # Test model paths
        for model_name, path in {
            "AnasAber/seamless-darija-eng": "AnasAber/seamless-darija-eng",
            "Anassk/MoroccanDarija-Llama-3.1-8B": "Anassk/MoroccanDarija-Llama-3.1-8B",
            "hananeChab/darija_englishV2.1": "hananeChab/darija_englishV2.1"
        }.items():
            self.assertEqual(self.service.model_paths[model_name], path)
            
    def test_fallback_configuration(self):
        """Test fallback model configuration"""
        self.assertIsNotNone(MODEL_CONFIG.get("fallback_models"))
        self.assertIn("darija_to_english", MODEL_CONFIG["fallback_models"])
        self.assertIn("english_to_darija", MODEL_CONFIG["fallback_models"])
        
    def test_device_handling(self):
        """Test device handling for models"""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Compare string representation to handle both string and device type
        self.assertEqual(str(self.service.device), str(device))

if __name__ == "__main__":
    unittest.main()
