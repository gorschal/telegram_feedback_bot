from unittest.mock import AsyncMock, MagicMock

from aiogram.types import Message

from src.handlers.unsupported_reply import unsupported_admin_reply_types


class TestUnsupportedAdminReplyTypes:
    async def test_replies_with_warning(self):
        msg = MagicMock(spec=Message)
        msg.reply = AsyncMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 99999
        await unsupported_admin_reply_types(msg)
        msg.reply.assert_awaited_once_with("This message type cannot be forwarded to the user.")
