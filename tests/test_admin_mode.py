from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Chat, Message, MessageEntity
from constants import ADMIN_CHAT_ID

from src.handlers.admin_mode import (
    INVALID_ID_ERROR,
    USER_ID_ERROR,
    extract_id,
    get_user_info,
    reply_to_user,
)


def _make_message_with_hashtag(text="Some message text #id12345", offset=None, length=8):
    msg = MagicMock(spec=Message)
    msg.text = text
    msg.caption = None
    msg.entities = [MessageEntity(type="hashtag", offset=text.find("#") if offset is None else offset, length=length)]
    msg.caption_entities = None
    msg.reply = AsyncMock()
    msg.answer = AsyncMock()
    msg.copy_to = AsyncMock()
    msg.chat = MagicMock(spec=Chat)
    msg.chat.id = ADMIN_CHAT_ID
    msg.from_user = MagicMock()
    msg.from_user.id = 99999
    return msg


class TestExtractId:
    def test_valid_hashtag(self):
        msg = _make_message_with_hashtag()
        assert extract_id(msg) == 12345

    def test_large_user_id(self):
        msg = _make_message_with_hashtag(text="Message #id999999999999", offset=8, length=15)
        assert extract_id(msg) == 999999999999

    def test_no_entities(self):
        msg = _make_message_with_hashtag()
        msg.entities = None
        msg.caption_entities = None
        with pytest.raises(ValueError, match=USER_ID_ERROR):
            extract_id(msg)

    def test_empty_entities(self):
        msg = _make_message_with_hashtag()
        msg.entities = []
        with pytest.raises(ValueError, match=USER_ID_ERROR):
            extract_id(msg)

    def test_last_entity_not_hashtag(self):
        msg = _make_message_with_hashtag()
        msg.entities = [MessageEntity(type="bold", offset=0, length=5)]
        with pytest.raises(ValueError, match=USER_ID_ERROR):
            extract_id(msg)

    def test_hashtag_too_short(self):
        msg = _make_message_with_hashtag(text="#id", offset=0, length=3)
        with pytest.raises(ValueError, match=INVALID_ID_ERROR):
            extract_id(msg)

    def test_hashtag_no_digits(self):
        msg = _make_message_with_hashtag(text="#idabc", offset=0, length=6)
        with pytest.raises(ValueError, match=INVALID_ID_ERROR):
            extract_id(msg)

    def test_uses_caption_when_text_none(self):
        msg = _make_message_with_hashtag()
        msg.text = None
        msg.caption = "Photo caption #id12345"
        msg.entities = None
        msg.caption_entities = [MessageEntity(type="hashtag", offset=msg.caption.find("#id"), length=8)]
        assert extract_id(msg) == 12345

    def test_multiple_entities_last_is_hashtag(self):
        msg = _make_message_with_hashtag()
        hashtag_offset = msg.text.find("#id")
        msg.entities = [
            MessageEntity(type="bold", offset=0, length=4),
            MessageEntity(type="hashtag", offset=hashtag_offset, length=8),
        ]
        assert extract_id(msg) == 12345


class TestGetUserInfo:
    async def test_success(self, mock_bot):
        reply_msg = _make_message_with_hashtag()
        msg = _make_message_with_hashtag()
        msg.reply_to_message = reply_msg
        user_chat = MagicMock(spec=Chat)
        user_chat.id = 12345
        user_chat.first_name = "Test"
        user_chat.last_name = "User"
        user_chat.username = "testuser"
        mock_bot.get_chat.return_value = user_chat
        await get_user_info(msg, mock_bot)
        msg.reply.assert_awaited_once()
        text = msg.reply.call_args[0][0]
        assert "Test User" in text
        assert "12345" in text
        assert "@testuser" in text

    async def test_success_no_username(self, mock_bot):
        reply_msg = _make_message_with_hashtag()
        msg = _make_message_with_hashtag()
        msg.reply_to_message = reply_msg
        user_chat = MagicMock(spec=Chat)
        user_chat.id = 12345
        user_chat.first_name = "Test"
        user_chat.last_name = None
        user_chat.username = None
        mock_bot.get_chat.return_value = user_chat
        await get_user_info(msg, mock_bot)
        text = msg.reply.call_args[0][0]
        assert "Test" in text
        assert "no" in text

    async def test_success_no_first_name(self, mock_bot):
        reply_msg = _make_message_with_hashtag()
        msg = _make_message_with_hashtag()
        msg.reply_to_message = reply_msg
        user_chat = MagicMock(spec=Chat)
        user_chat.id = 12345
        user_chat.first_name = None
        user_chat.last_name = None
        user_chat.username = "testuser"
        mock_bot.get_chat.return_value = user_chat
        await get_user_info(msg, mock_bot)
        text = msg.reply.call_args[0][0]
        assert "Name:" in text

    async def test_extract_id_error(self, mock_bot):
        msg = _make_message_with_hashtag()
        msg.reply_to_message = _make_message_with_hashtag()
        msg.reply_to_message.entities = None
        msg.reply_to_message.caption_entities = None
        await get_user_info(msg, mock_bot)
        msg.reply.assert_awaited_once_with(USER_ID_ERROR)

    async def test_telegram_api_error(self, mock_bot):
        reply_msg = _make_message_with_hashtag()
        msg = _make_message_with_hashtag()
        msg.reply_to_message = reply_msg
        mock_bot.get_chat.side_effect = TelegramAPIError(method="get_chat", message="Chat not found")
        await get_user_info(msg, mock_bot)
        msg.reply.assert_awaited_once()
        assert "Failed to get user info" in msg.reply.call_args[0][0]


class TestReplyToUser:
    async def test_success(self):
        reply_msg = _make_message_with_hashtag()
        msg = _make_message_with_hashtag()
        msg.reply_to_message = reply_msg
        await reply_to_user(msg)
        msg.copy_to.assert_awaited_once_with(12345)

    async def test_extract_id_error(self):
        msg = _make_message_with_hashtag()
        msg.reply_to_message = _make_message_with_hashtag()
        msg.reply_to_message.entities = None
        msg.reply_to_message.caption_entities = None
        await reply_to_user(msg)
        msg.reply.assert_awaited_once_with(USER_ID_ERROR)

    async def test_telegram_api_error(self):
        reply_msg = _make_message_with_hashtag()
        msg = _make_message_with_hashtag()
        msg.reply_to_message = reply_msg
        msg.copy_to.side_effect = TelegramAPIError(method="copy_message", message="Cannot forward")
        await reply_to_user(msg)
        msg.reply.assert_awaited_once()
        assert "Failed to send message to user" in msg.reply.call_args[0][0]
