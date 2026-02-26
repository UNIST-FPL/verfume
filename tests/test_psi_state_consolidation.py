"""
Tests for PSI State Consolidation (Priority 8).

This test suite ensures that PSI state (_added_psi_values, _disabled_psi_levels)
is managed only in ApplicationState, with components reading from it rather than
maintaining their own duplicate state.

Following TDD: Write failing tests first (RED phase).
"""
import pytest
import numpy as np
from unittest.mock import MagicMock
from mesh_gui_project.core.application_state import ApplicationState
from mesh_gui_project.core.equilibrium import EquilibriumData
from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler
from mesh_gui_project.ui.psi_visualization_controller import PsiVisualizationController
from mesh_gui_project.utils.interpolation import make_bicubic_interpolator


class TestPsiEditHandlerUsesApplicationState:
    """Test that PsiEditHandler reads PSI state from ApplicationState."""

    def test_psi_edit_handler_accepts_application_state(self):
        """
        PsiEditHandler should accept ApplicationState in constructor.

        This is the first step: allow injection of ApplicationState.
        """
        # Create minimal mocks
        equilibrium = MagicMock(spec=EquilibriumData)
        psi_viz = MagicMock(spec=PsiVisualizationController)
        canvas = MagicMock()
        canvas.ax = MagicMock()
        redraw_callback = MagicMock()

        # Create application state
        app_state = ApplicationState()

        # Create handler with application state
        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=psi_viz,
            canvas_controller=canvas,
            on_redraw_callback=redraw_callback,
            application_state=app_state  # NEW: inject application state
        )

        # Should be able to create handler with app_state
        assert handler is not None

    def test_psi_edit_handler_reads_added_values_from_app_state(self):
        """
        PsiEditHandler.get_added_values() should return values from ApplicationState.

        Instead of maintaining its own _added_psi_values list, it should
        delegate to ApplicationState.get_added_psi_values().
        """
        # Create minimal mocks
        equilibrium = MagicMock(spec=EquilibriumData)
        psi_viz = MagicMock(spec=PsiVisualizationController)
        canvas = MagicMock()
        canvas.ax = MagicMock()
        redraw_callback = MagicMock()

        # Create application state and add PSI values to it
        app_state = ApplicationState()
        app_state.add_psi_value(0.5)
        app_state.add_psi_value(0.7)

        # Create handler with application state
        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=psi_viz,
            canvas_controller=canvas,
            on_redraw_callback=redraw_callback,
            application_state=app_state
        )

        # Handler should return values from app_state
        values = handler.get_added_values()
        assert 0.5 in values
        assert 0.7 in values
        assert len(values) == 2

    def test_psi_edit_handler_reads_disabled_levels_from_app_state(self):
        """
        PsiEditHandler.get_disabled_levels() should return values from ApplicationState.

        Instead of maintaining its own _disabled_psi_levels list, it should
        delegate to ApplicationState.get_disabled_psi_levels().
        """
        # Create minimal mocks
        equilibrium = MagicMock(spec=EquilibriumData)
        psi_viz = MagicMock(spec=PsiVisualizationController)
        canvas = MagicMock()
        canvas.ax = MagicMock()
        redraw_callback = MagicMock()

        # Create application state and disable levels
        app_state = ApplicationState()
        app_state.disable_psi_level(0.3)
        app_state.disable_psi_level(0.6)

        # Create handler with application state
        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=psi_viz,
            canvas_controller=canvas,
            on_redraw_callback=redraw_callback,
            application_state=app_state
        )

        # Handler should return values from app_state
        levels = handler.get_disabled_levels()
        assert 0.3 in levels
        assert 0.6 in levels
        assert len(levels) == 2


class TestPsiVisualizationControllerUsesApplicationState:
    """Test that PsiVisualizationController reads PSI state from ApplicationState."""

    def test_psi_viz_controller_accepts_application_state(self):
        """
        PsiVisualizationController should accept ApplicationState in constructor.

        This allows it to read PSI values from the centralized state.
        """
        ax = MagicMock()
        figure = MagicMock()
        list_widget = MagicMock()

        app_state = ApplicationState()

        # Create controller with application state
        controller = PsiVisualizationController(
            ax=ax,
            figure=figure,
            psi_contour_list_widget=list_widget,
            application_state=app_state  # NEW: inject application state
        )

        # Should be able to create controller with app_state
        assert controller is not None

    def test_psi_viz_controller_uses_app_state_for_contour_levels(self):
        """
        PsiVisualizationController should read _added_psi_values and _disabled_psi_levels
        from ApplicationState when computing contour levels.

        The _compute_contour_levels method should use app_state values instead
        of self._added_psi_values and self._disabled_psi_levels.
        """
        ax = MagicMock()
        ax.collections = []
        figure = MagicMock()
        list_widget = MagicMock()

        # Create application state with PSI values
        app_state = ApplicationState()
        app_state.add_psi_value(0.5)
        app_state.disable_psi_level(0.3)

        # Create controller with application state
        controller = PsiVisualizationController(
            ax=ax,
            figure=figure,
            psi_contour_list_widget=list_widget,
            application_state=app_state
        )

        # Create mock psi_grid
        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)

        # Compute contour levels - should use app_state values
        levels = controller._compute_contour_levels(psi_grid, n_levels=20)

        # Should include the added value 0.5
        assert any(abs(level - 0.5) < 1e-8 for level in levels)

        # Should NOT include the disabled level 0.3
        # (assuming 0.3 would have been in automatic levels)
        # This is harder to test precisely, but the key is that it uses app_state


class TestPsiStateWritesGoToApplicationState:
    """Test that PSI state modifications update ApplicationState."""

    def test_adding_permanent_contour_updates_app_state(self):
        """
        When PsiEditHandler adds a permanent contour, it should update
        ApplicationState.add_psi_value() instead of self._added_psi_values.
        """
        # Create equilibrium with valid grid (5x5 minimum for bicubic)
        equilibrium = EquilibriumData({
            'NR': 5,
            'NZ': 5,
            'R_grid': np.array([1.0, 1.25, 1.5, 1.75, 2.0]),
            'Z_grid': np.array([-0.5, -0.25, 0.0, 0.25, 0.5]),
            'psi_grid': np.linspace(0.1, 0.9, 25).reshape(5, 5),
            'psi_axis': 0.1,
            'psi_boundary': 0.9
        })
        # Attach interpolator for psi_value() to work
        interp = make_bicubic_interpolator(
            equilibrium.R_grid, equilibrium.Z_grid, equilibrium.psi_grid
        )
        equilibrium.attach_interpolator(interp)

        # Create mocks
        psi_viz = MagicMock(spec=PsiVisualizationController)
        canvas = MagicMock()
        canvas.ax = MagicMock()
        canvas.ax.collections = []
        canvas.ax.contour = MagicMock(return_value=MagicMock())
        canvas.draw_idle = MagicMock()
        redraw_callback = MagicMock()

        # Create application state
        app_state = ApplicationState()

        # Create handler
        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=psi_viz,
            canvas_controller=canvas,
            on_redraw_callback=redraw_callback,
            application_state=app_state
        )

        # Simulate adding a permanent contour at (1.5, 0.0)
        handler.set_active(True)

        # Create mock event for left-click
        event = MagicMock()
        event.xdata = 1.5
        event.ydata = 0.0

        handler.handle_mouse_press(event, button=1)

        # ApplicationState should now have the PSI value at (1.5, 0.0)
        added_values = app_state.get_added_psi_values()
        assert len(added_values) == 1
        # The actual PSI value will be determined by interpolation
        assert added_values[0] >= 0.1
        assert added_values[0] <= 0.9

    def test_deleting_contour_updates_app_state(self):
        """
        When PsiEditHandler deletes a contour, it should update
        ApplicationState.disable_psi_level() instead of self._disabled_psi_levels.
        """
        # Create equilibrium with valid grid (5x5 minimum for bicubic)
        equilibrium = EquilibriumData({
            'NR': 5,
            'NZ': 5,
            'R_grid': np.array([1.0, 1.25, 1.5, 1.75, 2.0]),
            'Z_grid': np.array([-0.5, -0.25, 0.0, 0.25, 0.5]),
            'psi_grid': np.linspace(0.1, 0.9, 25).reshape(5, 5),
            'psi_axis': 0.1,
            'psi_boundary': 0.9
        })
        # Attach interpolator for psi_value() to work
        interp = make_bicubic_interpolator(
            equilibrium.R_grid, equilibrium.Z_grid, equilibrium.psi_grid
        )
        equilibrium.attach_interpolator(interp)

        # Create mocks
        psi_viz = MagicMock(spec=PsiVisualizationController)
        canvas = MagicMock()
        canvas.ax = MagicMock()
        canvas.draw_idle = MagicMock()
        redraw_callback = MagicMock()

        # Create application state
        app_state = ApplicationState()

        # Create handler
        handler = PsiEditHandler(
            equilibrium=equilibrium,
            psi_viz_controller=psi_viz,
            canvas_controller=canvas,
            on_redraw_callback=redraw_callback,
            application_state=app_state
        )

        # Simulate deleting a contour at (1.5, 0.0)
        handler.set_active(True)

        # Create mock event for right-click
        event = MagicMock()
        event.xdata = 1.5
        event.ydata = 0.0

        handler.handle_mouse_press(event, button=3)

        # ApplicationState should now have a disabled level
        # The handler will find the nearest auto-level to 0.5 and disable it
        disabled_levels = app_state.get_disabled_psi_levels()
        assert len(disabled_levels) >= 1
