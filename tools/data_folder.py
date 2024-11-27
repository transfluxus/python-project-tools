from functools import lru_cache
from pathlib import Path
from typing import Union, Optional

from tools.env_root import root
from tools.files import load_json
from tools.mkdir import SmartPath


@lru_cache
def base_data_folder() -> SmartPath:
    return SmartPath(root()) / "data"

def create_data_folder(name: Union[str, Path]) -> SmartPath:
    # generate python code that scans the path and generated a python file
    # with BASE_<NAME>_PATH: str = "..."
    # and for p in [...]:
    # p.mkdir(exists_ok=True)
    return base_data_folder() / Path(name)

def get_data_folders(get_paths: bool = False) -> list[tuple[str, Optional[dict]]]:
    """
    gets data folder names, checks if they have a metadata file in data called name.json.
    which should contains json-ld metadata.
    """
    results = []
    for folder in base_data_folder().glob("*"):
        fn = folder.name
        name_o_path: Union[str,Path] = folder if get_paths else fn
        metadata_file = base_data_folder() / f"{fn}.json"
        metadata = load_json(metadata_file) if metadata_file.exists() else None
        results.append((name_o_path, metadata))
    return results



if __name__ == "__main__":
    create_data_folder("sa")
    get_data_folders()