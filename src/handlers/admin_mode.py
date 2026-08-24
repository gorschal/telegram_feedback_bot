"""Administrator message handlers.

Functions:
    extract_id: Extract user_id from the #id<user_id> hashtag
    get_user_info: Get user information via /who
    reply_to_user: Forward the administrator's reply to the user
"""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import Chat, Message

from src.core.config_reader import config

logger = logging.getLogger(__name__)

HASHTAG_PREFIX_LENGTH = 3
MIN_HASHTAG_LENGTH = 4
USER_ID_ERROR = "Could not extract user ID from reply!"
INVALID_ID_ERROR = "Invalid user ID for reply!"

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


def extract_id(message: Message) -> int:
    """Extracts the user_id from the hashtag at the end of the message.

    Args:
        message: Message with the #id<user_id> hashtag at the end.

    Returns:
        The user ID extracted from the hashtag.

    Raises:
        ValueError: If the hashtag is missing or has an invalid format.
    """
    entities = message.entities or message.caption_entities
    if not entities or entities[-1].type != "hashtag":
        raise ValueError(USER_ID_ERROR)

    hashtag = entities[-1].extract_from(message.text or message.caption)
    if len(hashtag) < MIN_HASHTAG_LENGTH or not hashtag[HASHTAG_PREFIX_LENGTH:].isdigit():
        raise ValueError(INVALID_ID_ERROR)

    return int(hashtag[HASHTAG_PREFIX_LENGTH:])


@router.message(Command(commands=["get", "who"]), F.reply_to_message)
async def get_user_info(message: Message, bot: Bot) -> None:
    """Sends information about the user based on a reply to their message."""

    def get_full_name(chat: Chat) -> str:
        if not chat.first_name:
            return ""
        if not chat.last_name:
            return chat.first_name
        return f"{chat.first_name} {chat.last_name}"

    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        logger.info("user_info_extract_error", extra={"admin_id": message.from_user.id, "error": str(ex)})
        await message.reply(str(ex))
        return

    try:
        user = await bot.get_chat(user_id)
    except TelegramAPIError as ex:
        logger.warning("user_info_api_error", extra={"user_id": user_id, "error": ex.message})
        await message.reply(f"Failed to get user info! Error: {ex.message}")
        return

    u = f"@{user.username}" if user.username else "no"
    logger.info("user_info_requested", extra={"user_id": user.id, "admin_id": message.from_user.id})
    await message.reply(f"Name: {get_full_name(user)}\nID: {user.id}\nUsername: {u}")


@router.message(F.reply_to_message)
async def reply_to_user(message: Message) -> None:
    """Forwards the administrator's message to the user via reply."""
    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        logger.info("reply_extract_error", extra={"admin_id": message.from_user.id, "error": str(ex)})
        await message.reply(str(ex))
        return

    try:
        await message.copy_to(user_id)
        logger.info("reply_sent", extra={"user_id": user_id, "admin_id": message.from_user.id})
    except TelegramAPIError as ex:
        logger.warning(
            "reply_failed",
            extra={"user_id": user_id, "admin_id": message.from_user.id, "error": ex.message},
        )
        await message.reply(f"Failed to send message to user! Error: {ex.message}")
