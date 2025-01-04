# File: tests/test_translation_service.py
"""
Translation Service Tests
Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/tests/test_translation_service.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import torch

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.translation.translation_service import TranslationService
from core.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

class TestTranslationService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.service = TranslationService()
        cls.test_model = "Helsinki-NLP/opus-mt-ar-en"  # Using reliable model for tests
        cls.test_text = "Hello, world!"
        logger.info("Test environment initialized")

    def setUp(self):
        """Set up each test"""
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

    def test_init(self):
        """Test initialization"""
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.model_paths)
        self.assertIsNotNone(self.service.default_model)
        logger.info("Initialization test passed")

    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModelForSeq2SeqLM.from_pretrained')
    def test_load_model(self, mock_model, mock_tokenizer):
        """Test model loading"""
        mock_model.return_value = MagicMock()
        mock_tokenizer.return_value = MagicMock()

        model, tokenizer = self.service.load_model(self.test_model)
        
        self.assertIsNotNone(model)
        self.assertIsNotNone(tokenizer)
        mock_model.from_pretrained.assert_called_once()
        mock_tokenizer.from_pretrained.assert_called_once()
        logger.info("Model loading test passed")

    def test_get_language_codes(self):
        """Test language code handling"""
        src_code, tgt_code = self.service.get_language_codes(
            self.test_model, "English", "Darija"
        )
        self.assertEqual(src_code, "en")
        self.assertEqual(tgt_code, "ar")
        logger.info("Language code test passed")

    @patch.object(TranslationService, 'load_model')
    def test_translate(self, mock_load_model):
        """Test translation"""
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load_model.return_value = (mock_model, mock_tokenizer)

        # Mock tokenizer behavior
        mock_tokenizer.return_value = {'input_ids': torch.tensor([[1, 2, 3]])}
        mock_model.generate.return_value = torch.tensor([[4, 5, 6]])
        mock_tokenizer.decode.return_value = "Translated text"

        result = self.service.translate(
            self.test_text, "English", "Darija", self.test_model
        )

        self.assertEqual(result, "Translated text")
        mock_load_model.assert_called_once_with(self.test_model)
        logger.info("Translation test passed")

    def test_get_supported_models(self):
        """Test model listing"""
        models = self.service.get_supported_models()
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0)
        self.assertIn("name", models[0])
        self.assertIn("family", models[0])
        logger.info("Model listing test passed")

    def test_error_handling(self):
        """Test error handling"""
        result = self.service.translate("", "English", "Darija", self.test_model)
        self.assertIsNone(result)
        logger.info("Error handling test passed")

    def test_memory_cleanup(self):
        """Test memory management"""
        initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        self.service._cleanup_memory()
        final_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        self.assertLessEqual(final_memory, initial_memory)
        logger.info("Memory cleanup test passed")

    def tearDown(self):
        """Clean up after each test"""
        self.service._cleanup_memory()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("Test environment cleaned up")

if __name__ == '__main__':
    unittest.main()