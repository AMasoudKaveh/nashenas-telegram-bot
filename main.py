# main.py

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from loader import bot, dp
from config import config
from database.db import init_db
from handlers import (
    start_router,
    callback_router,
    anonymous_chat_router,
    anonymous_message_router,
    help_rules_router,
    special_contact_router,
)


async def on_startup(app: web.Application):
    """
    Application startup hook.

    Initializes the database. Webhook is assumed to be already set manually
    (for example via curl or a deployment script).
    """
    print("📦 Initializing database...")
    init_db()
    print("🚀 Startup done. Webhook is expected to be configured externally.")


async def on_shutdown(app: web.Application):
    """
    Application shutdown hook.

    Closes the bot session gracefully.
    """
    print("🔴 Shutting down bot...")
    await bot.session.close()
    print("🛑 Bot session closed.")


def setup_routers() -> None:
    """
    Register all routers on the dispatcher.
    """
    dp.include_router(start_router)
    dp.include_router(callback_router)
    dp.include_router(anonymous_chat_router)
    dp.include_router(anonymous_message_router)
    dp.include_router(help_rules_router)
    dp.include_router(special_contact_router)


def main() -> None:
    """
    Entry point for running the webhook-based Telegram bot.
    """
    setup_routers()

    app = web.Application()

    # Webhook path must match your reverse-proxy / Telegram webhook configuration.
    webhook_path = getattr(config, "WEBHOOK_PATH", "/telegram-webhook")

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=webhook_path)

    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(
        app,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )


if __name__ == "__main__":
    main()
