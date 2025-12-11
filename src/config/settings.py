from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DB_URL: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int

    # JWT
    PORT: int
    SERVER_PREFIX: str

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()  # type: ignore
