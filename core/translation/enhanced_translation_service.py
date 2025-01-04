"""Enhanced translation service that extends the base service.
IMPORTANT: This file extends the existing functionality without modifying working files.
DO NOT modify this file directly - create a new extension if changes are needed.
"""

import logging
from typing import Optional

from .translation_service import TranslationService as BaseTranslationService

logger = logging.getLogger(__name__)


class EnhancedTranslationService(BaseTranslationService):
    """Enhanced translation service that ensures compatibility with all interfaces.
    Extends the base TranslationService without modifying it.
    """

    def __init__(self):
        """Initialize the enhanced translation service."""
        super().__init__()
        logger.info("Enhanced translation service initialized")

    def translate(
        self, text: str, source_lang: str, target_lang: str, model: str
    ) -> Optional[str]:
        """Enhanced translate method that ensures model parameter is handled correctly.

        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
            model: Model to use for translation

        Returns:
            Translated text or None if translation fails

        """
        try:
            # Call parent's translate method with all parameters
            return super().translate(
                text=text, source_lang=source_lang, target_lang=target_lang, model=model
            )
        except TypeError as e:
            if "unexpected keyword argument 'model'" in str(e):
                # If parent doesn't accept model parameter, try without it
                logger.warning(
                    "Parent translate method doesn't accept model parameter, trying without it"
                )
                return super().translate(
                    text=text, source_lang=source_lang, target_lang=target_lang
                )
            raise
