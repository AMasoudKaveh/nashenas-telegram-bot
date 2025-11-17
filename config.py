# config.py
from dataclasses import dataclass
import os


@dataclass
class Config:
    """
    Application configuration.

    All sensitive values (bot token, admin IDs, etc.) should be provided
    via environment variables and NOT hard-coded in the source code.
    """
    BOT_TOKEN: str
    BOT_USERNAME: str
    ADMIN_ID: int | None
    LOG_CHANNEL_ID: int | None
    WEBHOOK_URL: str
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = 9000


def load_config() -> Config:
    """
    Load configuration from environment variables.

    Expected environment variables:
      - BOT_TOKEN          (required)
      - BOT_USERNAME       (optional, defaults to "YourBotUsernameHere")
      - ADMIN_ID           (optional, integer)
      - LOG_CHANNEL_ID     (optional, integer)
      - WEBHOOK_URL        (optional, defaults to "https://example.com/telegram-webhook")
      - WEBAPP_HOST        (optional, defaults to "0.0.0.0")
      - WEBAPP_PORT        (optional, integer, defaults to 9000)
    """
    bot_token = os.getenv("BOT_TOKEN", "")
    if not bot_token:
        # For development you can provide a placeholder, but for production
        # it's better to fail fast if the token is missing.
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    bot_username = os.getenv("BOT_USERNAME", "YourBotUsernameHere")

    admin_id_env = os.getenv("ADMIN_ID")
    admin_id = int(admin_id_env) if admin_id_env else None

    log_channel_env = os.getenv("LOG_CHANNEL_ID")
    log_channel_id = int(log_channel_env) if log_channel_env else None

    webhook_url = os.getenv("WEBHOOK_URL", "https://example.com/telegram-webhook")

    webapp_host = os.getenv("WEBAPP_HOST", "0.0.0.0")
    webapp_port_env = os.getenv("WEBAPP_PORT", "9000")
    try:
        webapp_port = int(webapp_port_env)
    except ValueError:
        webapp_port = 9000

    return Config(
        BOT_TOKEN=bot_token,
        BOT_USERNAME=bot_username,
        ADMIN_ID=admin_id,
        LOG_CHANNEL_ID=log_channel_id,
        WEBHOOK_URL=webhook_url,
        WEBAPP_HOST=webapp_host,
        WEBAPP_PORT=webapp_port,
    )


config = load_config()
