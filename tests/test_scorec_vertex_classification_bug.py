"""
Test for vertex classification bug with large mesh indices.

BUG: EntityClassifier.classify_vertices uses mesh vertex indices
as model vertex tags, which causes PUMI to fail when loading meshes
where mesh vertex indices exceed the number of model vertices.

Example: If corner vertex at mesh index 5000 is classified as (0, 5000)
but the model only has 5 vertices (tags 0-4), PUMI will fail.

FIX: classify_vertices must map corner vertices to their model tags (0-N)
using the vertex_to_tag mapping from BoundaryExtractor.
"""
import pytest
import numpy as np


def test_vertex_classification_uses_model_tags_not_mesh_indices():
    """
    Vertices should be classified to model entity TAGS, not mesh indices.

    This test creates a mesh where corner vertices have high mesh indices,
    which would cause PUMI to fail if we use mesh indices as model tags.
    """
    from mesh_gui_project.core.scorec_utils import EntityClassifier

    # Create a simple square mesh with vertices at high indices
    # Vertices: 1000, 1001, 1002, 1003 (high indices to trigger bug)
    vertices = np.array([
        [0.0, 0.0],  # Index 0 (but imagine this is at index 1000)
        [1.0, 0.0],  # Index 1 (but imagine this is at index 1001)
        [1.0, 1.0],  # Index 2 (but imagine this is at index 1002)
        [0.0, 1.0]   # Index 3 (but imagine this is at index 1003)
    ])

    # Boundary edges forming a square
    boundary_edges = {(0, 1), (1, 2), (2, 3), (3, 0)}

    # Edge chains (4 edges, 4 corners)
    edge_chains = [
        [0, 1],  # Bottom edge: corners 0, 1
        [1, 2],  # Right edge: corners 1, 2
        [2, 3],  # Top edge: corners 2, 3
        [3, 0]   # Left edge: corners 3, 0
    ]

    # The vertex_to_tag mapping that BoundaryExtractor creates
    # Maps mesh vertex index → model vertex tag
    vertex_to_tag = {0: 0, 1: 1, 2: 2, 3: 3}

    classifier = EntityClassifier()

    # CRITICAL: classifier must accept and use vertex_to_tag
    vertex_class = classifier.classify_vertices(
        vertices, boundary_edges, edge_chains, vertex_to_tag
    )

    # Verify corner vertices are classified with model tags (0-3), NOT mesh indices
    assert vertex_class[0] == (0, 0), "Corner at mesh index 0 should map to model tag 0"
    assert vertex_class[1] == (0, 1), "Corner at mesh index 1 should map to model tag 1"
    assert vertex_class[2] == (0, 2), "Corner at mesh index 2 should map to model tag 2"
    assert vertex_class[3] == (0, 3), "Corner at mesh index 3 should map to model tag 3"


def test_large_mesh_vertex_classification():
    """
    Test with a mesh that has many vertices where corners are at high indices.

    This simulates a real KSTAR mesh with 11,540 vertices where corner vertices
    might be at indices like 500, 2000, 5000, etc.
    """
    from mesh_gui_project.core.scorec_utils import EntityClassifier

    # Create mesh with 100 vertices where only vertices 10, 30, 70, 90 are corners
    n_vertices = 100
    vertices = np.random.rand(n_vertices, 2)

    # Boundary: a square with corners at high indices
    corner_indices = [10, 30, 70, 90]
    boundary_edges = {(10, 30), (30, 70), (70, 90), (90, 10)}
    edge_chains = [
        [10, 30],
        [30, 70],
        [70, 90],
        [90, 10]
    ]

    # Model tags are 0, 1, 2, 3 (NOT 10, 30, 70, 90!)
    vertex_to_tag = {10: 0, 30: 1, 70: 2, 90: 3}

    classifier = EntityClassifier()
    vertex_class = classifier.classify_vertices(
        vertices, boundary_edges, edge_chains, vertex_to_tag
    )

    # Verify corners use model tags, not mesh indices
    assert vertex_class[10] == (0, 0), "Mesh vertex 10 → model vertex 0"
    assert vertex_class[30] == (0, 1), "Mesh vertex 30 → model vertex 1"
    assert vertex_class[70] == (0, 2), "Mesh vertex 70 → model vertex 2"
    assert vertex_class[90] == (0, 3), "Mesh vertex 90 → model vertex 3"

    # Verify interior vertices classify to model face
    assert vertex_class[0] == (2, 0), "Interior vertex → model face"
    assert vertex_class[50] == (2, 0), "Interior vertex → model face"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
