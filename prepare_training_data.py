"""
Script to prepare training data using DarijaBERT quality validation
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add current directory to path to find the pipeline module
sys.path.append('.')
from darija_translation_pipeline import DarijaTranslationPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrainingDataPreparator:
    def __init__(
        self,
        quality_threshold: float = 0.6,
        max_samples: Optional[int] = None
    ):
        self.pipeline = DarijaTranslationPipeline()
        self.quality_threshold = quality_threshold
        self.max_samples = max_samples
        
    def initialize(self) -> bool:
        """Initialize the pipeline"""
        return self.pipeline.initialize()
        
    def process_file(
        self,
        input_path: Path,
        output_path: Path
    ) -> Dict[str, Any]:
        """
        Process a training data file
        
        Args:
            input_path: Path to input file (tab-separated eng\tdarija)
            output_path: Path to save processed data
            
        Returns:
            Dict with processing statistics
        """
        stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "quality_scores": []
        }
        
        valid_pairs = []
        
        try:
            logger.info(f"Processing file: {input_path}")
            
            with open(input_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if self.max_samples is not None and stats["total"] >= self.max_samples:
                        break
                        
                    stats["total"] += 1
                    if line_num % 10 == 0:
                        logger.info(
                            f"Processed {line_num} lines. "
                            f"Valid: {stats['valid']}"
                        )
                        
                    try:
                        # Split line into English and Darija
                        eng, darija = line.strip().split('\t')
                        
                        # Check Darija quality
                        quality = self.pipeline.check_darija_quality(darija)
                        stats["quality_scores"].append(quality)
                        
                        if quality >= self.quality_threshold:
                            # Validate translation
                            eng_to_darija = self.pipeline.translate(
                                eng,
                                source_lang="eng",
                                target_lang="ary"
                            )
                            
                            darija_to_eng = self.pipeline.translate(
                                darija,
                                source_lang="ary",
                                target_lang="eng"
                            )
                            
                            valid_pairs.append({
                                "english": eng,
                                "darija": darija,
                                "quality_score": quality,
                                "eng_to_darija_quality": eng_to_darija.get("translation_quality"),
                                "back_translation": darija_to_eng.get("translation")
                            })
                            stats["valid"] += 1
                        else:
                            stats["invalid"] += 1
                            
                    except Exception as e:
                        logger.warning(f"Error processing line {line_num}: {str(e)}")
                        stats["invalid"] += 1
                        
            # Calculate quality statistics
            if stats["quality_scores"]:
                stats["avg_quality"] = sum(stats["quality_scores"]) / len(stats["quality_scores"])
                stats["min_quality"] = min(stats["quality_scores"])
                stats["max_quality"] = max(stats["quality_scores"])
            
            # Save processed data
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "statistics": stats,
                    "pairs": valid_pairs
                }, f, ensure_ascii=False, indent=2)
                
            logger.info("\nProcessing completed:")
            logger.info(f"Total samples: {stats['total']}")
            logger.info(f"Valid samples: {stats['valid']}")
            logger.info(f"Invalid samples: {stats['invalid']}")
            if "avg_quality" in stats:
                logger.info(f"Average quality: {stats['avg_quality']:.4f}")
                
            return stats
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {"error": str(e)}

def main():
    """Main function"""
    # Configure paths
    input_file = Path("data/raw/training_pairs.txt")
    output_file = Path("data/processed/validated_pairs.json")
    
    # Initialize preparator
    preparator = TrainingDataPreparator(
        quality_threshold=0.6,
        max_samples=100  # For testing, remove for full processing
    )
    
    if not preparator.initialize():
        logger.error("Failed to initialize pipeline")
        return
        
    # Process data
    stats = preparator.process_file(input_file, output_file)
    
    if "error" in stats:
        logger.error(f"Processing failed: {stats['error']}")
    else:
        logger.info("\nProcessing completed successfully!")
        
if __name__ == "__main__":
    main()
