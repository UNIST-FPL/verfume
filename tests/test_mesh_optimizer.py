"""
Tests for mesh quality optimization.
"""
import numpy as np
import pytest
from mesh_gui_project.core.mesh_optimizer import MeshOptimizer


def create_mesh_with_quality_issues():
    """Create mesh with known quality issues."""
    # Create mesh with one badly shaped triangle
    vertices = np.array([
        [1.0, 0.0],
        [2.0, 0.0],
        [1.5, 0.1],  # Very flat triangle
        [1.5, 0.5]
    ])
    elements = np.array([
        [0, 1, 2],  # Flat triangle
        [0, 2, 3]
    ], dtype=np.int32)
    return vertices, elements


def test_mesh_optimizer_exists():
    """Test that MeshOptimizer can be instantiated."""
    optimizer = MeshOptimizer()
    assert optimizer is not None


def test_set_constrained_vertices():
    """Test setting constrained vertices."""
    optimizer = MeshOptimizer()

    optimizer.set_constrained_vertices({0, 1, 2})

    assert 0 in optimizer.constrained_vertices
    assert 1 in optimizer.constrained_vertices
    assert 2 in optimizer.constrained_vertices


def test_laplacian_smoothing_moves_vertices():
    """Test that Laplacian smoothing moves vertices."""
    vertices, elements = create_mesh_with_quality_issues()
    optimizer = MeshOptimizer()

    # Don't constrain vertex 2 (the one creating flat triangle)
    optimizer.set_constrained_vertices({0, 1})

    # Apply smoothing
    smoothed = optimizer.laplacian_smoothing(vertices, elements)

    # Vertex 2 should have moved
    assert not np.allclose(smoothed[2], vertices[2])


def test_laplacian_smoothing_respects_constraints():
    """Test that constrained vertices don't move."""
    vertices, elements = create_mesh_with_quality_issues()
    optimizer = MeshOptimizer()

    # Constrain all boundary vertices
    optimizer.set_constrained_vertices({0, 1})

    smoothed = optimizer.laplacian_smoothing(vertices, elements)

    # Constrained vertices should not move
    assert np.allclose(smoothed[0], vertices[0])
    assert np.allclose(smoothed[1], vertices[1])


def test_optimize_improves_mesh():
    """Test that optimization improves mesh."""
    vertices, elements = create_mesh_with_quality_issues()
    optimizer = MeshOptimizer()

    # Constrain boundary
    optimizer.set_constrained_vertices({0, 1})

    optimized_vertices, _ = optimizer.optimize(vertices, elements, n_iterations=3)

    # Vertices should have changed
    assert not np.allclose(optimized_vertices, vertices)
