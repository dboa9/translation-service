"""
Enhanced Streamlit interface for the translation service.
IMPORTANT: This file extends the existing functionality without modifying working files.
DO NOT modify this file directly - create a new extension if changes are needed.
"""

import streamlit as st
import sys
from pathlib import Path
import logging
from typing import Dict, Any, List

# Add parent directory to path to allow imports
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.translation.translation_service import TranslationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation_interface.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedTranslationInterface:
    def __init__(self):
        """Initialize the enhanced translation interface."""
        self.service = TranslationService()
        self.models = {
            "English to Darija": "BAKKALIAYOUB/DarijaTranslation-V1",
            "Darija to English": "lachkarsalim/LatinDarija_English-v2"
        }
        
    def setup_session_state(self):
        """Initialize session state variables."""
        if 'translation_history' not in st.session_state:
            st.session_state.translation_history = []
            
    def render_header(self):
        """Render the interface header."""
        st.title("🌐 Darija Translation Service")
        st.markdown("""
        Translate between English and Darija using state-of-the-art models.
        """)
        
    def render_translation_interface(self):
        """Render the main translation interface."""
        # Translation direction selector
        direction = st.selectbox(
            "Select Translation Direction",
            options=list(self.models.keys())
        )
        
        # Input text area
        input_text = st.text_area(
            "Enter text to translate",
            height=100,
            key="input_text"
        )
        
        # Translation button
        if st.button("Translate", key="translate_button"):
            if not input_text:
                st.warning("Please enter some text to translate")
                return
                
            try:
                # Determine source and target languages
                source_lang, target_lang = direction.split(" to ")
                model = self.models[direction]
                
                # Show translation in progress
                with st.spinner("Translating..."):
                    # Call translate with parameters in correct order
                    translation = self.service.translate(
                        text=input_text,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        model=model  # This parameter is expected by the service
                    )
                
                if translation:
                    # Display translation result
                    st.success("Translation Complete!")
                    st.markdown("### Translation:")
                    st.markdown(f"**{translation}**")
                    
                    # Add to history
                    st.session_state.translation_history.append({
                        "input": input_text,
                        "output": translation
                    })
                else:
                    st.error("Translation failed. Please try again.")
                    
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                st.error(f"An error occurred: {str(e)}")
                
    def render_history(self):
        """Render translation history."""
        if st.session_state.translation_history:
            st.markdown("### Recent Translations")
            for i, entry in enumerate(reversed(st.session_state.translation_history[-5:])):
                with st.expander(f"Translation {len(st.session_state.translation_history) - i}"):
                    st.markdown(f"**Direction:** {entry['direction']}")
                    st.markdown(f"**Input:** {entry['input']}")
                    st.markdown(f"**Output:** {entry['output']}")
                    
    def render_model_info(self):
        """Render information about available models."""
        with st.expander("ℹ️ Model Information"):
            st.markdown("""
            ### Available Models
            
            1. **English to Darija**
               - Model: BAKKALIAYOUB/DarijaTranslation-V1
               - Specialized for English to Darija translation
               
            2. **Darija to English**
               - Model: lachkarsalim/LatinDarija_English-v2
               - Optimized for Darija to English translation
            """)
            
    def run(self):
        """Run the Streamlit interface."""
        try:
            # Initialize session state
            self.setup_session_state()
            
            # Render interface components
            self.render_header()
            self.render_translation_interface()
            self.render_history()
            self.render_model_info()
            
        except Exception as e:
            logger.error(f"Interface error: {str(e)}")
            st.error(f"An error occurred while running the interface: {str(e)}")

def main():
    interface = EnhancedTranslationInterface()
    interface.run()

if __name__ == "__main__":
    main()
