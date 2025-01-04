import unittest
from unittest.mock import patch, MagicMock
from core.interfaces.extended_web_interface import ExtendedTranslationService

class TestExtendedWebInterface(unittest.TestCase):
    def setUp(self):
        self.translation_service = ExtendedTranslationService()

    @patch('core.interfaces.model_loader.AutoTokenizer')
    @patch('core.interfaces.model_loader.AutoModelForSeq2SeqLM')
    def test_load_model(self, mock_model, mock_tokenizer):
        mock_model.from_pretrained.return_value = MagicMock()
        mock_tokenizer.from_pretrained.return_value = MagicMock()

        model, tokenizer = self.translation_service.model_loader.load_model("translation")

        self.assertIsNotNone(model)
        self.assertIsNotNone(tokenizer)
        mock_model.from_pretrained.assert_called_once()
        mock_tokenizer.from_pretrained.assert_called_once()

    @patch('core.interfaces.extended_web_interface.ExtendedTranslationService.translate')
    def test_translate(self, mock_translate):
        mock_translate.return_value = "Translated text"
        result = self.translation_service.translate("Hello", "English", "Darija")
        self.assertEqual(result, "Translated text")

    @patch('core.interfaces.extended_web_interface.ExtendedTranslationService.transliterate')
    def test_transliterate(self, mock_transliterate):
        mock_transliterate.return_value = "Transliterated text"
        result = self.translation_service.transliterate("مرحبا")
        self.assertEqual(result, "Transliterated text")

if __name__ == '__main__':
    unittest.main()
