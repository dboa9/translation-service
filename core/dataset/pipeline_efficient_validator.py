"""
Pipeline-based efficient validator that extends dataset validator functionality
while maintaining compatibility with existing tests.
"""
from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
import json
from transformers import pipeline, Pipeline
import torch

from .dataset_validator import DatasetValidator
from ..utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

class PipelineEfficientValidator(DatasetValidator):
    """
    Efficient validator using transformers pipeline API.
    Extends base validator while adding token-efficient processing.
    """
    
    def __init__(self, base_path: str, batch_size: int = 8):
        """
        Initialize the pipeline efficient validator.
        
        Args:
            base_path: Base path for dataset operations
            batch_size: Size of batches for processing
        """
        # Initialize with empty config, will be set in validate_dataset_efficiently
        super().__init__(config={})
        self.base_path = Path(base_path)
        self.batch_size = batch_size
        self.model_name = "MBZUAI-Paris/Atlas-Chat-9B"
        self._pipeline: Optional[Pipeline] = None
        
    @property
    def pipe(self) -> Optional[Pipeline]:
        """Get the pipeline instance."""
        return self._pipeline
        
    @pipe.setter
    def pipe(self, value: Optional[Pipeline]):
        """Set the pipeline instance."""
        self._pipeline = value
        
    def initialize_pipeline(self) -> bool:
        """
        Initialize the transformers pipeline for validation.
        
        Returns:
            bool: True if initialization succeeds
        """
        try:
            logger.info(f"Initializing pipeline with model: {self.model_name}")
            self._pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                model_kwargs={"torch_dtype": torch.bfloat16},
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {str(e)}")
            self._pipeline = None
            return False
            
    def validate_batch(self, samples: List[Dict[str, Any]]) -> List[bool]:
        """
        Validate a batch of samples efficiently.
        
        Args:
            samples: List of samples to validate
            
        Returns:
            List[bool]: Validation results for each sample
        """
        # Initialize pipeline if needed
        if self._pipeline is None:
            if not self.initialize_pipeline():
                return [False] * len(samples)
                
        # At this point, self._pipeline should be initialized
        if self._pipeline is None:
            logger.error("Pipeline initialization failed")
            return [False] * len(samples)
            
        try:
            results = []
            for sample in samples:
                # Basic validation first
                if not self._validate_sample_structure(sample):
                    results.append(False)
                    continue
                    
                # Format for model input
                messages = [{"role": "user", "content": sample["input"]}]
                
                # Get model response
                try:
                    # Pipeline returns a list of dictionaries
                    output = self._pipeline(messages, max_new_tokens=64)
                    if isinstance(output, list) and len(output) > 0:
                        # Access the generated text from the response
                        generated_text = output[0].get("generated_text", "")
                        valid = bool(generated_text and len(generated_text.strip()) > 0)
                        results.append(valid)
                    else:
                        results.append(False)
                except Exception as e:
                    logger.warning(f"Sample validation failed: {str(e)}")
                    results.append(False)
                    
            return results
            
        except Exception as e:
            logger.error(f"Batch validation failed: {str(e)}")
            return [False] * len(samples)
            
    def _validate_sample_structure(self, sample: Dict[str, Any]) -> bool:
        """
        Validate basic sample structure without model inference.
        
        Args:
            sample: Sample to validate
            
        Returns:
            bool: True if structure is valid
        """
        required_fields = ["input", "output"]
        return all(
            field in sample and isinstance(sample[field], str)
            for field in required_fields
        )
        
    def validate_dataset_efficiently(
        self, 
        dataset_config: Dict[str, Any],
        max_samples: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate dataset with efficient batching and early stopping.
        
        Args:
            dataset_config: Dataset configuration dictionary
            max_samples: Maximum number of samples to validate
            
        Returns:
            Dict[str, Any]: Validation results and metrics
        """
        try:
            # Update config for base validator
            self.config = dataset_config
            
            # Load dataset samples
            dataset_path = self.base_path / dataset_config.get("path", "")
            samples = self._load_dataset_samples(dataset_path)
            
            if max_samples:
                samples = samples[:max_samples]
                
            valid_count = 0
            total_processed = 0
            
            # Process in batches
            for i in range(0, len(samples), self.batch_size):
                batch = samples[i:i + self.batch_size]
                results = self.validate_batch(batch)
                
                valid_count += sum(results)
                total_processed += len(results)
                
                # Log progress
                if total_processed % 100 == 0:
                    logger.info(
                        f"Processed {total_processed}/{len(samples)} samples. "
                        f"Valid: {valid_count}"
                    )
                    
            return {
                "success": True,
                "total_samples": total_processed,
                "valid_samples": valid_count,
                "validation_rate": valid_count / total_processed if total_processed else 0
            }
            
        except Exception as e:
            logger.error(f"Dataset validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _load_dataset_samples(self, dataset_path: Path) -> List[Dict[str, Any]]:
        """
        Load dataset samples efficiently.
        
        Args:
            dataset_path: Path to dataset
            
        Returns:
            List[Dict[str, Any]]: List of dataset samples
        """
        try:
            if not dataset_path.exists():
                logger.error(f"Dataset path does not exist: {dataset_path}")
                return []
                
            # Handle different dataset formats
            if dataset_path.is_file():
                if dataset_path.suffix == '.json':
                    with open(dataset_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict) and 'samples' in data:
                            return data['samples']
                        else:
                            logger.error("Invalid JSON dataset format")
                            return []
                            
                elif dataset_path.suffix == '.jsonl':
                    samples = []
                    with open(dataset_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                sample = json.loads(line.strip())
                                samples.append(sample)
                            except json.JSONDecodeError:
                                continue
                    return samples
                    
            elif dataset_path.is_dir():
                # Handle directory of files
                samples = []
                for file_path in dataset_path.glob('*.json*'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if file_path.suffix == '.jsonl':
                                for line in f:
                                    try:
                                        sample = json.loads(line.strip())
                                        samples.append(sample)
                                    except json.JSONDecodeError:
                                        continue
                            else:
                                data = json.load(f)
                                if isinstance(data, list):
                                    samples.extend(data)
                                elif isinstance(data, dict) and 'samples' in data:
                                    samples.extend(data['samples'])
                    except Exception as e:
                        logger.warning(f"Error loading file {file_path}: {str(e)}")
                        continue
                return samples
                
            logger.error(f"Unsupported dataset format: {dataset_path}")
            return []
            
        except Exception as e:
            logger.error(f"Error loading dataset samples: {str(e)}")
            return []
