import os
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

config_dir = Path(__file__).parents[1]
env_path = config_dir / "config" / ".env"
yaml_path = config_dir / "config"


class DatabaseConfig(BaseModel):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str
    pool_size: int = Field(gt=0)
    max_overflow: int = Field(gt=5)

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class AuthJwt(BaseModel):
    private_key_path: Path = config_dir / "certs" / "jwt-private.pem"
    public_key_path: Path = config_dir / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expired_minutes: int = 15


class ServerConfig(BaseModel):
    host: str
    port: int
    reload: bool = Field(default=False)


class LoggerConfig(BaseModel):
    level: str
    format: str
    date_format: str


class Settings(BaseSettings):
    # Core settings
    environment: str = Field(default="development")

    # Database nested config from dote_env file
    database: DatabaseConfig
    jwt: AuthJwt = Field(default_factory=AuthJwt)
    model_config = SettingsConfigDict(
        env_file=(env_path, ".env.production"), env_nested_delimiter="__"
    )

    # Applicaton nested config from development.yaml file
    server: ServerConfig
    logger: LoggerConfig

    @classmethod
    def settings_customise_sources(
        cls, settings_cls: type[BaseSettings], **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        env = os.getenv("ENVIRONMENT", "development")  # noqa: F841

        yaml_files = []
        for config_name in ["development", "production"]:
            config_file = yaml_path / f"{config_name}.yaml"
            if config_file.exists():
                yaml_files.append(str(config_file))

        return (
            kwargs["init_settings"],
            kwargs["env_settings"],
            kwargs["dotenv_settings"],
            YamlConfigSettingsSource(
                settings_cls, yaml_file=yaml_files if yaml_files else None
            ),
        )


settings = Settings()
