from unittest.mock import AsyncMock, MagicMock

from aiogram.types import ContentType, Message
from constants import ADMIN_CHAT_ID

from src.handlers.admin_no_reply import has_no_reply


def _make_admin_message(content_type=ContentType.TEXT):
    msg = MagicMock(spec=Message)
    msg.reply = AsyncMock()
    msg.content_type = content_type
    msg.chat = MagicMock()
    msg.chat.id = ADMIN_CHAT_ID
    msg.reply_to_message = None
    msg.from_user = MagicMock()
    msg.from_user.id = 99999
    return msg


class TestHasNoReply:
    async def test_replies_for_text(self):
        msg = _make_admin_message()
        await has_no_reply(msg)
        msg.reply.assert_awaited_once_with("This message is not a reply to any other message!")

    async def test_skips_new_chat_members(self):
        msg = _make_admin_message(content_type=ContentType.NEW_CHAT_MEMBERS)
        await has_no_reply(msg)
        msg.reply.assert_not_called()

    async def test_skips_left_chat_member(self):
        msg = _make_admin_message(content_type=ContentType.LEFT_CHAT_MEMBER)
        await has_no_reply(msg)
        msg.reply.assert_not_called()
