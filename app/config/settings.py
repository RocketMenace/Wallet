from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    # Project metadata
    project_name: str = Field(default="Wallet Service")
    version: str = Field(default="0.1.0")
    debug: bool = Field(default=True, alias="DEBUG")

    # Database configuration
    postgres_db: str = Field(default="wallet_service", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    # Database connection pool settings
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_url: str = Field(default="", alias="DATABASE_URL")

    # Application settings
    app_port: int = Field(default=8000, alias="APP_PORT")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")


settings = Settings()