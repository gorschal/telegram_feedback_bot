"""Set up bot commands for users and administrators.

Configures bot commands:
- For all users: /help
- For the administrator: /who, /ban, /shadowban, /unban, /list_banned
"""

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from src.core.config_reader import config

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot) -> None:
    """Sets up bot commands for the default scope and the administrator chat."""
    usercommands = [
        BotCommand(command="help", description="Help on using the bot"),
    ]
    await bot.set_my_commands(usercommands, scope=BotCommandScopeDefault())

    admin_commands = [
        BotCommand(command="who", description="Get user info"),
        BotCommand(command="ban", description="Ban a user"),
        BotCommand(command="shadowban", description="Shadowban a user"),
        BotCommand(command="unban", description="Unban a user"),
        BotCommand(command="list_banned", description="List banned users"),
    ]
    try:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=config.admin_chat_id))
    except TelegramBadRequest:
        logger.warning("Admin chat %s not found. Admin commands not set.", config.admin_chat_id)
