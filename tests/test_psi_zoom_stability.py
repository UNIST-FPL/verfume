"""
Test PSI contour editing zoom stability.

Regression test to ensure zoom is preserved during PSI contour editing operations.
"""
import sys
import pytest
import numpy as np
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
def window_zoomed(qapp):
    """Create MainWindow with loaded equilibrium and zoomed view."""
    window = MainWindow()

    # Load equilibrium
    geqdsk_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    window.load_geqdsk(geqdsk_file)

    # Zoom in to a small region
    ax = window.canvas_controller.ax
    ax.set_xlim(1.6, 2.0)
    ax.set_ylim(-0.2, 0.2)
    window.canvas_controller.draw()

    # Enable PSI contour display
    window.psi_display_contour_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()

    # Enter PSI edit mode
    window.psi_edit_mode_button.setChecked(True)
    window._on_psi_edit_mode_toggled(True)

    return window


def test_zoom_stable_when_adding_first_contour(window_zoomed):
    """Test that zoom remains stable when adding first PSI contour while zoomed in."""
    window = window_zoomed
    ax = window.canvas_controller.ax

    # Get zoom limits before adding contour
    xlim_before = ax.get_xlim()
    ylim_before = ax.get_ylim()

    # Verify we're zoomed in (range should be small, < 1m)
    xlim_range = xlim_before[1] - xlim_before[0]
    ylim_range = ylim_before[1] - ylim_before[0]
    assert xlim_range < 1.0, f"X range should be < 1m (zoomed in), got {xlim_range}"
    assert ylim_range < 1.0, f"Y range should be < 1m (zoomed in), got {ylim_range}"

    # Add a PSI contour by clicking at (1.8, 0.0)
    window.psi_edit_handler._add_permanent_contour(1.8, 0.0)

    # Get zoom limits after adding contour
    xlim_after = ax.get_xlim()
    ylim_after = ax.get_ylim()

    # Verify zoom hasn't changed
    assert xlim_before == xlim_after, f"X limits changed from {xlim_before} to {xlim_after}"
    assert ylim_before == ylim_after, f"Y limits changed from {ylim_before} to {ylim_after}"


def test_zoom_stable_when_moving_mouse_after_adding_contour(window_zoomed):
    """Test that zoom remains stable when moving mouse after adding a contour."""
    window = window_zoomed
    ax = window.canvas_controller.ax

    # Add a contour first
    window.psi_edit_handler._add_permanent_contour(1.8, 0.0)

    # Get zoom limits before mouse movement
    xlim_before = ax.get_xlim()
    ylim_before = ax.get_ylim()

    # Move mouse to update preview contour
    window.psi_edit_handler._update_preview_contour(1.85, 0.05)

    # Get zoom limits after mouse movement
    xlim_after = ax.get_xlim()
    ylim_after = ax.get_ylim()

    # Verify zoom hasn't changed
    assert xlim_before == xlim_after, f"X limits changed from {xlim_before} to {xlim_after}"
    assert ylim_before == ylim_after, f"Y limits changed from {ylim_before} to {ylim_after}"


def test_zoom_stable_when_adding_second_contour(window_zoomed):
    """Test that zoom remains stable when adding second PSI contour."""
    window = window_zoomed
    ax = window.canvas_controller.ax

    # Add first contour
    window.psi_edit_handler._add_permanent_contour(1.8, 0.0)

    # Move mouse
    window.psi_edit_handler._update_preview_contour(1.85, 0.05)

    # Get zoom limits before adding second contour
    xlim_before = ax.get_xlim()
    ylim_before = ax.get_ylim()

    # Add second contour
    window.psi_edit_handler._add_permanent_contour(1.7, -0.05)

    # Get zoom limits after adding second contour
    xlim_after = ax.get_xlim()
    ylim_after = ax.get_ylim()

    # Verify zoom hasn't changed
    assert xlim_before == xlim_after, f"X limits changed from {xlim_before} to {xlim_after}"
    assert ylim_before == ylim_after, f"Y limits changed from {ylim_before} to {ylim_after}"


def test_zoom_stable_through_complete_editing_sequence(window_zoomed):
    """Test zoom stability through complete editing sequence: add, move, add, move, add."""
    window = window_zoomed
    ax = window.canvas_controller.ax

    # Record initial zoom
    xlim_initial = ax.get_xlim()
    ylim_initial = ax.get_ylim()

    # Sequence of operations
    operations = [
        ("add_contour", 1.8, 0.0),
        ("move_mouse", 1.85, 0.05),
        ("add_contour", 1.7, -0.05),
        ("move_mouse", 1.9, 0.1),
        ("add_contour", 1.75, 0.08),
    ]

    for i, op in enumerate(operations):
        if op[0] == "add_contour":
            window.psi_edit_handler._add_permanent_contour(op[1], op[2])
        elif op[0] == "move_mouse":
            window.psi_edit_handler._update_preview_contour(op[1], op[2])

        # Check zoom after each operation
        xlim_current = ax.get_xlim()
        ylim_current = ax.get_ylim()

        assert xlim_initial == xlim_current, \
            f"After operation {i} ({op[0]}): X limits changed from {xlim_initial} to {xlim_current}"
        assert ylim_initial == ylim_current, \
            f"After operation {i} ({op[0]}): Y limits changed from {ylim_initial} to {ylim_current}"


def test_zoom_stable_with_very_small_zoom(window_zoomed):
    """Test zoom stability with very small zoom range (< 0.1m)."""
    window = window_zoomed
    ax = window.canvas_controller.ax

    # Zoom in to very small region (< 0.1m range)
    ax.set_xlim(1.75, 1.85)  # 0.1m range
    ax.set_ylim(-0.05, 0.05)  # 0.1m range
    window.canvas_controller.draw()

    xlim_before = ax.get_xlim()
    ylim_before = ax.get_ylim()

    # Add contour
    window.psi_edit_handler._add_permanent_contour(1.8, 0.0)

    xlim_after = ax.get_xlim()
    ylim_after = ax.get_ylim()

    # Verify even very small zoom is preserved
    assert xlim_before == xlim_after, f"X limits changed from {xlim_before} to {xlim_after}"
    assert ylim_before == ylim_after, f"Y limits changed from {ylim_before} to {ylim_after}"
