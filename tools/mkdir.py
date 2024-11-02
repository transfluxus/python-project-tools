import logging
import re
import shutil
from pathlib import Path
from typing import Union, TypedDict, Literal

import bagit
from pydantic.v1 import PathNotExistsError

from tools.experiment.inner_bag import MBag

logger = logging.getLogger(__name__)

exist_literal = Literal["error", "overwrite", "must_exist"]
source_handling_literal = Literal["move", "copy", "copy_cache"]

class SmrtPathKws(TypedDict):
    exists: exist_literal


class SmartPath(type(Path()), ):
    """
    An enhanced Path class that automatically creates directories and provides
    intuitive path joining using the division operator.

    Features:
    - Automatic directory creation when instantiated
    - Division operator (/) for path joining
    - Type hinting support
    - Maintains all standard pathlib.Path functionality
    """

    def __new__(cls, *args, **kwargs):
        # Create the path object using the parent class
        if isinstance(args, tuple) and len(args) > 0:
            return super().__new__(cls, args[0], **kwargs)
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs: SmrtPathKws):
        # Initialize using parent's init
        super().__init__()

        exists = kwargs.get("exist")
        self.valid = False

        if not exists:
            # logger.warning(f"exists keyword missing for {self}. Path not valid")
            exists = "create"

        if not self.exists():
            if exists == "must_exist":
                raise PathNotExistsError(path=self.absolute())
            elif exists == "version":
                self = self.versioned()
                # self.mkdir(parents=True)
            else:  # elif exists == "create":
                self.mkdir(parents=True)
        else:
            if exists == "error":
                raise FileExistsError(self)
            elif exists == "overwrite":
                logger.debug(f"overwriting {self}")
                shutil.rmtree(self)
            else:  # ignore
                self.valid = True

    def __truediv__(self, key: Union[
        str, Path, 'SmartPath', tuple[exist_literal, Union[str, Path, 'SmartPath']]]) -> 'SmartPath':
        """
        Override the division operator to join paths and create directories.

        Args:
            key: Path component to join (string or Path-like object)

        Returns:
            SmartPath: A new SmartPath instance for the joined path
        """
        if isinstance(key, tuple):
            return SmartPath(super().__truediv__(key[1]), {"exist": key[0]})
        else:
            return SmartPath(super().__truediv__(key), {"exists": "must_exist"})

    def read(self, encoding: str = "utf-8") -> str:
        return self.read_text(encoding=encoding)

    # CreateBag(Protocol)
    def get_path(self) -> Path:
        return self

    def create_bag(self, info: dict) -> MBag:
        bag = bagit.make_bag(self, info)
        return MBag(self, bag)

    def versioned(self) -> 'SmartPath':
        """
        Create a versioned path by adding _N suffix before the extension.
        Examines sibling paths to determine the next available version number.

        Args:
            path (Path): Original path to version

        Returns:
            Path: New path with version number added

        Examples:
            >>> get_versioned_path(Path('test.txt'))
            Path('test_1.txt')  # If no versions exist
            >>> get_versioned_path(Path('test.txt'))
            Path('test_2.txt')  # If test_1.txt exists
            >>> get_versioned_path(Path('test_1.txt'))
            Path('test_2.txt')  # Creates next version regardless of input version
        """
        # Split the path into stem and suffix
        abs_path = self.absolute()
        stem = abs_path.stem
        suffix = self.suffix
        parent = abs_path.parent

        # Remove any existing version number from the stem
        base_stem = re.sub(r'_\d+$', '', stem)

        # Get all sibling files that match the pattern base_stem_N.suffix
        pattern = f"{base_stem}_*{suffix}"
        existing_versions = [p for p in parent.glob(pattern)
                             if re.match(f"{base_stem}_\\d+{suffix}$", p.name)]

        # Extract version numbers from existing files
        version_numbers = []
        for version_path in existing_versions:
            match = re.search(r'_(\d+)' + re.escape(suffix) + '$', version_path.name)
            if match:
                version_numbers.append(int(match.group(1)))

        # Determine next version number
        next_version = 0 if not version_numbers else max(version_numbers) + 1

        # Create new path with version number
        new_path = parent / ("error", f"{base_stem}_{next_version}{suffix}")

        # EXISING CHECKING
        """ options:
            error: name must not exist in parent, when first version is created
            make_first
        """
        return new_path


if __name__ == "__main__":
    p = SmartPath(exist="must_exist")
    print(p.absolute())
    smapp = p / ("overwrite", "bag")
    smapp.create_bag({"cool": 14})

    try:
        p = SmartPath("sasa", exist="must_exist")
    except PathNotExistsError as e:
        pass  # test

    p2 = SmartPath("vvv", exist="version")
    p2.create_bag({"cool": 14})
