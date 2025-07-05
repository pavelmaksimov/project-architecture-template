import threading
from contextlib import contextmanager
from pathlib import Path
import typing as t

from pydantic import PostgresDsn, AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

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


class LazySettings[T]:
    """
    Creates settings in lazy manner and allows parameters to be replaced if an instance has already been created.

    Base example:
        Settings = SettingsFactory(MY_PARAM=1)
        assert Settings().MY_PARAM == 1

        Settings.replace_params(MY_PARAM=2)
        assert Settings().MY_PARAM == 2

    Example with local param values:
        Settings = SettingsFactory(MY_PARAM=1)

        with Settings.local(MY_PARAM=2):
            assert Settings().MY_PARAM == 2

        assert Settings().MY_PARAM == 1
    """

    def __init__(self, settings_class: type[T]):
        self._settings_class: type[T] = settings_class
        self.__thread_local_storage = threading.local()  # Thread-Local storage

    def __call__(self) -> T:
        if not hasattr(self.__thread_local_storage, "settings"):
            self.__thread_local_storage.settings = self._settings_class()
        return self.__thread_local_storage.settings

    @contextmanager
    def local(self, **kwargs):
        previous_settings = getattr(self.__thread_local_storage, "settings", None)

        self.__thread_local_storage.settings = self._settings_class(**kwargs)
        try:
            yield
        finally:
            self.__thread_local_storage.settings = previous_settings


Settings = LazySettings(SettingsValidator)
