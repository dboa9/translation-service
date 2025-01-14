# Darija-English Translation Model Deployment Guide

This guide outlines the process for testing the model locally, deploying to EC2, and starting model training.

## Prerequisites

1. Local Environment:
   - Conda environment activated: `/mnt/c/conda_envs/myenv`
   - All requirements installed: `pip install -r requirements.txt`
   - Sufficient disk space (check with `df -h`)

2. EC2 Environment:
   - AWS EC2 instance with Deep Learning AMI
   - Sufficient storage (recommended: 100GB+)
   - GPU support (recommended: p3.2xlarge or better)
   - SSH key pair for access

## Stage 1: Local Testing

1. Activate conda environment:
   ```bash
   conda activate /mnt/c/conda_envs/myenv
   ```

2. Run the test suite:
   ```bash
   # Run dataset handler tests
   python -m unittest tests/test_dataset_handlers.py -v
   
   # Run data loading tests
   python tests/lightweight_data_load_test.py
   
   # Run dataset validation
   python validation/scripts/dataset-cache-validator.py
   ```

3. Verify test results:
   - Check logs in `logs/` directory
   - Ensure all tests pass
   - Address any validation issues

## Stage 2: EC2 Deployment

1. Make deployment script executable:
   ```bash
   chmod +x deployment/scripts/local_to_ec2_deployment.sh
   ```

2. Run deployment script:
   ```bash
   ./deployment/scripts/local_to_ec2_deployment.sh
   ```
   
   When prompted:
   - Enter your EC2 instance IP
   - Provide path to your EC2 key file

3. Verify deployment:
   - Connect to EC2: `ssh -i <key-file> ubuntu@<ec2-ip>`
   - Check files in `~/darija_project/`
   - Verify directory structure matches local setup

## Stage 3: Model Training

1. Connect to EC2 instance:
   ```bash
   ssh -i <key-file> ubuntu@<ec2-ip>
   ```

2. Navigate to project directory:
   ```bash
   cd ~/darija_project
   ```

3. Start training:
   ```bash
   # For full training with hyperparameter optimization
   python3 darija_english_model_claud_deep_seek_gpt_ec2.py --mode train --n_trials 10
   
   # For resuming from checkpoint
   python3 darija_english_model_claud_deep_seek_gpt_ec2.py --mode train --resume_from_checkpoint
   ```

4. Monitor training:
   - Check logs in `logs/` directory
   - Monitor GPU usage: `nvidia-smi`
   - View TensorBoard metrics:
     ```bash
     tensorboard --logdir=model_output/logs
     ```

## Troubleshooting

1. Dataset Loading Issues:
   - Check disk space: `df -h`
   - Verify cache directory permissions
   - Check dataset validation logs

2. GPU Issues:
   - Verify CUDA availability: `nvidia-smi`
   - Check GPU memory usage
   - Clear CUDA cache if needed

3. Training Issues:
   - Check learning rate and batch size
   - Monitor loss values
   - Verify model checkpoints are saving

4. Memory Issues:
   - Reduce batch size
   - Enable gradient checkpointing
   - Monitor memory usage: `free -h`

## Important Notes

1. Data Management:
   - Regular backups of model checkpoints
   - Monitor disk usage during training
   - Clean up old checkpoints if needed

2. Performance Optimization:
   - Adjust batch size based on GPU memory
   - Monitor training metrics
   - Use gradient accumulation for large models

3. Security:
   - Keep EC2 key secure
   - Update security group rules
   - Monitor EC2 usage and costs

## Next Steps

After successful deployment and initial training:

1. Evaluate model performance:
   - Check BLEU scores
   - Validate translations
   - Compare with baseline models

2. Fine-tune hyperparameters:
   - Adjust learning rate
   - Modify batch sizes
   - Tune model-specific parameters

3. Prepare for production:
   - Set up model serving
   - Implement monitoring
   - Plan scaling strategy

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages
3. Monitor system resources
4. Document any recurring issues

Remember to regularly backup your data and model checkpoints during the training process.
