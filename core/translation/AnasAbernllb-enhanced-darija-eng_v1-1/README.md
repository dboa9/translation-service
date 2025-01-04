---
base_model:
- facebook/nllb-200-3.3B
datasets:
- AnasAber/DoDA_sentences_darija_english
language:
- en
library_name: transformers
pipeline_tag: text2text-generation
tags:
- darija
- translation
- moroccan_arabic
- english_darija
- NLP
- Machine translation
- nllb
- facebook
- fine tuning
---
# NLLB Enhanced Darija-English Translation Model

This is an **ongoing project**, constantly improving as the model is training on more data.

## Model Details

- **Model Name**: nllb-enhanced-darija-eng_v1.1
- **Base Model**: facebook/nllb-200-3.3B
- **Model Type**: Fine-tuned translation model
- **Languages**: Moroccan Arabic (Darija) ↔ English
- **Developer**: Anas ABERCHIH

## Model Description

This model is a fine-tuned version of Facebook's NLLB-200 3.3B model, specifically optimized for translation between Moroccan Arabic (Darija) and English. 
It leverages the power of the base NLLB model while being tailored for the nuances of Darija, making it particularly effective for Moroccan Arabic to English translations and vice versa.

### Training Data


For now, the model is trained on a dataset of 40,000 sentence pairs:

- Training set: 32,780 pairs
- Validation set: 5,785 pairs
- Test set: 6,806 pairs

Each entry in the dataset contains:
- Darija text (Arabic script)
- English translation

### Training Procedure

- **Training Duration**: Approximately 5 hours (18,053 seconds)
- **Number of Epochs**: 5
- **Final Training Loss**: 1.5218
- **Training Samples per Second**: 9.078
- **Training Steps per Second**: 0.071

## Intended Use

This model is intended to be used directly for translating text from Moroccan Arabic (Darija) to English.
It can be deployed in various applications requiring translation services.
### Direct Use

This model is designed for:
1. Translating Moroccan Arabic (Darija) text to English
2. Translating English text to Moroccan Arabic (Darija)

It can be particularly useful for:
- Localization of content for Moroccan audiences
- Cross-cultural communication between Darija speakers and English speakers
- Assisting in the understanding of Moroccan social media content, informal writing, or dialect-heavy texts

### Downstream Use

The model can be integrated into various applications, such as:
- Machine translation systems focusing on Moroccan content
- Chatbots or virtual assistants for Moroccan users
- Content analysis tools for Moroccan social media or web content
- Educational tools for language learners (both Darija and English)

## Limitations and Bias
The model's performance may be influenced by biases present in the training data, such as the representation of certain dialectal variations or cultural nuances. 
Additionally, the model's accuracy may vary depending on the complexity of the text being translated and the presence of out-of-vocabulary words.

### Out-of-Scope Use

This model should not be used for:
1. Legal or medical translations where certified human translators are required
2. Translating other Arabic dialects or Modern Standard Arabic (MSA) to English (or vice versa)
3. Understanding or generating spoken language directly (it's designed for text)

### Recommendations

- Always review the output for critical applications, especially when dealing with nuanced or context-dependent content
- Be aware that the model may not capture all regional variations within Moroccan Arabic
- For formal or professional content, consider post-editing by a human translator

## How to Get Started

To use this model:

1. Install the Transformers library:
   ```
   pip install transformers
   ```

2. Load the model and tokenizer:
   ```python
   from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
   
   model_name = "AnasAber/nllb-enhanced-darija-eng_v1.1"
   model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
   tokenizer = AutoTokenizer.from_pretrained(model_name)
   ```

3. Translate text:
   ```python
   def translate(text, src_lang, tgt_lang):
       inputs = tokenizer(text, return_tensors="pt")
       translated = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang])
       return tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
   
   # Darija to English
   darija_text = "كيفاش نقدر نتعلم الإنجليزية بسرعة؟"
   english_translation = translate(darija_text, src_lang="ary_Arab", tgt_lang="eng_Latn")
   print(english_translation)
   
   # English to Darija
   english_text = "How can I learn English quickly?"
   darija_translation = translate(english_text, src_lang="eng_Latn", tgt_lang="ary_Arab")
   print(darija_translation)
   ```

Remember to handle exceptions and implement proper error checking in production environments.

## Ethical Considerations

- Respect privacy and data protection laws when using this model with user-generated content
- Be aware of potential biases in the training data that may affect translations
- Use the model responsibly and avoid applications that could lead to discrimination or harm

## Citations

[Include any relevant citations or references here]

## Contact Information

For questions or feedback about this model, please contact Anas ABERCHIH at [https://www.linkedin.com/in/anas-aberchih-%F0%9F%87%B5%F0%9F%87%B8-b6007121b/] or [https://github.com/AnasAber].