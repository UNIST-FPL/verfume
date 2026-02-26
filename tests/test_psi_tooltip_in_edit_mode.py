#!/usr/bin/env python
"""
Test that Ctrl+hover shows psi tooltip even when Edit Psi Contours mode is active.

This test verifies that pressing Ctrl while in Edit Psi Contours mode
shows the psi value balloon tooltip instead of the preview contour.
"""
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator
from mesh_gui_project.ui.canvas_controller import CanvasController
from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler


@pytest.fixture
def app():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_ctrl_hover_shows_tooltip_in_edit_mode(app):
    """
    Test that Ctrl+hover shows tooltip in addition to preview when Edit mode is active.

    Behavioral change: When Edit Psi Contours is ON and Ctrl is pressed,
    the tooltip should be shown in addition to the preview contour.
    """
    # Setup mock components
    canvas_controller = Mock(spec=CanvasController)
    psi_edit_handler = Mock(spec=PsiEditHandler)
    mesh_edit_handler = Mock()
    tooltip_callback = Mock()

    # Configure mocks
    canvas_controller.ax = Mock()
    canvas_controller.is_panning.return_value = False
    psi_edit_handler.is_active.return_value = True
    mesh_edit_handler.is_active.return_value = False
    mesh_edit_handler.is_dragging.return_value = False

    # Create coordinator
    coordinator = MouseInteractionCoordinator(
        psi_edit_handler=psi_edit_handler,
        mesh_edit_handler=mesh_edit_handler,
        canvas_controller=canvas_controller,
        on_tooltip_update_callback=tooltip_callback
    )

    # Create mock event with Ctrl pressed
    event = Mock()
    event.inaxes = canvas_controller.ax
    event.xdata = 1.5
    event.ydata = 0.0

    # Simulate Ctrl key pressed by patching QApplication.keyboardModifiers
    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers') as mock_modifiers:
        mock_modifiers.return_value = Qt.ControlModifier

        # Handle mouse motion
        coordinator.handle_mouse_motion(event)

    # ASSERT: Tooltip callback should be called in addition to preview handler
    tooltip_callback.assert_called_once_with(event)

    # ASSERT: PSI edit handler's mouse motion should ALSO be called (for preview)
    psi_edit_handler.handle_mouse_motion.assert_called_once_with(event)


def test_no_ctrl_shows_preview_in_edit_mode(app):
    """
    Test that without Ctrl, preview contour is shown when Edit mode is active.

    This ensures we didn't break the existing preview behavior.
    Additionally, tooltip callback is called with None to hide any visible tooltip.
    """
    # Setup mock components
    canvas_controller = Mock(spec=CanvasController)
    psi_edit_handler = Mock(spec=PsiEditHandler)
    mesh_edit_handler = Mock()
    tooltip_callback = Mock()

    # Configure mocks
    canvas_controller.ax = Mock()
    canvas_controller.is_panning.return_value = False
    psi_edit_handler.is_active.return_value = True
    psi_edit_handler.handle_mouse_motion.return_value = True
    mesh_edit_handler.is_active.return_value = False
    mesh_edit_handler.is_dragging.return_value = False

    # Create coordinator
    coordinator = MouseInteractionCoordinator(
        psi_edit_handler=psi_edit_handler,
        mesh_edit_handler=mesh_edit_handler,
        canvas_controller=canvas_controller,
        on_tooltip_update_callback=tooltip_callback
    )

    # Create mock event WITHOUT Ctrl pressed
    event = Mock()
    event.inaxes = canvas_controller.ax
    event.xdata = 1.5
    event.ydata = 0.0

    # Simulate NO Ctrl key
    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers') as mock_modifiers:
        mock_modifiers.return_value = Qt.NoModifier

        # Handle mouse motion
        coordinator.handle_mouse_motion(event)

    # ASSERT: PSI edit handler should be called (preview behavior)
    psi_edit_handler.handle_mouse_motion.assert_called_once_with(event)

    # ASSERT: Tooltip callback should be called with None to hide tooltip
    tooltip_callback.assert_called_once_with(None)
