import sys
import os
from pathlib import Path

import streamlit as st

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(os.path.abspath('.'))  # Add current working directory as well

import core.translation.translation_service
from ..translation.translation_service import TranslationService

def main():
    """
    Main function to set up the Streamlit interface for the Darija Translation Service.

    This function configures the Streamlit page, initializes the translation service,
    and creates tabs for different translation modes (Translation and Transliteration).
    It also handles user inputs for source language selection, text input, and translation.

    Tabs:
    - Translation: Allows users to select a source language, input text, and get the translation.
    - Transliteration: Placeholder for future script conversion functionality.

    Expander:
    - Model Information: Displays information about the current translation model if available.

    Attributes:
        translation_service (TranslationService): An instance of the TranslationService class.

    Raises:
        AttributeError: If the translation_service does not have the 'get_model_info' method.
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
            color: #000000;  /* Black text for better contrast */
            background-color: #FFFFFF;  /* White background */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize translation service
    translation_service = core.translation.translation_service.TranslationService()

    # Check if get_model_info exists
    if hasattr(translation_service, 'get_model_info'):
        st.success("get_model_info method found.")
    else:
        st.error("get_model_info method is missing.")

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
            else:
                model_name = ""
                target_lang = ""

            input_text = st.text_area(
                f"Enter {source_lang} text",
                height=200
            )

        with col2:
            st.subheader("Translation")
            if st.button("Translate", type="primary"):
                if input_text:
                    with st.spinner("Translating..."):
                        model_info = translation_service.get_model_info(model_name)
                        translation = translation_service.translate(
                            text=input_text,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            model=model_name
                        )
                        if translation:
                            st.text_area(
                                f"{target_lang} Translation",
                                value=translation,
                                height=200,
                                disabled=True,
                                key="translated_text",
                                class_="translated-text"
                            )
                        else:
                            st.error("Translation failed. Please try again.")
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
        if 'model_info' in locals() and model_info:
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

if __name__ == "__main__":
    main()
