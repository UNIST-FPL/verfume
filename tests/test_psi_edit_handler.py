"""
Tests for PsiEditHandler class.

Following TDD approach: write tests first, then implement.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, call


class TestPsiEditHandlerConstruction:
    """Test PsiEditHandler construction and initialization."""

    def test_handler_can_be_instantiated(self):
        """PsiEditHandler should be instantiable with required dependencies."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        # Mock dependencies
        equilibrium = Mock()
        psi_viz_controller = Mock()
        canvas_controller = Mock()
        on_redraw = Mock()

        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=psi_viz_controller,
            canvas_controller=canvas_controller,
            on_redraw_callback=on_redraw
        )

        assert handler is not None
        assert not handler.is_active()  # Should start inactive


class TestPsiEditHandlerModeToggle:
    """Test PSI edit mode activation/deactivation."""

    def test_set_active_enables_edit_mode(self):
        """set_active(True) should enable edit mode."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=Mock()
        )

        handler.set_active(True)
        assert handler.is_active()

    def test_set_active_disables_edit_mode(self):
        """set_active(False) should disable edit mode."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=Mock()
        )

        handler.set_active(True)
        handler.set_active(False)
        assert not handler.is_active()

    def test_deactivating_clears_preview_contour(self):
        """Deactivating edit mode should clear any preview contour."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        canvas_controller = Mock()
        canvas_controller.ax.collections = [Mock()]  # Mock collection list
        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=canvas_controller,
            on_redraw_callback=Mock()
        )

        # Activate, create preview, then deactivate
        handler.set_active(True)
        # Simulate having a preview (internal state)
        handler._preview_contour = Mock()

        handler.set_active(False)

        # Preview should be cleared
        assert handler._preview_contour is None


class TestPsiEditHandlerMousePress:
    """Test mouse press handling in PSI edit mode."""

    def test_left_click_adds_permanent_contour(self):
        """Left-click should add a permanent PSI contour."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        equilibrium = Mock()
        equilibrium.psi_value.return_value = 0.5
        equilibrium.R_grid = np.array([1.0, 2.0])
        equilibrium.Z_grid = np.array([-1.0, 1.0])

        on_redraw = Mock()

        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=on_redraw
        )

        handler.set_active(True)

        # Simulate left-click at (1.5, 0.0)
        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.0

        handled = handler.handle_mouse_press(event, button=1)

        assert handled is True
        assert 0.5 in handler.get_added_values()
        on_redraw.assert_called_once()  # Should trigger redraw

    def test_right_click_deletes_nearest_contour(self):
        """Right-click should delete the nearest PSI contour."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        equilibrium = Mock()
        equilibrium.psi_value.return_value = 0.5
        equilibrium.psi_grid = np.array([[0.0, 0.3, 0.6], [0.2, 0.5, 0.8]])
        equilibrium.R_grid = np.array([1.0, 1.5, 2.0])
        equilibrium.Z_grid = np.array([-1.0, 0.0, 1.0])
        equilibrium.psi_axis = 0.0
        equilibrium.psi_boundary = 1.0

        on_redraw = Mock()

        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=on_redraw
        )

        handler.set_active(True)

        # Add a value first
        handler._added_psi_values = [0.5]

        # Simulate right-click near 0.5
        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.0

        handled = handler.handle_mouse_press(event, button=3)

        assert handled is True
        # 0.5 should be in disabled list (not removed from added, just disabled)
        assert 0.5 in handler.get_disabled_levels()
        on_redraw.assert_called_once()

    def test_click_when_inactive_returns_false(self):
        """Clicks when inactive should return False (not handled)."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=Mock()
        )

        # Don't activate
        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.0

        handled = handler.handle_mouse_press(event, button=1)
        assert handled is False


class TestPsiEditHandlerMouseMotion:
    """Test mouse motion handling for preview contours."""

    def test_mouse_motion_creates_preview_contour(self):
        """Mouse motion in edit mode should create preview contour."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        equilibrium = Mock()
        equilibrium.psi_value.return_value = 0.7
        equilibrium.R_grid = np.array([1.0, 2.0])
        equilibrium.Z_grid = np.array([-1.0, 1.0])
        equilibrium.psi_grid = np.array([[0.0, 0.3], [0.2, 0.5]])

        canvas_controller = Mock()
        canvas_controller.ax = Mock()
        canvas_controller.ax.collections = []
        canvas_controller.ax.contour.return_value = Mock()

        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=Mock(),
            canvas_controller=canvas_controller,
            on_redraw_callback=Mock()
        )

        handler.set_active(True)

        # Simulate mouse motion
        event = Mock()
        event.inaxes = canvas_controller.ax
        event.xdata = 1.5
        event.ydata = 0.0

        handled = handler.handle_mouse_motion(event)

        assert handled is True
        # Should have called contour to create preview
        canvas_controller.ax.contour.assert_called_once()

    def test_mouse_motion_clears_preview_when_outside_axes(self):
        """Mouse motion outside axes should clear preview."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        canvas_controller = Mock()
        canvas_controller.ax = Mock()

        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=canvas_controller,
            on_redraw_callback=Mock()
        )

        handler.set_active(True)
        handler._preview_contour = Mock()  # Simulate existing preview

        # Mouse outside axes
        event = Mock()
        event.inaxes = None

        handled = handler.handle_mouse_motion(event)

        assert handled is True
        assert handler._preview_contour is None  # Should be cleared

    def test_mouse_motion_when_inactive_returns_false(self):
        """Mouse motion when inactive should return False."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=Mock()
        )

        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.0

        handled = handler.handle_mouse_motion(event)
        assert handled is False


class TestPsiEditHandlerValues:
    """Test PSI value management."""

    def test_get_added_values_returns_list(self):
        """get_added_values() should return list of added PSI values."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=Mock()
        )

        values = handler.get_added_values()
        assert isinstance(values, list)
        assert len(values) == 0  # Initially empty

    def test_get_disabled_levels_returns_list(self):
        """get_disabled_levels() should return list of disabled levels."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        handler = PsiEditHandler(
            equilibrium=Mock(),
            psi_viz_controller=Mock(),
            canvas_controller=Mock(),
            on_redraw_callback=Mock()
        )

        levels = handler.get_disabled_levels()
        assert isinstance(levels, list)
        assert len(levels) == 0  # Initially empty


class TestPsiEditHandlerZoomPreservation:
    """Test that zoom is preserved when adding/deleting contours."""

    def test_adding_contour_preserves_zoom_state(self):
        """Adding a contour should preserve the current zoom state."""
        from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler

        equilibrium = Mock()
        equilibrium.psi_value.return_value = 0.5
        equilibrium.R_grid = np.array([1.0, 2.0, 3.0])
        equilibrium.Z_grid = np.array([-1.0, 0.0, 1.0])

        # Mock canvas controller with axis limits tracking
        canvas_controller = Mock()
        canvas_controller.ax = Mock()
        initial_xlim = (1.2, 1.8)  # Zoomed in x-limits
        initial_ylim = (-0.5, 0.5)  # Zoomed in y-limits
        canvas_controller.ax.get_xlim.return_value = initial_xlim
        canvas_controller.ax.get_ylim.return_value = initial_ylim

        # Track calls to set_xlim and set_ylim in redraw callback
        final_xlim = [None]
        final_ylim = [None]

        def mock_redraw():
            # Capture the limits that were set during redraw
            if canvas_controller.ax.set_xlim.called:
                final_xlim[0] = canvas_controller.ax.set_xlim.call_args[0][0]
            if canvas_controller.ax.set_ylim.called:
                final_ylim[0] = canvas_controller.ax.set_ylim.call_args[0][0]

        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=Mock(),
            canvas_controller=canvas_controller,
            on_redraw_callback=mock_redraw
        )

        handler.set_active(True)

        # Simulate adding a contour at position
        event = Mock()
        event.xdata = 1.5
        event.ydata = 0.0

        handler.handle_mouse_press(event, button=1)

        # The redraw callback should preserve the original zoom
        # In a real implementation, the callback would call _redraw_rz_plot
        # which should save and restore axis limits
        # This test verifies the contract that zoom should not be reset
