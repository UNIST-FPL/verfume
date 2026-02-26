"""About dialog for Verfume application."""
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon


class AboutDialog(QDialog):
    """About dialog showing application information."""

    def __init__(self, parent=None):
        """
        Initialize the About dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("About Verfume")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMaximumWidth(600)
        self.setMinimumHeight(400)

        # Set window icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'resources',
            'FPLUNIST_LOGO.png'
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._create_ui()

    def _create_ui(self):
        """Create the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header section with title/description on left and logo on right
        header_layout = QHBoxLayout()

        # Left side: Title, version, and description
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        # Title
        title_label = QLabel("Verfume")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_layout.addWidget(title_label)

        # Version
        version_label = QLabel("Version 0.0.0-beta")
        version_font = QFont()
        version_font.setPointSize(12)
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        version_label.setStyleSheet("color: gray;")
        text_layout.addWidget(version_label)

        # Description with rainbow-colored acronym parts (darker colors for better contrast)
        description_html = (
            '<span style="color: #D32F2F; font-weight: bold;">V</span>'
            '<span style="color: #F57C00; font-weight: bold;">E</span>'
            '<span style="color: #F9A825; font-weight: bold;">R</span>'
            'satile '
            '<span style="color: #388E3C; font-weight: bold;">F</span>'
            '<span style="color: #1976D2; font-weight: bold;">U</span>'
            'sion '
            '<span style="color: #7B1FA2; font-weight: bold;">M</span>'
            '<span style="color: #8E24AA; font-weight: bold;">E</span>'
            'shing tool'
        )
        description_label = QLabel(description_html)
        description_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        description_label.setWordWrap(False)
        text_layout.addWidget(description_label)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        # Right side: Logo
        logo_label = QLabel()
        # Get the path to the logo file
        # Assume the resources folder is in mesh_gui_project/resources
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'resources',
            'FPLUNIST_LOGO.png'
        )

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale the logo to a reasonable size (100x100 pixels)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            header_layout.addWidget(logo_label)

        layout.addLayout(header_layout)
        layout.addSpacing(10)

        # Information text browser (for clickable links)
        info_browser = QTextBrowser()
        info_browser.setOpenExternalLinks(True)
        info_browser.setMaximumHeight(240)
        info_browser.setStyleSheet("border: none; background-color: transparent;")

        info_text = f"""
        <p style="margin: 5px 0;"><b>Provider:</b> FPL@UNIST</p>
        <p style="margin: 5px 0;"><b>Contact:</b> <a href="mailto:esyoon@unist.ac.kr">esyoon@unist.ac.kr</a></p>
        <p style="margin: 5px 0;"><b>License:</b> AGPL-3.0</p>
        <p style="margin: 5px 0;"><b>Copyright:</b> © 2026 UNIST FPL</p>
        <p style="margin: 15px 0 5px 0;"><b>Links:</b></p>
        <p style="margin: 2px 0 2px 15px;">• GitHub: <a href="https://github.com/UNIST-FPL/verfume">github.com/UNIST-FPL/verfume</a></p>
        <p style="margin: 2px 0 2px 15px;">• Website: <a href="https://unist-fpl.github.io">unist-fpl.github.io</a></p>
        <p style="margin: 15px 0 5px 0;"><b>Contributors:</b></p>
        <p style="margin: 2px 0 2px 15px;">Eisung (E.S.) Yoon</p>
        """

        info_browser.setHtml(info_text)
        layout.addWidget(info_browser)

        layout.addSpacing(10)

        # Close button
        close_button = QPushButton("Close")
        close_button.setMaximumWidth(100)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)
