import typing as t
from enum import Enum
from pathlib import Path

from pydantic import PostgresDsn, AfterValidator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from project.utils.structures import SafeLazyInit

__all__ = ["Settings"]


def not_empty_validator(value):
    if not value:
        error_msg = "Field cannot be empty"
        raise ValueError(error_msg)
    return value


NotEmptyStrT = t.Annotated[str, AfterValidator(not_empty_validator)]
NotEmptySecretStrT = t.Annotated[SecretStr, AfterValidator(not_empty_validator)]

MONITORING_APP_NAME = "<project_name>"
API_ROOT_PATH = "/api"


class Envs(Enum):
    PROD = "PROD"  # to work at a prod stand
    LAMBDA = "LAMBDA"  # to work at a stable stand
    SANDBOX = "SANDBOX"  # to work on a test stand
    TEST = "TEST"  # for run testing
    LOCAL = "LOCAL"  # for local development


class SettingsValidator(BaseSettings):
    # Application
    ENV: Envs = Envs.LOCAL
    ACCESS_TOKEN: NotEmptySecretStrT
    HISTORY_WINDOW: int = 20

    # Keycloak
    KEYCLOAK_URL: str = ""
    KEYCLOAK_CLIENT_ID: str = ""
    KEYCLOAK_USERNAME: str = ""
    KEYCLOAK_PASSWORD: SecretStr | None = None

    # Database
    SQLALCHEMY_DATABASE_DSN: PostgresDsn  # Example: postgresql+psycopg2://user:password@localhost:5432/database
    DATABASE_PRE_PING: t.Annotated[bool, "Checks and creates connection if closed before requesting"] = False

    # Redis
    REDIS_HOST: str = ""
    REDIS_PORT: str = ""
    REDIS_DB: str = ""

    # LLM
    LLM_MODEL: NotEmptyStrT
    LLM_API_KEY: NotEmptySecretStrT
    LLM_MIDDLE_PROXY_URL: str = ""
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 8192

    # Loading local settings for development environment.
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent / ".env", extra="allow")

    def is_local(self):
        return self.ENV == Envs.LOCAL

    def is_production(self):
        return self.ENV == Envs.PROD

    def is_testable(self):
        return self.ENV in (Envs.LAMBDA, Envs.SANDBOX)

    def is_any_stand(self):
        return self.ENV in (Envs.PROD, Envs.LAMBDA, Envs.SANDBOX)


Settings = SafeLazyInit(SettingsValidator)
