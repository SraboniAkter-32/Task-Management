from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    database_url: str
    database_name: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str

    class Config:
        env_file = ".env"


settings = Settings()
