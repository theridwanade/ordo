import json
from pathlib import Path
from typing import Optional
from .models import SourceConfig

class ConfigManager:
    """Manages configuration persistence and loading."""
    
    def __init__(self, config_file: str = "sources.json"):
        self.config_file = Path(config_file)
    
    def load_last_sources(self) -> Optional[SourceConfig]:
        """Load the last used source configuration."""
        if not self.config_file.exists():
            return None
            
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            return SourceConfig.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None
    
    def save_sources(self, config: SourceConfig) -> None:
        """Save source configuration to file."""
        self.config_file.touch(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config.to_dict(), f, indent=4)
