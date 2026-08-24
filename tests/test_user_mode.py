from unittest.mock import AsyncMock, patch

from aiogram.types import ContentType
from constants import ADMIN_CHAT_ID, USER_ID

from src.core.block_lists import banned, shadowbanned
from src.handlers.user_mode import (
    _send_expiring_notification,
    cmd_help,
    cmd_start,
    supported_media,
    text_message,
    unsupported_types,
)


class TestCmdStart:
    async def test_sends_welcome(self, mock_user_message):
        await cmd_start(mock_user_message)
        mock_user_message.answer.assert_awaited_once()


class TestCmdHelp:
    async def test_sends_help(self, mock_user_message):
        await cmd_help(mock_user_message)
        mock_user_message.answer.assert_awaited_once()


class TestTextMessage:
    async def test_text_too_long(self, mock_user_message, mock_bot):
        mock_user_message.text = "x" * 4001
        mock_user_message.html_text = "x" * 4001
        await text_message(mock_user_message, mock_bot)
        mock_user_message.reply.assert_awaited_once()
        assert "too long" in mock_user_message.reply.call_args[0][0]

    async def test_banned_user(self, mock_user_message, mock_bot):
        banned.add(USER_ID)
        await text_message(mock_user_message, mock_bot)
        mock_user_message.answer.assert_awaited_once_with("You have been banned. Your messages will not be delivered.")
        mock_bot.send_message.assert_not_called()

    async def test_shadowbanned_user(self, mock_user_message, mock_bot):
        shadowbanned.add(USER_ID)
        await text_message(mock_user_message, mock_bot)
        mock_user_message.answer.assert_not_called()
        mock_user_message.reply.assert_not_called()
        mock_bot.send_message.assert_not_called()

    async def test_normal_user(self, mock_user_message, mock_bot):
        with patch("src.handlers.user_mode.create_task"):
            await text_message(mock_user_message, mock_bot)
        mock_bot.send_message.assert_awaited_once()
        args, kwargs = mock_bot.send_message.call_args
        chat_id, text = args[0], args[1]
        assert chat_id == ADMIN_CHAT_ID
        assert f"#id{USER_ID}" in text
        assert kwargs.get("parse_mode") == "HTML"


class TestSupportedMedia:
    async def test_caption_too_long(self, mock_user_message):
        mock_user_message.caption = "x" * 1001
        await supported_media(mock_user_message)
        mock_user_message.reply.assert_awaited_once()
        assert "too long" in mock_user_message.reply.call_args[0][0]

    async def test_banned_user(self, mock_user_message):
        banned.add(USER_ID)
        await supported_media(mock_user_message)
        mock_user_message.answer.assert_awaited_once_with("You have been banned. Your messages will not be delivered.")
        mock_user_message.copy_to.assert_not_called()

    async def test_shadowbanned_user(self, mock_user_message):
        shadowbanned.add(USER_ID)
        await supported_media(mock_user_message)
        mock_user_message.answer.assert_not_called()
        mock_user_message.reply.assert_not_called()
        mock_user_message.copy_to.assert_not_called()

    async def test_normal_user(self, mock_user_message):
        with patch("src.handlers.user_mode.create_task"):
            await supported_media(mock_user_message)
        mock_user_message.copy_to.assert_awaited_once()
        args, kwargs = mock_user_message.copy_to.call_args
        assert args[0] == ADMIN_CHAT_ID
        assert f"#id{USER_ID}" in kwargs.get("caption", "")

    async def test_normal_user_with_caption(self, mock_user_message):
        mock_user_message.caption = "photo caption"
        with patch("src.handlers.user_mode.create_task"):
            await supported_media(mock_user_message)
        mock_user_message.copy_to.assert_awaited_once()
        _, kwargs = mock_user_message.copy_to.call_args
        assert "photo caption" in kwargs["caption"]
        assert f"#id{USER_ID}" in kwargs["caption"]


class TestUnsupportedTypes:
    async def test_ignores_new_chat_members(self, mock_user_message):
        mock_user_message.content_type = ContentType.NEW_CHAT_MEMBERS
        await unsupported_types(mock_user_message)
        mock_user_message.reply.assert_not_called()

    async def test_ignores_left_chat_member(self, mock_user_message):
        mock_user_message.content_type = ContentType.LEFT_CHAT_MEMBER
        await unsupported_types(mock_user_message)
        mock_user_message.reply.assert_not_called()

    async def test_ignores_video_chat_started(self, mock_user_message):
        mock_user_message.content_type = ContentType.VIDEO_CHAT_STARTED
        await unsupported_types(mock_user_message)
        mock_user_message.reply.assert_not_called()

    async def test_ignores_video_chat_ended(self, mock_user_message):
        mock_user_message.content_type = ContentType.VIDEO_CHAT_ENDED
        await unsupported_types(mock_user_message)
        mock_user_message.reply.assert_not_called()

    async def test_ignores_video_chat_participants_invited(self, mock_user_message):
        mock_user_message.content_type = ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED
        await unsupported_types(mock_user_message)
        mock_user_message.reply.assert_not_called()

    async def test_ignores_message_auto_delete_timer_changed(self, mock_user_message):
        mock_user_message.content_type = ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED
        await unsupported_types(mock_user_message)
        mock_user_message.reply.assert_not_called()

    async def test_replies_for_unsupported_type(self, mock_user_message):
        mock_user_message.content_type = ContentType.STICKER
        await unsupported_types(mock_user_message)
        mock_user_message.reply.assert_awaited_once_with(
            "This message type is not supported. Please send something else."
        )


class TestSendExpiringNotification:
    async def test_sends_notification_and_auto_deletes(self, mock_user_message):
        with patch("src.handlers.user_mode.sleep", AsyncMock()):
            await _send_expiring_notification(mock_user_message)
        mock_user_message.reply.assert_awaited_once_with("Message sent!")
        reply_msg = mock_user_message.reply.return_value
        reply_msg.delete.assert_awaited_once()
