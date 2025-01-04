---
license: apache-2.0
base_model: 
language:
- ar
- en
pipeline_tag: translation
widget:
- text: "salam ,labas ?"
- text: " kanbghik bzaf"
---
---
license: apache-2.0
base_model: 




# This model's role is to translate Daraija with Latin words or Arabizi into English. It was trained on 170,000 rows of translation examples.

This model is a fine-tuned version of [](https://huggingface.co/) on anDarija Open Dataset (DODa), an ambitious open-source project dedicated to the Moroccan dialect. With about 150,000 entries, DODa is arguably the largest open-source collaborative project for Darija <=> English translation built for Natural Language Processing purposes.



### Training hyperparameters

The following hyperparameters were used during training:
- GPU : H100 80GB SXM5
- train_batch_size: 32
- eval_batch_size: 32
- num_epochs: 5
- mixed_precision_training: True FP16 enabled