from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

config_dir = Path(__file__).parents[1]
env_path = config_dir / ".env"
yaml_path = config_dir / "config.yaml"


class DatabaseConfig(BaseSettings):
	DB_HOST: str
	DB_PORT: int
	DB_USER: str
	DB_PASS: str
	DB_NAME: str
	pool_size: int = Field(gt=0)
	max_overflow: int = Field(gt=5)
	model_config = SettingsConfigDict(env_file=env_path)

	@property
	def DB_URL(self):
		return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class LoggerConfig(BaseSettings):
	level: str
	format: str
	date_format: str


class ServerConfig(BaseSettings):
	host: str
	port: int
	reload: bool


class YamlConfig(BaseSettings):
	logger: LoggerConfig
	server: ServerConfig


class AppConfig:
	def __init__(self):
		self.yaml = self.load_config()
		self.env = DatabaseConfig()

	@staticmethod
	def load_config() -> YamlConfig:
		with open(yaml_path) as f:
			data: dict = yaml.safe_load(f)
		return YamlConfig(**data)


settings = AppConfig()
