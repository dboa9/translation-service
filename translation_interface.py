"""
Streamlit interface for the Darija Translation Service.

IMPORTANT: This file contains changes suggested by GitHub Copilot.
The following changes require explicit authorization before modification:

1. Lines 38-44 - get_model_info error handling:
   - Added try-except block for model info retrieval
   - REQUIRES AUTHORIZATION before modifying error handling

2. Lines 98-102 - Translation error handling:
   - Added comprehensive error handling for translation process
   - REQUIRES AUTHORIZATION before modifying error handling

3. Lines 151-158 - Model info display:
   - Added error handling for model info display in expander
   - REQUIRES AUTHORIZATION before modifying error handling

DO NOT MODIFY THESE SECTIONS WITHOUT EXPLICIT AUTHORIZATION
"""

import logging
import streamlit as st
from core.translation.translation_service import TranslationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("translation_interface.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to set up the Streamlit interface for the Darija Translation Service.
    """
    st.set_page_config(
        page_title="Darija Translation Service",
        page_icon="🌐",
        layout="wide"
    )

    st.title("🌐 Darija Translation Service")

    # Add custom CSS for better text color contrast
    st.markdown(
        """
        <style>
        .translated-text {
            color: #FFFFFF;  /* White text for better contrast */
            background-color: #000000;  /* Black background */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    try:
        # Initialize translation service
        translation_service = TranslationService()
        logger.info("Translation service initialized successfully")
        
        # Initialize model name
        model_name = ""
        target_lang = ""

        # Create tabs for different translation modes
        tab1, tab2 = st.tabs(["Translation", "Transliteration"])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Source")
                source_lang = st.radio(
                    "Select source language:",
                    ["English", "Darija", "Latin Darija"],
                    horizontal=True,
                    key="source_lang_select"
                )

                if source_lang == "English":
                    model_name = "BAKKALIAYOUB/DarijaTranslation-V1"
                    target_lang = "Darija"
                elif source_lang == "Darija":
                    model_name = "lachkarsalim/LatinDarija_English-v2"
                    target_lang = "English"
                elif source_lang == "Latin Darija":
                    model_name = "lachkarsalim/LatinDarija_English-v2"
                    target_lang = "English"

                # Show model info
                if model_name:
                    try:
                        model_info = translation_service.get_model_info(model_name)
                        if model_info:
                            st.info(f"🔄 Selected model: {model_name}")
                    except Exception as e:
                        logger.error(f"Error getting model info: {str(e)}")
                        st.error(f"Error getting model info: {str(e)}")

                input_text = st.text_area(
                    f"Enter {source_lang} text",
                    height=200,
                    key="source_text_input"
                )

            with col2:
                st.subheader("Translation")
                if st.button("Translate", type="primary", key="translate_btn"):
                    if input_text:
                        with st.spinner("Translating..."):
                            try:
                                logger.info(f"Getting model info for {model_name}")
                                model_info = translation_service.get_model_info(model_name)
                                logger.info(f"Model info: {model_info}")
                                
                                logger.info(f"Translating text: {input_text}")
                                # Get language codes from model config
                                model_info = translation_service.get_model_info(model_name)
                                lang_codes = model_info.get("lang_codes", {})
                                
                                # Use language codes from config
                                translation = translation_service.translate(
                                    text=input_text,
                                    source_lang=lang_codes.get("source", source_lang),
                                    target_lang=lang_codes.get("target", target_lang),
                                    model=model_name
                                )
                                
                                if translation:
                                    logger.info(f"Translation successful: {translation}")
                                    st.text_area(
                                        f"{target_lang} Translation",
                                        value=translation,
                                        height=200,
                                        key="translation_output",
                                        disabled=True,
                                        class_="translated-text"
                                    )
                                else:
                                    logger.error("Translation returned None")
                                    st.error("Translation failed. Please try again.")
                            except Exception as e:
                                logger.error(f"Translation error: {str(e)}")
                                st.error(f"Translation error: {str(e)}")
                    else:
                        st.warning("Please enter text to translate.")

        with tab2:
            st.subheader("Arabic Script ⟷ Latin Script")
            text_to_convert = st.text_area(
                "Enter text to convert",
                height=200,
                key="script_convert_input"
            )

            if st.button("Convert Script", type="primary", key="convert_btn"):
                if text_to_convert:
                    st.info("Script conversion functionality coming soon!")
                else:
                    st.warning("Please enter text to convert.")

        with st.expander("ℹ️ Model Information"):
            try:
                if model_name:
                    model_info = translation_service.get_model_info(model_name)
                    if model_info:
                        direction = model_info.get("direction", "N/A")
                        source_lang_code = model_info.get("lang_codes", {}).get("source", "N/A")
                        target_lang_code = model_info.get("lang_codes", {}).get("target", "N/A")
                        st.markdown(f"""
                        **Current Model:** {model_name}
                        **Direction:** {direction}
                        **Input Language:** {source_lang_code}
                        **Output Language:** {target_lang_code}
                        **Status:** 🟡 Using HuggingFace API
                        """)
                    else:
                        st.markdown(f"**Current Model:** {model_name}")
            except Exception as e:
                logger.error(f"Error displaying model info: {str(e)}")
                st.error("Error displaying model information")

    except Exception as e:
        logger.error(f"Error initializing translation service: {str(e)}")
        st.error(f"Error initializing translation service: {str(e)}")

if __name__ == "__main__":
    main()
