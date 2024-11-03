import json
import logging
import logging.config
import os
from typing import Any

from src.const import PROJECT_PATH, LOG_CONFIG_FILE

default_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "raw": {
            "format": "%(message)s"
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

new_logger_default_config = {
    "level": "DEBUG",
    "handlers": ["console"],
    "propagate": False
}


def init_logger():
    # check if  exists
    if not LOG_CONFIG_FILE.exists():
        print(f"Creating logging config file at: {LOG_CONFIG_FILE}")
        # if not, create it
        LOG_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_CONFIG_FILE.write_text(json.dumps(default_log_config, ensure_ascii=False, indent=2),
                                   encoding="utf-8")


def reload_config() -> dict[str, Any]:
    config_data = json.loads(LOG_CONFIG_FILE.read_text(encoding="utf-8"))
    logging.config.dictConfig(config_data)
    return config_data


def add_logger(name):
    config_data["loggers"][name] = new_logger_default_config
    # write to file
    LOG_CONFIG_FILE.write_text(json.dumps(config_data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_or_create_logger(name: str) -> logging.Logger:
    # if not cls.initialized:
    #     cls.init_logger()
    if name not in config_data["loggers"]:
        add_logger(name)
        logging.config.dictConfig(config_data)
    return logging.getLogger(name)


def get_module_name(file_path: str) -> str:
    """Get the module name based on the file's location in the project."""
    relative_path = os.path.relpath(file_path, PROJECT_PATH)
    module_name = os.path.splitext(relative_path)[0]
    module_name = module_name.replace(os.sep, '.')
    return module_name


def get_b5_logger(file_path: str) -> logging.Logger:
    return get_or_create_logger(get_module_name(file_path))


init_logger()
config_data: dict[str, Any] = reload_config()
