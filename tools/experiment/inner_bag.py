import shutil
from pathlib import Path

import bagit


class MBag():

    def __init__(self, path: Path, bag: bagit.Bag):
        self._path = path
        self._bag = bag

    @property
    def data_path(self) -> Path:
        return Path(self._path) / "data"

    def add_paths(self, paths: list[Path], source: list[str] = None):
        if not self._bag.is_valid():
            print(f"invalid bag {self._path}. Cannot add paths.")

        if not source:
            source = ["copy"] * len(paths)

        for file, source_type in zip(paths, source):
            if source_type == "move":
                shutil.move(file, self._path / "data")
            elif source_type == "copy":
                if file.is_dir():
                    shutil.copytree(file, self.data_path/ file.name)
                else:
                    shutil.copy2(file,self.data_path / file.name)
            elif source_type == "copy_cache":
                # todo also if it changed. so update
                if not (self.data_path / file).exists():
                    shutil.copy2(file, self.data_path)

        self._bag.save(manifests=True)

# something which allows, to add folders/files, and it will update the bag /manifest accordingly with the right policies and schema