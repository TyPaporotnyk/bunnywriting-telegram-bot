from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TELEGRAM_BOT_TOKEN: str

    KOMMO_SECRET_KEY: str
    KOMMO_INTEGRATION_ID: str
    KOMMO_REDIRECT_URL: str
    KOMMO_URL_BASE: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str

    @property
    def DATABASE_URL(self):
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def ASYNC_DATABASE_URL(self):
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
