"""Unit tests for main entry point."""

from unittest.mock import Mock, patch

from eval_hub.main import main


class TestMainEntryPoint:
    """Test main entry point functionality."""

    @patch("eval_hub.main.uvicorn.run")
    @patch("eval_hub.main.create_app")
    @patch("eval_hub.main.get_settings")
    def test_main_function(self, mock_get_settings, mock_create_app, mock_uvicorn_run):
        """Test main function calls uvicorn with correct parameters."""
        # Setup mocks
        mock_settings = Mock()
        mock_settings.api_host = "0.0.0.0"
        mock_settings.api_port = 8080
        mock_settings.log_level = "INFO"
        mock_get_settings.return_value = mock_settings

        mock_app = Mock()
        mock_create_app.return_value = mock_app

        # Call main function
        main()

        # Verify function calls
        mock_get_settings.assert_called_once()
        mock_create_app.assert_called_once()

        # Verify uvicorn.run was called with correct parameters
        mock_uvicorn_run.assert_called_once_with(
            mock_app,
            host="0.0.0.0",
            port=8080,
            log_level="info",  # Should be lowercased
            access_log=True,
            server_header=False,
        )

    @patch("eval_hub.main.uvicorn.run")
    @patch("eval_hub.main.create_app")
    @patch("eval_hub.main.get_settings")
    def test_main_with_different_settings(
        self, mock_get_settings, mock_create_app, mock_uvicorn_run
    ):
        """Test main function with different settings."""
        # Setup mocks with different values
        mock_settings = Mock()
        mock_settings.api_host = "127.0.0.1"
        mock_settings.api_port = 3000
        mock_settings.log_level = "DEBUG"
        mock_get_settings.return_value = mock_settings

        mock_app = Mock()
        mock_create_app.return_value = mock_app

        # Call main function
        main()

        # Verify uvicorn.run was called with new parameters
        mock_uvicorn_run.assert_called_once_with(
            mock_app,
            host="127.0.0.1",
            port=3000,
            log_level="debug",  # Should be lowercased
            access_log=True,
            server_header=False,
        )
