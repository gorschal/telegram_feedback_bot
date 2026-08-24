from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    bot_token: SecretStr
    admin_chat_id: int
    remove_sent_confirmation: bool = True
    debug: bool = True
    webhook_domain: str | None = None
    webhook_path: str = "/webhook"
    app_host: str | None = "0.0.0.0"
    app_port: int | None = 9000
    custom_bot_api: str | None = None
    proxy: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()  # pyright: ignore[reportCallIssue]
