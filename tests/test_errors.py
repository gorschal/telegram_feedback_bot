import logging

from aiogram.types import ErrorEvent, Update

from src.handlers.errors import error_handler


class TestErrorHandler:
    async def test_logs_error(self, caplog):
        update = Update(update_id=1)
        exception = ValueError("test error")
        event = ErrorEvent(update=update, exception=exception)
        with caplog.at_level(logging.ERROR):
            await error_handler(event)
        assert "update_error" in caplog.text
