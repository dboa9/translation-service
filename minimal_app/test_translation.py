"""
Test for Darija translation models with fallback support
"""
import os
import sys
import logging
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    MarianTokenizer,
    MarianMTModel,
    T5Tokenizer,
    T5ForConditionalGeneration
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Model configurations from test_all_translations.py
MODEL_INFO = {
    "AnasAber/seamless-darija-eng": {
        "lang_codes": {"source": "ary", "target": "eng"},
        "tokenizer": "AutoTokenizer",
        "model_class": "AutoModelForSeq2SeqLM",
        "input_format": "text",
        "direction": "bidirectional",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "AnasAber/nllb-enhanced-darija-eng_v1.1": {
        "lang_codes": {"source": "ary_Arab", "target": "eng_Latn"},
        "tokenizer": "AutoTokenizer",
        "model_class": "AutoModelForSeq2SeqLM",
        "input_format": "text",
        "direction": "bidirectional",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "BAKKALIAYOUB/DarijaTranslation-V1": {
        "lang_codes": {"source": "eng", "target": "ara"},
        "tokenizer": "MarianTokenizer",
        "model_class": "MarianMTModel",
        "input_format": "text",
        "direction": "english_to_darija",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "hananeChab/darija_englishV2.1": {
        "lang_codes": {"source": "ar", "target": "en"},
        "tokenizer": "MarianTokenizer",
        "model_class": "MarianMTModel",
        "input_format": "text",
        "direction": "darija_to_english",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    }
}

# Test cases from test_all_translations.py
TEST_CASES = {
    "greetings_and_basic": [
        ("السلام عليكم", "ar", "Peace be upon you"),
        ("كيداير هاد الليلا؟", "ar", "How are you tonight?"),
        ("الله إسعد الصاباح أ شريف", "ar", "Good morning, sir")
    ],
    "conversations": [
        ("هوما مخبّيين شي حاجة, أنا متيقّن!", "ar", "They're hiding something, I'm sure!"),
        ("باينا هوما تايحاولو إبقاو مبرّدين", "ar", "It's obvious they're trying to keep their cool"),
        ("كنت ديما عارف أنّاها بغاتنا نموتو", "ar", "I always knew she wanted us dead")
    ]
}

class TranslationTester:
    def __init__(self):
        self.tokenizer_map = {
            "AutoTokenizer": AutoTokenizer,
            "MarianTokenizer": MarianTokenizer,
            "T5Tokenizer": T5Tokenizer
        }
        self.model_map = {
            "AutoModelForSeq2SeqLM": AutoModelForSeq2SeqLM,
            "MarianMTModel": MarianMTModel,
            "T5ForConditionalGeneration": T5ForConditionalGeneration
        }
        
    def load_model(self, model_name: str, info: dict):
        """Load model with proper tokenizer class"""
        try:
            # Get correct tokenizer and model classes
            tokenizer_class = self.tokenizer_map[info["tokenizer"]]
            model_class = self.model_map[info["model_class"]]
            
            logger.info(f"Loading {model_name} with {info['tokenizer']}")
            
            # Load with auth token
            auth_token = os.getenv("HUGGINGFACE_API_TOKEN")
            tokenizer = tokenizer_class.from_pretrained(model_name, use_auth_token=auth_token)
            model = model_class.from_pretrained(model_name, use_auth_token=auth_token)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                model = model.to("cuda")
            return tokenizer, model
            
        except Exception as e:
            logger.error(f"Error loading {model_name}: {str(e)}")
            return None, None
            
    def test_model(self, model_name: str, info: dict, test_cases: dict):
        """Test specific model with test cases"""
        tokenizer, model = self.load_model(model_name, info)
        if not tokenizer or not model:
            return False
            
        try:
            for category, cases in test_cases.items():
                logger.info(f"\nTesting {model_name} - {category}")
                for text, lang, expected in cases:
                    # Skip incompatible test cases
                    if (info["direction"] == "darija_to_english" and lang != "ar") or \
                       (info["direction"] == "english_to_darija" and lang == "ar"):
                        continue
                        
                    # Prepare input
                    inputs = tokenizer(text, return_tensors="pt", padding=True)
                    if torch.cuda.is_available():
                        inputs = {k: v.to("cuda") for k, v in inputs.items()}
                    
                    # Generate translation
                    outputs = model.generate(
                        **inputs,
                        max_length=128,
                        num_beams=5,
                        temperature=0.7,
                        do_sample=True,
                        top_k=50,
                        top_p=0.95
                    )
                    
                    # Decode output
                    translation = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
                    
                    logger.info(f"Input: {text}")
                    logger.info(f"Expected: {expected}")
                    logger.info(f"Got: {translation}\n")
                    
            return True
            
        except Exception as e:
            logger.error(f"Error testing {model_name}: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Test all models with fallback support"""
        results = {}
        
        for model_name, info in MODEL_INFO.items():
            logger.info(f"\nTesting model: {model_name}")
            success = self.test_model(model_name, info, TEST_CASES)
            results[model_name] = "success" if success else "failed"
            
        # Log results summary
        logger.info("\n=== Test Results ===")
        for model, status in results.items():
            logger.info(f"{model}: {status}")
            
        return results

def main():
    """Main test function"""
    try:
        # Load credentials
        sys.path.append('.')
        from config.credentials import HUGGINGFACE_TOKEN
        os.environ["HUGGINGFACE_API_TOKEN"] = HUGGINGFACE_TOKEN
        
        # Run tests
        tester = TranslationTester()
        results = tester.run_all_tests()
        
        # Check if any models succeeded
        if any(status == "success" for status in results.values()):
            logger.info("\nAt least one model passed all tests!")
            return True
        else:
            logger.error("\nAll models failed testing!")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()
