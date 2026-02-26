"""Main entry point for mesh_gui_project."""
import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

from mesh_gui_project.ui.main_window import MainWindow
from mesh_gui_project.utils.logging_setup import setup_logging


def main():
    """
    Main entry point for the application.

    Initializes QApplication, creates MainWindow, and shows it.
    Provides user-friendly error dialogs on exceptions.
    """
    # Set up logging
    logger = setup_logging()
    logger.info("Starting Verfume")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Verfume")
    app.setOrganizationName("FPL@UNIST")

    # Set application icon
    icon_path = os.path.join(
        os.path.dirname(__file__),
        'mesh_gui_project',
        'resources',
        'FPLUNIST_LOGO.png'
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    try:
        # Create and show main window
        window = MainWindow()
        window.show()

        logger.info("Main window created and shown")

        # Start event loop
        return app.exec_()

    except Exception as e:
        # Log the exception
        logger.error(f"Fatal error: {e}", exc_info=True)

        # Show user-friendly error dialog
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText("An unexpected error occurred")
        error_dialog.setInformativeText(str(e))
        error_dialog.setDetailedText(traceback.format_exc())
        error_dialog.exec_()

        return 1


if __name__ == '__main__':
    sys.exit(main())
