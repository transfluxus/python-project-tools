from csv import DictReader
from pathlib import Path
from typing import Union, Any, Optional



from tools.env_root import root


def load_json(path: Path) -> dict:
    import orjson
    return orjson.loads(path.read_text(encoding="utf-8"))


def read_data(path: Path, config: Optional[dict] = None):
    """
    Read data from file. Formats supported: json, csv, excel
    - json is read straight into a dict
    - csv is read into a DictReader object
    - excel is read into a dict of sheet names and lists of rows

    :return:
    """
    if path.suffix == ".json":
        import orjson
        return orjson.loads(path.read_text(encoding="utf-8"))
    elif path.suffix == ".yaml":
        try:
            import yaml
            from yaml import Loader
        except ImportError:
            raise
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
        raise NotImplementedError(f"File format '{path.suffix}' not supported")


def save_json(path: Union[str, Path], data: Union[dict, Any], indent_2: Optional[bool] = True, encoding: str = "utf-8") -> None:
    try:
        import orjson
        no_orjson = False
    except ImportError:
        import json
        no_orjson = True

    path = Path(path)

    if no_orjson:
        json.dump(data, path.open("w", encoding=encoding), indent=2)
    else:
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


def get_latest_file(folder: Path, type_filter: Optional[str] = "*") -> Optional[Path]:
    folder.glob(f"*.{type_filter}")


def levenhstein_get_similar_filenames(filename: str | Path, directory: Path, ignore_suffix: bool = True) -> list[Path]:
    """

    :param filename:
    :param directory:
    :param return_only_filename: instead of full path
    :param ignore_suffix:
    :return:
    """
    fp: Path = Path(filename) if isinstance(filename, str) else filename
    #assert fp.relative_to(directory)
    file_map = {
        f.stem if ignore_suffix else f.name : f
        for f in directory.glob("*.*")
    }
    search_ = fp.stem if ignore_suffix else fp.name
    from tools.fast_levenhstein import levenhstein_get_closest_matches
    return [file_map[fn].stem for fn in levenhstein_get_closest_matches(search_, list(file_map.keys()), threshold=0.4)]

