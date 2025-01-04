# Minimal Darija Translation App

A streamlit interface for the AnasAber/seamless-darija-eng translation model.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API token:
- Edit `config/credentials.py`
- Add your Hugging Face API token

3. Test configuration:
```bash
python test_translation.py
```

4. Run the app:
```bash
chmod +x run.sh
./run.sh
```

## Files

- `streamlit_app.py`: Main application interface
- `test_translation.py`: Model configuration test
- `requirements.txt`: Python dependencies
- `run.sh`: Startup script
- `config/credentials.py`: API token configuration

## Model Configuration

- Model: AnasAber/seamless-darija-eng
- Task: text2text-generation
- Language Codes:
  * English: "eng"
  * Darija: "ary"
- Tokenizer: SeamlessM4TTokenizer

## Directory Structure

```
minimal_app/
├── streamlit_app.py
├── test_translation.py
├── requirements.txt
├── run.sh
├── README.md
├── config/
│   └── credentials.py
├── cache/  (created by run.sh)
└── logs/   (created by run.sh)
