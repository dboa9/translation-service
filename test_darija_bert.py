"""Test script to verify DarijaBERT model functionality with proper tokenizer configuration
"""
import logging
from typing import List, Tuple

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DarijaBERTTester:
    def __init__(self):
        self.tokenizer_config = {
            "do_lower_case": True,
            "unk_token": "[UNK]",
            "sep_token": "[SEP]",
            "pad_token": "[PAD]",
            "cls_token": "[CLS]",
            "mask_token": "[MASK]",
            "tokenize_chinese_chars": True,
            "strip_accents": None,
            "do_basic_tokenize": True,
            "never_split": None
        }
        self.model_name = "SI2M-Lab/DarijaBERT"
        self.tokenizer = None
        self.model = None
        
    def initialize(self):
        """Initialize the model and tokenizer with proper configuration"""
        try:
            logger.info("Loading DarijaBERT tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                **self.tokenizer_config
            )
            
            logger.info("Loading DarijaBERT model...")
            self.model = AutoModelForMaskedLM.from_pretrained(self.model_name)
            
            # Move to GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
            self.model = self.model.to(self.device)
            self.model.eval()
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False
            
    def get_mask_predictions(
        self,
        text: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Get top-k predictions for masked token in text.
        
        Args:
            text: Input text with [MASK] token
            top_k: Number of top predictions to return
            
        Returns:
            List of (token, probability) tuples

        """
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = outputs.logits
                
            # Find masked token position
            mask_token_index = torch.where(
                inputs["input_ids"] == self.tokenizer.mask_token_id
            )[1]
            
            if len(mask_token_index) == 0:
                logger.warning("No mask token found in input text")
                return []
                
            # Get probabilities for masked position
            mask_token_logits = predictions[0, mask_token_index, :]
            probs = torch.nn.functional.softmax(mask_token_logits, dim=-1)
            
            # Get top k predictions
            top_k_probs, top_k_indices = torch.topk(probs, top_k, dim=-1)
            
            # Convert to tokens
            results = []
            for token_id, prob in zip(
                top_k_indices[0].tolist(),
                top_k_probs[0].tolist()
            ):
                token = self.tokenizer.decode([token_id])
                results.append((token, prob))
                
            return results
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return []
            
    def test_basic_masked_prediction(self):
        """Test basic masked token prediction"""
        logger.info("\nTesting basic masked prediction...")
        
        test_cases = [
            "أنا كنتكلم [MASK] مغربية.",
            "السلام [MASK] كيف حالك",
            "[MASK] صباح الخير",
            "مرحبا [MASK] الدار البيضاء"
        ]
        
        for text in test_cases:
            logger.info(f"\nInput text: {text}")
            predictions = self.get_mask_predictions(text)
            
            if predictions:
                logger.info("Top 5 predictions:")
                for token, prob in predictions:
                    logger.info(f"- {token}: {prob:.4f}")
            else:
                logger.warning("No predictions generated")
                
    def test_tokenizer(self):
        """Test tokenizer functionality"""
        logger.info("\nTesting tokenizer...")
        
        test_texts = [
            "مرحبا كيف حالك",
            "الدار البيضاء مدينة جميلة",
            "أنا كنتكلم دارجة"
        ]
        
        for text in test_texts:
            tokens = self.tokenizer.tokenize(text)
            logger.info(f"\nText: {text}")
            logger.info(f"Tokens: {tokens}")
            
def main():
    logger.info("Starting DarijaBERT test...")
    
    tester = DarijaBERTTester()
    if not tester.initialize():
        logger.error("Failed to initialize DarijaBERT")
        return
        
    # Run tests
    tester.test_tokenizer()
    tester.test_basic_masked_prediction()
    
if __name__ == "__main__":
    main()
