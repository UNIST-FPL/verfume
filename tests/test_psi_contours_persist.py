"""
Regression test for PSI contours disappearing bug.

Bug history:
- Originally fixed in commit fccec67 ("Fix PSI contours disappearing when adding contours in edit mode")
- Regressed during Phase 2-3 refactoring when PSI edit handler was extracted
- Root cause: PSI edit handler's preview contour state not being reset after ax.clear()

This test ensures PSI contours remain visible after adding a new contour in PSI edit mode.
"""
import sys
import pytest
import numpy as np
from unittest.mock import Mock
from PyQt5.QtWidgets import QApplication
from mesh_gui_project.ui.main_window import MainWindow


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def window_with_equilibrium(qapp):
    """Create MainWindow with loaded equilibrium data."""
    window = MainWindow()

    # Load a test gEQDSK file
    geqdsk_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    window.load_geqdsk(geqdsk_file)

    return window


def test_psi_contours_visible_after_adding_contour_in_edit_mode(window_with_equilibrium):
    """
    Test that PSI contours remain visible after adding a contour in PSI edit mode.

    Regression test for bug where all PSI contours would disappear when user clicked
    to add a new contour in PSI edit mode.

    Bug scenario (before fix):
    1. Load equilibrium
    2. Enable PSI contour display
    3. Enter PSI edit mode
    4. Left-click to add contour
    5. BUG: All PSI contours disappear

    Expected behavior (after fix):
    - PSI contours should remain visible after adding a contour
    - Both automatic and user-added contours should be displayed
    """
    window = window_with_equilibrium

    # Enable PSI contour display
    window.psi_display_contour_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()

    # Verify contours are visible initially
    assert window._psi_contour_plot is not None, "PSI contours should be visible"
    assert len(window.canvas_controller.ax.collections) > 0, "Should have contour collections"

    # Store initial collection count
    initial_collections = len(window.canvas_controller.ax.collections)

    # Enter PSI edit mode
    window.psi_edit_handler.set_active(True)

    # Get a valid position in the middle of the PSI grid
    R_center = (window.equilibrium.R_grid.min() + window.equilibrium.R_grid.max()) / 2
    Z_center = (window.equilibrium.Z_grid.min() + window.equilibrium.Z_grid.max()) / 2

    # Create a mock mouse event for left-click
    mock_event = Mock()
    mock_event.xdata = R_center
    mock_event.ydata = Z_center
    mock_event.button = 1  # Left button
    mock_event.inaxes = window.canvas_controller.ax

    # Simulate left-click to add a contour
    # This will trigger _on_redraw_callback() which calls _redraw_rz_plot()
    window.psi_edit_handler.handle_mouse_press(mock_event, button=1)

    # Verify contours are STILL visible after adding contour
    assert window._psi_contour_plot is not None, \
        "PSI contours should STILL be visible after adding contour (BUG: they disappeared!)"

    assert len(window.canvas_controller.ax.collections) > 0, \
        "Should STILL have contour collections after adding contour"

    # Verify the PSI contour checkbox is still checked
    assert window.psi_display_contour_checkbox.isChecked(), \
        "PSI contour checkbox should still be checked"

    # Verify a contour was actually added
    added_values = window.psi_edit_handler.get_added_values()
    assert len(added_values) == 1, "Should have added one PSI contour"

def test_psi_preview_contour_state_reset_after_redraw(window_with_equilibrium):
    """
    Test that PSI edit handler's preview contour state is properly reset after redraw.

    This is the root cause fix: when _redraw_rz_plot() calls ax.clear(), it must
    also reset the PSI edit handler's preview contour state to prevent stale references.
    """
    window = window_with_equilibrium

    # Enable PSI contours and enter edit mode
    window.psi_display_contour_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()
    window.psi_edit_handler.set_active(True)

    # Create a preview contour by moving mouse
    R_center = (window.equilibrium.R_grid.min() + window.equilibrium.R_grid.max()) / 2
    Z_center = (window.equilibrium.Z_grid.min() + window.equilibrium.Z_grid.max()) / 2

    mock_event = Mock()
    mock_event.xdata = R_center
    mock_event.ydata = Z_center
    mock_event.inaxes = window.canvas_controller.ax

    # Create preview contour
    window.psi_edit_handler.handle_mouse_motion(mock_event)

    # Verify preview contour exists
    assert window.psi_edit_handler._preview_contour is not None, \
        "Preview contour should exist after mouse motion"

    # Now trigger a redraw (simulates adding a contour)
    window._redraw_rz_plot()

    # CRITICAL: Preview contour state should be reset after ax.clear()
    # This is the fix for the bug
    assert window.psi_edit_handler._preview_contour is None, \
        "Preview contour should be reset to None after redraw (this prevents the bug)"

    assert window.psi_edit_handler._preview_collections_count == 0, \
        "Preview collections count should be reset to 0 after redraw"


def test_psi_contours_persist_across_multiple_additions(window_with_equilibrium):
    """
    Test that PSI contours persist when adding multiple contours in sequence.

    This ensures the fix works reliably for multiple operations, not just the first one.
    """
    window = window_with_equilibrium

    # Enable both contour and filled contours
    window.psi_display_contour_checkbox.setChecked(True)
    window.psi_display_contourf_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()

    # Enter edit mode
    window.psi_edit_handler.set_active(True)

    # Add 3 contours at different positions
    R_range = window.equilibrium.R_grid.max() - window.equilibrium.R_grid.min()
    Z_range = window.equilibrium.Z_grid.max() - window.equilibrium.Z_grid.min()
    R_min = window.equilibrium.R_grid.min()
    Z_min = window.equilibrium.Z_grid.min()

    positions = [
        (R_min + 0.3 * R_range, Z_min + 0.5 * Z_range),
        (R_min + 0.5 * R_range, Z_min + 0.5 * Z_range),
        (R_min + 0.7 * R_range, Z_min + 0.5 * Z_range),
    ]

    for R, Z in positions:
        mock_event = Mock()
        mock_event.xdata = R
        mock_event.ydata = Z
        mock_event.button = 1
        mock_event.inaxes = window.canvas_controller.ax

        # Add contour
        window.psi_edit_handler.handle_mouse_press(mock_event, button=1)

        # Verify contours STILL visible after each addition
        assert window._psi_contour_plot is not None, \
            f"Contours should be visible after adding contour at ({R:.2f}, {Z:.2f})"

        assert window._psi_contourf_plot is not None, \
            f"Filled contours should be visible after adding contour at ({R:.2f}, {Z:.2f})"

    # Verify all 3 contours were added
    added_values = window.psi_edit_handler.get_added_values()
    assert len(added_values) == 3, "Should have added 3 PSI contours"

    # Verify final state: contours still visible
    assert window._psi_contour_plot is not None, "Contours should be visible after all additions"
    assert window._psi_contourf_plot is not None, "Filled contours should be visible after all additions"
    assert len(window.canvas_controller.ax.collections) > 0, "Should have contour collections"
