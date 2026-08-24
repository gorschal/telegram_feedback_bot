from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommandScopeChat, BotCommandScopeDefault
from constants import ADMIN_CHAT_ID

from src.core.commands_worker import set_bot_commands


class TestSetBotCommands:
    async def test_sets_user_and_admin_commands(self, mock_bot):
        await set_bot_commands(mock_bot)
        assert mock_bot.set_my_commands.await_count == 2

    async def test_user_commands_scope(self, mock_bot):
        await set_bot_commands(mock_bot)
        call = mock_bot.set_my_commands.call_args_list[0]
        commands, kwargs = call[0], call[1]
        assert len(commands[0]) == 1
        assert commands[0][0].command == "help"
        assert isinstance(kwargs["scope"], BotCommandScopeDefault)

    async def test_admin_commands_scope(self, mock_bot):
        await set_bot_commands(mock_bot)
        call = mock_bot.set_my_commands.call_args_list[1]
        commands, kwargs = call[0], call[1]
        assert len(commands[0]) == 5
        admin_commands = {c.command for c in commands[0]}
        assert admin_commands == {"who", "ban", "shadowban", "unban", "list_banned"}
        assert isinstance(kwargs["scope"], BotCommandScopeChat)
        assert kwargs["scope"].chat_id == ADMIN_CHAT_ID

    async def test_handles_telegram_bad_request_gracefully(self, mock_bot):
        mock_bot.set_my_commands.side_effect = [
            None,
            TelegramBadRequest(method="set_my_commands", message="Chat not found"),
        ]
        await set_bot_commands(mock_bot)  # should not raise
        assert mock_bot.set_my_commands.await_count == 2
