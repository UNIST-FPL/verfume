"""Tests for MeshQualityAnalyzer module."""
import pytest
import numpy as np
from mesh_gui_project.core.mesh_quality import MeshQualityAnalyzer


class TestMeshQualityAnalyzer:
    """Test MeshQualityAnalyzer class."""

    def test_mesh_quality_analyzer_exists(self):
        """Test that MeshQualityAnalyzer class can be imported."""
        from mesh_gui_project.core.mesh_quality import MeshQualityAnalyzer
        assert MeshQualityAnalyzer is not None

    def test_compute_aspect_ratios_simple_triangle(self):
        """Test aspect ratio computation for a simple equilateral triangle."""
        # Equilateral triangle (should have aspect ratio close to 1)
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.5, np.sqrt(3)/2]
        ])
        elements = np.array([[0, 1, 2]])

        aspect_ratios = MeshQualityAnalyzer.compute_aspect_ratios(vertices, elements)

        assert len(aspect_ratios) == 1
        # Equilateral triangle should have good aspect ratio (close to 1.15)
        assert aspect_ratios[0] < 1.5

    def test_compute_aspect_ratios_elongated_triangle(self):
        """Test aspect ratio computation for an elongated triangle."""
        # Very elongated triangle (poor aspect ratio)
        vertices = np.array([
            [0.0, 0.0],
            [10.0, 0.0],
            [5.0, 0.1]
        ])
        elements = np.array([[0, 1, 2]])

        aspect_ratios = MeshQualityAnalyzer.compute_aspect_ratios(vertices, elements)

        assert len(aspect_ratios) == 1
        # Elongated triangle should have high aspect ratio
        assert aspect_ratios[0] > 5.0

    def test_compute_min_angles_equilateral(self):
        """Test minimum angle computation for equilateral triangle."""
        # Equilateral triangle (all angles 60 degrees)
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.5, np.sqrt(3)/2]
        ])
        elements = np.array([[0, 1, 2]])

        min_angles = MeshQualityAnalyzer.compute_min_angles(vertices, elements)

        assert len(min_angles) == 1
        # All angles should be ~60 degrees
        assert abs(min_angles[0] - 60.0) < 1.0

    def test_compute_min_angles_right_triangle(self):
        """Test minimum angle computation for right triangle."""
        # Right triangle with 90, 45, 45 degree angles
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0]
        ])
        elements = np.array([[0, 1, 2]])

        min_angles = MeshQualityAnalyzer.compute_min_angles(vertices, elements)

        assert len(min_angles) == 1
        # Minimum angle should be ~45 degrees
        assert abs(min_angles[0] - 45.0) < 1.0

    def test_compute_areas_simple_triangle(self):
        """Test area computation for a simple triangle."""
        # Right triangle with base=1, height=1, area=0.5
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0]
        ])
        elements = np.array([[0, 1, 2]])

        areas = MeshQualityAnalyzer.compute_areas(vertices, elements)

        assert len(areas) == 1
        assert abs(areas[0] - 0.5) < 1e-10

    def test_compute_areas_multiple_triangles(self):
        """Test area computation for multiple triangles."""
        # Two triangles forming a square
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ])
        elements = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ])

        areas = MeshQualityAnalyzer.compute_areas(vertices, elements)

        assert len(areas) == 2
        # Each triangle should have area 0.5
        assert abs(areas[0] - 0.5) < 1e-10
        assert abs(areas[1] - 0.5) < 1e-10

    def test_check_inverted_elements_normal_triangle(self):
        """Test inverted element detection for normal triangle."""
        # Normal counter-clockwise triangle
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0]
        ])
        elements = np.array([[0, 1, 2]])

        inverted = MeshQualityAnalyzer.check_inverted_elements(vertices, elements)

        assert len(inverted) == 0

    def test_check_inverted_elements_inverted_triangle(self):
        """Test inverted element detection for inverted triangle."""
        # Inverted (clockwise) triangle
        vertices = np.array([
            [0.0, 0.0],
            [0.0, 1.0],  # Swapped to make clockwise
            [1.0, 0.0]
        ])
        elements = np.array([[0, 1, 2]])

        inverted = MeshQualityAnalyzer.check_inverted_elements(vertices, elements)

        assert len(inverted) == 1
        assert inverted[0] == 0

    def test_compute_all_metrics_returns_dict(self):
        """Test that compute_all_metrics returns a dictionary with all metrics."""
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.5, np.sqrt(3)/2]
        ])
        elements = np.array([[0, 1, 2]])

        metrics = MeshQualityAnalyzer.compute_all_metrics(vertices, elements)

        assert isinstance(metrics, dict)
        assert 'aspect_ratios' in metrics
        assert 'min_angles' in metrics
        assert 'areas' in metrics
        assert len(metrics['aspect_ratios']) == 1
        assert len(metrics['min_angles']) == 1
        assert len(metrics['areas']) == 1

    def test_compute_all_metrics_multiple_triangles(self):
        """Test compute_all_metrics with multiple triangles."""
        # Four triangles in a mesh
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [2.0, 0.0],
            [0.5, 1.0],
            [1.5, 1.0]
        ])
        elements = np.array([
            [0, 1, 3],
            [1, 4, 3],
            [1, 2, 4]
        ])

        metrics = MeshQualityAnalyzer.compute_all_metrics(vertices, elements)

        assert len(metrics['aspect_ratios']) == 3
        assert len(metrics['min_angles']) == 3
        assert len(metrics['areas']) == 3

    def test_degenerate_triangle_handling(self):
        """Test handling of degenerate (zero-area) triangles."""
        # Degenerate triangle (all points collinear)
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [2.0, 0.0]
        ])
        elements = np.array([[0, 1, 2]])

        metrics = MeshQualityAnalyzer.compute_all_metrics(vertices, elements)

        # Should handle gracefully (area ~0, aspect ratio inf)
        assert metrics['areas'][0] < 1e-10
        assert np.isinf(metrics['aspect_ratios'][0]) or metrics['aspect_ratios'][0] > 1000
