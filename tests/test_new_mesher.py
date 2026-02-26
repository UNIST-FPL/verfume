"""
Tests for new contour-constrained mesh generation.
"""
import numpy as np
import pytest
from mesh_gui_project.core.new_mesher import ContourMesher


def create_circular_boundary(center=(1.5, 0.0), radius=0.3, n_points=20):
    """Helper to create circular boundary."""
    theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    R = center[0] + radius * np.cos(theta)
    Z = center[1] + radius * np.sin(theta)
    return np.column_stack([R, Z])


def test_contour_mesher_exists():
    """Test that ContourMesher can be instantiated."""
    mesher = ContourMesher()
    assert mesher is not None


def test_generate_mesh_from_boundary():
    """Test generating mesh from boundary only."""
    mesher = ContourMesher()

    # Create simple circular boundary
    boundary = create_circular_boundary(radius=0.3, n_points=30)

    vertices, elements = mesher.generate_mesh(boundary, target_element_size=0.05)

    # Verify mesh properties
    assert vertices is not None
    assert elements is not None
    assert vertices.shape[1] == 2  # (R, Z) columns
    assert elements.shape[1] == 3  # Triangles
    assert len(vertices) > len(boundary)  # Interior vertices added
    assert len(elements) > 0


def test_compute_quality_metrics():
    """Test computing mesh quality metrics."""
    mesher = ContourMesher()

    # Create simple mesh
    boundary = create_circular_boundary(radius=0.3, n_points=30)
    vertices, elements = mesher.generate_mesh(boundary, target_element_size=0.05)

    # Compute metrics
    metrics = mesher.compute_quality_metrics(vertices, elements)

    # Verify metrics exist
    assert 'aspect_ratios' in metrics
    assert 'min_angles' in metrics
    assert 'areas' in metrics

    # Check shapes
    assert len(metrics['aspect_ratios']) == len(elements)
    assert len(metrics['min_angles']) == len(elements)
    assert len(metrics['areas']) == len(elements)

    # Quality checks
    assert np.all(metrics['aspect_ratios'] > 0)
    assert np.all(metrics['min_angles'] >= 0)
    assert np.all(metrics['min_angles'] <= 180)
    assert np.all(metrics['areas'] > 0)
