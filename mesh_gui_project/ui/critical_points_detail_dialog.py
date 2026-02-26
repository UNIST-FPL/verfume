"""
Detail dialog for displaying full precision critical points data.

Shows comprehensive information about O-points and X-points including
comparisons with gEQDSK header values.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QTabWidget, QWidget, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CriticalPointsDetailDialog(QDialog):
    """Dialog showing detailed critical points information with full precision."""

    def __init__(self, handler, parent=None):
        """
        Initialize the detail dialog.

        Args:
            handler: PsiCriticalPointsHandler instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.handler = handler
        self.setWindowTitle("Critical Points Analysis - Detailed View")
        self.setMinimumSize(700, 500)

        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        """Setup the dialog UI with tabs and text displays."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Full Report (all data)
        self.full_report_text = QTextEdit()
        self.full_report_text.setReadOnly(True)
        self.full_report_text.setFont(QFont("Monospace", 9))
        self.tabs.addTab(self.full_report_text, "Full Report")

        # Tab 2: O-Points only
        self.o_points_text = QTextEdit()
        self.o_points_text.setReadOnly(True)
        self.o_points_text.setFont(QFont("Monospace", 9))
        self.tabs.addTab(self.o_points_text, "O-Points")

        # Tab 3: X-Points only
        self.x_points_text = QTextEdit()
        self.x_points_text.setReadOnly(True)
        self.x_points_text.setFont(QFont("Monospace", 9))
        self.tabs.addTab(self.x_points_text, "X-Points")

        # Button layout
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_button)

        button_layout.addStretch()

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

    def _populate_data(self):
        """Populate all tabs with critical points data."""
        # Get full formatted text from handler
        full_text = self.handler.format_display_text()
        self.full_report_text.setPlainText(full_text)

        # Extract O-Points section
        o_points_text = self._extract_section(full_text, "O-Points:")
        self.o_points_text.setPlainText(o_points_text)

        # Extract X-Points section
        x_points_text = self._extract_section(full_text, "X-Points:")
        self.x_points_text.setPlainText(x_points_text)

    def _extract_section(self, text: str, section_header: str) -> str:
        """
        Extract a specific section from the full text.

        Args:
            text: Full text containing multiple sections
            section_header: Header to search for (e.g., "O-Points:")

        Returns:
            Extracted section text
        """
        lines = text.split('\n')
        section_lines = []
        in_section = False

        for line in lines:
            if line.startswith(section_header):
                in_section = True
                section_lines.append(line)
            elif in_section:
                # Check if we've reached another section header
                if line and not line.startswith(' ') and ':' in line:
                    break
                section_lines.append(line)

        return '\n'.join(section_lines) if section_lines else "No data"

    def _copy_to_clipboard(self):
        """Copy current tab content to clipboard."""
        current_tab_index = self.tabs.currentIndex()

        if current_tab_index == 0:
            text = self.full_report_text.toPlainText()
        elif current_tab_index == 1:
            text = self.o_points_text.toPlainText()
        else:
            text = self.x_points_text.toPlainText()

        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        # Update button text briefly
        original_text = self.copy_button.text()
        self.copy_button.setText("Copied!")
        QApplication.processEvents()

        # Reset button text after delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.copy_button.setText(original_text))
