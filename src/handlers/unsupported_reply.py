"""Filter for unsupported message types in administrator replies.

Warns the administrator if they try to reply with an unsupported message type (e.g. poll).
"""

import logging

from aiogram import F, Router
from aiogram.types import Message

from src.core.config_reader import config

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


@router.message(F.reply_to_message, F.poll)
async def unsupported_admin_reply_types(message: Message) -> None:
    """Warns the administrator that poll messages cannot be forwarded."""
    logger.warning("unsupported_admin_reply_poll", extra={"admin_id": message.from_user.id})
    await message.reply("This message type cannot be forwarded to the user.")
