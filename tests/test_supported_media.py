from unittest.mock import MagicMock

from aiogram.types import ContentType

from src.filters import SupportedMediaFilter


class TestSupportedMediaFilter:
    @staticmethod
    def _make_message(content_type: str) -> MagicMock:
        msg = MagicMock()
        msg.content_type = content_type
        return msg

    def test_supported_animation(self):
        assert SupportedMediaFilter()(self._make_message(ContentType.ANIMATION))

    def test_supported_audio(self):
        assert SupportedMediaFilter()(self._make_message(ContentType.AUDIO))

    def test_supported_document(self):
        assert SupportedMediaFilter()(self._make_message(ContentType.DOCUMENT))

    def test_supported_photo(self):
        assert SupportedMediaFilter()(self._make_message(ContentType.PHOTO))

    def test_supported_video(self):
        assert SupportedMediaFilter()(self._make_message(ContentType.VIDEO))

    def test_supported_voice(self):
        assert SupportedMediaFilter()(self._make_message(ContentType.VOICE))

    def test_unsupported_text(self):
        assert not SupportedMediaFilter()(self._make_message(ContentType.TEXT))

    def test_unsupported_sticker(self):
        assert not SupportedMediaFilter()(self._make_message(ContentType.STICKER))

    def test_unsupported_location(self):
        assert not SupportedMediaFilter()(self._make_message(ContentType.LOCATION))

    def test_unsupported_poll(self):
        assert not SupportedMediaFilter()(self._make_message(ContentType.POLL))

    def test_unsupported_contact(self):
        assert not SupportedMediaFilter()(self._make_message(ContentType.CONTACT))
