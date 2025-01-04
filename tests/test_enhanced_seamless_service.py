import unittest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.translation.translation.enhanced_seamless_service import EnhancedSeamlessService

class TestEnhancedSeamlessService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = EnhancedSeamlessService()

    def test_english_to_darija(self):
        english_text = "Hello, how are you?"
        darija_translation = self.service.translate(english_text, "English", "Darija")
        self.assertIsNotNone(darija_translation)
        self.assertNotEqual(darija_translation, english_text)
        self.assertNotIn("Translation error", darija_translation)
        print(f"English to Darija: '{english_text}' -> '{darija_translation}'")

    def test_darija_to_english(self):
        darija_text = "كيف داير؟"
        english_translation = self.service.translate(darija_text, "Darija", "English")
        self.assertIsNotNone(english_translation)
        self.assertNotEqual(english_translation, darija_text)
        self.assertNotIn("Translation error", english_translation)
        print(f"Darija to English: '{darija_text}' -> '{english_translation}'")

    def test_invalid_language(self):
        text = "Hello"
        translation = self.service.translate(text, "English", "Invalid")
        self.assertIn("Translation error", translation)
        print(f"Invalid language test result: {translation}")

    def test_empty_text(self):
        translation = self.service.translate("", "English", "Darija")
        self.assertIn("Translation error", translation)
        print(f"Empty text test result: {translation}")

    def test_batch_translation(self):
        texts = ["Hello", "How are you?", "Good morning"]
        translations = self.service.batch_translate(texts, "English", "Darija")
        self.assertEqual(len(translations), len(texts))
        for original, translated in zip(texts, translations):
            self.assertNotEqual(original, translated)
            self.assertNotIn("Translation error", translated)
            print(f"Batch translation: '{original}' -> '{translated}'")

if __name__ == '__main__':
    unittest.main()
