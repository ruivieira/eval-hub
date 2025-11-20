"""Unit tests for logging utilities."""

from unittest.mock import Mock

from eval_hub.core.logging import log_evaluation_complete


class TestLoggingUtilities:
    """Test logging utility functions."""

    def test_log_evaluation_complete(self):
        """Test log_evaluation_complete function."""
        # Create mock logger
        mock_logger = Mock()

        # Call the function
        log_evaluation_complete(
            logger=mock_logger,
            evaluation_id="test-eval-123",
            status="completed",
            duration_seconds=45.5,
            additional_info="test data",
        )

        # Verify the logger was called correctly
        mock_logger.info.assert_called_once_with(
            "Evaluation completed",
            evaluation_id="test-eval-123",
            status="completed",
            duration_seconds=45.5,
            additional_info="test data",
        )

    def test_log_evaluation_complete_minimal_args(self):
        """Test log_evaluation_complete with minimal arguments."""
        mock_logger = Mock()

        log_evaluation_complete(
            logger=mock_logger,
            evaluation_id="eval-456",
            status="failed",
            duration_seconds=12.0,
        )

        mock_logger.info.assert_called_once_with(
            "Evaluation completed",
            evaluation_id="eval-456",
            status="failed",
            duration_seconds=12.0,
        )
