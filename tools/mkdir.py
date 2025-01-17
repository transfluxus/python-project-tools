import re
from functools import lru_cache
from pathlib import Path
from typing import Union, TypedDict, Literal, Optional, TYPE_CHECKING

#from pydantic.v1 import PathNotExistsError

from tools.files import save_json

exist_literal = Literal["must_not_exist", "overwrite", "must_exist", "not-set"]
source_handling_literal = Literal["move", "copy", "copy_cache"]

if TYPE_CHECKING:
    from tools.experiment.inner_bag import MBag


# @lru_cache
# def logger():
#     from tools import project_logging
#     return project_logging.get_logger(__name__)


class SmrtPathKws(TypedDict):
    exists: exist_literal
    data: Union[dict, str]


class SmartPath(type(Path())):
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
        super().__init__(args[0])

        exists = kwargs.get("exist")
        self.valid = False

        if not exists:
            # logger().warning(f"exists keyword missing for {self}. Path not valid")
            exists = "not-set"

        data_passed = kwargs.get("data")

        def check_write_data() -> bool:
            if data_passed and self.suffix == ".json":
                save_json(self, data_passed)
                return True
            return False

        if not self.exists():
            if exists == "must_exist":
                raise ValueError(path=self.absolute())
            elif exists == "version":
                self = self.versioned()
                # todo...
                ##logger().info(f"versioning {self}")
                # self.mkdir(parents=True)
            elif exists == "create":
                self.mkdir(parents=True)
            else:
                if not self.suffix:
                    # todo...
                    # logger().info(f"creating {self}")
                    self.mkdir()
                else:
                    check_write_data()
                    # logger().info(
                    #     f"not creating {self}. Probably meant to be a file. needs to be set explicitly to ¡create")
        else:
            if exists == "must_not_exist":
                raise FileExistsError(self)
            elif exists == "overwrite":
                #logger().debug(f"overwriting {self}")
                if self.suffix:
                    check_write_data()
                else:
                    pass
                    # shutil.rmtree(self)
            else:  # ignore
                self.valid = True

    def __truediv__(self, key: Union[
        str, Path, 'SmartPath', tuple[exist_literal, Union[str, Path, 'SmartPath'], Optional[dict]]]) -> 'SmartPath':
        """
        Override the division operator to join paths and create directories.

        Args:
            key: Path component to join (string or Path-like object)

        Returns:
            SmartPath: A new SmartPath instance for the joined path
        """
        if isinstance(key, tuple):
            if len(key) >= 3:
                kws = {"exist": key[1], "data": key[2]}
            elif len(key) == 2:
                kws = {"exist": key[1], "data": None}
            else:
                kws = {"exist": "not-set", "data": None}
            return SmartPath(super().__truediv__(key[1]), **kws)
        else:
            kws = {"exist": "not-set", "data": None}
            p = Path(self) / key
            return SmartPath(p, **kws)

    def read(self, encoding: str = "utf-8") -> str:
        return self.read_text(encoding=encoding)

    # CreateBag(Protocol)
    def get_path(self) -> Path:
        return self

    def create_bag(self, info: dict) -> "MBag":
        try:
            import bagit
        except ImportError:
            print("Please install bagit to use this function")
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
    except ValueError as e:
        pass  # test

    p2 = SmartPath("vvv", exist="version")
    p2.create_bag({"cool": 14})
