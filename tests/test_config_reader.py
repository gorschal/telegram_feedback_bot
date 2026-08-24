from src.core.config_reader import Settings


class TestSettings:
    def test_create_with_explicit_values(self):
        s = Settings(bot_token="test:token", admin_chat_id=-1001234567890)
        assert s.admin_chat_id == -1001234567890
        assert s.bot_token.get_secret_value() == "test:token"
        assert s.debug is True
        assert s.remove_sent_confirmation is True

    def test_default_values(self):
        s = Settings(bot_token="test:token", admin_chat_id=123)
        assert s.webhook_path == "/webhook"
        assert s.app_host == "0.0.0.0"  # noqa: S104
        assert s.app_port == 9000
        assert s.webhook_domain is None
        assert s.custom_bot_api is None

    def test_override_defaults(self):
        s = Settings(
            bot_token="test:token",
            admin_chat_id=123,
            debug=False,
            remove_sent_confirmation=False,
            webhook_domain="https://example.com",
        )
        assert s.debug is False
        assert s.remove_sent_confirmation is False
        assert s.webhook_domain == "https://example.com"
