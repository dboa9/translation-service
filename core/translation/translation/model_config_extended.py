"""
Extended Model Configuration for Translation Service
"""

from typing import Dict, Any
from ..model_config import MODEL_CONFIG

EXTENDED_MODEL_CONFIG: Dict[str, Any] = {
    **MODEL_CONFIG,
    "additional_models": {
        "AnasAber/seamless-darija-eng": {
            "model_family": "seamless",
            "direction": "both",
            "description": "Seamless Enhanced Darija-English Translation Model",
            "use_case": ["translation"],
            "trusted": True,
            "source_lang": "ary",
            "target_lang": "eng",
            "model_max_length": 512,
            "special_tokens": {
                "eos_token": "</s>",
                "unk_token": "<unk>",
                "pad_token": "<pad>"
            }
        }
    }
}
