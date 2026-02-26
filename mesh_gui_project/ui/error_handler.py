"""
Error Handler for centralized dialog management.

Extracted from MainWindow as part of Phase 3 Quick Wins refactoring.
Provides consistent error, warning, confirmation, and info dialogs.
"""
from typing import Optional
from PyQt5.QtWidgets import QMessageBox, QWidget


class ErrorHandler:
    """
    Centralized handler for error and information dialogs.

    Responsibilities:
    - Show warning dialogs
    - Show error/critical dialogs
    - Show confirmation dialogs (Yes/No)
    - Show information dialogs
    - Provide consistent dialog styling and behavior
    """

    def __init__(self, parent_window: Optional[QWidget] = None):
        """
        Initialize error handler.

        Args:
            parent_window: Parent QWidget for dialogs (can be None for testing)
        """
        self.parent_window = parent_window

    def show_warning(self, title: str, message: str):
        """
        Show a warning dialog.

        Args:
            title: Dialog title
            message: Warning message to display
        """
        QMessageBox.warning(self.parent_window, title, message)

    def show_error(self, title: str, message: str):
        """
        Show a critical error dialog.

        Args:
            title: Dialog title
            message: Error message to display
        """
        QMessageBox.critical(self.parent_window, title, message)

    def ask_confirmation(self, title: str, message: str) -> bool:
        """
        Show a confirmation dialog with Yes/No buttons.

        Args:
            title: Dialog title
            message: Confirmation question to display

        Returns:
            True if user clicked Yes, False if user clicked No
        """
        reply = QMessageBox.question(
            self.parent_window,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default button
        )
        return reply == QMessageBox.Yes

    def show_info(self, title: str, message: str):
        """
        Show an information dialog.

        Args:
            title: Dialog title
            message: Information message to display
        """
        QMessageBox.information(self.parent_window, title, message)
