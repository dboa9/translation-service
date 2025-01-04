# File: tests/core/model_config.py

MODEL_CONFIG = {
    "translation_models": {
        "hananeChab/darija_englishV2.1": {
            "model_family": "marian",
            "direction": "both",
            "description": "Bidirectional Darija-English translation model (v2.1)",
            "use_case": ["translation"],
            "trusted": False,
            "requirements": ["transformers>=4.30.2", "torch>=2.0.0"]
        },
        "Anassk/MoroccanDarija-Llama-3.1-8B": {
            "model_family": "llama",
            "direction": "both",
            "description": "Llama-based Moroccan Darija model (3.1B parameters)",
            "use_case": ["translation", "generation"],
            "trusted": False,
            "requirements": ["transformers>=4.30.2", "torch>=2.0.0"]
        },
        "centino00/darija-to-english": {
            "model_family": "marian",
            "direction": "ar-en",
            "description": "Darija to English translation model",
            "use_case": ["translation"],
            "trusted": False,
            "requirements": ["transformers>=4.30.2"]
        },
        "lachkarsalim/LatinDarija_English-v2": {
            "model_family": "marian",
            "direction": "both",
            "description": "Latin Darija to English translation (v2)",
            "use_case": ["translation", "transliteration"],
            "trusted": False,
            "requirements": ["transformers>=4.30.2"]
        },
        "ychafiqui/darija-to-english-2": {
            "model_family": "nllb",
            "direction": "ar-en",
            "description": "Improved Darija to English translation model",
            "use_case": ["translation"],
            "trusted": True,  # This model works reliably
            "requirements": ["transformers>=4.30.2"]
        },
        "atlasia/Transliteration-Moroccan-Darija": {
            "model_family": "marian",
            "direction": "both",
            "description": "Moroccan Darija transliteration model",
            "use_case": ["transliteration"],
            "trusted": False,
            "requirements": ["transformers>=4.30.2"]
        },
        "Helsinki-NLP/opus-mt-ar-en": {
            "model_family": "marian",
            "direction": "ar-en",
            "description": "Helsinki NLP Arabic-English translation",
            "use_case": ["translation", "msa_support"],
            "trusted": True,  # This model works reliably
            "requirements": ["transformers>=4.30.2"]
        },
        "lachkarsalim/Helsinki-translation-English_Moroccan-Arabic": {
            "model_family": "marian",
            "direction": "en-ar",
            "description": "Helsinki NLP English to Moroccan Arabic",
            "use_case": ["translation", "msa_support"],
            "trusted": False,
            "requirements": ["transformers>=4.30.2"]
        }
    },
    "default_model": "Helsinki-NLP/opus-mt-ar-en",  # Most reliable default
    "fallback_models": [
        "Helsinki-NLP/opus-mt-ar-en",
        "ychafiqui/darija-to-english-2"
    ],
    "generation_config": {
        "marian": {
            "max_length": 128,
            "num_beams": 4,
            "early_stopping": True,
            "no_repeat_ngram_size": 3,
            "do_sample": False,
            "temperature": 1.0,
            "length_penalty": 1.0,
            "use_cache": True
        },
        "nllb": {
            "max_length": 128,
            "num_beams": 4,
            "early_stopping": True,
            "no_repeat_ngram_size": 3,
            "do_sample": False,
            "temperature": 1.0,
            "length_penalty": 1.0,
            "use_cache": True
        },
        "llama": {
            "max_length": 256,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "num_return_sequences": 1,
            "num_beams": 4,
            "early_stopping": True,
            "use_cache": True,
            "length_penalty": 1.0
        }
    },
    "model_load_config": {
        "marian": {
            "use_fast": False,
            "force_download": False,
            "local_files_only": False,
            "use_safetensors": True
        },
        "nllb": {
            "use_fast": False,
            "force_download": False,
            "local_files_only": False,
            "use_auth_token": False
        },
        "llama": {
            "use_fast": False,
            "force_download": False,
            "local_files_only": False,
            "load_in_8bit": False,
            "load_in_4bit": False,
            "use_safetensors": True
        }
    }
}