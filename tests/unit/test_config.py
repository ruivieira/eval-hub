"""Unit tests for configuration utilities."""

from eval_hub.core.config import Settings


class TestConfigUtilities:
    """Test configuration utility functions."""

    def test_settings_basic_initialization(self):
        """Test that Settings can be initialized with basic values."""
        settings = Settings(app_name="Test App", debug=True, api_port=9000)

        assert settings.app_name == "Test App"
        assert settings.debug is True
        assert settings.api_port == 9000

    def test_settings_defaults(self):
        """Test Settings default values."""
        settings = Settings()

        assert settings.app_name == "Eval Hub"
        assert settings.version == "0.1.0"
        assert settings.debug is False
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.max_concurrent_evaluations == 10

    def test_backend_configs_default(self):
        """Test default backend configurations."""
        settings = Settings()

        assert "lm-evaluation-harness" in settings.backend_configs
        assert "guidellm" in settings.backend_configs

        lm_eval_config = settings.backend_configs["lm-evaluation-harness"]
        assert lm_eval_config["image"] == "eval-harness:latest"
        assert lm_eval_config["timeout"] == 3600
