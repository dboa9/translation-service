---
license: apache-2.0
base_model: 
tags:
- generated_from_trainer
metrics:
- bleu
model-index:
- name: darija-latin-to-english-new
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# darija-latin-to-english-new

This model is a fine-tuned version of [](https://huggingface.co/) on the None dataset.
It achieves the following results on the evaluation set:
- Loss: 0.0525
- Bleu: 29.8636
- Gen Len: 8.8467

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 2e-05
- train_batch_size: 32
- eval_batch_size: 32
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 5
- mixed_precision_training: Native AMP

### Training results

| Training Loss | Epoch | Step | Validation Loss | Bleu    | Gen Len |
|:-------------:|:-----:|:----:|:---------------:|:-------:|:-------:|
| 0.0219        | 5.0   | 1400 | 0.0525          | 29.8636 | 8.8467  |


### Framework versions

- Transformers 4.38.1
- Pytorch 2.1.2
- Datasets 2.1.0
- Tokenizers 0.15.2
