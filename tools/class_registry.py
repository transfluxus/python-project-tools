import sys
import inspect
import importlib.util
from pathlib import Path
from typing import Dict, Type, TypeVar, Optional

T = TypeVar('T')


class Registry:
    """Registry that works relative to where it's instantiated"""

    def __init__(self, base_path: Optional[str] = None):
        self._classes: Dict[str, Type] = {}

        # If no base_path provided, use the caller's location
        if base_path is None:
            caller_frame = inspect.currentframe().f_back
            caller_file = caller_frame.f_globals.get('__file__')
            if caller_file:
                self.base_path = Path(caller_file).parent
            else:
                self.base_path = Path.cwd()
        else:
            self.base_path = Path(base_path)

    def register(self, name: str):
        """Decorator to register a class"""

        def decorator(class_obj: Type[T]) -> Type[T]:
            self._classes[name] = class_obj
            class_obj._registry_name = name
            return class_obj

        return decorator

    def load_from_path(self, path: Path):
        """Load module from file path - triggers decorator registration"""
        if not path.is_absolute():
            _path = self.base_path / path

        sys.path.insert(0, path.parent.as_posix())
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        finally:
            sys.path.pop(0)

    def load_instances(self, folder: str = "instances"):
        """Load all modules from instances folder relative to base_path"""
        instances_path = self.base_path / folder

        if not instances_path.exists():
            print(f"No {folder} folder found at {instances_path}")
            return

        for py_file in instances_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            self.load_from_path(py_file)

    def get(self, name: str) -> Optional[Type]:
        return self._classes.get(name)

    def create(self, name: str, *args, **kwargs):
        class_obj = self.get(name)
        return class_obj(*args, **kwargs) if class_obj else None

    def list_all(self) -> list[str]:
        return list(self._classes.keys())