from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
from functools import lru_cache

from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    mongo_username: str
    mongo_password: str
    mongo_host: str
    mongo_port: int
    mongo_database: str

    chunk_size: int = 1024 * 1024

    postgres_username: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5433
    postgres_database: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int

    @property
    def postgres_database_url(self) -> str:
        url = URL.create(drivername="postgresql+psycopg2", username=self.postgres_username, password=self.postgres_password,
                         host=self.postgres_host, port=self.postgres_port, database=self.postgres_database)

        return url.render_as_string(hide_password=False)

    @property
    def mongo_database_url(self) -> str:
        return (f"mongodb://{quote_plus(self.mongo_username)}:{quote_plus(self.mongo_password)}@"
                f"{self.mongo_host}:{self.mongo_port}/{self.mongo_database}?"
                f"authSource=admin")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
