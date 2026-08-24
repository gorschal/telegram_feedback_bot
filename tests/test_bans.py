from unittest.mock import AsyncMock, MagicMock

from aiogram.types import Message, MessageEntity
from constants import ADMIN_CHAT_ID

from src.core.block_lists import banned, shadowbanned
from src.handlers.bans import cmd_ban, cmd_list_banned, cmd_shadowban, cmd_unban


def _make_reply_msg(user_id: int = 12345) -> MagicMock:
    hashtag = f"#id{user_id}"
    reply = MagicMock(spec=Message)
    reply.text = f"Some text {hashtag}"
    reply.caption = None
    offset = reply.text.find(hashtag)
    reply.entities = [MessageEntity(type="hashtag", offset=offset, length=len(hashtag))]
    reply.caption_entities = None
    return reply


def _make_admin_msg(reply_to_message=None) -> MagicMock:
    msg = MagicMock(spec=Message)
    msg.reply = AsyncMock()
    msg.answer = AsyncMock()
    msg.reply_to_message = reply_to_message
    msg.chat = MagicMock()
    msg.chat.id = ADMIN_CHAT_ID
    msg.from_user = MagicMock()
    msg.from_user.id = 99999
    return msg


class TestCmdBan:
    async def test_ban_user(self):
        reply = _make_reply_msg()
        msg = _make_admin_msg(reply_to_message=reply)
        await cmd_ban(msg)
        assert 12345 in banned
        msg.reply.assert_awaited_once()
        assert "banned" in msg.reply.call_args[0][0]

    async def test_extract_error(self):
        msg = _make_admin_msg(reply_to_message=_make_reply_msg())
        msg.reply_to_message.entities = None
        msg.reply_to_message.caption_entities = None
        await cmd_ban(msg)
        assert 12345 not in banned
        msg.reply.assert_awaited_once()


class TestCmdShadowban:
    async def test_shadowban_user(self):
        reply = _make_reply_msg()
        msg = _make_admin_msg(reply_to_message=reply)
        await cmd_shadowban(msg)
        assert 12345 in shadowbanned
        msg.reply.assert_awaited_once()
        assert "shadowbanned" in msg.reply.call_args[0][0]

    async def test_extract_error(self):
        msg = _make_admin_msg(reply_to_message=_make_reply_msg())
        msg.reply_to_message.entities = None
        msg.reply_to_message.caption_entities = None
        await cmd_shadowban(msg)
        assert 12345 not in shadowbanned
        msg.reply.assert_awaited_once()


class TestCmdUnban:
    async def test_unban_banned_user(self):
        banned.add(12345)
        reply = _make_reply_msg()
        msg = _make_admin_msg(reply_to_message=reply)
        await cmd_unban(msg)
        assert 12345 not in banned
        assert 12345 not in shadowbanned
        msg.reply.assert_awaited_once()
        assert "unbanned" in msg.reply.call_args[0][0]

    async def test_unban_shadowbanned_user(self):
        shadowbanned.add(12345)
        reply = _make_reply_msg()
        msg = _make_admin_msg(reply_to_message=reply)
        await cmd_unban(msg)
        assert 12345 not in banned
        assert 12345 not in shadowbanned
        msg.reply.assert_awaited_once()
        assert "unbanned" in msg.reply.call_args[0][0]

    async def test_unban_not_banned_user(self):
        reply = _make_reply_msg()
        msg = _make_admin_msg(reply_to_message=reply)
        await cmd_unban(msg)
        msg.reply.assert_awaited_once()
        assert "unbanned" in msg.reply.call_args[0][0]

    async def test_extract_error(self):
        msg = _make_admin_msg(reply_to_message=_make_reply_msg())
        msg.reply_to_message.entities = None
        msg.reply_to_message.caption_entities = None
        await cmd_unban(msg)
        msg.reply.assert_awaited_once()


class TestCmdListBanned:
    async def test_no_bans(self):
        msg = _make_admin_msg()
        await cmd_list_banned(msg)
        msg.answer.assert_awaited_once_with("No banned users.")

    async def test_with_banned_users(self):
        banned.add(1)
        banned.add(2)
        msg = _make_admin_msg()
        await cmd_list_banned(msg)
        msg.answer.assert_awaited_once()
        text = msg.answer.call_args[0][0]
        assert "Banned users:" in text
        assert "#id1" in text
        assert "#id2" in text

    async def test_with_shadowbanned_users(self):
        shadowbanned.add(3)
        msg = _make_admin_msg()
        await cmd_list_banned(msg)
        msg.answer.assert_awaited_once()
        text = msg.answer.call_args[0][0]
        assert "Shadowbanned users:" in text
        assert "#id3" in text

    async def test_with_both_banned_and_shadowbanned(self):
        banned.add(1)
        shadowbanned.add(2)
        msg = _make_admin_msg()
        await cmd_list_banned(msg)
        msg.answer.assert_awaited_once()
        text = msg.answer.call_args[0][0]
        assert "Banned users:" in text
        assert "Shadowbanned users:" in text
