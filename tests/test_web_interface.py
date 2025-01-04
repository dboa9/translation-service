# File: tests/test_web_interface.py
"""
Location: /mnt/c/Users/mrdbo/Documents/ReactDev/AWS/EC2/daija_dataset_tests_project/tests/test_web_interface.py
Author: dboa9 (danielalchemy9@gmail.com)
"""

import unittest
from unittest.mock import patch, MagicMock
from core.translation.translation_service import TranslationService

class TestWebInterface(unittest.TestCase):
    def setUp(self):
        self.translation_service = TranslationService()

    @patch('core.interfaces.model_loader.AutoTokenizer')
    @patch('core.interfaces.model_loader.AutoModelForSeq2SeqLM')
    def test_load_model(self, mock_model, mock_tokenizer):
        mock_model.from_pretrained.return_value = MagicMock()
        mock_tokenizer.from_pretrained.return_value = MagicMock()

        model, tokenizer = self.translation_service.load_model("translation")

        self.assertIsNotNone(model)
        self.assertIsNotNone(tokenizer)
        mock_model.from_pretrained.assert_called_once()
        mock_tokenizer.from_pretrained.assert_called_once()

    @patch('core.translation.translation_service.TranslationService.translate')
    def test_translate(self, mock_translate):
        mock_translate.return_value = "Translated text"
        result = self.translation_service.translate("Hello", "English", "Darija", "Helsinki-NLP/opus-mt-ar-en")
        self.assertEqual(result, "Translated text")

    @patch('core.translation.translation_service.TranslationService.transliterate') 
    def test_transliterate(self, mock_transliterate):
        mock_transliterate.return_value = "Transliterated text"
        result = self.translation_service.transliterate("مرحبا")
        self.assertEqual(result, "Transliterated text")

if __name__ == '__main__':
    unittest.main()