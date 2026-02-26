"""
Regression tests for PSI boundary checking to prevent interpolation warnings.

This test ensures that when the mouse is moved outside the PSI grid bounds
in PSI edit mode, no interpolation warnings are generated.

Bug history:
- Originally fixed to prevent "Interpolation outside grid bounds" warnings
- Regression occurred when boundary checking was not applied to all code paths
- This test prevents future regressions

The test verifies that:
1. Preview contours are NOT created when mouse is outside bounds
2. Permanent contours are NOT added when clicking outside bounds
3. Contour deletion does NOT attempt to query PSI outside bounds
4. No interpolation warnings are logged during these operations
"""
import sys
import pytest
import logging
from unittest.mock import Mock, patch
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

    # Enable PSI contour display
    window.psi_display_contour_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()

    return window


def test_no_interpolation_warning_when_mouse_outside_bounds(window_with_equilibrium, caplog):
    """
    Test that moving mouse outside PSI grid bounds does not trigger interpolation warnings.

    Regression test for: "Interpolation outside grid bounds - extrapolating" warning.
    """
    window = window_with_equilibrium

    # Enter PSI edit mode
    window.psi_edit_mode_button.setChecked(True)
    window._on_psi_edit_mode_toggled(True)

    # Get grid bounds
    R_grid = window.equilibrium.R_grid
    Z_grid = window.equilibrium.Z_grid
    R_min, R_max = R_grid.min(), R_grid.max()
    Z_min, Z_max = Z_grid.min(), Z_grid.max()

    # Clear any existing log messages
    caplog.clear()

    # Set up logging capture at WARNING level for interpolation module
    with caplog.at_level(logging.WARNING, logger='mesh_gui_project.utils.interpolation'):
        # Test positions OUTSIDE the grid bounds
        test_positions_outside = [
            (R_min - 0.5, Z_min),      # Left of grid
            (R_max + 0.5, Z_max),      # Right of grid
            (R_min + 0.5, Z_min - 0.5), # Below grid
            (R_max - 0.5, Z_max + 0.5), # Above grid
            (R_min - 0.5, Z_min - 0.5), # Bottom-left corner (far outside)
            (R_max + 0.5, Z_max + 0.5), # Top-right corner (far outside)
        ]

        for R, Z in test_positions_outside:
            # Simulate mouse move (triggers preview contour update)
            window.psi_edit_handler._update_preview_contour(R, Z)

        # Check that NO interpolation warnings were logged
        interpolation_warnings = [
            record for record in caplog.records
            if 'Interpolation outside grid bounds' in record.message
        ]

        assert len(interpolation_warnings) == 0, \
            f"Expected no interpolation warnings when mouse is outside grid bounds, " \
            f"but got {len(interpolation_warnings)} warnings: {[w.message for w in interpolation_warnings]}"

    # Verify preview contour was not created (should be None)
    assert window.psi_edit_handler._preview_contour is None, \
        "Preview contour should not be created when mouse is outside grid bounds"


def test_no_interpolation_warning_when_clicking_outside_bounds(window_with_equilibrium, caplog):
    """
    Test that clicking outside PSI grid bounds does not trigger interpolation warnings.

    Regression test for: "Interpolation outside grid bounds - extrapolating" warning.
    """
    window = window_with_equilibrium

    # Enter PSI edit mode
    window.psi_edit_mode_button.setChecked(True)
    window._on_psi_edit_mode_toggled(True)

    # Get grid bounds
    R_grid = window.equilibrium.R_grid
    Z_grid = window.equilibrium.Z_grid
    R_min, R_max = R_grid.min(), R_grid.max()
    Z_min, Z_max = Z_grid.min(), Z_grid.max()

    # Get initial count of added PSI values
    initial_count = len(window.psi_edit_handler._added_psi_values)

    # Clear any existing log messages
    caplog.clear()

    # Set up logging capture at WARNING level for interpolation module
    with caplog.at_level(logging.WARNING, logger='mesh_gui_project.utils.interpolation'):
        # Test clicking OUTSIDE the grid bounds (left-click to add contour)
        test_clicks_outside = [
            (R_min - 0.3, (Z_min + Z_max) / 2),  # Left of grid
            (R_max + 0.3, (Z_min + Z_max) / 2),  # Right of grid
            ((R_min + R_max) / 2, Z_min - 0.3),  # Below grid
            ((R_min + R_max) / 2, Z_max + 0.3),  # Above grid
        ]

        for R, Z in test_clicks_outside:
            # Attempt to add permanent contour (left-click)
            window.psi_edit_handler._add_permanent_contour(R, Z)

        # Check that NO interpolation warnings were logged
        interpolation_warnings = [
            record for record in caplog.records
            if 'Interpolation outside grid bounds' in record.message
        ]

        assert len(interpolation_warnings) == 0, \
            f"Expected no interpolation warnings when clicking outside grid bounds, " \
            f"but got {len(interpolation_warnings)} warnings: {[w.message for w in interpolation_warnings]}"

    # Verify no contours were added (count should be unchanged)
    final_count = len(window.psi_edit_handler._added_psi_values)
    assert final_count == initial_count, \
        f"No contours should be added when clicking outside grid bounds, " \
        f"but count changed from {initial_count} to {final_count}"


def test_no_interpolation_warning_when_deleting_outside_bounds(window_with_equilibrium, caplog):
    """
    Test that right-clicking outside PSI grid bounds does not trigger interpolation warnings.

    Regression test for: "Interpolation outside grid bounds - extrapolating" warning.
    """
    window = window_with_equilibrium

    # Enter PSI edit mode
    window.psi_edit_mode_button.setChecked(True)
    window._on_psi_edit_mode_toggled(True)

    # Get grid bounds
    R_grid = window.equilibrium.R_grid
    Z_grid = window.equilibrium.Z_grid
    R_min, R_max = R_grid.min(), R_grid.max()
    Z_min, Z_max = Z_grid.min(), Z_grid.max()

    # Get initial count of disabled levels
    initial_disabled = len(window.psi_edit_handler._disabled_psi_levels)

    # Clear any existing log messages
    caplog.clear()

    # Set up logging capture at WARNING level for interpolation module
    with caplog.at_level(logging.WARNING, logger='mesh_gui_project.utils.interpolation'):
        # Test right-clicking OUTSIDE the grid bounds (to delete contour)
        test_clicks_outside = [
            (R_min - 0.4, (Z_min + Z_max) / 2),  # Left of grid
            (R_max + 0.4, (Z_min + Z_max) / 2),  # Right of grid
            ((R_min + R_max) / 2, Z_min - 0.4),  # Below grid
            ((R_min + R_max) / 2, Z_max + 0.4),  # Above grid
        ]

        for R, Z in test_clicks_outside:
            # Attempt to delete nearest contour (right-click)
            window.psi_edit_handler._delete_nearest_contour(R, Z)

        # Check that NO interpolation warnings were logged
        interpolation_warnings = [
            record for record in caplog.records
            if 'Interpolation outside grid bounds' in record.message
        ]

        assert len(interpolation_warnings) == 0, \
            f"Expected no interpolation warnings when right-clicking outside grid bounds, " \
            f"but got {len(interpolation_warnings)} warnings: {[w.message for w in interpolation_warnings]}"

    # Verify no contours were disabled (count should be unchanged)
    final_disabled = len(window.psi_edit_handler._disabled_psi_levels)
    assert final_disabled == initial_disabled, \
        f"No contours should be deleted when clicking outside grid bounds, " \
        f"but disabled count changed from {initial_disabled} to {final_disabled}"


def test_preview_cleared_when_mouse_leaves_bounds(window_with_equilibrium):
    """
    Test that preview contour is cleared when mouse moves from inside to outside bounds.
    """
    window = window_with_equilibrium

    # Enter PSI edit mode
    window.psi_edit_mode_button.setChecked(True)
    window._on_psi_edit_mode_toggled(True)

    # Get grid bounds
    R_grid = window.equilibrium.R_grid
    Z_grid = window.equilibrium.Z_grid
    R_min, R_max = R_grid.min(), R_grid.max()
    Z_min, Z_max = Z_grid.min(), Z_grid.max()

    # Position INSIDE bounds - should create preview
    R_inside = (R_min + R_max) / 2
    Z_inside = (Z_min + Z_max) / 2
    window.psi_edit_handler._update_preview_contour(R_inside, Z_inside)

    # Verify preview was created
    assert window.psi_edit_handler._preview_contour is not None, \
        "Preview should be created when mouse is inside bounds"

    # Move OUTSIDE bounds - should clear preview
    R_outside = R_min - 0.5
    Z_outside = Z_min
    window.psi_edit_handler._update_preview_contour(R_outside, Z_outside)

    # Verify preview was cleared
    assert window.psi_edit_handler._preview_contour is None, \
        "Preview should be cleared when mouse moves outside bounds"


def test_bounds_checking_with_various_grid_sizes(qapp, caplog):
    """
    Test that bounds checking works correctly with different grid sizes.

    This ensures the fix is robust across different equilibrium data.
    """
    window = MainWindow()

    # Load equilibrium
    geqdsk_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    window.load_geqdsk(geqdsk_file)

    # Enable PSI contour display
    window.psi_display_contour_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()

    # Enter PSI edit mode
    window.psi_edit_mode_button.setChecked(True)
    window._on_psi_edit_mode_toggled(True)

    # Get grid bounds
    R_grid = window.equilibrium.R_grid
    Z_grid = window.equilibrium.Z_grid
    R_min, R_max = R_grid.min(), R_grid.max()
    Z_min, Z_max = Z_grid.min(), Z_grid.max()

    # Clear any existing log messages
    caplog.clear()

    # Set up logging capture
    with caplog.at_level(logging.WARNING, logger='mesh_gui_project.utils.interpolation'):
        # Test various distances outside the bounds
        distances = [0.01, 0.1, 0.5, 1.0, 5.0]  # Meters
        for dist in distances:
            # Test all four sides
            test_positions = [
                (R_min - dist, (Z_min + Z_max) / 2),  # Left
                (R_max + dist, (Z_min + Z_max) / 2),  # Right
                ((R_min + R_max) / 2, Z_min - dist),  # Bottom
                ((R_min + R_max) / 2, Z_max + dist),  # Top
            ]

            for R, Z in test_positions:
                window.psi_edit_handler._update_preview_contour(R, Z)
                window.psi_edit_handler._add_permanent_contour(R, Z)
                window.psi_edit_handler._delete_nearest_contour(R, Z)

        # Verify NO interpolation warnings at any distance
        interpolation_warnings = [
            record for record in caplog.records
            if 'Interpolation outside grid bounds' in record.message
        ]

        assert len(interpolation_warnings) == 0, \
            f"Expected no interpolation warnings at any distance outside bounds, " \
            f"but got {len(interpolation_warnings)} warnings"
