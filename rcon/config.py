import yaml
import logging
import os
from pathlib import Path
from cachetools.func import ttl_cache

logger = logging.getLogger(__name__)


@ttl_cache(600)
def get_config():
    root = os.getenv('CONFIG_DIR', 'config/')
    default_config_path = Path(root) / Path('default_config.yml')
    user_config_path = Path(root) / Path('config.yml')
    user_config = {}
    try:
        with default_config_path.open() as f:
            config = yaml.safe_load(stream=f)
    except FileNotFoundError:
        logger.error("Unable to open default config at %s", str(default_config_path))
        raise
    except yaml.YAMLError:
        logger.error("Default config is invalid YAML")
        raise
    try:
        with user_config_path.open() as f:
            user_config = yaml.safe_load(stream=f)
    except FileNotFoundError:
        logger.warning("No user config found, defaults only are loaded")
    except yaml.YAMLError:
        logger.error("User config at '%s' is invalid YAML", str(user_config_path))
        raise

    config.update(user_config)
    return config