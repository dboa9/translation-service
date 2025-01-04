---
tags:
- generated_from_trainer
model-index:
- name: Transliteration-Moroccan-Darija
  results: []
datasets:
- atlasia/ATAM
language:
- ar
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# Transliteration-Moroccan-Darija

This model is trained to convert Moroccan Darija text written in Arabizi (Latin script) to Arabic letters. 
Whether you're dealing with informal texts, social media posts, or any other content in Moroccan Arabizi, the model is here to help you accurately transliterate it into Arabic script.

## Model Overview

Our model is built upon the powerful Transformer architecture, leveraging state-of-the-art natural language processing techniques. 
It has been trained from scratch on the "atlasia/ATAM" dataset, specifically for the task of transliterating Moroccan Darija Arabizi into Arabic letters, ensuring high-quality and accurate transliterations.
Furthermore, we trained a BPE Tokenizer specifically for this task.

## Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 3e-05
- train_batch_size: 128
- eval_batch_size: 128
- seed: 42
- gradient_accumulation_steps: 2
- total_train_batch_size: 256
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- lr_scheduler_warmup_ratio: 0.02
- num_epochs: 120

## Framework versions

- Transformers 4.39.2
- Pytorch 2.2.2+cpu
- Datasets 2.18.0
- Tokenizers 0.15.2
  
## Usage

Using our model for transliteration is simple and straightforward. 
You can integrate it into your projects or workflows via the Hugging Face Transformers library. 
Here's a basic example of how to use the model in Python:

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("BounharAbdelaziz/Transliteration-Moroccan-Darija")
model = AutoModelForSeq2SeqLM.from_pretrained("BounharAbdelaziz/Transliteration-Moroccan-Darija")

# Define your Moroccan Darija Arabizi text
input_text = "Your Moroccan Darija Arabizi text goes here."

# Tokenize the input text
input_tokens = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)

# Perform transliteration
output_tokens = model.generate(**input_tokens)

# Decode the output tokens
output_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)

print("Transliteration:", output_text)
```

## Example

Let's see an example of transliterating Moroccan Darija Arabizi to Arabic:

**Input**: "kayn chi"

**Output**: "كاين شي"


## Limiations

This version has some limitations mainly due to the Tokenizer.
We're currently collecting more data with the aim of continous improvements.

## Feedback

We're continuously striving to improve our model's performance and usability and we will be improving it incrementaly. 
If you have any feedback, suggestions, or encounter any issues, please don't hesitate to reach out to us.

