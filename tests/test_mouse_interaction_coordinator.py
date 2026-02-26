"""
Tests for MouseInteractionCoordinator class.

Following TDD approach: write tests first, then implement.
"""
import pytest
from unittest.mock import Mock, MagicMock, call


class TestMouseInteractionCoordinatorConstruction:
    """Test MouseInteractionCoordinator construction and initialization."""

    def test_coordinator_can_be_instantiated(self):
        """MouseInteractionCoordinator should be instantiable with required dependencies."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        # Mock dependencies
        psi_edit_handler = Mock()
        mesh_edit_handler = Mock()
        canvas_controller = Mock()
        on_tooltip_update = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=on_tooltip_update
        )

        assert coordinator is not None


class TestMousePressRouting:
    """Test mouse press event routing to appropriate handlers."""

    def test_mesh_edit_mode_gets_priority_on_left_click(self):
        """When mesh edit mode is active, it should handle left-clicks first."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_active.return_value = True
        mesh_edit_handler.handle_mouse_press.return_value = True  # Handled

        psi_edit_handler = Mock()
        psi_edit_handler.is_active.return_value = False

        canvas_controller = Mock()
        canvas_controller.ax = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.inaxes = canvas_controller.ax
        event.button = 1
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_mouse_press(event)

        # Mesh edit handler should be called
        mesh_edit_handler.handle_mouse_press.assert_called_once_with(event)
        # PSI edit handler should NOT be called
        psi_edit_handler.handle_mouse_press.assert_not_called()
        # Pan should NOT be started
        canvas_controller.start_pan.assert_not_called()

    def test_psi_edit_mode_handles_left_click_when_mesh_inactive(self):
        """PSI edit mode handles left-click when mesh edit is inactive."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        psi_edit_handler = Mock()
        psi_edit_handler.is_active.return_value = True
        psi_edit_handler.handle_mouse_press.return_value = True

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_active.return_value = False

        canvas_controller = Mock()
        canvas_controller.ax = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.inaxes = canvas_controller.ax
        event.button = 1
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_mouse_press(event)

        # PSI edit handler should be called
        psi_edit_handler.handle_mouse_press.assert_called_once_with(event, button=1)
        # Pan should NOT be started
        canvas_controller.start_pan.assert_not_called()

    def test_psi_edit_mode_handles_right_click(self):
        """PSI edit mode should handle right-clicks (delete contour)."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        psi_edit_handler = Mock()
        psi_edit_handler.is_active.return_value = True
        psi_edit_handler.handle_mouse_press.return_value = True

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_active.return_value = False

        canvas_controller = Mock()
        canvas_controller.ax = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.inaxes = canvas_controller.ax
        event.button = 3  # Right-click
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_mouse_press(event)

        # PSI edit handler should be called with button=3
        psi_edit_handler.handle_mouse_press.assert_called_once_with(event, button=3)

    def test_pan_starts_when_no_edit_mode_active(self):
        """When no edit mode is active, left-click should start panning."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        psi_edit_handler = Mock()
        psi_edit_handler.is_active.return_value = False

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_active.return_value = False

        canvas_controller = Mock()
        canvas_controller.ax = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.inaxes = canvas_controller.ax
        event.button = 1
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_mouse_press(event)

        # Pan should be started
        canvas_controller.start_pan.assert_called_once_with(1.5, 0.5)

    def test_click_outside_axes_does_nothing(self):
        """Clicks outside axes should not trigger any action."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        psi_edit_handler = Mock()
        mesh_edit_handler = Mock()
        canvas_controller = Mock()
        canvas_controller.ax = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.inaxes = None  # Outside axes
        event.button = 1

        coordinator.handle_mouse_press(event)

        # Nothing should be called
        psi_edit_handler.handle_mouse_press.assert_not_called()
        mesh_edit_handler.handle_mouse_press.assert_not_called()
        canvas_controller.start_pan.assert_not_called()


class TestMouseReleaseRouting:
    """Test mouse release event routing."""

    def test_mesh_edit_handler_gets_release_event(self):
        """Mouse release should be routed to mesh edit handler."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        mesh_edit_handler = Mock()
        mesh_edit_handler.handle_mouse_release.return_value = True

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=Mock(),
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=Mock(),
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.button = 1

        coordinator.handle_mouse_release(event)

        # Mesh edit handler should be called
        mesh_edit_handler.handle_mouse_release.assert_called_once_with(event)

    def test_pan_ends_when_mesh_edit_not_handling(self):
        """When mesh edit doesn't handle release, pan should end."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        mesh_edit_handler = Mock()
        mesh_edit_handler.handle_mouse_release.return_value = False  # Not handled

        canvas_controller = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=Mock(),
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.button = 1

        coordinator.handle_mouse_release(event)

        # Pan should end
        canvas_controller.end_pan.assert_called_once()


class TestMouseMotionRouting:
    """Test mouse motion event routing with priority system."""

    def test_mesh_dragging_has_highest_priority(self):
        """When dragging a vertex, mesh edit handler gets priority."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_dragging.return_value = True
        mesh_edit_handler.handle_mouse_motion.return_value = True

        psi_edit_handler = Mock()
        canvas_controller = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_mouse_motion(event)

        # Mesh edit should handle
        mesh_edit_handler.handle_mouse_motion.assert_called_once_with(event)
        # PSI edit and pan should NOT be called
        psi_edit_handler.handle_mouse_motion.assert_not_called()
        canvas_controller.update_pan.assert_not_called()

    def test_panning_has_second_priority(self):
        """When panning, pan should be updated."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_dragging.return_value = False

        psi_edit_handler = Mock()

        canvas_controller = Mock()
        canvas_controller.is_panning.return_value = True
        canvas_controller.ax = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.inaxes = canvas_controller.ax
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_mouse_motion(event)

        # Pan should be updated
        canvas_controller.update_pan.assert_called_once_with(1.5, 0.5)
        # PSI edit should NOT be called
        psi_edit_handler.handle_mouse_motion.assert_not_called()

    def test_psi_edit_preview_when_not_dragging_or_panning(self):
        """PSI edit mode shows preview when not dragging or panning."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator
        from unittest.mock import patch

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_dragging.return_value = False

        psi_edit_handler = Mock()
        psi_edit_handler.is_active.return_value = True
        psi_edit_handler.handle_mouse_motion.return_value = True

        canvas_controller = Mock()
        canvas_controller.is_panning.return_value = False
        canvas_controller.canvas = None  # Prevent setCursor from being called

        on_tooltip_update = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=on_tooltip_update
        )

        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.5

        # Mock QApplication.keyboardModifiers to return no modifiers (Ctrl not pressed)
        with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=0):
            coordinator.handle_mouse_motion(event)

        # PSI edit should handle (show preview)
        psi_edit_handler.handle_mouse_motion.assert_called_once_with(event)
        # Tooltip callback should be called with None to hide tooltip (Ctrl not pressed)
        on_tooltip_update.assert_called_once_with(None)

    def test_tooltip_shown_when_no_edit_mode_or_panning(self):
        """Tooltip is shown when no edit mode is active and not panning."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        mesh_edit_handler = Mock()
        mesh_edit_handler.is_dragging.return_value = False
        mesh_edit_handler.is_active.return_value = False

        psi_edit_handler = Mock()
        psi_edit_handler.is_active.return_value = False

        canvas_controller = Mock()
        canvas_controller.is_panning.return_value = False

        on_tooltip_update = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=psi_edit_handler,
            mesh_edit_handler=mesh_edit_handler,
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=on_tooltip_update
        )

        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_mouse_motion(event)

        # Tooltip should be updated
        on_tooltip_update.assert_called_once_with(event)


class TestMouseScrollHandling:
    """Test mouse scroll event handling."""

    def test_scroll_event_delegated_to_canvas_controller(self):
        """Scroll events should be handled by canvas controller (zoom)."""
        from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator

        canvas_controller = Mock()

        coordinator = MouseInteractionCoordinator(
            psi_edit_handler=Mock(),
            mesh_edit_handler=Mock(),
            canvas_controller=canvas_controller,
            on_tooltip_update_callback=Mock()
        )

        event = Mock()
        event.button = 'up'
        event.xdata = 1.5
        event.ydata = 0.5

        coordinator.handle_scroll(event)

        # Scroll should be handled by canvas controller (via on_scroll_zoom)
        canvas_controller.on_scroll_zoom.assert_called_once_with(event)
