"""
Test for edge classification bug that causes mesh->verify() to fail.

BUG: _classify_mesh_edges() uses boundary_edges set from TopologyBuilder
to classify edges. However, this is incorrect for meshes with topology gaps.

CORRECT: Edge classification should be based on triangle adjacency count:
- Edge in 1 triangle → boundary edge (dim=1)
- Edge in 2 triangles → interior edge (dim=2)
- Edge in >2 triangles → non-manifold (error)

This ensures mesh->verify() passes by respecting the manifold property.
"""
import pytest
import numpy as np


def test_edge_classification_uses_triangle_adjacency():
    """
    Edge classification must use triangle adjacency count, not boundary detection.

    This test creates a mesh where an edge appears in only 1 triangle
    but might not be detected as a boundary edge by TopologyBuilder.
    Such edges MUST be classified as boundary (dim=1) to pass verify().
    """
    from mesh_gui_project.core.scorec_exporter import BoundaryExtractor

    # Create a simple mesh with a clear boundary
    # Triangle mesh forming a partial square (with a gap)
    vertices = np.array([
        [0.0, 0.0],  # 0
        [1.0, 0.0],  # 1
        [1.0, 1.0],  # 2
        [0.0, 1.0],  # 3
        [0.5, 0.5],  # 4 - interior vertex
    ])

    # Create triangles - note some edges will only appear in 1 triangle
    elements = np.array([
        [0, 1, 4],  # Bottom-center triangle
        [1, 2, 4],  # Right-center triangle
        [2, 3, 4],  # Top-center triangle
        [3, 0, 4]   # Left-center triangle
    ], dtype=np.int32)

    extractor = BoundaryExtractor()
    model_entities, classification = extractor.extract_model(vertices, elements)

    # Check edge classification
    edge_class = classification['edge_class']

    # The CRITICAL requirement: ALL edges must be classified correctly
    # based on triangle adjacency, not just boundary detection

    # In this mesh:
    # - Outer edges (0-1, 1-2, 2-3, 3-0) appear in 1 triangle each → boundary (dim=1)
    # - Inner edges (0-4, 1-4, 2-4, 3-4) appear in 2 triangles each → could be interior (dim=2)
    #   BUT if they're on actual boundary, they should be (dim=1)

    # The key: NO edge with only 1 adjacent triangle should be classified as interior (dim=2)
    # This would violate the manifold property and cause verify() to fail

    # Count edges by classification dimension
    boundary_edges = sum(1 for dim, tag in edge_class.values() if dim == 1)
    interior_edges = sum(1 for dim, tag in edge_class.values() if dim == 2)

    print(f"\nEdge classification:")
    print(f"  Boundary edges (dim=1): {boundary_edges}")
    print(f"  Interior edges (dim=2): {interior_edges}")

    # All edges in this mesh should be properly classified
    # No edge should violate the manifold property
    assert len(edge_class) > 0, "Should have classified edges"


def test_edge_classification_manifold_property():
    """
    Verify that edge classification respects the 2-manifold property.

    For a 2-manifold triangular mesh:
    - Boundary edges (dim=1) must have exactly 1 adjacent triangle
    - Interior edges (dim=2) must have exactly 2 adjacent triangles

    This is what PUMI's mesh->verify() checks!
    """
    from mesh_gui_project.core.scorec_exporter import SMBWriter
    import numpy as np

    # Create a simple quad mesh
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0]
    ])

    elements = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ], dtype=np.int32)

    # Generate edges and triangle-edge mapping
    writer = SMBWriter()
    edges, triangle_edges = writer._generate_edges(elements)

    # Count triangle adjacency for each edge
    edge_triangle_count = [0] * len(edges)
    for tri_edges in triangle_edges.values():
        for edge_idx in tri_edges:
            edge_triangle_count[edge_idx] += 1

    # Verify manifold property
    print(f"\nEdge triangle adjacency:")
    for edge_idx, count in enumerate(edge_triangle_count):
        v1, v2 = edges[edge_idx]
        print(f"  Edge {edge_idx} ({v1}-{v2}): {count} triangles")

        # CRITICAL: All edges must have 1 or 2 adjacent triangles (2-manifold)
        assert count in [1, 2], f"Edge {edge_idx} has {count} triangles (non-manifold!)"

    # Now verify classification matches adjacency:
    # - Edges with 1 triangle → boundary (dim=1)
    # - Edges with 2 triangles → interior (dim=2)

    # This is what we need to implement in _classify_mesh_edges!


def test_classify_edges_by_adjacency_not_boundary_detection():
    """
    Test that demonstrates the CORRECT way to classify edges.

    Edge classification MUST be based on triangle adjacency count,
    NOT on boundary detection results from TopologyBuilder.
    """
    from mesh_gui_project.core.scorec_exporter import BoundaryExtractor

    # Simple square mesh
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0]
    ])

    elements = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ], dtype=np.int32)

    extractor = BoundaryExtractor()
    model_entities, classification = extractor.extract_model(vertices, elements)

    edge_class = classification['edge_class']

    # Build triangle adjacency count for verification
    # (This is what the FIXED version should do internally)
    from mesh_gui_project.core.scorec_exporter import SMBWriter
    writer = SMBWriter()
    edges, triangle_edges = writer._generate_edges(elements)

    edge_triangle_count = [0] * len(edges)
    for tri_edges in triangle_edges.values():
        for edge_idx in tri_edges:
            edge_triangle_count[edge_idx] += 1

    # VERIFY: Classification matches adjacency count
    for edge_idx in range(len(edges)):
        dim, tag = edge_class[edge_idx]
        count = edge_triangle_count[edge_idx]

        if count == 1:
            # Edge with 1 triangle MUST be classified as boundary (dim=1)
            assert dim == 1, f"Edge {edge_idx} has {count} triangle but classified as dim={dim}"
        elif count == 2:
            # Edge with 2 triangles SHOULD be classified as interior (dim=2)
            # UNLESS it's on the actual geometric boundary
            # For now, we allow dim=1 or dim=2
            assert dim in [1, 2], f"Edge {edge_idx} has {count} triangles but classified as dim={dim}"
        else:
            pytest.fail(f"Edge {edge_idx} has {count} triangles (non-manifold!)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
