"""
Memory-efficient pipeline combining DarijaBERT and Seamless models for bidirectional translation
"""
from transformers import (
    AutoTokenizer,
    AutoModelForMaskedLM,
    AutoModelForSeq2SeqLM,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    PreTrainedModel
)
import torch
import logging
import gc
from typing import Dict, Any, Optional, Union, cast
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type alias for tokenizer types
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]

class DarijaTranslationPipeline:
    def __init__(self):
        self.darija_bert_name = "SI2M-Lab/DarijaBERT"
        self.seamless_name = "AnasAber/seamless-darija-eng"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Language codes
        self.lang_codes = {
            "eng": "eng",  # English
            "ary": "ary"   # Darija
        }
        
        # Initialize as None
        self.bert_model: Optional[PreTrainedModel] = None
        self.bert_tokenizer: Optional[TokenizerType] = None
        self.translation_model: Optional[PreTrainedModel] = None
        self.translation_tokenizer: Optional[TokenizerType] = None
        
    def _clear_gpu_memory(self):
        """Clear GPU memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
    def initialize_bert(self) -> bool:
        """Initialize DarijaBERT model"""
        try:
            logger.info("Loading DarijaBERT...")
            self._clear_gpu_memory()
            
            # Load in 8-bit to save memory
            self.bert_model = AutoModelForMaskedLM.from_pretrained(
                self.darija_bert_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            self.bert_tokenizer = AutoTokenizer.from_pretrained(
                self.darija_bert_name
            )
            
            return True
        except Exception as e:
            logger.error(f"DarijaBERT initialization failed: {str(e)}")
            return False
            
    def initialize_translator(self) -> bool:
        """Initialize translation model"""
        try:
            logger.info("Loading translation model...")
            self._clear_gpu_memory()
            
            # Load in 8-bit to save memory
            self.translation_model = AutoModelForSeq2SeqLM.from_pretrained(
                self.seamless_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            self.translation_tokenizer = AutoTokenizer.from_pretrained(
                self.seamless_name
            )
            
            return True
        except Exception as e:
            logger.error(f"Translation model initialization failed: {str(e)}")
            return False
            
    def initialize(self) -> bool:
        """Initialize both models sequentially"""
        return self.initialize_bert() and self.initialize_translator()
            
    def check_darija_quality(self, text: str) -> float:
        """Check Darija text quality using DarijaBERT"""
        if not self.bert_model or not self.bert_tokenizer:
            return 0.0
            
        try:
            tokenizer = cast(TokenizerType, self.bert_tokenizer)
            model = cast(PreTrainedModel, self.bert_model)
            
            # Tokenize with smaller max length
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = model(**inputs)
                
            # Calculate confidence
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            confidence = probs.max(dim=-1).values.mean().item()
            
            return confidence
            
        except Exception as e:
            logger.error(f"Quality check failed: {str(e)}")
            return 0.0
            
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """Translate text between English and Darija"""
        if not all([
            self.translation_model,
            self.translation_tokenizer,
            self.bert_model,
            self.bert_tokenizer
        ]):
            return {"error": "Models not initialized"}
            
        try:
            tokenizer = cast(TokenizerType, self.translation_tokenizer)
            model = cast(PreTrainedModel, self.translation_model)
            
            # Validate language codes
            if source_lang not in self.lang_codes or target_lang not in self.lang_codes:
                return {"error": "Invalid language code"}
                
            # Check Darija quality if applicable
            quality_score = None
            if source_lang == "ary":
                quality_score = self.check_darija_quality(text)
                if quality_score < 0.5:
                    logger.warning(f"Low Darija quality score: {quality_score}")
                    
            # Prepare input with smaller max length
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256
            ).to(self.device)
            
            # Add target language token
            target_lang_token = f"<2{target_lang}>"
            inputs["forced_bos_token_id"] = tokenizer.encode(
                target_lang_token,
                add_special_tokens=False
            )[0]
            
            # Generate translation
            with torch.no_grad():
                output_ids = model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    forced_bos_token_id=inputs["forced_bos_token_id"],
                    max_new_tokens=256,
                    num_beams=3,
                    length_penalty=0.6
                )
                
            # Decode output
            translation = tokenizer.decode(
                output_ids[0],
                skip_special_tokens=True
            )
            
            # Check translation quality if target is Darija
            translation_score = None
            if target_lang == "ary":
                translation_score = self.check_darija_quality(translation)
                
            # Clear some memory
            self._clear_gpu_memory()
            
            return {
                "translation": translation,
                "source_quality": quality_score,
                "translation_quality": translation_score
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return {"error": str(e)}

def main():
    """Test the pipeline"""
    pipeline = DarijaTranslationPipeline()
    
    if not pipeline.initialize():
        logger.error("Failed to initialize pipeline")
        return
        
    # Test cases
    test_cases = [
        {
            "text": "Hello, how are you?",
            "source": "eng",
            "target": "ary"
        },
        {
            "text": "كيف حالك",
            "source": "ary",
            "target": "eng"
        }
    ]
    
    for case in test_cases:
        logger.info(f"\nTranslating: {case['text']}")
        logger.info(f"Source: {case['source']} -> Target: {case['target']}")
        
        result = pipeline.translate(
            case["text"],
            case["source"],
            case["target"]
        )
        
        if "error" in result:
            logger.error(f"Error: {result['error']}")
        else:
            logger.info(f"Translation: {result['translation']}")
            if result.get("source_quality"):
                logger.info(f"Source quality: {result['source_quality']:.4f}")
            if result.get("translation_quality"):
                logger.info(f"Translation quality: {result['translation_quality']:.4f}")
                
if __name__ == "__main__":
    main()
