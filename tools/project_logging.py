"""
Project-wide logging configuration module.

This module provides a centralized way to manage logging configuration across a project.
It supports:
- JSON-based logging configuration
- Dynamic logger creation
- Module-based logger naming
- Automatic configuration file management
"""

import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Optional

# Default logging configuration
DEFAULT_LOG_CONFIG = {
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
    "loggers": {},
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

DEFAULT_LOGGER_CONFIG = {
    "level": "DEBUG",
    "handlers": ["console"],
    "propagate": False
}


class LoggingManager:
    """
    Manages project-wide logging configuration and logger creation.
    """

    def __init__(self, config_path: Path, project_root: Path):
        """
        Initialize the logging manager.

        Args:
            config_path: Path to the logging configuration file
            project_root: Root path of the project for module name resolution
        """
        self.config_path = config_path
        self.project_root = project_root
        self.config_data: Optional[dict[str, Any]] = None
        self.initialized = False

    def init_logging(self) -> None:
        """
        Initialize logging configuration. Creates default config file if it doesn't exist.
        """
        if not self.config_path.exists():
            print(f"Creating logging config file at: {self.config_path}")
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(
                json.dumps(DEFAULT_LOG_CONFIG, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        self.reload_config()
        self.initialized = True

    def reload_config(self) -> None:
        """
        Reload logging configuration from file and apply it.

        Raises:
            json.JSONDecodeError: If config file contains invalid JSON
            OSError: If config file cannot be read
        """
        try:
            self.config_data = json.loads(self.config_path.read_text(encoding="utf-8"))
            logging.config.dictConfig(self.config_data)
        except (json.JSONDecodeError, OSError) as e:
            logging.error(f"Failed to load logging config: {e}")
            self.config_data = DEFAULT_LOG_CONFIG.copy()
            logging.config.dictConfig(self.config_data)

    def add_logger(self, name: str) -> None:
        """
        Add a new logger configuration.

        Args:
            name: Name of the logger to add
        """
        if not self.config_data:
            self.reload_config()

        self.config_data["loggers"][name] = DEFAULT_LOGGER_CONFIG.copy()
        try:
            self.config_path.write_text(
                json.dumps(self.config_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logging.config.dictConfig(self.config_data)
        except OSError as e:
            logging.error(f"Failed to save logger configuration: {e}")

    def get_or_create_logger(self, name: str) -> logging.Logger:
        """
        Get an existing logger or create a new one if it doesn't exist.

        Args:
            name: Name of the logger to get or create

        Returns:
            logging.Logger: Configured logger instance
        """
        if not self.initialized:
            self.init_logging()

        if not self.config_data or name not in self.config_data["loggers"]:
            self.add_logger(name)
        return logging.getLogger(name)

    def get_module_name(self, file_path: str) -> str:
        """
        Get the module name based on the file's location in the project.

        Args:
            file_path: Absolute path to the Python file

        Returns:
            str: Module name in dot notation
        """
        try:
            relative_path = os.path.relpath(file_path, self.project_root)
            module_name = os.path.splitext(relative_path)[0]
            return module_name.replace(os.sep, '.')
        except ValueError as e:
            logging.warning(f"Could not resolve module name for {file_path}: {e}")
            return os.path.splitext(os.path.basename(file_path))[0]

    def get_file_logger(self, file_path: str) -> logging.Logger:
        """
        Get a logger for a specific file using its module path.

        Args:
            file_path: Absolute path to the Python file

        Returns:
            logging.Logger: Configured logger instance
        """
        return self.get_or_create_logger(self.get_module_name(file_path))


# Global instance
_manager: Optional[LoggingManager] = None


def initialize_logging(config_path: Path, project_root: Path) -> None:
    """
    Initialize the global logging manager.

    Args:
        config_path: Path to the logging configuration file
        project_root: Root path of the project
    """
    global _manager
    _manager = LoggingManager(config_path, project_root)
    _manager.init_logging()


def get_logger(file_path: str) -> logging.Logger:
    """
    Get a logger for the specified file.

    Args:
        file_path: Absolute path to the Python file

    Returns:
        logging.Logger: Configured logger instance

    Raises:
        RuntimeError: If logging hasn't been initialized
    """
    if _manager is None:
        raise RuntimeError("Logging not initialized. Call initialize_logging first.")
    return _manager.get_file_logger(file_path)