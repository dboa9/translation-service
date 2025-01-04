"""Enhanced Streamlit interface for the translation service.
IMPORTANT: This file extends the existing functionality without modifying working files.
DO NOT modify this file directly - create a new extension if changes are needed.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import streamlit as st

from core.translation.translation_service import TranslationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("translation_interface.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the Streamlit interface."""
    st.set_page_config(
        page_title="Darija Translation Service", page_icon="🌐", layout="wide"
    )

    st.title("🌐 Darija Translation Service")
    st.markdown("""
    Translate between English and Darija using state-of-the-art models.
    """)

    # Initialize translation service - using the original working service
    service = TranslationService()

    # Model configurations
    models = {
        "English to Darija": {
            "model": "BAKKALIAYOUB/DarijaTranslation-V1",
            "source": "English",
            "target": "Darija",
        },
        "Darija to English": {
            "model": "lachkarsalim/LatinDarija_English-v2",
            "source": "Darija",
            "target": "English",
        },
    }

    # Translation direction selector
    direction = st.selectbox(
        "Select Translation Direction", options=list(models.keys())
    )

    # Get model info for selected direction
    model_config = models[direction]

    # Input text area
    input_text = st.text_area(f"Enter {model_config['source']} text", height=150)

    # Translation button
    if st.button("Translate", type="primary"):
        if not input_text:
            st.warning("Please enter text to translate")
            return

        try:
            # Show translation in progress
            with st.spinner("Translating..."):
                logger.info(f"Attempting translation with config: {model_config}")
                logger.info(f"Input text: {input_text}")
                try:
                    translation = service.translate(
                        text=input_text,
                        source_lang=model_config["source"],
                        target_lang=model_config["target"],
                        model=model_config["model"],
                    )
                    logger.info(f"Translation result: {translation}")
                except Exception as e:
                    logger.error(f"Translation failed with error: {str(e)}")
                    raise

            if translation:
                st.success("Translation Complete!")
                st.markdown("### Translation:")
                st.markdown(f"**{translation}**")
            else:
                st.error("Translation failed. Please try again.")

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            st.error(f"An error occurred: {str(e)}")

    # Model information
    with st.expander("ℹ️ Model Information"):
        st.markdown(f"""
        ### Current Configuration
        - **Direction:** {direction}
        - **Model:** {model_config['model']}
        - **Source Language:** {model_config['source']}
        - **Target Language:** {model_config['target']}
        """)


if __name__ == "__main__":
    main()
