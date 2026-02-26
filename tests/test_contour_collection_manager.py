"""
Tests for ContourCollectionManager utility class.

This utility manages matplotlib contour collections lifecycle,
eliminating duplication across PSI handlers and controllers.
"""
import pytest
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes


class TestContourCollectionManager:
    """Test suite for ContourCollectionManager."""

    @pytest.fixture
    def ax(self):
        """Create a matplotlib axes for testing."""
        fig, ax = plt.subplots()
        yield ax
        plt.close(fig)

    @pytest.fixture
    def manager(self, ax):
        """Create a ContourCollectionManager instance."""
        from mesh_gui_project.utils.contour_collection_manager import ContourCollectionManager
        return ContourCollectionManager(ax)

    def test_manager_initialization(self, ax):
        """Test that manager initializes correctly."""
        from mesh_gui_project.utils.contour_collection_manager import ContourCollectionManager

        manager = ContourCollectionManager(ax)

        assert manager.ax is ax
        assert len(manager._tracked_collections) == 0

    def test_track_contour_single_collection(self, manager, ax):
        """Test tracking a contour that creates a single collection."""
        # Record collections before
        collections_before = len(ax.collections)

        # Create a simple contour (this typically adds 1 collection)
        X, Y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        Z = X + Y
        ax.contour(X, Y, Z, levels=[0.5])

        # Track the contour
        manager.track_contour("test_contour", collections_before)

        # Verify it's tracked
        assert "test_contour" in manager._tracked_collections
        assert manager._tracked_collections["test_contour"] == 1

    def test_track_contour_multiple_levels(self, manager, ax):
        """Test tracking a contour with multiple levels (one collection per level)."""
        # Record collections before
        collections_before = len(ax.collections)

        # Create a contour with multiple levels (matplotlib adds 1 collection per level)
        X, Y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        Z = X + Y
        ax.contour(X, Y, Z, levels=[0.3, 0.5, 0.7])
        actual_count = len(ax.collections) - collections_before

        # Track the contour
        manager.track_contour("multi_contour", collections_before)

        # Verify it's tracked with correct count (actual collections added)
        assert "multi_contour" in manager._tracked_collections
        assert manager._tracked_collections["multi_contour"] == actual_count

    def test_clear_contour_removes_collections(self, manager, ax):
        """Test that clearing a contour removes its collections."""
        # Create and track a contour
        collections_before = len(ax.collections)
        X, Y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        Z = X + Y
        ax.contour(X, Y, Z, levels=[0.5])
        manager.track_contour("test_contour", collections_before)

        # Record count after adding
        collections_after_add = len(ax.collections)

        # Clear the contour
        manager.clear_contour("test_contour")

        # Verify collections were removed
        assert len(ax.collections) == collections_before
        assert "test_contour" not in manager._tracked_collections

    def test_clear_contour_multiple_collections(self, manager, ax):
        """Test clearing a contour with multiple collections."""
        # Create and track a multi-level contour
        collections_before = len(ax.collections)
        X, Y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        Z = X + Y
        ax.contour(X, Y, Z, levels=[0.3, 0.5, 0.7])
        manager.track_contour("multi_contour", collections_before)

        # Clear the contour
        manager.clear_contour("multi_contour")

        # Verify all collections were removed
        assert len(ax.collections) == collections_before
        assert "multi_contour" not in manager._tracked_collections

    def test_clear_nonexistent_contour(self, manager, ax):
        """Test that clearing a non-existent contour is safe (no-op)."""
        initial_count = len(ax.collections)

        # Should not raise an error
        manager.clear_contour("nonexistent")

        # Collections should be unchanged
        assert len(ax.collections) == initial_count

    def test_track_multiple_contours(self, manager, ax):
        """Test tracking multiple different contours."""
        X, Y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        Z = X + Y

        # Track first contour
        before1 = len(ax.collections)
        ax.contour(X, Y, Z, levels=[0.3])
        manager.track_contour("contour1", before1)

        # Track second contour
        before2 = len(ax.collections)
        ax.contour(X, Y, Z, levels=[0.5, 0.7])
        count2 = len(ax.collections) - before2
        manager.track_contour("contour2", before2)

        # Verify both are tracked with actual collection counts
        assert "contour1" in manager._tracked_collections
        assert "contour2" in manager._tracked_collections
        assert manager._tracked_collections["contour1"] == 1
        assert manager._tracked_collections["contour2"] == count2

    def test_clear_specific_contour_preserves_others(self, manager, ax):
        """Test that clearing one contour doesn't affect others."""
        X, Y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        Z = X + Y

        # Create two contours
        before1 = len(ax.collections)
        ax.contour(X, Y, Z, levels=[0.3])
        manager.track_contour("contour1", before1)

        before2 = len(ax.collections)
        ax.contour(X, Y, Z, levels=[0.5])
        manager.track_contour("contour2", before2)

        total_after = len(ax.collections)

        # Clear only the second contour (most recent)
        manager.clear_contour("contour2")

        # Verify contour2 is gone but contour1 remains
        assert "contour2" not in manager._tracked_collections
        assert "contour1" in manager._tracked_collections
        assert len(ax.collections) == total_after - 1

    def test_retrack_contour_overwrites_previous(self, manager, ax):
        """Test that tracking a contour with same name overwrites previous."""
        X, Y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        Z = X + Y

        # Track first contour with 1 level
        before1 = len(ax.collections)
        ax.contour(X, Y, Z, levels=[0.3])
        manager.track_contour("preview", before1)

        assert manager._tracked_collections["preview"] == 1

        # Track another contour with same name
        before2 = len(ax.collections)
        ax.contour(X, Y, Z, levels=[0.5, 0.7])
        count2 = len(ax.collections) - before2
        manager.track_contour("preview", before2)

        # Should overwrite with actual collection count for new contour
        assert manager._tracked_collections["preview"] == count2
