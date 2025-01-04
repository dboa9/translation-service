import sys
import os
from pathlib import Path
import logging

import streamlit as st

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

# Import directly from file in same directory
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))
import interface_translation_service

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

    try:
        # Initialize interface translation service with debug logging
        translation_service = interface_translation_service.InterfaceTranslationService()
        logger.info("Translation service initialized successfully")
        logger.info(f"Available methods: {dir(translation_service)}")
        logger.info(f"Has get_model_info: {hasattr(translation_service, 'get_model_info')}")
        logger.info(f"Service type: {type(translation_service)}")
        
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
                    horizontal=True
                )

                if source_lang == "English":
                    model_name = "AnasAber/seamless-darija-eng"
                    target_lang = "Darija"
                elif source_lang == "Darija":
                    model_name = "AnasAber/seamless-darija-eng"
                    target_lang = "English"
                elif source_lang == "Latin Darija":
                    model_name = "lachkarsalim/LatinDarija_English-v2"
                    target_lang = "English"

                input_text = st.text_area(
                    f"Enter {source_lang} text",
                    height=200
                )

            with col2:
                st.subheader("Translation")
                if st.button("Translate", type="primary"):
                    if input_text:
                        with st.spinner("Translating..."):
                            try:
                                logger.info(f"Getting model info for {model_name}")
                                model_info = translation_service.get_model_info(model_name)
                                logger.info(f"Model info: {model_info}")
                                
                                logger.info(f"Translating text: {input_text}")
                                translation = translation_service.translate(
                                    text=input_text,
                                    source_lang=source_lang,
                                    target_lang=target_lang,
                                    model=model_name
                                )
                                
                                if translation:
                                    logger.info(f"Translation successful: {translation}")
                                    st.text_area(
                                        f"{target_lang} Translation",
                                        value=translation,
                                        height=200,
                                        disabled=True
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
                height=200
            )

            if st.button("Convert Script", type="primary"):
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
