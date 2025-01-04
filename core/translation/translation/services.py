"""Base translation service implementations"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseTranslationService(ABC):
    """Abstract base class for translation services"""
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language"""
        pass
    
    @abstractmethod
    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """Translate multiple texts from source language to target language"""
        pass

class UnifiedTranslationService(BaseTranslationService):
    """Base implementation of unified translation service"""
    
    def __init__(self):
        self.language_codes = {
            "english": "eng",
            "darija": "ary"
        }
        logger.info("UnifiedTranslationService initialized")
    
    def get_language_code(self, language: str) -> str:
        """Get standardized language code"""
        return self.language_codes.get(language.lower(), language.lower())
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Default implementation - should be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement translate method")
    
    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """Default batch translation implementation"""
        return [self.translate(text, source_lang, target_lang) for text in texts]
