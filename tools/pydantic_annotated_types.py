from datetime import datetime
from pathlib import Path
from typing import Annotated

from pydantic import PlainSerializer

SerializableDatetime = Annotated[
    datetime, PlainSerializer(lambda dt: dt.isoformat(), return_type=str, when_used='json')
]

SerializableDatetimeAlways = Annotated[
    datetime, PlainSerializer(lambda dt: dt.isoformat(), return_type=str, when_used='always')
]

SerializablePath = Annotated[
    Path, PlainSerializer(lambda p: p.as_posix(), return_type=str)]