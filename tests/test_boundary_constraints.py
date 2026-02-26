"""
Tests for boundary vertex constraints during mesh editing and optimization.
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
def window_with_mesh(qapp):
    """Create MainWindow with generated mesh."""
    window = MainWindow()

    # Load a test gEQDSK file
    geqdsk_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    window.load_geqdsk(geqdsk_file)

    # Switch to Mesh Editing tab
    window.left_tabs.setCurrentIndex(2)

    # Enable PSI contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Generate mesh
    window.generate_mesh_button.click()

    return window


def test_boundary_vertices_identified(window_with_mesh):
    """
    Test that boundary vertices are correctly identified after mesh generation.
    """
    window = window_with_mesh

    # Verify boundary vertices were identified
    assert window._boundary_vertex_indices is not None
    assert len(window._boundary_vertex_indices) > 0

    # Verify boundary was stored
    assert window._mesh_boundary is not None
    assert len(window._mesh_boundary) > 0


def test_boundary_vertices_stay_on_boundary_during_optimization(window_with_mesh):
    """
    Test that boundary vertices don't move during "Remesh & Optimize".
    """
    window = window_with_mesh

    # Get initial boundary vertex positions
    initial_boundary_positions = {}
    for vertex_idx in window._boundary_vertex_indices:
        initial_boundary_positions[vertex_idx] = window._mesh_vertices[vertex_idx].copy()

    # Click Remesh & Optimize
    window.remesh_optimize_button.click()

    # Verify boundary vertices haven't moved
    for vertex_idx in window._boundary_vertex_indices:
        final_position = window._mesh_vertices[vertex_idx]
        initial_position = initial_boundary_positions[vertex_idx]

        # Boundary vertices should be exactly the same
        assert np.allclose(final_position, initial_position, atol=1e-10), \
            f"Boundary vertex {vertex_idx} moved from {initial_position} to {final_position}"


def test_interior_vertices_move_during_optimization(window_with_mesh):
    """
    Test that interior (non-boundary) vertices DO move during optimization.
    """
    window = window_with_mesh

    # Find some interior vertices (not on boundary)
    interior_vertex_indices = []
    for i in range(len(window._mesh_vertices)):
        if i not in window._boundary_vertex_indices:
            interior_vertex_indices.append(i)

    assert len(interior_vertex_indices) > 0, "Should have some interior vertices"

    # Get initial interior vertex positions
    initial_positions = {}
    for vertex_idx in interior_vertex_indices[:10]:  # Check first 10 interior vertices
        initial_positions[vertex_idx] = window._mesh_vertices[vertex_idx].copy()

    # Click Remesh & Optimize
    window.remesh_optimize_button.click()

    # Verify at least some interior vertices moved
    moved_count = 0
    for vertex_idx in initial_positions:
        final_position = window._mesh_vertices[vertex_idx]
        initial_position = initial_positions[vertex_idx]

        if not np.allclose(final_position, initial_position, atol=1e-6):
            moved_count += 1

    assert moved_count > 0, "At least some interior vertices should have moved during optimization"


def test_boundary_vertex_constrained_to_contour_in_edit_mode(window_with_mesh):
    """
    Test that boundary vertices can only move along the boundary contour in edit mode.
    """
    window = window_with_mesh

    # Enter edit mode
    window.enter_edit_mode_button.setChecked(True)
    assert window._mesh_edit_mode_active is True

    # Get a boundary vertex
    boundary_vertex_idx = list(window._boundary_vertex_indices)[0]
    original_position = window._mesh_editor.vertices[boundary_vertex_idx].copy()

    # Try to move it to a position far from the boundary (interior point)
    centroid = window._mesh_vertices.mean(axis=0)
    window._mesh_editor.move_vertex(boundary_vertex_idx, centroid[0], centroid[1])

    # Get the new position
    new_position = window._mesh_editor.vertices[boundary_vertex_idx]

    # Verify it was projected to the boundary (stayed on boundary contour)
    # It should NOT be at the centroid
    assert not np.allclose(new_position, centroid, atol=1e-3), \
        "Boundary vertex should not move to arbitrary interior position"

    # Verify it's still on the boundary (close to a boundary edge or point)
    min_dist_to_boundary = float('inf')

    # Check distance to boundary points and edges
    boundary = window._mesh_boundary
    for i in range(len(boundary)):
        p1 = boundary[i]
        p2 = boundary[(i + 1) % len(boundary)]

        # Distance to point
        dist_to_p1 = np.linalg.norm(new_position - p1)
        min_dist_to_boundary = min(min_dist_to_boundary, dist_to_p1)

        # Distance to edge
        edge = p2 - p1
        edge_length_sq = np.dot(edge, edge)
        if edge_length_sq > 1e-10:
            t = np.dot(new_position - p1, edge) / edge_length_sq
            t = np.clip(t, 0, 1)
            projection = p1 + t * edge
            dist_to_edge = np.linalg.norm(new_position - projection)
            min_dist_to_boundary = min(min_dist_to_boundary, dist_to_edge)

    assert min_dist_to_boundary < 0.01, \
        f"Boundary vertex should stay on boundary (min dist: {min_dist_to_boundary})"


def test_interior_vertex_moves_freely_in_edit_mode(window_with_mesh):
    """
    Test that interior vertices can move freely (not constrained to boundary).
    """
    window = window_with_mesh

    # Enter edit mode
    window.enter_edit_mode_button.setChecked(True)
    assert window._mesh_edit_mode_active is True

    # Find centroid (should be an interior point)
    centroid = window._mesh_vertices.mean(axis=0)

    # Find vertex closest to centroid (interior vertex)
    distances_to_centroid = np.linalg.norm(window._mesh_vertices - centroid, axis=1)
    interior_vertex_idx = np.argmin(distances_to_centroid)

    # Verify it's not a boundary vertex
    assert interior_vertex_idx not in window._boundary_vertex_indices

    original_position = window._mesh_editor.vertices[interior_vertex_idx].copy()

    # Move it to a new position
    new_R = original_position[0] + 0.05
    new_Z = original_position[1] + 0.05
    window._mesh_editor.move_vertex(interior_vertex_idx, new_R, new_Z)

    # Get the new position
    new_position = window._mesh_editor.vertices[interior_vertex_idx]

    # Verify it moved to the desired position (not constrained)
    assert np.allclose(new_position, [new_R, new_Z], atol=1e-3), \
        "Interior vertex should move freely to new position"
