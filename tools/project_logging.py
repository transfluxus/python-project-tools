"""
Project-wide logging configuration module.

This module provides a centralized way to manage logging configuration across a project.
Features:
- Automatic initialization on import
- JSON-based logging configuration
- Dynamic logger creation
- Module-based logger naming
- Automatic configuration file management
- File-based logging with rotation

Example:
    ```python
    from tools.project_logging import get_logger

    logger = get_logger(__file__)
    logger.info("This is a log message")
    ```
"""

import json
import logging
import logging.config
import logging.handlers
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

from tools.data_folder import base_data_folder
from tools.env_root import root
from tools.files import save_json

# Default logging configuration with file handlers
DEFAULT_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "raw": {
            "format": "%(message)s"
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    },
    "loggers": {},
    "root": {
        "level": "INFO",
        "handlers": ["console", "file_handler", "error_file_handler"]
    }
}

DEFAULT_LOGGER_CONFIG = {
    "level": "INFO",
    "handlers": ["console", "file_handler", "error_file_handler"],
    "propagate": False
}


class LoggingManager:
    """
    Manages project-wide logging configuration and logger creation.

    @param config_path: Path - Path to the logging configuration file
    @param project_root: Path - Root path of the project for module name resolution
    @type config_path: Path
    @type project_root: Path
    """
    _instance = None

    def __new__(cls, *args, **kwargs) -> "LoggingManager":
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_root: Optional[Path] = None, config_path: Optional[Path] = None):
        # Setup log directory structure using create_data_folder
        from tools.data_folder import create_data_folder
        from tools.mkdir import SmartPath
        self.log_dir = create_data_folder("logs")

        self.config_path: SmartPath
        if not project_root:
            project_root = root()
        if config_path:
            self.config_path = SmartPath(config_path)
        else:
            self.config_path = SmartPath(base_data_folder() / "log_conf.json", **{"data": DEFAULT_LOG_CONFIG})
        self.config_path / ("txt-logs", "create", DEFAULT_LOG_CONFIG)
        # self.config_path = config_path
        self.project_root = project_root
        self.config_data: Optional[dict[str, Any]] = None
        self.initialized = False
        self.orig_handler_filenames: dict[str, Path] = {}
        self.init_logging()

    def init_logging(self) -> None:
        """
        Initialize logging configuration. Creates default config file if it doesn't exist.

        @return: None
        @rtype: None
        """
        if not self.config_path.exists():
            logging.info(f"Creating logging config file at: {self.config_path}")
            save_json(self.config_path, DEFAULT_LOG_CONFIG)
        self.reload_config()
        self.initialized = True

    def reload_config(self) -> None:
        """
        Reload logging configuration from file and apply it.

        @raises json.JSONDecodeError: If config file contains invalid JSON
        @raises OSError: If config file cannot be read
        """
        try:
            self.config_data = json.loads(self.config_path.read_text(encoding="utf-8"))
            for handler_name, handler in self.config_data["handlers"].items():
                if "filename" in handler:
                    file_path = Path(handler["filename"])
                    self.orig_handler_filenames[handler_name] = file_path
                    if not file_path.is_absolute():
                        handler["filename"] = str(self.log_dir / file_path)
            logging.config.dictConfig(self.config_data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Failed to load logging config: {e}")  # Use print since logging isn't configured yet
            self.config_data = DEFAULT_LOG_CONFIG.copy()
            logging.config.dictConfig(self.config_data)
        except TypeError as e:
            print(f"Failed to load logging config: {e}")  # Use print since logging isn't configured yet
            #print(self.config_data)
            logging.config.dictConfig(self.config_data)

    def add_logger(self, name: str) -> None:
        """
        Add a new logger configuration.

        @param name: Name of the logger to add
        @type name: str
        """
        if not self.config_data:
            self.reload_config()

        if name not in self.config_data["loggers"]:
            self.config_data["loggers"][name] = DEFAULT_LOGGER_CONFIG.copy()
            config_copy = deepcopy(self.config_data)
            try:
                # make handler-filenames relative again:
                for handler_name, handler in config_copy["handlers"].items():
                    if "filename" in handler:
                        handler["filename"] = str(self.orig_handler_filenames[handler_name])
                save_json(self.config_path, config_copy)
                logging.config.dictConfig(self.config_data)
            except OSError as e:
                logging.error(f"Failed to save logger configuration: {e}")

    def get_or_create_logger(self, name: str) -> logging.Logger:
        """
        Get an existing logger or create a new one if it doesn't exist.

        @param name: Name of the logger to get or create
        @type name: str
        @return: Configured logger instance
        @rtype: logging.Logger
        """
        if not self.initialized:
            self.init_logging()

        if not self.config_data or name not in self.config_data["loggers"]:
            self.add_logger(name)
        return logging.getLogger(name)

    def get_module_name(self, file_path: str) -> str:
        """
        Get the module name based on the file's location in the project.

        @param file_path: Absolute path to the Python file
        @type file_path: str
        @return: Module name in dot notation
        @rtype: str
        """
        try:
            relative_path = os.path.relpath(file_path, self.project_root)
            module_name = os.path.splitext(relative_path)[0]
            dotted = module_name.replace(os.sep, '.')
            dotted = re.compile("\\.+").sub(".",dotted)
            return dotted
        except ValueError as e:
            logging.warning(f"Could not resolve module name for {file_path}: {e}")
            return os.path.splitext(os.path.basename(file_path))[0]

    def get_file_logger(self, file_path: str) -> logging.Logger:
        """
        Get a logger for a specific file using its module path.

        @param file_path: Absolute path to the Python file
        @type file_path: str
        @return: Configured logger instance
        @rtype: logging.Logger
        """
        return self.get_or_create_logger(self.get_module_name(file_path))


# Global instance - automatically initialized on module import
# _manager = LoggingManager()

def get_logger(file_path: str) -> logging.Logger:
    """
    Get a logger for the specified file.

    @param file_path: Absolute path to the Python file
    @type file_path: str
    @return: Configured logger instance
    @rtype: logging.Logger
    """
    if not "/" in file_path and not file_path.endswith(".py"):
        file_path = file_path.replace(".", "/") + ".py"
    if "site-packages" in file_path:
        fp_parts = file_path.split("/")
        fp_parts = fp_parts[fp_parts.index("site-packages")+1:]
        file_path = "/".join(fp_parts)
    return LoggingManager(None).get_file_logger(file_path)


def get_model_logger(clz: Any, extra: Optional[str] = None) -> logging.Logger:
    _extra = f"-[{extra}]" if extra else ""
    try:
        module_name = clz.__module__
        clz_name = clz.__name__
    except Exception as err:
        logger = get_logger(__file__)
        logger.error(f"Could not resolve module name for {clz}: {err}")
        module_name = "unknown"
        clz_name =str(clz)
    return get_logger(f"{module_name}.{clz_name}{_extra}")


# Test the logger when run as main
if __name__ == "__main__":
    logger = get_logger(__file__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
