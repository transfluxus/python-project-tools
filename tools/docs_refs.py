from jsonschema import validate, ValidationError
from mypy.build import TypedDict
from psycopg2.extensions import JSONB
from sqlalchemy import Column, Integer
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import declarative_base, Mapped
from sqlalchemy.orm import validates

Base = declarative_base()

DataStruct = TypedDict('DataStruct', {"@id": Mapped[str], "data": Mapped[dict]})


class Doc(Base):
    __tablename__ = 'docs'
    id: Mapped[int] = Column(Integer, primary_key=True)
    data: Mapped[dict] = Column(MutableDict.as_mutable(JSONB), nullable=False)
    schema: Mapped[DataStruct] = Column(MutableDict.as_mutable(JSONB), nullable=False)

    @validates('data')
    def validate_data(self, key, value):
        schema = self.schema.get('@schema', {})
        try:
            validate(instance=value, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Data validation error: {e.message}")
        return value
