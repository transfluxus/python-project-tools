"""
SHOULD NOT IMPORT ANY OTHER TOOL
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

#from _config import CONFIG

__SET_ROOT:Path= None

@lru_cache
def root(module_path_str: Optional[str] = None) -> Path:
    global __SET_ROOT
    if __SET_ROOT:
        return __SET_ROOT
    elif not module_path_str:
        module_path_str = "."
        # print("WARNING: module_path_str is required first time calling root")
    current = Path(module_path_str).absolute().parent
    while not (current / ".env").exists():
        current = current.parent
        if current == current.parent:
            raise Exception("root not found")
    os.chdir(current)
    __SET_ROOT = current
    return current


# @lru_cache
# def project_name() -> str:
#     root_dir = root()
#     project_name = CONFIG.PROJECT_NAME
#     if project_name:
#         return project_name
#     return root_dir.name


#ROOT_PATH = root()
