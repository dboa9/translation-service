---
license: cc-by-nc-4.0
base_model: facebook/nllb-200-distilled-600M
tags:
- generated_from_trainer
model-index:
- name: darija-to-english-2
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# darija-to-english-2

This model is a fine-tuned version of [facebook/nllb-200-distilled-600M](https://huggingface.co/facebook/nllb-200-distilled-600M) on the None dataset.
It achieves the following results on the evaluation set:
- eval_loss: 0.8135
- eval_bleu: 64.1706
- eval_gen_len: 25.2214
- eval_runtime: 1276.1391
- eval_samples_per_second: 5.048
- eval_steps_per_second: 0.632
- epoch: 3.0
- step: 9663

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 0.0002
- train_batch_size: 8
- eval_batch_size: 8
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 5
- mixed_precision_training: Native AMP

### Framework versions

- Transformers 4.37.0
- Pytorch 2.1.2
- Datasets 2.1.0
- Tokenizers 0.15.1
