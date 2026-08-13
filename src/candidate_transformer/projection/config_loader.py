import json
import os
from candidate_transformer.models.config import OutputConfig

class ConfigError(Exception):
    pass

def load_config(path: str) -> OutputConfig:
    if not os.path.exists(path):
        raise ConfigError(f"Config file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return OutputConfig.model_validate(data)
    except Exception as e:
        raise ConfigError(f"Invalid config at {path}: {e}")