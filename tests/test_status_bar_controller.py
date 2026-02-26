"""
Tests for StatusBarController.

This module tests the status bar message controller which provides
centralized, semantic methods for displaying status messages.
"""
import pytest
from unittest.mock import Mock, call
from mesh_gui_project.ui.status_bar_controller import StatusBarController


class TestStatusBarControllerConstruction:
    """Test StatusBarController construction."""

    def test_controller_can_be_instantiated(self):
        """StatusBarController should be instantiable with a status bar."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)
        assert controller is not None
        assert controller.status_bar == mock_status_bar


class TestStatusBarControllerReady:
    """Test 'Ready' status display."""

    def test_show_ready_displays_ready_message(self):
        """show_ready should display 'Ready' with no timeout."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)

        controller.show_ready()

        mock_status_bar.showMessage.assert_called_once_with('Ready')

    def test_show_ready_with_context(self):
        """show_ready_with_context should display 'Ready' with context info."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)

        controller.show_ready_with_context("Waiting for input")

        # Should combine messages
        expected_call = call("Ready | Waiting for input")
        assert expected_call in mock_status_bar.showMessage.call_args_list


class TestStatusBarControllerMessages:
    """Test general message display."""

    def test_show_message_with_default_timeout(self):
        """show_message should use default timeout when not specified."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)

        controller.show_message("Test message")

        mock_status_bar.showMessage.assert_called_once_with(
            "Test message",
            StatusBarController.DEFAULT_TIMEOUT
        )

    def test_show_message_with_custom_timeout(self):
        """show_message should use custom timeout when specified."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)

        controller.show_message("Test message", timeout=3000)

        mock_status_bar.showMessage.assert_called_once_with("Test message", 3000)


class TestStatusBarControllerSuccess:
    """Test success message display."""

    def test_show_success_uses_default_timeout(self):
        """show_success should display message with default timeout."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)

        controller.show_success("Operation completed")

        mock_status_bar.showMessage.assert_called_once_with(
            "Operation completed",
            StatusBarController.DEFAULT_TIMEOUT
        )


class TestStatusBarControllerInfo:
    """Test info message display."""

    def test_show_info_uses_short_timeout(self):
        """show_info should display message with short timeout."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)

        controller.show_info("Processing...")

        mock_status_bar.showMessage.assert_called_once_with(
            "Processing...",
            StatusBarController.SHORT_TIMEOUT
        )


class TestStatusBarControllerError:
    """Test error message display."""

    def test_show_error_uses_default_timeout(self):
        """show_error should display error message with default timeout."""
        mock_status_bar = Mock()
        controller = StatusBarController(mock_status_bar)

        controller.show_error("Operation failed: test error")

        mock_status_bar.showMessage.assert_called_once_with(
            "Operation failed: test error",
            StatusBarController.DEFAULT_TIMEOUT
        )


class TestStatusBarControllerConstants:
    """Test timeout constants."""

    def test_default_timeout_is_5_seconds(self):
        """DEFAULT_TIMEOUT should be 5000 milliseconds."""
        assert StatusBarController.DEFAULT_TIMEOUT == 5000

    def test_short_timeout_is_3_seconds(self):
        """SHORT_TIMEOUT should be 3000 milliseconds."""
        assert StatusBarController.SHORT_TIMEOUT == 3000
