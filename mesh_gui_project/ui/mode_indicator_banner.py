"""
Mode Indicator Banner widget.

Displays a colored banner at the top of the canvas showing the active edit mode
and available actions. Part of Phase 1 UX improvements.
"""
from PyQt5.QtWidgets import QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor


class ModeIndicatorBanner(QFrame):
    """
    Banner widget that displays the current edit mode and available actions.

    Shows:
    - Yellow banner for PSI Edit Mode with actions
    - Orange banner for Mesh Edit Mode with actions
    - Hidden when no edit mode is active
    """

    def __init__(self, parent=None):
        """Initialize mode indicator banner."""
        super().__init__(parent)

        # Create label for mode text
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11pt;
                padding: 8px;
                color: #000000;
            }
        """)

        # Set frame style
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)

        # Layout
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Initially hidden
        self.hide()

    def show_psi_edit_mode(self):
        """Show banner for PSI Edit Mode."""
        self.label.setText("EDIT MODE: PSI Contours  |  Left-Click: Add  |  Right-Click: Delete  |  Ctrl+Hover: Show Values")

        # Set yellow background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 200))  # Light yellow
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.show()

    def show_mesh_edit_mode(self):
        """Show banner for Mesh Edit Mode."""
        self.label.setText("EDIT MODE: Mesh Vertices  |  Click: Select Vertex  |  Drag: Move Vertex  |  Boundary vertices constrained to contour")

        # Set orange background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 220, 180))  # Light orange
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.show()

    def hide_mode(self):
        """Hide the mode indicator banner."""
        self.hide()
