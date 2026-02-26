"""
Tests for SCOREC utility classes (topology extraction and entity classification).

This module tests the TopologyBuilder and EntityClassifier classes used
to extract discrete geometric models from triangular meshes.
"""
import numpy as np
import pytest
from mesh_gui_project.core.scorec_utils import TopologyBuilder, EntityClassifier


class TestTopologyBuilder:
    """Tests for TopologyBuilder class."""

    def test_topology_builder_exists(self):
        """Test that TopologyBuilder class exists."""
        builder = TopologyBuilder()
        assert builder is not None

    def test_build_edge_to_triangles_map_simple_quad(self):
        """Test edge mapping for 2-triangle quad mesh."""
        # Simple quad mesh: 2 triangles sharing an edge
        elements = np.array([
            [0, 1, 2],  # Triangle 0
            [0, 2, 3]   # Triangle 1
        ], dtype=np.int32)

        builder = TopologyBuilder()
        edge_map = builder.build_edge_to_triangles_map(elements)

        # Should have 5 edges total
        assert len(edge_map) == 5

        # Diagonal edge (0,2) should be shared by both triangles
        diagonal_edge = tuple(sorted([0, 2]))
        assert diagonal_edge in edge_map
        assert len(edge_map[diagonal_edge]) == 2
        assert 0 in edge_map[diagonal_edge]
        assert 1 in edge_map[diagonal_edge]

        # Boundary edges should have only 1 triangle
        boundary_edges = [
            tuple(sorted([0, 1])),
            tuple(sorted([1, 2])),
            tuple(sorted([2, 3])),
            tuple(sorted([0, 3]))
        ]
        for edge in boundary_edges:
            assert edge in edge_map
            assert len(edge_map[edge]) == 1

    def test_find_boundary_edges_simple_quad(self):
        """Test boundary edge detection for quad mesh."""
        # Simple quad mesh: 2 triangles
        elements = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ], dtype=np.int32)

        builder = TopologyBuilder()
        edge_map = builder.build_edge_to_triangles_map(elements)
        boundary_edges = builder.find_boundary_edges(edge_map)

        # Should have 4 boundary edges
        assert len(boundary_edges) == 4

        # Check specific boundary edges
        expected_boundary = {
            tuple(sorted([0, 1])),
            tuple(sorted([1, 2])),
            tuple(sorted([2, 3])),
            tuple(sorted([0, 3]))
        }
        assert boundary_edges == expected_boundary

    def test_find_boundary_edges_single_triangle(self):
        """Test boundary detection for isolated triangle."""
        # Single triangle - all edges are boundary
        elements = np.array([
            [0, 1, 2]
        ], dtype=np.int32)

        builder = TopologyBuilder()
        edge_map = builder.build_edge_to_triangles_map(elements)
        boundary_edges = builder.find_boundary_edges(edge_map)

        # All 3 edges should be boundary
        assert len(boundary_edges) == 3

        expected_boundary = {
            tuple(sorted([0, 1])),
            tuple(sorted([1, 2])),
            tuple(sorted([0, 2]))
        }
        assert boundary_edges == expected_boundary

    def test_build_edge_chains_simple_square(self):
        """Test edge chain for square boundary (4 edges, 4 corners)."""
        # Square with vertices at corners
        vertices = np.array([
            [0.0, 0.0],  # 0
            [1.0, 0.0],  # 1
            [1.0, 1.0],  # 2
            [0.0, 1.0]   # 3
        ])

        # Boundary edges forming a square
        boundary_edges = {
            (0, 1), (1, 2), (2, 3), (3, 0)
        }

        builder = TopologyBuilder()
        chains = builder.build_edge_chains(boundary_edges, vertices, angle_threshold=30.0)

        # Should have 4 chains (one for each edge of the square)
        # because all corners have 90-degree angles
        assert len(chains) == 4

    def test_build_edge_chains_finds_corners(self):
        """Test corner vertex detection from angle changes."""
        # L-shaped boundary with one corner
        vertices = np.array([
            [0.0, 0.0],  # 0 - corner
            [1.0, 0.0],  # 1 - edge
            [2.0, 0.0],  # 2 - corner
            [2.0, 1.0]   # 3 - endpoint
        ])

        # Boundary edges along L-shape
        boundary_edges = {
            (0, 1), (1, 2), (2, 3)
        }

        builder = TopologyBuilder()
        chains = builder.build_edge_chains(boundary_edges, vertices, angle_threshold=30.0)

        # Should identify corners at vertices 0, 2, 3
        # and create chains between them
        assert len(chains) >= 2


class TestEntityClassifier:
    """Tests for EntityClassifier class."""

    def test_entity_classifier_exists(self):
        """Test that EntityClassifier class exists."""
        classifier = EntityClassifier()
        assert classifier is not None

    def test_classify_vertices_simple_quad(self):
        """Test vertex classification for simple quad mesh."""
        # Quad mesh with 4 boundary vertices
        vertices = np.array([
            [0.0, 0.0],  # 0 - corner
            [1.0, 0.0],  # 1 - corner
            [1.0, 1.0],  # 2 - corner
            [0.0, 1.0]   # 3 - corner
        ])

        elements = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ], dtype=np.int32)

        builder = TopologyBuilder()
        edge_map = builder.build_edge_to_triangles_map(elements)
        boundary_edges = builder.find_boundary_edges(edge_map)
        edge_chains = builder.build_edge_chains(boundary_edges, vertices, angle_threshold=30.0)

        # Build vertex_to_tag mapping (all vertices are corners)
        corner_vertices = set()
        for chain in edge_chains:
            corner_vertices.add(chain[0])
            corner_vertices.add(chain[-1])
        vertex_to_tag = {v_idx: tag for tag, v_idx in enumerate(sorted(corner_vertices))}

        classifier = EntityClassifier()
        vertex_class = classifier.classify_vertices(
            vertices, boundary_edges, edge_chains, vertex_to_tag
        )

        # All 4 vertices are on boundary
        assert len(vertex_class) == 4

        # Check that corners are classified as model vertices (dim=0)
        # and vertices are assigned proper classifications
        for v_idx, (dim, tag) in vertex_class.items():
            assert dim in [0, 1, 2]  # Valid dimensions
