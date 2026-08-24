"""Handlers for ban, shadowban and unban commands.

Commands:
    /ban — ban a user with a notification
    /shadowban — shadowban a user without a notification
    /unban — remove a ban
    /list_banned — list all blocked users
"""

import logging
from contextlib import suppress

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.core.block_lists import banned, shadowbanned
from src.core.config_reader import config
from src.handlers.admin_mode import extract_id

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


@router.message(Command(commands=["ban"]), F.reply_to_message)
async def cmd_ban(message: Message) -> None:
    """Bans a user based on a reply to their message."""
    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        await message.reply(str(ex))
        return
    banned.add(int(user_id))
    logger.info("user_banned", extra={"user_id": int(user_id), "admin_id": message.from_user.id})
    await message.reply(f"ID {user_id} has been banned. The user will be notified when trying to send a message.")


@router.message(Command(commands=["shadowban"]), F.reply_to_message)
async def cmd_shadowban(message: Message) -> None:
    """Bans a user without a notification (shadowban)."""
    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        await message.reply(str(ex))
        return
    shadowbanned.add(int(user_id))
    logger.info("user_shadowbanned", extra={"user_id": int(user_id), "admin_id": message.from_user.id})
    await message.reply(f"ID {user_id} has been shadowbanned. The user will not know they are blocked.")


@router.message(Command(commands=["unban"]), F.reply_to_message)
async def cmd_unban(message: Message) -> None:
    """Removes a ban from a user based on a reply to their message."""
    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        await message.reply(str(ex))
        return
    user_id = int(user_id)
    with suppress(KeyError):
        banned.remove(user_id)
    with suppress(KeyError):
        shadowbanned.remove(user_id)
    logger.info("user_unbanned", extra={"user_id": user_id, "admin_id": message.from_user.id})
    await message.reply(f"ID {user_id} has been unbanned.")


@router.message(Command(commands=["list_banned"]))
async def cmd_list_banned(message: Message) -> None:
    """Outputs the list of all banned and shadowbanned users."""
    has_bans = len(banned) > 0 or len(shadowbanned) > 0
    if not has_bans:
        logger.info("list_banned_empty", extra={"admin_id": message.from_user.id})
        await message.answer("No banned users.")
        return
    result = []
    if len(banned) > 0:
        result.append("Banned users:")
        result.extend(f"• #id{item}" for item in banned)
    if len(shadowbanned) > 0:
        result.append("\nShadowbanned users:")
        result.extend(f"• #id{item}" for item in shadowbanned)

    logger.info(
        "list_banned",
        extra={
            "admin_id": message.from_user.id,
            "banned_count": len(banned),
            "shadowbanned_count": len(shadowbanned),
        },
    )
    await message.answer("\n".join(result))
