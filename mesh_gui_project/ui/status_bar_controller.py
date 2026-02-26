"""
Status Bar Controller for centralized status message management.
"""
from typing import Optional


class StatusBarController:
    """Centralized controller for status bar messages."""

    DEFAULT_TIMEOUT = 5000  # 5 seconds
    SHORT_TIMEOUT = 3000    # 3 seconds

    def __init__(self, status_bar):
        """
        Initialize status bar controller.

        Args:
            status_bar: QStatusBar instance from MainWindow
        """
        self.status_bar = status_bar

    def show_ready(self):
        """Show 'Ready' status with no timeout."""
        self.status_bar.showMessage('Ready')

    def show_ready_with_context(self, context: str):
        """
        Show 'Ready' status with additional context.

        Args:
            context: Additional context information to display
        """
        message = f"Ready | {context}"
        self.status_bar.showMessage(message)

    def show_message(self, message: str, timeout: Optional[int] = None):
        """
        Show temporary message with optional timeout.

        Args:
            message: Message to display
            timeout: Timeout in milliseconds (default: DEFAULT_TIMEOUT)
        """
        timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        self.status_bar.showMessage(message, timeout)

    def show_success(self, message: str):
        """
        Show success message with default timeout.

        Args:
            message: Success message to display
        """
        self.status_bar.showMessage(message, self.DEFAULT_TIMEOUT)

    def show_info(self, message: str):
        """
        Show info message with short timeout.

        Args:
            message: Info message to display
        """
        self.status_bar.showMessage(message, self.SHORT_TIMEOUT)

    def show_error(self, message: str):
        """
        Show error message with default timeout.

        Args:
            message: Error message to display
        """
        self.status_bar.showMessage(message, self.DEFAULT_TIMEOUT)
