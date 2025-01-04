---
license: apache-2.0
base_model: 
tags:
- generated_from_trainer
metrics:
- bleu
model-index:
- name: darija_englishV2.1
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# darija_englishV2.1

This model is a fine-tuned version of [](https://huggingface.co/) on an unknown dataset.
It achieves the following results on the evaluation set:
- Loss: 1.3635
- Bleu: 32.8666
- Gen Len: 11.7901

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
- train_batch_size: 10
- eval_batch_size: 10
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 7
- mixed_precision_training: Native AMP

### Training results

| Training Loss | Epoch | Step  | Validation Loss | Bleu    | Gen Len |
|:-------------:|:-----:|:-----:|:---------------:|:-------:|:-------:|
| 1.641         | 1.0   | 1594  | 1.4631          | 29.3791 | 11.6872 |
| 1.2871        | 2.0   | 3188  | 1.3761          | 30.8465 | 12.0999 |
| 1.1067        | 3.0   | 4782  | 1.3503          | 32.7058 | 11.6206 |
| 0.9456        | 4.0   | 6376  | 1.3462          | 32.5581 | 11.8712 |
| 0.8611        | 5.0   | 7970  | 1.3497          | 33.0669 | 11.7258 |
| 0.7806        | 6.0   | 9564  | 1.3601          | 33.2093 | 11.7203 |
| 0.7293        | 7.0   | 11158 | 1.3635          | 32.8666 | 11.7901 |


### Framework versions

- Transformers 4.40.1
- Pytorch 2.3.0+cu121
- Datasets 2.19.0
- Tokenizers 0.19.1
