from csv import DictReader
from pathlib import Path
from typing import Union, Any, Optional

import yaml
from yaml import Loader

from tools.env_root import root


def load_json(path: Path) -> dict:
    return orjson.loads(path.read_text(encoding="utf-8"))


import orjson


def read_data(path: Path, config: Optional[dict] = None):
    """
    Read data from file. Formats supported: json, csv, excel
    - json is read straight into a dict
    - csv is read into a DictReader object
    - excel is read into a dict of sheet names and lists of rows

    :return:
    """
    if path.suffix == ".json":
        return orjson.loads(path.read_text(encoding="utf-8"))
    elif path.suffix == ".yaml":
        return yaml.load(path.read_text(encoding="utf-8"),  Loader=Loader)
    elif path.suffix == ".csv":
        if not config:
            config = {}
        return list(DictReader(path.open(encoding="utf-8"), **config))
    # excel
    elif path.suffix == ".xlsx":
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl not installed")
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        return {sheet.title: list(sheet.values) for sheet in workbook.worksheets}
    # xml
    elif path.suffix == ".xml":
        try:
            import xmltodict
        except ImportError:
            raise ImportError("xmltodict not installed")
        return xmltodict.parse(path.read_text(encoding="utf-8"))
    else:
        raise NotImplementedError(f"File format {path.suffix} not supported")


def save_json(path: Union[str, Path], data: Union[dict, Any], indent_2: Optional[bool] = True, encoding: str = "utf-8") -> None:
    path = Path(path)
    if indent_2:
        content = orjson.dumps(
            data,
            option=orjson.OPT_INDENT_2,
            default=str
        )
    else:
        content = orjson.dumps(data, default=str)

    path.write_bytes(content)


def as_path(path: str | Path) -> Path:
    return Path(path)

# todo test
def get_abs_path(path: Path, base_dir: Optional[Path] = None) -> Path:
    if path.is_absolute():
        return path
    else:
        if base_dir is None:
            return root() / path
        else:
            return base_dir / path



def relative_to_project_path(path: Path, parenthesis: bool = True) -> str:
    p = str(path.relative_to(root()))
    if parenthesis:
        return f"'{p}'"
    else:
        return p
