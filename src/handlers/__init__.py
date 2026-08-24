"""Package of message and command handlers for the bot.

Modules:
    admin_mode: Processing administrator replies to users.
    admin_no_reply: Warnings about missing replies to admin messages.
    bans: Ban, shadowban and unban commands.
    errors: Global error handler.
    message_edit: Processing of edited messages.
    unsupported_reply: Filter for unsupported types in admin replies.
    user_mode: Forwarding messages from users to the admin.
"""

from aiogram import Router

from . import admin_mode, admin_no_reply, bans, errors, message_edit, unsupported_reply, user_mode


def setup_routers() -> Router:
    """Creates and configures the main router with all sub-routers.

    Returns:
        The main router with the 7 connected sub-routers.
    """
    router = Router()
    router.include_router(errors.router)
    router.include_router(unsupported_reply.router)
    router.include_router(bans.router)
    router.include_router(admin_no_reply.router)
    router.include_router(admin_mode.router)
    router.include_router(message_edit.router)
    router.include_router(user_mode.router)

    return router
