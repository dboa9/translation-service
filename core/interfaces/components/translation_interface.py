"""
Translation interface component for the translation service
"""
from __future__ import annotations
import streamlit as st
from .base_interface import BaseInterface
import logging
import time
from pathlib import Path
import sys
from typing import Dict, Optional
import yaml

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.translation.translation_service import TranslationService

logger = logging.getLogger(__name__)

class TranslationInterface(BaseInterface):
    """Interface component for handling translations"""
    
    def __init__(self) -> None:
        """Initialize translation interface"""
        super().__init__()
        self.translation_service: TranslationService = TranslationService()
        self.source_text: str = ""
        self.translation_result: str = ""
        self.source_lang: str = "ary"  # Default to Darija
        self.target_lang: str = "eng"  # Default to English
        
        # Get supported languages from service
        self.supported_languages: Dict[str, str] = {
            "ary": "Darija",
            "ary_Latn": "Latin Darija",
            "eng": "English"
        }
    
    def render(self) -> None:
        """Render translation interface"""
        st.title("Translation Service")
        
        # Get selected model info
        selected_model = st.session_state.get('selected_model', '')
        model_info = self.translation_service.get_model_info(selected_model) if selected_model else {}
        
        # Get required language codes from model
        lang_codes = model_info.get("lang_codes", {})
        required_source = lang_codes.get("source", "")
        required_target = lang_codes.get("target", "")
        
        # Language selection
        col1, col2 = st.columns(2)
        with col1:
            # Filter source languages based on model requirements
            source_options = ["ary", "ary_Latn", "eng"]
            if required_source:
                source_options = [required_source]
            
            self.source_lang = st.selectbox(
                "Source Language",
                source_options,
                index=source_options.index(required_source) if required_source in source_options else 0,
                format_func=lambda x: self.supported_languages.get(x, x)
            )
        
        with col2:
            # Filter target languages based on model requirements
            target_options = ["eng", "ary"]
            if required_target:
                target_options = [required_target]
            
            self.target_lang = st.selectbox(
                "Target Language",
                target_options,
                index=target_options.index(required_target) if required_target in target_options else 0,
                format_func=lambda x: self.supported_languages.get(x, x)
            )
        
        # Show language requirements if any
        if required_source or required_target:
            st.info(
                f"This model requires:\n"
                f"- Source language: {self.supported_languages.get(required_source, required_source)}\n"
                f"- Target language: {self.supported_languages.get(required_target, required_target)}"
            )
        
        # Input text area
        self.source_text = st.text_area(
            "Enter text to translate",
            value=self.source_text,
            height=100,
            help="Enter the text you want to translate"
        )
        
        # Translation button
        if st.button("Translate"):
            self._perform_translation()
        
        # Display translation result
        if self.translation_result:
            st.subheader("Translation")
            st.write(self.translation_result)
    
    def update(self) -> None:
        """Update translation interface state"""
        if not self.initialized:
            self.initialize()
    
    def _setup(self) -> None:
        """Setup translation interface specific configurations"""
        try:
            # No initialization needed for TranslationService
            logger.info("Translation interface ready")
        except Exception as e:
            logger.error(f"Error setting up translation interface: {str(e)}")
            st.error("Failed to setup translation interface")
    
    def _perform_translation(self) -> None:
        """Perform translation and update interface"""
        if not self.source_text:
            st.warning("Please enter text to translate")
            return
        
        if not hasattr(st.session_state, 'selected_model') or not st.session_state.selected_model:
            st.warning("Please select a model first")
            return
            
        # Validate selected model
        config_path = Path("config/model_config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if not config or "translation_models" not in config:
                    st.error("Invalid model configuration")
                    return
                if st.session_state.selected_model not in config["translation_models"]:
                    st.error(f"Selected model '{st.session_state.selected_model}' not found in configuration")
                    return
        
        try:
            start_time = time.time()
            
            # Get the selected model
            selected_model = st.session_state.selected_model
            
            # Perform translation
            self.translation_result = self.translation_service.translate(
                text=self.source_text,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                model=selected_model
            )
            
            # Calculate time taken
            time_taken = time.time() - start_time
            
            # # Update monitoring
            # if hasattr(st.session_state, 'monitoring_interface'):
            #     st.session_state.monitoring_interface.add_translation_entry(
            #         source=self.source_text,
            #         translation=self.translation_result,
            #         model=selected_model,
            #         time_taken=time_taken,
            #         success=True
            #     )
            
            logger.info(f"Translation completed in {time_taken:.2f}s")
            
        except Exception as e:
            error_msg = f"Translation failed: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            
            # # Update monitoring with failed translation
            # if hasattr(st.session_state, 'monitoring_interface'):
            #     st.session_state.monitoring_interface.add_translation_entry(
            #         source=self.source_text,
            #         translation="",
            #         model=st.session_state.selected_model,
            #         time_taken=0.0,
            #         success=False
            #     )
