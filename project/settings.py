from pathlib import Path
import typing as t

from pydantic import PostgresDsn, AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

from project.utils.structures import SafeLazyInit

__all__ = ["Settings"]


def not_empty_validator(value):
    if not value:
        error_msg = "Field cannot be empty"
        raise ValueError(error_msg)
    return value


NotEmptyStrT = t.Annotated[str, AfterValidator(not_empty_validator)]


class SettingsValidator(BaseSettings):
    ENV: t.Literal["DEV", "PROD", "TEST"] = "PROD"
    ACCESS_TOKEN: NotEmptyStrT
    SQLALCHEMY_DATABASE_DSN: PostgresDsn  # Example: postgresql+psycopg2://user:password@localhost:5432/database
    HISTORY_WINDOW: int = 20

    KEYCLOAK_URL: str = ""
    KEYCLOAK_CLIENT_ID: str = ""
    KEYCLOAK_USERNAME: str = ""
    KEYCLOAK_PASSWORD: str = ""

    DATABASE_PRE_PING: t.Annotated[bool, "Checks and creates connection if closed before requesting"] = False

    # Loading local settings for development environment.
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent / ".env", extra="allow")


Settings = SafeLazyInit(SettingsValidator)
