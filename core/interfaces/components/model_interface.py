"""
Model interface component for model selection and configuration
"""
import streamlit as st
import logging
from core.translation.translation_service import TranslationService
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelInterface:
    """Interface component for model management"""

    def __init__(self):
        """Initialize interface"""
        self.service = TranslationService()
        self.available_models = self._load_available_models()
        self.language_codes = self.service.get_supported_languages()

    def _load_available_models(self):
        """Load available models from config file"""
        config_path = Path(__file__).parent.parent.parent / "config" / "model_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return list(config.get("translation_models", {}).keys())
        
    def render(self):
        """Render the model interface"""
        # Model selection
        st.selectbox(
            "Available Models",
            options=self.available_models,
            key="selected_model",
            help="Select a model to use for translation"
        )
        
        # Show model status
        if st.session_state.get("selected_model"):
            model = st.session_state.selected_model
            st.write("Model Status:")
            st.info(f"Using model: {model}")
            
            # Show language code mappings
            if model in self.language_codes:
                with st.expander("Language Code Mappings"):
                    st.json(self.language_codes[model])
    
    def update(self):
        """Update interface state"""
        pass
