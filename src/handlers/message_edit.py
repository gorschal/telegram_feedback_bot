"""Handler for edited messages.

Warns the user or administrator that edited messages are not forwarded.
"""

import logging

from aiogram import Router
from aiogram.types import Message

from src.core.config_reader import config

logger = logging.getLogger(__name__)

router = Router()


@router.edited_message()
async def edited_message_warning(message: Message) -> None:
    """Warns that the edited message will not be visible to the recipient."""
    if message.chat.id == config.admin_chat_id:
        logger.info("admin_edit_ignored", extra={"chat_id": message.chat.id})
    await message.reply("Edited message won't be visible to the recipient. Please send a new message.")
