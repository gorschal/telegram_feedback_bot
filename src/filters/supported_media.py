from aiogram.filters import BaseFilter
from aiogram.types import ContentType, Message


class SupportedMediaFilter(BaseFilter):
    """Filter for checking whether a message contains supported media types.

    Supported types: animation, audio, document, photo, video, voice messages.
    """

    def __call__(self, message: Message) -> bool:
        """Checks whether the message content type is a supported media.

        Args:
            message: The message object to check.

        Returns:
            True if the message contains supported media, otherwise False.
        """
        return message.content_type in (
            ContentType.ANIMATION,
            ContentType.AUDIO,
            ContentType.DOCUMENT,
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.VOICE,
        )
