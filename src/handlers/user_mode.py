"""Handlers for messages from users.

Forwards user messages to the administrator with the #id<user_id> appended.
Supports text messages and media (photos, videos, audio, files, voice messages).
"""

import logging
from asyncio import create_task, sleep

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import ContentType, Message

from src.core.block_lists import banned, shadowbanned
from src.core.config_reader import config
from src.filters import SupportedMediaFilter

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000
MAX_CAPTION_LENGTH = 1000

router = Router()


def _on_notification_task_done(task: object) -> None:
    """Logs exceptions from background notification tasks."""
    t = task  # type: ignore[assignment]
    if t.done() and t.exception() is not None:  # type: ignore[union-attr]
        logger.exception("notification_task_failed", exc_info=t.exception())  # type: ignore[union-attr]


async def _send_expiring_notification(message: Message) -> None:
    """Send a confirmation message that can be auto-deleted."""
    msg = await message.reply("Message sent!")
    if config.remove_sent_confirmation:
        await sleep(5.0)
        await msg.delete()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message) -> None:
    """Sends a welcome message to the user."""
    logger.info("user_started", extra={"user_id": message.from_user.id, "username": message.from_user.username})
    await message.answer(
        "Hi there! \n"
        "With my help you can get in touch with my owner and receive a reply. "
        "Just type something in this chat."
    )


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message) -> None:
    """Sends a help message describing the bot's capabilities."""
    logger.info("user_help", extra={"user_id": message.from_user.id})
    await message.answer(
        "With my help you can contact telegram technical support and get a reply.\n"
        "Just keep writing in this chat. Note that not all message types are supported – "
        "only text, photos, videos, audio, files and voice messages."
    )


@router.message(F.text)
async def text_message(message: Message, bot: Bot) -> None:
    """Forwards the user's text message to the administrator."""
    user_id = message.from_user.id

    if len(message.text) > MAX_MESSAGE_LENGTH:
        logger.info("text_too_long", extra={"user_id": user_id, "length": len(message.text)})
        await message.reply("Message is too long (max 4000 characters). Please shorten it and try again.")
        return

    if user_id in banned:
        logger.info("text_banned_user", extra={"user_id": user_id})
        await message.answer("You have been banned. Your messages will not be delivered.")
    elif user_id in shadowbanned:
        logger.info("text_shadowbanned_user", extra={"user_id": user_id})
        return
    else:
        logger.info("text_forwarded", extra={"user_id": user_id, "admin_chat_id": config.admin_chat_id})
        await bot.send_message(config.admin_chat_id, message.html_text + f"\n\n#id{user_id}", parse_mode="HTML")
        task = create_task(_send_expiring_notification(message))
        task.add_done_callback(_on_notification_task_done)


@router.message(SupportedMediaFilter())
async def supported_media(message: Message) -> None:
    """Forwards the user's media message to the administrator."""
    user_id = message.from_user.id

    if message.caption and len(message.caption) > MAX_CAPTION_LENGTH:
        logger.info("media_caption_too_long", extra={"user_id": user_id, "length": len(message.caption)})
        await message.reply("Caption is too long (max 1000 characters). Please shorten it and try again.")
        return

    if user_id in banned:
        logger.info("media_banned_user", extra={"user_id": user_id})
        await message.answer("You have been banned. Your messages will not be delivered.")
    elif user_id in shadowbanned:
        logger.info("media_shadowbanned_user", extra={"user_id": user_id})
        return
    else:
        logger.info("media_forwarded", extra={"user_id": user_id, "content_type": message.content_type})
        await message.copy_to(
            config.admin_chat_id,
            caption=((message.caption or "") + f"\n\n#id{user_id}"),
            parse_mode="HTML",
        )
        task = create_task(_send_expiring_notification(message))
        task.add_done_callback(_on_notification_task_done)


@router.message()
async def unsupported_types(message: Message) -> None:
    """Warns the user about an unsupported message type."""
    if message.content_type not in (
        ContentType.NEW_CHAT_MEMBERS,
        ContentType.LEFT_CHAT_MEMBER,
        ContentType.VIDEO_CHAT_STARTED,
        ContentType.VIDEO_CHAT_ENDED,
        ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
        ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED,
        ContentType.NEW_CHAT_PHOTO,
        ContentType.DELETE_CHAT_PHOTO,
        ContentType.SUCCESSFUL_PAYMENT,
        "proximity_alert_triggered",
        ContentType.NEW_CHAT_TITLE,
        ContentType.PINNED_MESSAGE,
    ):
        logger.info(
            "unsupported_message_type",
            extra={"user_id": message.from_user.id, "content_type": message.content_type},
        )
        await message.reply("This message type is not supported. Please send something else.")
