import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("BOT_TOKEN", "test:test")
os.environ.setdefault("ADMIN_CHAT_ID", "-1001234567890")

import pytest
from aiogram.types import Chat, Message, User

from src.core.block_lists import banned, shadowbanned
from src.core.config_reader import config

ADMIN_CHAT_ID = -1001234567890
USER_ID = 12345


def pytest_configure():
    tests_dir = Path(__file__).parent
    if str(tests_dir) not in sys.path:
        sys.path.insert(0, str(tests_dir))


@pytest.fixture(autouse=True)
def _clear_block_lists():
    banned.clear()
    shadowbanned.clear()


@pytest.fixture(autouse=True)
def _patch_config():
    with (
        patch.object(config, "admin_chat_id", ADMIN_CHAT_ID),
        patch.object(config, "remove_sent_confirmation", True),  # noqa: FBT003
    ):
        yield


@pytest.fixture
def mock_bot():
    return AsyncMock()


@pytest.fixture
def mock_user_message():
    reply_result = AsyncMock()
    reply_result.delete = AsyncMock()
    msg = MagicMock(spec=Message)
    msg.message_id = 1
    msg.text = "test message"
    msg.html_text = "test message"
    msg.caption = None
    msg.content_type = "text"
    msg.reply = AsyncMock(return_value=reply_result)
    msg.answer = AsyncMock()
    msg.copy_to = AsyncMock()
    msg.delete = AsyncMock()
    msg.from_user = MagicMock(spec=User)
    msg.from_user.id = USER_ID
    msg.from_user.is_bot = False
    msg.from_user.first_name = "Test"
    msg.from_user.last_name = "User"
    msg.from_user.username = "testuser"
    msg.chat = MagicMock(spec=Chat)
    msg.chat.id = USER_ID
    msg.chat.type = "private"
    msg.entities = None
    msg.caption_entities = None
    return msg
