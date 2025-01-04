
---
language:
- ar
- en
tags:
- darija
- moroccan arabic
- english
- translation
- llama
license: mit
pipeline_tag: text2text-generation
---

# MoroccanDarija-Llama-3.1-8B

This model translates Moroccan Darija (Moroccan Arabic) to English. It's based on the Llama 3.1 8B model, fine-tuned on a dataset of Darija-English sentence pairs.

## Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "Anassk/MoroccanDarija-Llama-3.1-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def translate(text):
    inputs = tokenizer(f"Translate the following Darija text to English: {text}", return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example usage
darija_text = "واش كاين شي حد هنا كيهضر الدارجة؟"
print(translate(darija_text))
```

## Model Details

- Base Model: Llama 3.1 8B
- Fine-tuned for: Moroccan Darija to English translation
- Suitable for: Conversational Moroccan Arabic, everyday phrases, and general text

## Limitations

This model's performance may vary depending on the complexity and specific dialect of the input Darija text. It works best with standard Moroccan Darija phrases and sentences. Highly colloquial or region-specific expressions may pose challenges.
