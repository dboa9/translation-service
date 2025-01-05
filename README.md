# Darija Translation Service

A translation service for Moroccan Darija (Arabic dialect) to English and vice versa, using various machine learning models and datasets.

## Features

- Multiple translation models support
- Dataset management and validation
- Web interface for translation
- Comprehensive testing suite
- EC2 deployment support

## Project Structure

```
├── core/                     # Core functionality
│   ├── interfaces/          # User interfaces
│   ├── translation/         # Translation services
│   ├── dataset/            # Dataset handling
│   └── validation/         # Validation utilities
├── config/                  # Configuration files
├── tests/                   # Test suites
├── deployment/             # Deployment scripts
└── frontend/               # Web interface
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
- Edit `config/credentials.py` with your Hugging Face API token
- Configure model settings in `config/model_config.yaml`

3. Run tests:
```bash
./run_tests.sh
```

4. Start the interface:
```bash
./run_interface.sh
```

## Models

The service supports multiple translation models:
- AnasAber/seamless-darija-eng
- Helsinki-translation-English_Moroccan-Arabic
- And more...

Models are downloaded on-demand and cached locally.

## Development

- Python 3.8+
- Uses Git LFS for large file handling
- Comprehensive test suite in `/tests`
- EC2 deployment scripts in `/deployment`

## License

MIT License
