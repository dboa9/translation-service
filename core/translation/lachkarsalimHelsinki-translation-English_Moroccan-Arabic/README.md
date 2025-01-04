---
language:
- en
- ar
---
Model Description :
This model is a fine-tuned version of a Transformer Model Helsinki-en-ar, adapted to translate text from English to Darija (Moroccan Arabic) . The fine-tuning process was conducted on a substantial dataset.

Fine-tuning Details
Source Model: Helsinki-NLP/opus-mt-en-ar
Fine-tuning Objective: To adapt the pre-existing English to Arabic translation model to perform translations from English to Arabic Darija .
Dataset: The model was fine-tuned using the Darija Open Dataset (DODa), an open-source project dedicated to the Moroccan dialect. DODa contains approximately 150,000 entries, making it one of the largest open-source collaborative projects for Darija <=> English translation aimed at Natural Language Processing (NLP) applications.
Training Examples: More than 15,000 translation pairs from Darija to Arabic were used for fine-tuning.
Training Time: The fine-tuning process took approximately 8 hours to complete


Acknowledgments :
I would like to acknowledge the contributors to the Darija Open Dataset (DODa) for providing an extensive and valuable resource for training this model. Their effort in building the largest open-source Darija dataset has significantly facilitated research and development in NLP applications tailored to Moroccan Arabic.