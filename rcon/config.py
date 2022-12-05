import logging
import os
from pathlib import Path

import yaml
from cachetools.func import ttl_cache

logger = logging.getLogger(__name__)


@ttl_cache(600)
def get_config():
    root = os.getenv("CONFIG_DIR", "config/")
    default_config_path = Path(root) / Path("default_config.yml")
    server_config_path = Path(root) / Path(
        f'config_{os.getenv("SERVER_NUMBER", 0)}.yml'
    )
    if server_config_path.exists():
        user_config_path = server_config_path
    else:
        user_config_path = Path(root) / Path("config.yml")
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
            logger.info("Loading config: %s", user_config_path)
            user_config = yaml.safe_load(stream=f)
    except FileNotFoundError:
        logger.warning("No user config found, defaults only are loaded")
    except yaml.YAMLError:
        logger.error("User config at '%s' is invalid YAML", str(user_config_path))

    config.update(user_config)
    return config
