"""
Tests for MeshEditHandler class.

Following TDD approach: write tests first, then implement.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, call, patch


class TestMeshEditHandlerConstruction:
    """Test MeshEditHandler construction and initialization."""

    def test_handler_can_be_instantiated(self):
        """MeshEditHandler should be instantiable with required dependencies."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        canvas_controller = Mock()
        on_mesh_update = Mock()

        handler = MeshEditHandler(
            canvas_controller=canvas_controller,
            on_mesh_update_callback=on_mesh_update
        )

        assert handler is not None
        assert not handler.is_active()  # Should start inactive


class TestMeshEditHandlerModeToggle:
    """Test mesh edit mode activation/deactivation."""

    def test_set_active_with_mesh_enables_edit_mode(self):
        """set_active(True) with mesh data should enable edit mode."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        success = handler.set_active(True, vertices, elements)

        assert success is True
        assert handler.is_active()

    def test_set_active_without_mesh_fails(self):
        """set_active(True) without mesh data should fail."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        success = handler.set_active(True, None, None)

        assert success is False
        assert not handler.is_active()

    def test_set_active_disables_edit_mode(self):
        """set_active(False) should disable edit mode."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        handler.set_active(False)

        assert not handler.is_active()

    def test_deactivating_clears_highlight(self):
        """Deactivating edit mode should clear vertex highlight."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        canvas_controller = Mock()
        canvas_controller.ax.plot.return_value = [Mock()]

        handler = MeshEditHandler(
            canvas_controller=canvas_controller,
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        # Simulate having a highlight
        mock_highlight = Mock()
        handler._vertex_highlight = mock_highlight

        handler.set_active(False)

        # Highlight should be cleared
        mock_highlight.remove.assert_called_once()
        assert handler._vertex_highlight is None


class TestMeshEditHandlerBoundaryConstraints:
    """Test setting boundary constraints on vertices."""

    def test_set_boundary_constraints_applies_to_vertices(self):
        """set_boundary_constraints should apply contour constraints."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        boundary = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
        boundary_indices = [0, 1]

        handler.set_boundary_constraints(boundary_indices, boundary)

        # Should have created mesh editor with constraints
        assert handler._mesh_editor is not None


class TestMeshEditHandlerMousePress:
    """Test mouse press handling in mesh edit mode."""

    def test_left_click_selects_nearby_vertex(self):
        """Left-click near a vertex should select it."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        canvas_controller = Mock()
        canvas_controller.ax.plot.return_value = [Mock()]

        handler = MeshEditHandler(
            canvas_controller=canvas_controller,
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        # Click near vertex 0
        event = Mock()
        event.xdata = 0.01
        event.ydata = 0.01

        handled = handler.handle_mouse_press(event)

        assert handled is True
        assert handler.is_dragging()

    def test_left_click_far_from_vertices_does_not_select(self):
        """Left-click far from vertices should not select."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        # Click far from any vertex
        event = Mock()
        event.xdata = 10.0
        event.ydata = 10.0

        handled = handler.handle_mouse_press(event)

        assert handled is False
        assert not handler.is_dragging()

    def test_click_when_inactive_returns_false(self):
        """Clicks when inactive should return False."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        event = Mock()
        event.xdata = 0.0
        event.ydata = 0.0

        handled = handler.handle_mouse_press(event)
        assert handled is False


class TestMeshEditHandlerMouseMotion:
    """Test mouse motion handling for vertex dragging."""

    def test_mouse_motion_while_dragging_moves_vertex(self):
        """Mouse motion while dragging should move the selected vertex."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        canvas_controller = Mock()
        canvas_controller.ax.plot.return_value = [Mock()]
        on_mesh_update = Mock()

        handler = MeshEditHandler(
            canvas_controller=canvas_controller,
            on_mesh_update_callback=on_mesh_update
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        # Select vertex 0
        event = Mock()
        event.xdata = 0.01
        event.ydata = 0.01
        handler.handle_mouse_press(event)

        # Drag to new position
        event.xdata = 0.5
        event.ydata = 0.5
        handled = handler.handle_mouse_motion(event)

        assert handled is True
        on_mesh_update.assert_called_once()  # Should trigger update

    def test_mouse_motion_when_not_dragging_returns_false(self):
        """Mouse motion when not dragging should return False."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        event = Mock()
        event.xdata = 0.5
        event.ydata = 0.5

        handled = handler.handle_mouse_motion(event)
        assert handled is False


class TestMeshEditHandlerMouseRelease:
    """Test mouse release handling to end dragging."""

    def test_mouse_release_ends_dragging(self):
        """Mouse release should end dragging."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        canvas_controller = Mock()
        canvas_controller.ax.plot.return_value = [Mock()]

        handler = MeshEditHandler(
            canvas_controller=canvas_controller,
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        # Start dragging
        event = Mock()
        event.xdata = 0.01
        event.ydata = 0.01
        handler.handle_mouse_press(event)

        assert handler.is_dragging()

        # Release
        handled = handler.handle_mouse_release(event)

        assert handled is True
        assert not handler.is_dragging()


class TestMeshEditHandlerMeshRetrieval:
    """Test retrieving modified mesh data."""

    def test_get_mesh_returns_current_state(self):
        """get_mesh() should return current vertices and elements."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        handler = MeshEditHandler(
            canvas_controller=Mock(),
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        v, e = handler.get_mesh()

        assert v is not None
        assert e is not None
        assert v.shape == (3, 2)
        assert e.shape == (1, 3)

    def test_get_manually_moved_vertices_returns_set(self):
        """get_manually_moved_vertices() should return set of moved indices."""
        from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler

        canvas_controller = Mock()
        canvas_controller.ax.plot.return_value = [Mock()]

        handler = MeshEditHandler(
            canvas_controller=canvas_controller,
            on_mesh_update_callback=Mock()
        )

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])
        handler.set_active(True, vertices, elements)

        # Move a vertex
        event = Mock()
        event.xdata = 0.01
        event.ydata = 0.01
        handler.handle_mouse_press(event)
        event.xdata = 0.5
        event.ydata = 0.5
        handler.handle_mouse_motion(event)
        handler.handle_mouse_release(event)

        moved = handler.get_manually_moved_vertices()

        assert isinstance(moved, set)
        assert 0 in moved  # Vertex 0 was moved
