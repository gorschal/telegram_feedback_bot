"""Warnings to the administrator about missing replies to a message.

Reminds the administrator that replying to a user requires using a reply to their message.
"""

import logging

from aiogram import F, Router
from aiogram.types import ContentType, Message

from src.core.config_reader import config

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


@router.message(~F.reply_to_message)
async def has_no_reply(message: Message) -> None:
    """Warns the administrator that the message is not a reply to any other message."""
    if message.content_type not in (ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER):
        logger.info("admin_message_no_reply", extra={"admin_id": message.from_user.id})
        await message.reply("This message is not a reply to any other message!")
