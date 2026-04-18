from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.networks import PostgresDsn, AnyUrl, RedisDsn


class Settings(BaseSettings):
    URL: str = "https://titanium.parts/catalog/zapasnye-chasti/"
    MARKUP_PERCENT: int = 25
    ITEMS_PER_PAGE: int = 54
    TITLE: str = 'Запчасти на сельскохозяйственную технику город Орел'
    DESCRIPTION: str = 'Запчасти для сельхозтехники город Орел'

    DB_URL: Union[PostgresDsn, AnyUrl]
    CELERY_BROKER_URL: RedisDsn
    CELERY_RESULT_BACKEND: RedisDsn

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
