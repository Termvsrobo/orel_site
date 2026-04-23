from typing import Union

from pydantic.networks import AnyUrl, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    URL: str = "https://titanium.parts/catalog/zapasnye-chasti/"
    MARKUP_PERCENT: int = 25
    ITEMS_PER_PAGE: int = 54
    TITLE: str = 'Запчасти на сельскохозяйственную технику город Орел'
    DESCRIPTION: str = (
        'Мы предлагаем широкий ассортимент запчастей для сельхозтехники John Deere, Claas, Case, New Holland, Lemken, '
        'Amazone, Manitou, Kuhn, G.B., ,  ПОЛЕСЬЕ, ДОН, МТЗ, БДМ-АГРО, БДТ-АГРО, БОБРУЙСКСЕЛЬМАШ, ПЕНЗАРАДИОЗАВОД, '
        'в наличии на складе в городе Орёл  и под заказ.'
    )

    DB_URL: Union[PostgresDsn, AnyUrl]
    CELERY_BROKER_URL: RedisDsn
    CELERY_RESULT_BACKEND: RedisDsn

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
