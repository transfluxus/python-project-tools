from functools import lru_cache
from pathlib import Path
import os

from config import CONFIG

@lru_cache
def root():
    current = Path(__file__).parent
    while not (current / ".env").exists():
        current = current.parent
        if current == current.parent:
            raise Exception("root not found")
    os.chdir(current)
    return current

@lru_cache
def project_name() -> str:
    root_dir = root()
    project_name = CONFIG.PROJECT_NAME
    if project_name:
        return project_name
    return root_dir.name

ROOT_PATH = root()