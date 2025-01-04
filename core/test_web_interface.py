import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tests.core.web_interface import TranslationService, main, MODEL_CONFIG

class TestWebInterface(unittest.TestCase):
    def setUp(self):
        self.translation_service = TranslationService()

    @patch('tests.core.web_interface.AutoTokenizer')
    @patch('tests.core.web_interface.AutoModelForSeq2SeqLM')
    def test_load_model(self, mock_model, mock_tokenizer):
        mock_model.from_pretrained.return_value = MagicMock()
        mock_tokenizer.from_pretrained.return_value = MagicMock()

        model_name = next(iter(MODEL_CONFIG["translation_models"]))
        model, tokenizer = self.translation_service.load_model(model_name)

        self.assertIsNotNone(model)
        self.assertIsNotNone(tokenizer)
        mock_model.from_pretrained.assert_called_once_with(model_name)
        mock_tokenizer.from_pretrained.assert_called_once_with(model_name)

    @patch.object(TranslationService, 'load_model')
    def test_translate(self, mock_load_model):
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load_model.return_value = (mock_model, mock_tokenizer)

        mock_tokenizer.return_value = {'input_ids': MagicMock()}
        mock_model.generate.return_value = [MagicMock()]
        mock_tokenizer.decode.return_value = "Translated text"

        model_name = next(iter(MODEL_CONFIG["translation_models"]))
        result = self.translation_service.translate("Hello", "English", "Darija", model_name)

        self.assertEqual(result, "Translated text")
        mock_load_model.assert_called_once_with(model_name)

    @patch.object(TranslationService, 'load_model')
    def test_transliterate(self, mock_load_model):
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load_model.return_value = (mock_model, mock_tokenizer)

        mock_tokenizer.return_value = {'input_ids': MagicMock()}
        mock_model.generate.return_value = [MagicMock()]
        mock_tokenizer.decode.return_value = "Transliterated text"

        model_name = next(model for model, config in MODEL_CONFIG["translation_models"].items() if "transliteration" in config["use_case"])
        result = self.translation_service.transliterate("مرحبا", model_name)

        self.assertEqual(result, "Transliterated text")
        mock_load_model.assert_called_once_with(model_name)

    @patch('tests.core.web_interface.st')
    def test_main_function(self, mock_st):
        # Mock Streamlit functions
        mock_st.set_page_config = MagicMock()
        mock_st.title = MagicMock()
        mock_st.selectbox.return_value = next(iter(MODEL_CONFIG["translation_models"]))
        mock_st.radio.return_value = "English"
        mock_st.text_area.return_value = "Hello"
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = True
        mock_st.spinner = MagicMock()
        mock_st.success = MagicMock()
        mock_st.markdown = MagicMock()

        # Mock TranslationService
        with patch.object(TranslationService, 'translate', return_value="Bonjour"):
            main()

        # Check if Streamlit functions were called
        mock_st.set_page_config.assert_called_once()
        mock_st.title.assert_called_once()
        mock_st.selectbox.assert_called_once()
        mock_st.radio.assert_called_once()
        mock_st.text_area.assert_called_once()
        mock_st.columns.assert_called_once_with(2)
        mock_st.button.assert_called()
        mock_st.success.assert_called_once_with("Translation complete!")
        
        # Check that markdown was called with both the translation result and the footer
        mock_st.markdown.assert_has_calls([
            call("**Bonjour**"),
            call(unittest.mock.ANY, unsafe_allow_html=True)
        ], any_order=True)

if __name__ == '__main__':
    unittest.main()
