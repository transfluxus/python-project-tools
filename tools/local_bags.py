from pathlib import Path
from typing import Any

try:
    import appdirs
    import bagit
except ImportError:
    print("install the optional dependencies [bags]")
# from tools.env_root import project_name
from tools.experiment.inner_bag import MBag
from tools.mkdir import SmartPath, exist_literal, source_handling_literal

# _project_name = project_name()


# TODO:...
_project_name = "TEMP"
ad = SmartPath(appdirs.user_data_dir(f"local_bags/{_project_name}"), **{"exist":"create"})


def _create_bag(files: list[Path],
               destination: Path,
               info: dict[str, Any],
               exists: exist_literal = "create",
               source: list[source_handling_literal] = None) -> MBag:

    _path = SmartPath(destination, **{"exist" : exists})
    bag = bagit.make_bag(destination, info)

    return MBag(destination, bag).add_paths(
        files,
        source,
    )

def local_bag(files: list[Path],
               name: str,
               info: dict[str, Any],
               source: list[source_handling_literal] = None) -> MBag:

    bag_dir = ad / ("error",name)
    bag = bagit.make_bag(bag_dir, info)
    bag.save(manifests=True)
    return MBag(bag_dir, bag).add_paths(
        files,
        source,
    )

def list_local_bags() -> list[str]:
    pass