"""
Test single model translation to verify functionality
"""
import unittest
import logging
import os
import sys
from pathlib import Path
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSingleModel(unittest.TestCase):
    """Test cases for AnasAber seamless model"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.model_name = "AnasAber/seamless-darija-eng"
        print(f"\nLoading model {cls.model_name}...")
        
        try:
            cls.tokenizer = AutoTokenizer.from_pretrained(cls.model_name)
            cls.model = AutoModelForSeq2SeqLM.from_pretrained(cls.model_name)
            if torch.cuda.is_available():
                cls.model = cls.model.to("cuda")
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            cls.model = None
            cls.tokenizer = None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using the model"""
        if self.model is None or self.tokenizer is None:
            self.skipTest("Model not loaded")
        
        # Get language code
        tgt_lang_code = "eng" if target_lang.lower() == "english" else "ary"
        
        # Tokenize input
        inputs = self.tokenizer(text, return_tensors="pt", padding=True)
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        # Generate translation
        outputs = self.model.generate(
            **inputs,
            max_length=128,
            num_beams=5,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            tgt_lang=tgt_lang_code
        )
        
        # Decode output
        translation = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return translation
    
    def test_english_to_darija(self):
        """Test English to Darija translation"""
        test_cases = [
            "Hello, how are you?",
            "Good morning",
            "What's your name?"
        ]
        
        print("\nTesting English to Darija translations:")
        for text in test_cases:
            print(f"\nTranslating: '{text}'")
            translation = self.translate_text(text, "english", "darija")
            print(f"Translation: '{translation}'")
            
            self.assertIsNotNone(translation)
            self.assertNotEqual(translation, text)
    
    def test_darija_to_english(self):
        """Test Darija to English translation"""
        test_cases = [
            "كيف داير؟",
            "صباح الخير",
            "شنو سميتك؟"
        ]
        
        print("\nTesting Darija to English translations:")
        for text in test_cases:
            print(f"\nTranslating: '{text}'")
            translation = self.translate_text(text, "darija", "english")
            print(f"Translation: '{translation}'")
            
            self.assertIsNotNone(translation)
            self.assertNotEqual(translation, text)

if __name__ == "__main__":
    unittest.main(verbosity=2)
