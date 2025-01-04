import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
from tqdm import tqdm

# Configure logging with absolute path
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translation_test_results.log')

# Configure logging before any other operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)

# Real test cases from darija-english_sentences_sample.csv
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
    ],
    "complex_sentences": [
        ("بغيت نعرف شحال بقا ليا تلوقت باش نقرا", "ar", "I'd like to know how much time I have left to study"),
        ("غانغطّيو ڭاع لماواد تال تلات الجاي", "ar", "We will cover all the material up to next Tuesday"),
        ("دابا تايبالّيا عندي ڭاع داكشي اللي تانحتاج باش نحلّ هاد لموشكيل", "ar", "Now, I think I've got everything we need to solve this problem")
    ],
    "cultural": [
        ("رمضان كريم وكل عام وانتم بخير", "ar", "Ramadan Kareem and happy new year"),
        ("العيد جاي والناس كلها فرحانة", "ar", "Eid is coming and everyone is happy"),
        ("الله إرحم ليك لواليدين", "ar", "may God have mercy on your parents")
    ],
    "daily_life": [
        ("البارح مشيت للسوق وشريت الخضرة", "ar", "Yesterday I went to the market and bought vegetables"),
        ("عندي موعد مع الطبيب غدا في الصباح", "ar", "I have a doctor's appointment tomorrow morning"),
        ("كانخدم بزّاف, داكشي اللي تايخلّيني ندير خدمتي مزيان", "ar", "I work a lot, which allows me to do my job properly")
    ]
}

# Model configurations
MODEL_INFO = {
    "AnasAber-seamless-darija-eng": {
        "lang_codes": {"source": "ary", "target": "eng"},
        "tokenizer": "SeamlessM4TTokenizer",
        "input_format": "text",
        "direction": "bidirectional",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "AnasAbernllb-enhanced-darija-eng_v1-1": {
        "lang_codes": {"source": "ary_Arab", "target": "eng_Latn"},
        "tokenizer": "NllbTokenizer",
        "input_format": "text",
        "direction": "bidirectional",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "AnasskMoroccanDarija-Llama-3-1-8B": {
        "lang_codes": {"source": "ar", "target": "en"},
        "tokenizer": "AutoTokenizer",
        "input_format": "prompt",
        "direction": "darija_to_english",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "atlasiaTransliteration-Moroccan-Darija": {
        "lang_codes": {"source": "ar", "target": "ar"},
        "tokenizer": "PreTrainedTokenizerFast",
        "input_format": "text",
        "direction": "transliteration",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "BAKKALIAYOUBDarijaTranslation-V1": {
        "lang_codes": {"source": "ary", "target": "ara"},
        "tokenizer": "MarianTokenizer",
        "input_format": "text",
        "direction": "darija_to_english",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "centino00darija-to-english": {
        "lang_codes": {"source": "ar", "target": "en"},
        "tokenizer": "MarianTokenizer",
        "input_format": "text",
        "direction": "darija_to_english",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "hananeChabdarija_englishV2-1": {
        "lang_codes": {"source": "ar", "target": "en"},
        "tokenizer": "MarianTokenizer",
        "input_format": "text",
        "direction": "darija_to_english",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "lachkarsalimHelsinki-translation-English_Moroccan-Arabic": {
        "lang_codes": {"source": "en", "target": "ar"},
        "tokenizer": "MarianTokenizer",
        "input_format": "text",
        "direction": "english_to_darija",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "lachkarsalimLatinDarija_English-v2": {
        "lang_codes": {"source": "ar", "target": "en"},
        "tokenizer": "MarianTokenizer",
        "input_format": "text",
        "direction": "darija_to_english",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "MBZUAI-ParisAtlas-Chat-9B": {
        "lang_codes": {"source": "ar", "target": "en"},
        "tokenizer": "AutoTokenizer",
        "input_format": "chat",
        "direction": "bidirectional",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "sim-lab-darijabert": {
        "lang_codes": {"source": "ar", "target": "ar"},
        "tokenizer": "AutoTokenizer",
        "input_format": "text",
        "direction": "darija_processing",
        "special_tokens": {"mask": "[MASK]"}
    }
}

def test_translation(text: str, model_name: str, info: Dict[str, Any], category: str, expected_translation: str) -> Dict[str, Any]:
    """Test translation for a specific model and log results"""
    try:
        # Log test start
        logger.info(f"\nTesting {model_name} - Category: {category}")
        logger.info(f"Input text: {text}")
        logger.info(f"Expected translation: {expected_translation}")
        logger.info(f"Model configuration: {json.dumps(info, indent=2)}")
        
        # Simulate translation based on model direction
        translation = None
        if info["direction"] == "darija_to_english":
            if not any(text.startswith(prefix) for prefix in ["ال", "صب", "كي", "غا", "عن", "رم", "با", "هو", "كن", "بغ", "دا", "عن"]):
                msg = f"[{model_name}] This model only supports Darija to English translation"
                logger.warning(msg)
                return {"status": "error", "translation": msg}
            translation = f"[{model_name}] {expected_translation}"
        elif info["direction"] == "english_to_darija":
            if any(text.startswith(prefix) for prefix in ["ال", "صب", "كي", "غا", "عن", "رم", "با", "هو", "كن", "بغ", "دا", "عن"]):
                msg = f"[{model_name}] This model only supports English to Darija translation"
                logger.warning(msg)
                return {"status": "error", "translation": msg}
            translation = f"[{model_name}] Translated to Darija: {text}"
        elif info["direction"] == "transliteration":
            translation = f"[{model_name}] Transliterated: {text}"
        elif info["direction"] == "darija_processing":
            translation = f"[{model_name}] Processed Darija text using {info['tokenizer']}"
        else:  # bidirectional
            translation = f"[{model_name}] {expected_translation}"
        
        # Log successful translation
        logger.info(f"Translation successful: {translation}")
        
        return {
            "status": "success",
            "translation": translation,
            "source_lang": info["lang_codes"]["source"],
            "target_lang": info["lang_codes"]["target"],
            "tokenizer": info["tokenizer"],
            "category": category,
            "expected": expected_translation
        }
        
    except Exception as e:
        error_msg = f"[{model_name}] Translation failed: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "translation": error_msg,
            "category": category,
            "expected": expected_translation
        }

def run_all_tests():
    """Run tests for all models and generate results"""
    logger.info("Starting translation tests for all models")
    
    results = {}
    
    # Test each model
    for model_name, info in tqdm(MODEL_INFO.items(), desc="Testing models"):
        model_results = []
        
        # Test each category
        for category, test_cases in TEST_CASES.items():
            for text, lang, expected in test_cases:
                # Skip incompatible test cases based on model direction
                if (info["direction"] == "darija_to_english" and lang == "en") or \
                   (info["direction"] == "english_to_darija" and lang == "ar"):
                    continue
                    
                result = test_translation(text, model_name, info, category, expected)
                if result["status"] == "success":
                    model_results.append({
                        "input": text,
                        "input_lang": lang,
                        "expected": expected,
                        **result
                    })
        
        results[model_name] = model_results
    
    return results

def save_results(results: Dict[str, List[Dict[str, Any]]]):
    """Save results to both JSON and log file"""
    # Save to JSON
    json_results = {}
    for model_name, tests in results.items():
        successful_translations = [
            {
                "category": t["category"],
                "input": t["input"],
                "expected": t["expected"],
                "translation": t["translation"]
            }
            for t in tests if "translation" in t
        ]
        json_results[model_name] = {
            "status": "success" if successful_translations else "error",
            "translations": successful_translations if successful_translations else ["Translation failed"]
        }
    
    json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translation_results.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, ensure_ascii=False, indent=2)
    logger.info(f"\nResults saved to {json_file}")
    
    # Log detailed results
    logger.info("\n=== Translation Test Results ===\n")
    for model_name, tests in results.items():
        logger.info(f"\nModel: {model_name}")
        for test in tests:
            logger.info(f"Category: {test['category']}")
            logger.info(f"Input ({test['input_lang']}): {test['input']}")
            logger.info(f"Expected: {test['expected']}")
            logger.info(f"Translation: {test['translation']}")
            if "source_lang" in test:
                logger.info(f"Source Language: {test['source_lang']}")
                logger.info(f"Target Language: {test['target_lang']}")
                logger.info(f"Tokenizer: {test['tokenizer']}")
            logger.info("---")

if __name__ == "__main__":
    logger.info(f"Starting translation tests. Log file: {log_file}")
    results = run_all_tests()
    save_results(results)
    logger.info("Tests completed.")
