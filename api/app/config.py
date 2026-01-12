from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_dsn: str
    meili_host: str
    meili_api_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
