"""
Tests for PsiLevelComputer utility class.

This utility computes PSI contour levels with filtering,
eliminating duplication across PSI handlers and controllers.
"""
import pytest
import numpy as np


class TestPsiLevelComputer:
    """Test suite for PsiLevelComputer."""

    def test_compute_levels_with_only_auto_levels(self):
        """Test computing levels with no user additions or disabled levels."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        # Create a simple PSI grid
        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        added_values = []
        disabled_levels = []
        n_levels = 5

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should return 5 evenly spaced levels from min to max
        assert len(levels) == 5
        assert levels[0] == pytest.approx(0.0, abs=1e-10)
        assert levels[-1] == pytest.approx(1.0, abs=1e-10)
        # Check they're evenly spaced
        assert np.allclose(np.diff(levels), 0.25)

    def test_compute_levels_with_added_values(self):
        """Test computing levels with user-added values."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        added_values = [0.3, 0.7]
        disabled_levels = []
        n_levels = 3  # Auto levels at 0.0, 0.5, 1.0

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should combine auto and added levels, sorted and unique
        # Auto: 0.0, 0.5, 1.0
        # Added: 0.3, 0.7
        # Combined: 0.0, 0.3, 0.5, 0.7, 1.0
        assert len(levels) == 5
        expected = np.array([0.0, 0.3, 0.5, 0.7, 1.0])
        assert np.allclose(levels, expected)

    def test_compute_levels_with_disabled_levels(self):
        """Test computing levels with disabled levels filtered out."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        added_values = []
        disabled_levels = [0.5]  # Disable middle level
        n_levels = 5  # Auto levels: 0.0, 0.25, 0.5, 0.75, 1.0

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should exclude 0.5
        assert len(levels) == 4
        assert 0.5 not in levels
        # Should include the others
        expected = np.array([0.0, 0.25, 0.75, 1.0])
        assert np.allclose(levels, expected)

    def test_compute_levels_with_added_and_disabled(self):
        """Test computing levels with both added and disabled values."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        added_values = [0.3, 0.7]
        disabled_levels = [0.5, 0.7]  # Disable auto 0.5 and added 0.7
        n_levels = 3  # Auto levels: 0.0, 0.5, 1.0

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Combined before filtering: 0.0, 0.3, 0.5, 0.7, 1.0
        # After filtering out 0.5 and 0.7: 0.0, 0.3, 1.0
        assert len(levels) == 3
        expected = np.array([0.0, 0.3, 1.0])
        assert np.allclose(levels, expected)

    def test_compute_levels_removes_duplicates(self):
        """Test that duplicate values are removed."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        # Add value that matches an auto level
        added_values = [0.5]  # This will match auto level
        disabled_levels = []
        n_levels = 3  # Auto levels: 0.0, 0.5, 1.0

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should have unique values only
        assert len(levels) == 3
        assert len(np.unique(levels)) == 3

    def test_compute_levels_all_disabled_returns_empty(self):
        """Test that disabling all levels returns empty array."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        added_values = []
        # Disable all auto levels
        disabled_levels = [0.0, 0.5, 1.0]
        n_levels = 3

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should return empty array
        assert len(levels) == 0

    def test_compute_levels_with_numpy_array_inputs(self):
        """Test that numpy arrays work as inputs for added/disabled."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        added_values = np.array([0.3, 0.7])
        disabled_levels = np.array([0.5])
        n_levels = 3

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should work with numpy arrays
        # Auto: 0.0, 0.5, 1.0
        # Added: 0.3, 0.7
        # Combined: 0.0, 0.3, 0.5, 0.7, 1.0
        # Disabled: 0.5
        # Result: 0.0, 0.3, 0.7, 1.0
        assert len(levels) == 4
        expected = np.array([0.0, 0.3, 0.7, 1.0])
        assert np.allclose(levels, expected)

    def test_compute_levels_returns_sorted_array(self):
        """Test that returned levels are sorted."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        # Add values in random order
        added_values = [0.9, 0.1, 0.6, 0.2]
        disabled_levels = []
        n_levels = 2

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should be sorted
        assert np.array_equal(levels, np.sort(levels))

    def test_compute_levels_with_negative_psi_values(self):
        """Test computing levels with negative PSI values."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        # PSI grid with negative values
        psi_grid = np.linspace(-1.0, 1.0, 100).reshape(10, 10)
        added_values = [-0.5, 0.5]
        disabled_levels = []
        n_levels = 3  # Auto levels: -1.0, 0.0, 1.0

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Combined and sorted: -1.0, -0.5, 0.0, 0.5, 1.0
        assert len(levels) == 5
        expected = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
        assert np.allclose(levels, expected)

    def test_compute_levels_with_empty_added_values(self):
        """Test that empty list for added_values works correctly."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.0, 1.0, 100).reshape(10, 10)
        added_values = []
        disabled_levels = []
        n_levels = 4

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Should only have auto levels
        assert len(levels) == 4

    def test_compute_levels_preserves_precision(self):
        """Test that floating point precision is preserved."""
        from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer

        psi_grid = np.linspace(0.123456, 0.987654, 100).reshape(10, 10)
        added_values = []
        disabled_levels = []
        n_levels = 2

        levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Check precision is maintained
        assert levels[0] == pytest.approx(0.123456, abs=1e-10)
        assert levels[1] == pytest.approx(0.987654, abs=1e-10)
