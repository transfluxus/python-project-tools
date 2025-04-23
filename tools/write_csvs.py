from csv import DictWriter
from pathlib import Path
from typing import Iterable


def write_csv(destination: Path,
              fieldnames: list[str],
              encoding: str = "utf-8",
              exist_ok:bool=True,
              write_header: bool = True, rows: Iterable[str] = None) -> bool:
    if not rows:
        return False
    if destination.exists() and not exist_ok:
        return False
    with destination.open("w", encoding=encoding) as f:
        writer = DictWriter(f, fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)



