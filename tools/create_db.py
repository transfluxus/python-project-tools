"""
Creates databases
Manages user permissions
Handles connection string generation
Uses SQLAlchemy as ORM
"""
from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import TypedDict
from sqlalchemy import Column, Integer
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import declarative_base, Mapped
from sqlalchemy.orm import validates

try:
    from jsonschema import validate, ValidationError
    from psycopg2.extensions import JSONB
    import sqlalchemy
    from sqlalchemy_utils import database_exists, create_database
except ImportError:
    print("Install the optional dependency [database]")


class PgConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='allow')
    PG_HOSTNAME: Optional[str]
    PG_PORT: Optional[int]
    PG_ADMIN_NAME: Optional[str]
    PG_ADMIN_PASSWORD: Optional[SecretStr]


try:
    PG_CONFIG = PgConfig()
except:
    PG_CONFIG = None


def connection_str(db_name: str= "postgres") -> str:
    admin = PG_CONFIG.PG_ADMIN_NAME
    host = PG_CONFIG.PG_HOSTNAME
    port = PG_CONFIG.PG_PORT
    pwd = PG_CONFIG.PG_ADMIN_PASSWORD.get_secret_value()
    return f"postgresql+psycopg2://{admin}:{pwd}@{host}:{port}/{db_name}"

def create_pg_db(db_name: str):

    #default_connection_string = f"postgresql+psycopg2://postgres:{pwd}@localhost/postgres"

    # Define the connection string for the database we want to create
    new_db_connection_string = connection_str(db_name)

    # Create the new database
    if not database_exists(new_db_connection_string):
        create_database(new_db_connection_string)
        print(f"Database '{db_name}' created successfully.")
    else:
        print(f"Database '{db_name}' already exists.")

    # Connect to the new database
    new_engine = sqlalchemy.create_engine(new_db_connection_string)

    # Test the connection
    with new_engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))
        print(f"Connected to '{db_name}' successfully.")

def get_engine(username: str, password: str, db_name: str) -> sqlalchemy.Engine:
    return sqlalchemy.create_engine(f"postgresql+psycopg2://{username}:{password}@localhost/{db_name}")

def create_user_grant_access(username: str, password: str, database_name: str):
    # SQL commands
    sql_commands = f"""
    CREATE USER {username} WITH PASSWORD '{password}';
    GRANT CONNECT ON DATABASE {database_name} TO {username};
    GRANT USAGE ON SCHEMA public TO {username};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {username};
    ALTER DATABASE {database_name} OWNER TO {username};
    GRANT CREATE ON SCHEMA public TO {username};
    """

    pwd = PG_CONFIG.PG_PASSWORD.get_secret_value()
    # Execute the SQL commands
    with get_engine("postgres", pwd,"postgres").connect() as conn:

        conn.execute(sqlalchemy.text(f"DROP USER IF EXISTS {username}"))

        conn.execute(sqlalchemy.text("COMMIT"))  # Ensure we're not in a transaction
        for command in sql_commands.split(';'):
            if command.strip():
                conn.execute(sqlalchemy.text(command))
        conn.execute(sqlalchemy.text("COMMIT"))

    print("User created and permissions granted successfully.")

"""
JSON schema validation
SQLAlchemy models
TypedDict definitions for data structures
"""


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
