from os.path import join
from pathlib import Path
from typing import Dict, Any
from dotenv import dotenv_values

# load .env file from project root
env_path = join(Path(__file__).parent.parent, ".env")
env_config = dotenv_values(dotenv_path=env_path)

# Default configuration
DEFAULT_CONFIG = {
    "PIC_PATH": "plantmon/pics",
    "INTERVAL_LENGTH": 120,
}


def get_config() -> Dict[str, Any]:
    """Load configuration from environment variables with defaults"""
    config = DEFAULT_CONFIG.copy()

    # Override with values from .env, NOT all env vars
    config.update(env_config)

    # Convert non-strings bc env vars are always str
    int_keys = ["INTERVAL_LENGTH", "SENSOR_MAX_RETRIES"]
    for key in int_keys:
        if key in config and isinstance(config[key], str):
            config[key] = int(config[key])

    return config


# refer to this config when importing
config = get_config()