import asyncio
import contextlib
import logging
import signal

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from src.core.commands_worker import set_bot_commands
from src.core.config_reader import config
from src.handlers import setup_routers

logger = logging.getLogger(__name__)


async def main() -> None:
    """Initializes and runs the bot in polling or webhook mode."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    session = AiohttpSession(proxy=config.proxy) if config.proxy else None
    bot = Bot(token=config.bot_token.get_secret_value(), session=session)

    if config.custom_bot_api:
        bot.session.api = TelegramAPIServer.from_base(config.custom_bot_api, is_local=True)

    dp = Dispatcher()
    router = setup_routers()
    dp.include_router(router)

    await set_bot_commands(bot)

    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("shutdown_signal_received")
        shutdown_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    try:
        if config.debug:
            logger.info("bot_starting_polling")
            await bot.delete_webhook()
            polling_task = asyncio.create_task(
                dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
            )
            await shutdown_event.wait()
            polling_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await polling_task
        else:
            logger.info("bot_starting_webhook", extra={"domain": config.webhook_domain, "port": config.app_port})

            aiohttp_logger = logging.getLogger("aiohttp.access")
            aiohttp_logger.setLevel(logging.CRITICAL)

            await bot.set_webhook(
                url=config.webhook_domain + config.webhook_path,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )

            app = web.Application()
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.webhook_path)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=config.app_host, port=config.app_port)
            await site.start()

            await shutdown_event.wait()
            await runner.cleanup()
    finally:
        logger.info("bot_shutdown")
        await bot.session.close()


asyncio.run(main())
