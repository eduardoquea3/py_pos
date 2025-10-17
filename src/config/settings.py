from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # JWT
    JWT_SECRET: str
    JWT_SECRET_REFRESH: str
    JWT_EXPIRATION: str = "1d"
    JWT_EXPIRATION_REFRESH: str = "7d"

    # Server
    PORT: int = 3005
    SERVER_PREFIX: str = "api"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
