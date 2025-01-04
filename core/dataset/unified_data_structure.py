# File: unified_data_structure.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class UnifiedDataSample:
    english: str
    darija: str
    source: Optional[str] = None
    id: Optional[str] = None
    includes_arabizi: Optional[bool] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedDataset:
    samples: List[UnifiedDataSample]
    name: str
    subset: Optional[str] = None


def convert_atlasia_to_unified(
    atlasia_sample: Dict[str, Any],
    subset: str
) -> UnifiedDataSample:
    unified_sample = UnifiedDataSample(
        english=atlasia_sample.get('english', ''),
        darija=atlasia_sample.get('darija', ''),
        source=atlasia_sample.get('source', subset),
        id=atlasia_sample.get('id'),
    )
    
    # Add any additional fields to metadata
    for key, value in atlasia_sample.items():
        if key not in ['english', 'darija', 'source', 'id']:
            unified_sample.metadata[key] = value
    
    return unified_sample


def convert_new_dataset_to_unified(
    new_sample: Dict[str, Any]
) -> UnifiedDataSample:
    return UnifiedDataSample(
        english=new_sample['english'],
        darija=new_sample['darija'],
        includes_arabizi=new_sample['includes_arabizi']
    )
