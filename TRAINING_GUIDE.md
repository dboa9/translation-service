# Training Guide: Bidirectional English-Darija Translation

This guide explains how to use the DarijaBERT + Seamless pipeline for training a robust bidirectional translation model.

## Pipeline Benefits

1. Data Quality Control:
   - DarijaBERT provides quality scores for Darija text
   - Helps identify and filter low-quality training samples
   - Validates both source and target Darija text

2. Translation Validation:
   - Checks translation quality in real-time
   - Provides confidence scores for translations
   - Helps identify problematic translations

## Training Process

### 1. Data Preparation

```python
from darija_translation_pipeline import DarijaTranslationPipeline

# Initialize pipeline
pipeline = DarijaTranslationPipeline()
pipeline.initialize()

# Process training data
def prepare_training_data(input_file, output_file, quality_threshold=0.5):
    valid_pairs = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            eng, darija = line.strip().split('\t')
            
            # Check Darija quality
            quality = pipeline.check_darija_quality(darija)
            
            if quality >= quality_threshold:
                valid_pairs.append({
                    'english': eng,
                    'darija': darija,
                    'quality_score': quality
                })
    
    # Save filtered data
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(valid_pairs, f, ensure_ascii=False, indent=2)
```

### 2. Training Data Validation

```python
def validate_translation_pair(eng_text, darija_text):
    # Check Darija quality
    darija_quality = pipeline.check_darija_quality(darija_text)
    
    # Translate English to Darija
    eng_to_darija = pipeline.translate(
        eng_text, 
        source_lang="eng", 
        target_lang="ary"
    )
    
    # Translate Darija to English
    darija_to_eng = pipeline.translate(
        darija_text,
        source_lang="ary",
        target_lang="eng"
    )
    
    return {
        'darija_quality': darija_quality,
        'eng_to_darija_quality': eng_to_darija.get('translation_quality'),
        'darija_to_eng': darija_to_eng.get('translation')
    }
```

### 3. Training Loop Integration

```python
def training_step(batch, quality_threshold=0.5):
    eng_texts = batch['english']
    darija_texts = batch['darija']
    
    # Validate batch samples
    valid_indices = []
    for i, (eng, darija) in enumerate(zip(eng_texts, darija_texts)):
        quality = pipeline.check_darija_quality(darija)
        if quality >= quality_threshold:
            valid_indices.append(i)
    
    # Filter batch to keep only high-quality samples
    filtered_eng = [eng_texts[i] for i in valid_indices]
    filtered_darija = [darija_texts[i] for i in valid_indices]
    
    # Proceed with training on filtered data
    # ... your training code here ...
```

## Best Practices

1. Data Quality:
   - Set appropriate quality thresholds based on your needs
   - Monitor quality scores distribution
   - Adjust thresholds if needed

2. Validation:
   - Regularly validate training data
   - Monitor translation quality trends
   - Keep track of rejected samples

3. Memory Management:
   - Clear GPU memory regularly
   - Use batch processing for large datasets
   - Monitor memory usage

## Example Usage

```python
# Initialize pipeline
pipeline = DarijaTranslationPipeline()
pipeline.initialize()

# Prepare training data
prepare_training_data(
    'raw_data.txt',
    'filtered_data.json',
    quality_threshold=0.6
)

# Validate translations
eng_text = "Hello, how are you?"
darija_text = "كيف حالك"
results = validate_translation_pair(eng_text, darija_text)

print(f"Darija Quality: {results['darija_quality']:.4f}")
print(f"Translation Quality: {results['eng_to_darija_quality']:.4f}")
print(f"Back Translation: {results['darija_to_eng']}")
```

## Quality Metrics

The pipeline provides several quality metrics:

1. Source Quality:
   - DarijaBERT confidence for source Darija text
   - Helps identify poor quality inputs

2. Translation Quality:
   - DarijaBERT confidence for translated Darija text
   - Helps evaluate translation accuracy

3. Back Translation:
   - Validates translation consistency
   - Helps identify semantic preservation

## Recommendations

1. Start with a high quality threshold (e.g., 0.7) and adjust based on:
   - Data availability
   - Quality requirements
   - Model performance

2. Monitor and log:
   - Quality scores distribution
   - Rejection rates
   - Translation consistency

3. Use the pipeline for:
   - Initial data cleaning
   - Ongoing validation
   - Model evaluation

This pipeline helps ensure high-quality training data and validates translations, leading to more robust bidirectional translation models.
