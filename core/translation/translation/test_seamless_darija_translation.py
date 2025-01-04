import unittest
import sys
import os

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from core.translation.translation.seamless_darija_translation_service import SeamlessDarijaTranslationService

class TestSeamlessDarijaTranslationService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = SeamlessDarijaTranslationService()

    def test_english_to_darija(self):
        english_text = "Hello, how are you?"
        darija_translation = self.service.translate(english_text, "English", "Darija")
        self.assertIsNotNone(darija_translation)
        self.assertNotEqual(darija_translation, english_text)
        print(f"English to Darija: '{english_text}' -> '{darija_translation}'")

    def test_darija_to_english(self):
        darija_text = "كيف داير؟"
        english_translation = self.service.translate(darija_text, "Darija", "English")
        self.assertIsNotNone(english_translation)
        self.assertNotEqual(english_translation, darija_text)
        print(f"Darija to English: '{darija_text}' -> '{english_translation}'")

    def test_batch_translation(self):
        texts = ["Hello", "How are you?", "Good morning"]
        translations = self.service.batch_translate(texts, "English", "Darija")
        self.assertEqual(len(translations), len(texts))
        for original, translated in zip(texts, translations):
            self.assertNotEqual(original, translated)
            print(f"Batch translation: '{original}' -> '{translated}'")

    def test_unknown_phrase_translation(self):
        unknown_text = "This is an unknown phrase"
        translation = self.service.translate(unknown_text, "English", "Darija")
        self.assertIsNotNone(translation)
        self.assertNotEqual(translation, unknown_text)
        print(f"Unknown phrase translation: '{unknown_text}' -> '{translation}'")

if __name__ == '__main__':
    unittest.main()
