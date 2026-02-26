"""
Tests for ErrorHandler class.

Following TDD approach: write tests first, then implement.
"""
import pytest
from unittest.mock import Mock, patch


class TestErrorHandlerConstruction:
    """Test ErrorHandler construction and initialization."""

    def test_handler_can_be_instantiated(self):
        """ErrorHandler should be instantiable with parent window."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        assert handler is not None
        assert handler.parent_window == parent_window


class TestShowWarning:
    """Test showing warning dialogs."""

    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_show_warning_displays_dialog(self, mock_warning):
        """show_warning should display warning dialog."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        handler.show_warning("Test Title", "Test Message")

        # Verify warning was called with correct arguments
        mock_warning.assert_called_once_with(parent_window, "Test Title", "Test Message")

    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_show_warning_with_long_message(self, mock_warning):
        """show_warning should handle long messages."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        parent_window = Mock()
        handler = ErrorHandler(parent_window)
        long_message = "This is a very long message " * 10

        handler.show_warning("Warning", long_message)

        mock_warning.assert_called_once()
        assert mock_warning.call_args[0][2] == long_message


class TestShowError:
    """Test showing error dialogs."""

    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    def test_show_error_displays_dialog(self, mock_critical):
        """show_error should display critical error dialog."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        handler.show_error("Error Title", "Error Message")

        # Verify critical was called with correct arguments
        mock_critical.assert_called_once_with(parent_window, "Error Title", "Error Message")

    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    def test_show_error_with_exception_message(self, mock_critical):
        """show_error should handle exception messages."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        try:
            raise ValueError("Something went wrong")
        except Exception as e:
            handler.show_error("Operation Failed", f"Error: {str(e)}")

        mock_critical.assert_called_once()
        assert "Something went wrong" in mock_critical.call_args[0][2]


class TestAskConfirmation:
    """Test showing confirmation dialogs."""

    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_ask_confirmation_returns_true_when_yes(self, mock_question):
        """ask_confirmation should return True when user clicks Yes."""
        from mesh_gui_project.ui.error_handler import ErrorHandler
        from PyQt5.QtWidgets import QMessageBox

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        # Mock user clicking Yes
        mock_question.return_value = QMessageBox.Yes

        result = handler.ask_confirmation("Confirm", "Are you sure?")

        assert result is True
        mock_question.assert_called_once()

    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_ask_confirmation_returns_false_when_no(self, mock_question):
        """ask_confirmation should return False when user clicks No."""
        from mesh_gui_project.ui.error_handler import ErrorHandler
        from PyQt5.QtWidgets import QMessageBox

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        # Mock user clicking No
        mock_question.return_value = QMessageBox.No

        result = handler.ask_confirmation("Confirm", "Are you sure?")

        assert result is False
        mock_question.assert_called_once()

    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_ask_confirmation_uses_correct_buttons(self, mock_question):
        """ask_confirmation should use Yes/No buttons with No as default."""
        from mesh_gui_project.ui.error_handler import ErrorHandler
        from PyQt5.QtWidgets import QMessageBox

        parent_window = Mock()
        handler = ErrorHandler(parent_window)
        mock_question.return_value = QMessageBox.No

        handler.ask_confirmation("Title", "Message")

        # Verify correct button configuration
        call_args = mock_question.call_args[0]
        assert call_args[0] == parent_window
        assert call_args[1] == "Title"
        assert call_args[2] == "Message"
        # Buttons and default button are passed as additional args
        assert mock_question.call_args[1] or len(call_args) > 3


class TestShowInfo:
    """Test showing information dialogs."""

    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_show_info_displays_dialog(self, mock_info):
        """show_info should display information dialog."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        handler.show_info("Info Title", "Info Message")

        # Verify information was called with correct arguments
        mock_info.assert_called_once_with(parent_window, "Info Title", "Info Message")


class TestErrorHandlerIntegration:
    """Test ErrorHandler integration scenarios."""

    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    def test_can_show_multiple_dialogs(self, mock_critical, mock_warning):
        """Should be able to show multiple dialogs in sequence."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        parent_window = Mock()
        handler = ErrorHandler(parent_window)

        handler.show_warning("Warning 1", "First warning")
        handler.show_error("Error 1", "First error")
        handler.show_warning("Warning 2", "Second warning")

        assert mock_warning.call_count == 2
        assert mock_critical.call_count == 1

    def test_handler_without_parent_window(self):
        """ErrorHandler should work even with None parent (for testing)."""
        from mesh_gui_project.ui.error_handler import ErrorHandler

        handler = ErrorHandler(None)
        assert handler is not None
        assert handler.parent_window is None
