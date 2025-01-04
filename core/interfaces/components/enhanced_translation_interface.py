"""
Enhanced translation interface using the enhanced unified translation service
"""
import streamlit as st
import logging
from typing import Dict, Optional
from core.translation.translation.enhanced_unified_translation_service import (
    EnhancedUnifiedTranslationService,
    MODEL_LANGUAGE_CODES
)

logger = logging.getLogger(__name__)

class EnhancedTranslationInterface:
    """Enhanced translation interface component"""

    def __init__(self):
        """Initialize interface"""
        self.service = EnhancedUnifiedTranslationService()
        self.available_models = self.service.get_available_models()
        self.language_codes = MODEL_LANGUAGE_CODES

    def render(self):
        """Render the translation interface"""
        st.title("Enhanced Darija Translation Service")

        # Model selection
        selected_model = st.selectbox(
            "Select Translation Model",
            options=self.available_models,
            index=0,
            help="Choose which model to use for translation"
        )

        # Get language codes for selected model
        model_langs = self.language_codes.get(selected_model, {})

        # Create two columns for source and target
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Source Text")
            source_lang = st.selectbox(
                "Source Language",
                options=["english", "darija"],
                key="source_lang"
            )
            source_text = st.text_area(
                "Enter text to translate",
                height=200,
                key="source_text"
            )

        with col2:
            st.subheader("Translation")
            target_lang = "darija" if source_lang == "english" else "english"
            st.info(f"Target Language: {target_lang}")

            if source_text:
                try:
                    # Show normalized language codes
                    source_code = self.service._normalize_language_code(source_lang, selected_model)
                    target_code = self.service._normalize_language_code(target_lang, selected_model)
                    st.caption(
                        f"Using language codes: {source_code} -> {target_code}"
                    )

                    # Perform translation
                    translation = self.service.translate(
                        source_text,
                        source_lang,
                        target_lang,
                        selected_model
                    )

                    # Display translation
                    st.text_area(
                        "Translation",
                        value=translation,
                        height=200,
                        key="translation_output",
                        disabled=True
                    )

                except Exception as e:
                    st.error(f"Translation error: {str(e)}")
                    logger.error(f"Translation failed: {str(e)}")

        # Model Information
        with st.expander("Model Information"):
            st.markdown(f"""
            **Selected Model**: {selected_model}

            **Language Code Mappings**:
            ```python
            {model_langs}
            ```
            """)

        # Translation History
        if "translation_history" not in st.session_state:
            st.session_state.translation_history = []

        if source_text and "translation_output" in st.session_state:
            history_entry = {
                "model": selected_model,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "source_text": source_text,
                "translation": st.session_state.translation_output
            }
            st.session_state.translation_history.append(history_entry)

        # Show translation history
        with st.expander("Translation History"):
            for idx, entry in enumerate(reversed(st.session_state.translation_history[-10:])):
                st.markdown(f"""
                **Translation {idx + 1}**
                - Model: {entry['model']}
                - {entry['source_lang'].title()} -> {entry['target_lang'].title()}
                - Source: {entry['source_text']}
                - Translation: {entry['translation']}
                ---
                """)

    def update(self):
        """Update interface state"""
        pass
