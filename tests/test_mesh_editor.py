"""
Tests for interactive mesh editor.
"""
import numpy as np
import pytest
from mesh_gui_project.ui.mesh_editor import MeshEditor


def create_simple_mesh():
    """Create simple triangular mesh for testing."""
    vertices = np.array([
        [1.0, 0.0],
        [2.0, 0.0],
        [1.5, 0.5],
        [1.5, -0.5]
    ])
    elements = np.array([
        [0, 1, 2],
        [0, 1, 3]
    ], dtype=np.int32)
    return vertices, elements


def test_mesh_editor_exists():
    """Test that MeshEditor can be instantiated."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    assert editor is not None
    assert len(editor.vertices) == 4
    assert len(editor.elements) == 2


def test_select_vertex():
    """Test selecting vertex by click."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Click near vertex 0
    idx = editor.select_vertex(1.01, 0.01, threshold=0.1)

    assert idx == 0
    assert 0 in editor.selected_vertices


def test_select_vertex_too_far():
    """Test that distant clicks don't select."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Click far from any vertex
    idx = editor.select_vertex(5.0, 5.0, threshold=0.1)

    assert idx is None
    assert len(editor.selected_vertices) == 0


def test_select_vertices_in_rectangle():
    """Test rectangle selection."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Select vertices in rectangle
    selected = editor.select_vertices_in_rectangle(0.9, 2.1, -0.1, 0.1)

    # Should select vertices 0 and 1
    assert 0 in selected
    assert 1 in selected
    assert 2 not in selected
    assert 3 not in selected


def test_move_vertex_unconstrained():
    """Test moving unconstrained vertex."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Move vertex 0
    editor.move_vertex(0, 1.1, 0.1)

    assert np.allclose(editor.vertices[0], [1.1, 0.1])


def test_move_vertex_constrained():
    """Test moving constrained vertex."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Define contour constraint
    contour = np.array([[1.0, 0.0], [1.0, 0.5], [1.0, 1.0]])
    editor.set_contour_constraint(0, contour)

    # Try to move vertex 0 away from contour
    editor.move_vertex(0, 1.5, 0.3)

    # Should snap to nearest contour point
    assert editor.vertices[0, 0] == 1.0  # R should be 1.0
    assert editor.vertices[0, 1] >= 0.0  # Z should be on contour


def test_move_selected_vertices():
    """Test batch moving selected vertices."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Select vertices 0 and 1
    editor.selected_vertices = {0, 1}

    # Move by offset
    editor.move_selected_vertices(0.1, 0.1)

    assert np.allclose(editor.vertices[0], [1.1, 0.1])
    assert np.allclose(editor.vertices[1], [2.1, 0.1])


def test_delete_vertex():
    """Test deleting vertex."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Delete vertex 2
    editor.delete_vertex(2)

    # Vertex should be marked as NaN
    assert np.isnan(editor.vertices[2, 0])

    # Triangle containing vertex 2 should be removed
    assert len(editor.elements) == 1


def test_get_mesh_filters_deleted():
    """Test that get_mesh filters out deleted vertices."""
    vertices, elements = create_simple_mesh()
    editor = MeshEditor(vertices, elements)

    # Delete vertex 2
    editor.delete_vertex(2)

    # Get filtered mesh
    clean_vertices, clean_elements = editor.get_mesh()

    # Should have 3 valid vertices
    assert len(clean_vertices) == 3
    assert not np.any(np.isnan(clean_vertices))
