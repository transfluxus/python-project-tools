"""
SHOULD NOT IMPORT ANY OTHER TOOL
"""
import os
import traceback
from functools import lru_cache
from pathlib import Path
from typing import Optional

__SET_ROOT: Path = None
__FIRST_ROOT_STACK_TRACE = None


@lru_cache
def root(module_path_str: Optional[str] = None) -> Path:
    global __SET_ROOT, __FIRST_ROOT_STACK_TRACE
    if __SET_ROOT and not module_path_str:
        return __SET_ROOT
    elif not module_path_str:
        module_path_str = "."
    else:
        if __FIRST_ROOT_STACK_TRACE:
            raise Exception(f"root can only be set once FIRST CALL LOCATION:\n\n {__FIRST_ROOT_STACK_TRACE}")
        __FIRST_ROOT_STACK_TRACE = ''.join(traceback.format_stack()[:-1])
    current = Path(module_path_str).absolute()
    if current.is_file():
        # print("WARNING: module_path_str is required first time calling root")
        current = Path(module_path_str).absolute().parent
    while not (current / ".env").exists():
        current = current.parent
        if current == current.parent:
            raise Exception("root not found. Maybe '.env' missing")
    os.chdir(current)
    __SET_ROOT = current
    root.cache_clear()
    return current
