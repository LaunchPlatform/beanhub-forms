import pathlib
import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    BEANCOUNT_DIR: pathlib.Path = pathlib.Path.cwd()


settings = Settings()
