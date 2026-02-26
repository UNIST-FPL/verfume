"""
Workflow Breadcrumb Indicator widget.

Displays the current step in the mesh generation workflow.
Part of Phase 1 UX improvements.
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont


class WorkflowBreadcrumb(QWidget):
    """
    Breadcrumb widget that shows the workflow: Load → Select → Generate → Optimize → Export

    Shows current step highlighted, completed steps in normal color, and future steps grayed out.
    """

    def __init__(self, parent=None):
        """Initialize workflow breadcrumb."""
        super().__init__(parent)

        # Create horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Define workflow steps (step_id, step_name)
        self.steps = [
            ("load", "Load File"),
            ("select", "Select Contour"),
            ("generate", "Generate Mesh"),
            ("optimize", "Optimize"),
            ("export", "Export")
        ]

        # Create labels for each step
        self.step_labels = []
        for i, (step_id, step_name) in enumerate(self.steps):
            # Add arrow between steps (except before first)
            if i > 0:
                arrow = QLabel(" → ")
                arrow.setStyleSheet("color: #666666; font-weight: bold;")
                layout.addWidget(arrow)

            # Create step label
            label = QLabel(step_name)
            label.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setPointSize(9)
            label.setFont(font)

            # Store reference
            self.step_labels.append((step_id, label))
            layout.addWidget(label)

        # Add stretch to left-align
        layout.addStretch()

        # Set initial state (no file loaded)
        self.set_step(None)

        # Set overall styling
        self.setStyleSheet("""
            WorkflowBreadcrumb {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
            }
        """)

    def set_step(self, current_step_id: str = None, skip_steps: list = None):
        """
        Set the current workflow step.

        Args:
            current_step_id: ID of current step ("load", "select", "generate", "optimize", "export")
                            or None to reset to initial state
            skip_steps: List of step IDs to mark as completed even if not current
                       (e.g., ["select"] when generating mesh from limiter)
        """
        if skip_steps is None:
            skip_steps = []

        # Find index of current step
        current_index = -1
        for i, (step_id, _) in enumerate(self.steps):
            if step_id == current_step_id:
                current_index = i
                break

        # Build set of step IDs to mark as completed
        skipped_step_ids = set(skip_steps)

        # Update label styles
        for i, (step_id, label) in enumerate(self.step_labels):
            step_name = self.steps[i][1]  # Get step name from tuple

            if current_index < 0:
                # No step active - all grayed out
                label.setText(step_name)  # Reset to original text (no checkmark)
                label.setStyleSheet("color: #999999; padding: 2px 4px;")
            elif i < current_index or step_id in skipped_step_ids:
                # Completed step (either passed or explicitly skipped) - green checkmark
                label.setText(f"✓ {step_name}")
                label.setStyleSheet("color: #00aa00; font-weight: bold; padding: 2px 4px;")
            elif i == current_index:
                # Current step - highlighted
                label.setText(step_name)
                label.setStyleSheet("""
                    color: #000000;
                    font-weight: bold;
                    background-color: #ffeb3b;
                    padding: 2px 4px;
                    border-radius: 3px;
                """)
            else:
                # Future step - grayed out
                label.setText(step_name)
                label.setStyleSheet("color: #999999; padding: 2px 4px;")
