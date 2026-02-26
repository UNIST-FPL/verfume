"""
Regression test for zoom preservation bug.

Bug: When adding PSI contours in edit mode, zoom was reset to show entire figure.
Root cause: Using adjustable='datalim' caused matplotlib to adjust data limits
when maintaining equal aspect ratio during redraw operations.
Fix: Changed to adjustable='box' which adjusts the physical box size instead.

This test verifies that:
1. Canvas is initialized with adjustable='box'
2. After redraw operations, adjustable mode remains 'box'
3. Axis limits are preserved across redraws
"""
import pytest
import numpy as np
from matplotlib.figure import Figure


class TestZoomPreservationRegression:
    """Regression tests for zoom preservation during PSI contour editing."""

    def test_canvas_controller_uses_box_adjustable(self):
        """Canvas controller should use adjustable='box' for aspect ratio."""
        from mesh_gui_project.ui.canvas_controller import CanvasController

        controller = CanvasController()
        canvas = controller.create_canvas()

        # Check that adjustable is 'box' (aspect='equal' is stored as numeric value)
        assert controller.ax.get_adjustable() == 'box'

    def test_clear_axes_preserves_box_adjustable(self):
        """Clearing axes should maintain adjustable='box' mode."""
        from mesh_gui_project.ui.canvas_controller import CanvasController

        controller = CanvasController()
        controller.create_canvas()

        # Clear axes (simulating redraw)
        controller.clear_axes()

        # Verify still using 'box' adjustable
        assert controller.ax.get_adjustable() == 'box'

    def test_redraw_with_zoom_maintains_limits(self):
        """
        Test that redrawing with zoom preserves axis limits.

        This is a regression test for the bug where adding a contour
        would reset zoom to show the entire figure.
        """
        from mesh_gui_project.ui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        import sys

        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        window = MainWindow()

        # Load equilibrium data
        geqdsk_path = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
        window.load_geqdsk(geqdsk_path)

        # Enable PSI contour display
        window.psi_display_contour_checkbox.setChecked(True)

        # Do initial plot
        window._redraw_rz_plot()

        # Simulate user zoom by setting specific limits
        zoomed_xlim = (1.5, 2.0)
        zoomed_ylim = (-0.3, 0.3)
        window.canvas_controller.ax.set_xlim(zoomed_xlim)
        window.canvas_controller.ax.set_ylim(zoomed_ylim)
        window.canvas_controller.draw()

        # Verify zoom is applied
        current_xlim = window.canvas_controller.ax.get_xlim()
        current_ylim = window.canvas_controller.ax.get_ylim()
        assert abs(current_xlim[0] - zoomed_xlim[0]) < 0.01
        assert abs(current_xlim[1] - zoomed_xlim[1]) < 0.01
        assert abs(current_ylim[0] - zoomed_ylim[0]) < 0.01
        assert abs(current_ylim[1] - zoomed_ylim[1]) < 0.01

        # Now trigger a redraw (as would happen when adding a contour)
        window._redraw_rz_plot()

        # Verify zoom is preserved (limits should be very close to original)
        final_xlim = window.canvas_controller.ax.get_xlim()
        final_ylim = window.canvas_controller.ax.get_ylim()

        # Allow small tolerance for floating point comparison
        assert abs(final_xlim[0] - zoomed_xlim[0]) < 0.01, \
            f"X-axis min changed from {zoomed_xlim[0]} to {final_xlim[0]}"
        assert abs(final_xlim[1] - zoomed_xlim[1]) < 0.01, \
            f"X-axis max changed from {zoomed_xlim[1]} to {final_xlim[1]}"
        assert abs(final_ylim[0] - zoomed_ylim[0]) < 0.01, \
            f"Y-axis min changed from {zoomed_ylim[0]} to {final_ylim[0]}"
        assert abs(final_ylim[1] - zoomed_ylim[1]) < 0.01, \
            f"Y-axis max changed from {zoomed_ylim[1]} to {final_ylim[1]}"

        # Verify adjustable mode is 'box'
        assert window.canvas_controller.ax.get_adjustable() == 'box'

        # Verify autoscale is disabled
        assert window.canvas_controller.ax.get_autoscale_on() == False

    def test_psi_edit_handler_redraw_preserves_zoom(self):
        """
        Test that adding a contour through PSI edit handler preserves zoom.

        This is an integration test that simulates the exact user workflow:
        1. Load equilibrium
        2. Enable PSI contours
        3. Zoom in
        4. Enter edit mode
        5. Add a contour
        6. Verify zoom is preserved
        """
        from mesh_gui_project.ui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        from unittest.mock import Mock
        import sys

        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        window = MainWindow()

        # Load equilibrium data
        geqdsk_path = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
        window.load_geqdsk(geqdsk_path)

        # Enable PSI contour display
        window.psi_display_contour_checkbox.setChecked(True)
        window._redraw_rz_plot()

        # Simulate user zoom
        zoomed_xlim = (1.6, 1.9)
        zoomed_ylim = (-0.2, 0.2)
        window.canvas_controller.ax.set_xlim(zoomed_xlim)
        window.canvas_controller.ax.set_ylim(zoomed_ylim)
        window.canvas_controller.draw()

        # Enable edit mode
        window.psi_edit_handler.set_active(True)

        # Simulate adding a contour (this triggers redraw)
        event = Mock()
        event.xdata = 1.75  # Within zoomed region
        event.ydata = 0.0
        window.psi_edit_handler.handle_mouse_press(event, button=1)

        # Verify zoom is still preserved after adding contour
        final_xlim = window.canvas_controller.ax.get_xlim()
        final_ylim = window.canvas_controller.ax.get_ylim()

        assert abs(final_xlim[0] - zoomed_xlim[0]) < 0.01, \
            f"Zoom was reset: X-axis min changed from {zoomed_xlim[0]} to {final_xlim[0]}"
        assert abs(final_xlim[1] - zoomed_xlim[1]) < 0.01, \
            f"Zoom was reset: X-axis max changed from {zoomed_xlim[1]} to {final_xlim[1]}"
        assert abs(final_ylim[0] - zoomed_ylim[0]) < 0.01, \
            f"Zoom was reset: Y-axis min changed from {zoomed_ylim[0]} to {final_ylim[0]}"
        assert abs(final_ylim[1] - zoomed_ylim[1]) < 0.01, \
            f"Zoom was reset: Y-axis max changed from {zoomed_ylim[1]} to {final_ylim[1]}"

    def test_boundary_preserved_when_toggling_psi_checkbox(self):
        """
        Test that axis boundaries are preserved when toggling PSI display checkbox.

        This is a regression test for the bug where turning on "Contour Lines"
        would change the axis boundaries.
        """
        from mesh_gui_project.ui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        import sys

        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        window = MainWindow()

        # Load equilibrium data (PSI checkbox is OFF initially)
        geqdsk_path = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
        window.load_geqdsk(geqdsk_path)

        # Get boundaries with PSI display OFF (just boundary and limiter shown)
        initial_xlim = window.canvas_controller.ax.get_xlim()
        initial_ylim = window.canvas_controller.ax.get_ylim()

        # Turn on PSI contour display
        window.psi_display_contour_checkbox.setChecked(True)

        # Get boundaries after turning on PSI display
        after_toggle_xlim = window.canvas_controller.ax.get_xlim()
        after_toggle_ylim = window.canvas_controller.ax.get_ylim()

        # Verify boundaries are preserved (within small tolerance)
        assert abs(after_toggle_xlim[0] - initial_xlim[0]) < 0.01, \
            f"Boundary changed: X-min changed from {initial_xlim[0]} to {after_toggle_xlim[0]}"
        assert abs(after_toggle_xlim[1] - initial_xlim[1]) < 0.01, \
            f"Boundary changed: X-max changed from {initial_xlim[1]} to {after_toggle_xlim[1]}"
        assert abs(after_toggle_ylim[0] - initial_ylim[0]) < 0.01, \
            f"Boundary changed: Y-min changed from {initial_ylim[0]} to {after_toggle_ylim[0]}"
        assert abs(after_toggle_ylim[1] - initial_ylim[1]) < 0.01, \
            f"Boundary changed: Y-max changed from {initial_ylim[1]} to {after_toggle_ylim[1]}"
