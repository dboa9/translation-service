from pathlib import Path
from .hf_base_loader import HFBaseLoader

class HFBaseLoaderWrapper(HFBaseLoader):
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent.parent
        super().__init__(base_dir=str(project_root))
