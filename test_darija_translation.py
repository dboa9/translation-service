import unittest
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from core.translation.translation.enhanced_translation_service import TranslationService

class TestDarijaTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = TranslationService()

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

    def test_latin_darija_to_english(self):
        latin_darija_text = "Kifash rak?"
        english_translation = self.service.translate(latin_darija_text, "Darija", "English")
        self.assertIsNotNone(english_translation)
        self.assertNotEqual(english_translation, latin_darija_text)
        print(f"Latin Darija to English: '{latin_darija_text}' -> '{english_translation}'")

    def test_batch_translation(self):
        texts = ["Hello", "How are you?", "Good morning"]
        translations = self.service.batch_translate(texts, "English", "Darija")
        self.assertEqual(len(translations), len(texts))
        for original, translated in zip(texts, translations):
            self.assertNotEqual(original, translated)
            print(f"Batch translation: '{original}' -> '{translated}'")

if __name__ == '__main__':
    unittest.main()
