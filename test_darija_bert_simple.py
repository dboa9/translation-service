"""
Simple test script for DarijaBERT masked language modeling
"""
from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch
import logging
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def decode_token(tokenizer, token_id: int) -> str:
    """Safely decode a single token ID"""
    return tokenizer.decode([int(token_id)])

def test_darija_bert():
    try:
        # 1. Load model and tokenizer
        logging.info("Loading DarijaBERT...")
        tokenizer = AutoTokenizer.from_pretrained("SI2M-Lab/DarijaBERT")
        model = AutoModelForMaskedLM.from_pretrained("SI2M-Lab/DarijaBERT")
        
        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        model.eval()
        
        # 2. Test cases
        test_cases = [
            "أنا [MASK] من المغرب",
            "السلام [MASK] كيف حالك",
            "مرحبا [MASK] الدار البيضاء"
        ]
        
        for text in test_cases:
            logging.info(f"\nTest text: {text}")
            
            # 3. Tokenize
            inputs = tokenizer(text, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # 4. Find mask token index
            mask_idx = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]
            
            if len(mask_idx) == 0:
                logging.warning("No mask token found in input")
                continue
                
            # 5. Get predictions
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = outputs.logits
                
            # 6. Get top 5 predictions for masked token
            mask_predictions = predictions[0, mask_idx]
            top_5_values, top_5_indices = torch.topk(mask_predictions, 5, dim=1)
            
            # 7. Get probabilities
            probs = torch.nn.functional.softmax(mask_predictions, dim=-1)
            
            # 8. Print results
            logging.info("Top 5 predictions for masked word:")
            for i, token_id in enumerate(top_5_indices[0]):
                # Convert tensor to integer
                token_id_int = int(token_id.item())
                token = decode_token(tokenizer, token_id_int)
                prob = probs[0][token_id].item()
                logging.info(f"Token: {token}, Probability: {prob:.4f}")
                
            # 9. Show complete sentence with top prediction
            top_token_id = int(top_5_indices[0][0].item())
            top_token = decode_token(tokenizer, top_token_id)
            complete_text = text.replace("[MASK]", top_token)
            logging.info(f"Most likely complete sentence:")
            logging.info(complete_text)
            logging.info("-" * 50)
            
        return True
        
    except Exception as e:
        logging.error(f"Error testing DarijaBERT: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def main():
    logging.info("Starting DarijaBERT test...")
    success = test_darija_bert()
    if success:
        logging.info("\nTest completed successfully!")
    else:
        logging.error("\nTest failed!")
        
if __name__ == "__main__":
    main()
