from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import Message
from constants import ADMIN_CHAT_ID

from src.handlers.message_edit import edited_message_warning


class TestEditedMessageWarning:
    async def test_replies_in_user_chat(self):
        msg = MagicMock(spec=Message)
        msg.reply = AsyncMock()
        msg.chat = MagicMock()
        msg.chat.id = 99999
        await edited_message_warning(msg)
        msg.reply.assert_awaited_once_with(
            "Edited message won't be visible to the recipient. Please send a new message."
        )

    async def test_replies_and_logs_in_admin_chat(self):
        msg = MagicMock(spec=Message)
        msg.reply = AsyncMock()
        msg.chat = MagicMock()
        msg.chat.id = ADMIN_CHAT_ID
        with patch("src.handlers.message_edit.logger") as mock_logger:
            await edited_message_warning(msg)
        mock_logger.info.assert_called_once()
        msg.reply.assert_awaited_once_with(
            "Edited message won't be visible to the recipient. Please send a new message."
        )
