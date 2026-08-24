"""Global error handler.

Catches all unhandled exceptions and logs them with full context.
"""

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)

router = Router()


@router.errors()
async def error_handler(event: ErrorEvent) -> None:
    """Logs errors with a full stack trace for debugging."""
    logger.exception("update_error", extra={"update": event.update})
