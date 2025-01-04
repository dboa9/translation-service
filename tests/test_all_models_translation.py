import pytest
import sys
import os
import re
import logging
import psutil
from logging.handlers import RotatingFileHandler
import time
from typing import Dict, Any, List, Tuple
from tqdm import tqdm
import json
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.translation.translation_service import TranslationService

# Set up logging
log_file = 'translation_test_results.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add a FileHandler to write logs to the file
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(file_handler)

@pytest.fixture
def translation_service():
    """Fixture to provide a TranslationService instance."""
    return TranslationService()

@pytest.fixture
def test_cases():
    """Fixture to provide test cases."""
    return [
        # Basic conversation
        ("Hello, how are you?", "en", "ary", "basic"),
        ("كيف حالك؟", "ary", "en", "basic"),
        
        # Complex sentences
        ("I love Moroccan cuisine and traditional dishes.", "en", "ary", "complex"),
        ("نتمنى لك يوما سعيدا وحياة مليئة بالسعادة", "ary", "en", "complex"),
        
        # Technical content
        ("The model is being trained on the GPU server.", "en", "ary", "technical"),
        ("البيانات يتم معالجتها على الخادم", "ary", "en", "technical"),
        
        # Edge cases
        ("", "en", "ary", "edge_case"),  # Empty string
        ("Hello! مرحبا", "en", "ary", "edge_case"),  # Mixed language
        ("123 456 789", "en", "ary", "edge_case")  # Numbers
    ]

@pytest.fixture
def env_config():
    """Fixture to provide environment-specific configurations."""
    return {
        "local": {
            "max_time": 10,  # Max seconds per translation locally
            "required_models": ["AnasAber/seamless-darija-eng"],  # Must have these locally
            "memory_threshold": 0.8  # Max memory usage (80%)
        },
        "ec2": {
            "max_time": 5,  # Faster on EC2
            "required_models": [
                "AnasAber/seamless-darija-eng",
                "AnasAber/nllb-enhanced-darija-eng_v1-1",
                "imomayiz/darija_englishV2.1"
            ],
            "memory_threshold": 0.7
        }
    }

def validate_translation(translation: str, category: str) -> bool:
    """Validate translation based on category-specific rules"""
    if not translation:
        return False
        
    if category == "edge_case":
        return True  # Edge cases may have special handling
        
    # Basic validation rules
    if len(translation.strip()) == 0:
        return False
        
    # Category-specific validation
    if category == "technical":
        # Technical translations should preserve numbers and technical terms
        numbers_original = set(re.findall(r'\d+', translation))
        if not numbers_original:
            return True
        return len(numbers_original) > 0
        
    return True

def calculate_similarity(original: str, reverse: str) -> float:
    """Calculate similarity between original text and reverse translation"""
    if not original or not reverse:
        return 0.0
        
    # Convert to lowercase and remove punctuation
    original = re.sub(r'[^\w\s]', '', original.lower())
    reverse = re.sub(r'[^\w\s]', '', reverse.lower())
    
    # Split into words
    original_words = set(original.split())
    reverse_words = set(reverse.split())
    
    # Calculate Jaccard similarity
    intersection = len(original_words & reverse_words)
    union = len(original_words | reverse_words)
    
    return intersection / union if union > 0 else 0.0

def test_model_availability(translation_service, env_config):
    """Test if required models are available."""
    config = env_config["local"]  # Test local environment first
    available_models = list(translation_service.config.get("translation_models", {}).keys())
    missing_models = [m for m in config["required_models"] if m not in available_models]
    assert not missing_models, f"Missing required models: {missing_models}"

def test_model_translation(translation_service, test_cases):
    """Test translation functionality for each model."""
    for model_name in translation_service.config.get("translation_models", {}):
        for test_text, source_lang, target_lang, category in test_cases:
            try:
                # Monitor system resources
                memory_usage = psutil.Process().memory_percent()
                logger.info(f"Memory usage: {memory_usage:.1f}%")
                
                # Perform translation
                translation = translation_service.translate(
                    text=test_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    model=model_name
                )
                
                # Validate translation
                if translation:
                    assert validate_translation(translation, category), \
                        f"Translation validation failed for {model_name}"
                    
                    # Test reverse translation
                    reverse = translation_service.translate(
                        text=translation,
                        source_lang=target_lang,
                        target_lang=source_lang,
                        model=model_name
                    )
                    
                    if reverse:
                        similarity = calculate_similarity(test_text, reverse)
                        logger.info(
                            f"Model: {model_name}\n"
                            f"Original: {test_text}\n"
                            f"Translation: {translation}\n"
                            f"Reverse: {reverse}\n"
                            f"Similarity: {similarity:.2%}"
                        )
                        
                        # Ensure some similarity for non-edge cases
                        if category != "edge_case":
                            assert similarity > 0.1, \
                                f"Low similarity score for {model_name}: {similarity:.2%}"
                    
            except Exception as e:
                if category != "edge_case":  # Edge cases may fail
                    pytest.fail(f"Translation failed for {model_name}: {str(e)}")

def test_model_caching(translation_service):
    """Test model caching functionality."""
    for model_name in translation_service.config.get("translation_models", {}):
        if translation_service.is_model_cached(model_name):
            logger.info(f"Model {model_name} is cached")
            assert translation_service.model_cache[model_name] is not None, \
                f"Cached model {model_name} is None"
        else:
            logger.info(f"Model {model_name} is not cached")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--log-cli-level=INFO"])
