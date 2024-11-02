from pathlib import Path
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='allow')
    PROJECT_NAME: Optional[str] = None

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

CONFIG = Config()
