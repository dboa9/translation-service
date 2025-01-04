"""
Streamlit application with multi-model support and fallback
"""
import logging
import os
import time
import streamlit as st
import psutil
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    MarianTokenizer,
    MarianMTModel,
    T5Tokenizer,
    T5ForConditionalGeneration
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configurations from test_all_translations.py
MODEL_INFO = {
    "AnasAber/seamless-darija-eng": {
        "lang_codes": {"source": "ary", "target": "eng"},
        "tokenizer": "AutoTokenizer",
        "model_class": "AutoModelForSeq2SeqLM",
        "input_format": "text",
        "direction": "bidirectional",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "AnasAber/nllb-enhanced-darija-eng_v1.1": {
        "lang_codes": {"source": "ary_Arab", "target": "eng_Latn"},
        "tokenizer": "AutoTokenizer",
        "model_class": "AutoModelForSeq2SeqLM",
        "input_format": "text",
        "direction": "bidirectional",
        "special_tokens": {"bos": "<s>", "eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "BAKKALIAYOUB/DarijaTranslation-V1": {
        "lang_codes": {"source": "eng", "target": "ara"},
        "tokenizer": "MarianTokenizer",
        "model_class": "MarianMTModel",
        "input_format": "text",
        "direction": "english_to_darija",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    },
    "hananeChab/darija_englishV2.1": {
        "lang_codes": {"source": "ar", "target": "en"},
        "tokenizer": "MarianTokenizer",
        "model_class": "MarianMTModel",
        "input_format": "text",
        "direction": "darija_to_english",
        "special_tokens": {"eos": "</s>", "pad": "<pad>", "unk": "<unk>"}
    }
}

@st.cache_resource
def load_model(model_name: str, info: dict):
    """Load model and tokenizer with caching"""
    try:
        # Get correct tokenizer and model classes
        tokenizer_map = {
            "AutoTokenizer": AutoTokenizer,
            "MarianTokenizer": MarianTokenizer,
            "T5Tokenizer": T5Tokenizer
        }
        model_map = {
            "AutoModelForSeq2SeqLM": AutoModelForSeq2SeqLM,
            "MarianMTModel": MarianMTModel,
            "T5ForConditionalGeneration": T5ForConditionalGeneration
        }
        
        tokenizer_class = tokenizer_map.get(info["tokenizer"])
        model_class = model_map.get(info["model_class"])
        
        if not tokenizer_class or not model_class:
            logger.error(f"Invalid tokenizer or model class for {model_name}")
            return None, None
        
        logger.info(f"Loading {model_name} with {info['tokenizer']}")
        
        # Load with auth token
        auth_token = os.getenv("HUGGINGFACE_API_TOKEN")
        tokenizer = tokenizer_class.from_pretrained(model_name, use_auth_token=auth_token)
        model = model_class.from_pretrained(model_name, use_auth_token=auth_token)
        
        if torch.cuda.is_available():
            model = model.to("cuda")
            
        return tokenizer, model
        
    except Exception as e:
        logger.error(f"Error loading {model_name}: {str(e)}")
        return None, None

class TranslationService:
    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")
        
        # Initialize model cache
        self.model_cache = {}
        self.max_retries = 3
        
    def get_model_for_direction(self, source_lang: str, target_lang: str):
        """Get appropriate model for translation direction"""
        direction = None
        if source_lang == "english" and target_lang == "darija":
            direction = "english_to_darija"
        elif source_lang == "darija" and target_lang == "english":
            direction = "darija_to_english"
            
        # First try bidirectional models
        for model_name, info in MODEL_INFO.items():
            if info["direction"] == "bidirectional":
                if model_name not in self.model_cache:
                    tokenizer, model = load_model(model_name, info)
                    if tokenizer and model:
                        self.model_cache[model_name] = (tokenizer, model, info)
                if model_name in self.model_cache:
                    return model_name, *self.model_cache[model_name]
                    
        # Then try direction-specific models
        for model_name, info in MODEL_INFO.items():
            if info["direction"] == direction:
                if model_name not in self.model_cache:
                    tokenizer, model = load_model(model_name, info)
                    if tokenizer and model:
                        self.model_cache[model_name] = (tokenizer, model, info)
                if model_name in self.model_cache:
                    return model_name, *self.model_cache[model_name]
                    
        return None, None, None, None
        
    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        """
        Translate text with model fallback support
        """
        if not text.strip():
            return {
                "translation": "Please enter text to translate",
                "model_used": None,
                "status": "error"
            }
            
        progress_text = st.empty()
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                # Get appropriate model
                model_name, tokenizer, model, info = self.get_model_for_direction(source_lang, target_lang)
                
                if not model_name or not tokenizer or not model or not info:
                    retries += 1
                    time.sleep(1)
                    continue
                    
                progress_text.text(f"Using model: {model_name}")
                
                # Prepare input
                inputs = tokenizer(text, return_tensors="pt", padding=True)
                if torch.cuda.is_available():
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                # Generate translation
                outputs = model.generate(
                    **inputs,
                    max_length=128,
                    num_beams=5,
                    temperature=0.7,
                    do_sample=True,
                    top_k=50,
                    top_p=0.95
                )
                
                # Decode output
                translation = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
                progress_text.empty()
                
                return {
                    "translation": translation,
                    "model_used": model_name,
                    "status": "success"
                }
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Translation error with {model_name}: {last_error}")
                retries += 1
                if model_name in self.model_cache:
                    del self.model_cache[model_name]
                time.sleep(1)
                
        progress_text.empty()
        error_msg = f"Translation failed after {retries} attempts"
        if last_error:
            error_msg += f": {last_error}"
            
        return {
            "translation": error_msg,
            "model_used": None,
            "status": "error"
        }

class TranslationApp:
    def __init__(self):
        self.service = TranslationService()
        
    def render_sidebar(self):
        with st.sidebar:
            st.header("Model Information")
            
            st.markdown("### Available Models")
            for model_name, info in MODEL_INFO.items():
                with st.expander(model_name):
                    st.markdown(f"**Direction:** {info['direction']}")
                    st.markdown(f"**Tokenizer:** {info['tokenizer']}")
                    st.markdown(f"**Language Codes:**")
                    st.json(info['lang_codes'])
                
            st.header("System Monitoring")
            st.text(f"CPU Usage: {psutil.cpu_percent()}%")
            st.text(f"Memory Usage: {psutil.virtual_memory().percent}%")
            if torch.cuda.is_available():
                st.text(f"GPU Memory: {torch.cuda.memory_allocated()/1024**2:.1f}MB")

    def render_main(self):
        st.title("Darija Translation Service")
        
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
                key="source_text",
                height=200,
                help="Type or paste text here"
            )
            
            if st.button("Translate"):
                if not source_text:
                    st.error("Please enter text to translate")
                else:
                    with col2:
                        st.subheader("Translation")
                        target_lang = "darija" if source_lang == "english" else "english"
                        st.info(f"Target Language: {target_lang}")
                        
                        with st.spinner("Translating..."):
                            result = self.service.translate(
                                source_text,
                                source_lang,
                                target_lang
                            )
                            
                            if result["status"] == "error":
                                st.error(result["translation"])
                            else:
                                st.text_area(
                                    "Translation Result",
                                    value=result["translation"],
                                    height=200,
                                    key="translation_output",
                                    help="Translation output will appear here",
                                    disabled=True
                                )
                                st.success(f"Translation completed using {result['model_used']}")

def main():
    try:
        st.set_page_config(
            page_title="Darija Translation Service",
            page_icon="🌐",
            layout="wide"
        )
        app = TranslationApp()
        app.render_sidebar()
        app.render_main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
