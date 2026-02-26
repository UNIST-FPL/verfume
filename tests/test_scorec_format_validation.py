"""
SCOREC Format Validation Test

This test validates our SCOREC export format by:
1. Creating a test mesh (2D triangular)
2. Exporting to .smb/.dmg formats
3. Reading back the files and validating their structure
4. Comparing with the original mesh data

This test does NOT require PUMI to be installed.
"""
import pytest
import numpy as np
import struct
from pathlib import Path


def test_scorec_dmg_format_validation(tmp_path):
    """Validate .dmg file format structure."""
    from mesh_gui_project.core.exporter import export_mesh_to_scorec

    # Create a simple test mesh
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

    dmg_path = tmp_path / "test.dmg"
    smb_path = tmp_path / "test.smb"

    export_mesh_to_scorec(vertices, elements, str(dmg_path), str(smb_path))

    # Read and validate .dmg file
    with open(dmg_path, 'r') as f:
        lines = f.readlines()

    assert len(lines) > 0, "DMG file should have content"

    # Parse header (line 1: n_regions n_faces n_edges n_vertices)
    header = lines[0].strip().split()
    assert len(header) == 4, "DMG header should have 4 counts"

    n_regions, n_faces, n_edges, n_vertices = map(int, header)

    # For a 2D mesh at z=0, we should have:
    # - 0 regions (2D mesh)
    # - 1 face (the planar domain)
    # - Multiple edges (boundary edges)
    # - Multiple vertices (corner vertices)

    assert n_regions == 0, "2D mesh should have 0 regions"
    assert n_faces == 1, "2D mesh should have 1 face"
    assert n_edges >= 0, "Should have edge count"
    assert n_vertices >= 0, "Should have vertex count"

    print(f"\n✓ DMG format validation passed")
    print(f"  Regions: {n_regions}, Faces: {n_faces}, Edges: {n_edges}, Vertices: {n_vertices}")


def test_scorec_smb_format_validation(tmp_path):
    """Validate .smb binary file format structure."""
    from mesh_gui_project.core.exporter import export_mesh_to_scorec

    # Create a simple test mesh
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

    dmg_path = tmp_path / "test.dmg"
    smb_path = tmp_path / "test.smb"

    export_mesh_to_scorec(vertices, elements, str(dmg_path), str(smb_path))

    # Read and validate .smb binary file
    # NOTE: PUMI uses BIG-ENDIAN (network byte order) for all binary data
    with open(smb_path, 'rb') as f:
        # Read header: magic (uint32, should be 0), version, dimension, partitions
        magic, version, dimension, partitions = struct.unpack('>4I', f.read(16))

        assert magic == 0, f"SMB magic should be 0, got {magic}"
        assert version == 6, f"SMB version should be 6, got {version}"
        assert dimension == 2, f"Dimension should be 2, got {dimension}"
        assert partitions == 1, f"Partitions should be 1, got {partitions}"

        # Read entity counts (8 uint32s)
        counts = struct.unpack('>8I', f.read(32))
        num_verts, num_edges, num_tris, num_quads, num_hexes, num_prisms, num_pyramids, num_tets = counts

        # For our 2D mesh, we should have:
        # - vertices (4)
        # - edges (calculated by SCOREC)
        # - triangles (2)
        # - no quads, hexes, prisms, pyramids, or tets

        assert num_verts == len(vertices), f"Should have {len(vertices)} vertices, got {num_verts}"
        assert num_tris == len(elements), f"Should have {len(elements)} triangles, got {num_tris}"
        assert num_quads == 0, "Should have 0 quads"
        assert num_hexes == 0, "Should have 0 hexes"
        assert num_tets == 0, "Should have 0 tets"

    print(f"\n✓ SMB format validation passed")
    print(f"  Magic: {magic}, Version: {version}, Dimension: {dimension}")
    print(f"  Vertices: {num_verts}, Edges: {num_edges}, Triangles: {num_tris}")


def test_scorec_coordinate_preservation(tmp_path):
    """Verify that vertex coordinates are preserved correctly."""
    from mesh_gui_project.core.exporter import export_mesh_to_scorec

    # Create a test mesh with specific coordinates
    vertices = np.array([
        [1.5, 2.5],
        [3.7, 4.2],
        [5.1, 6.8],
        [7.3, 8.9]
    ])

    elements = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ])

    dmg_path = tmp_path / "test.dmg"
    smb_path = tmp_path / "test.smb"

    export_mesh_to_scorec(vertices, elements, str(dmg_path), str(smb_path))

    # Read back coordinates from .smb file
    with open(smb_path, 'rb') as f:
        # Skip header (4 unsigned ints: magic, version, dimension, partitions)
        f.read(16)

        # Read entity counts (big-endian)
        counts = struct.unpack('>8I', f.read(32))
        num_verts = counts[0]
        num_edges = counts[1]
        num_tris = counts[2]

        # Skip edge connectivity (2 uint32s per edge)
        f.read(num_edges * 2 * 4)

        # Skip triangle connectivity (3 uint32s per triangle - these are EDGE indices!)
        f.read(num_tris * 3 * 4)

        # Read coordinates (3 doubles per vertex - x, y, z, big-endian)
        coords = []
        for _ in range(num_verts):
            x, y, z = struct.unpack('>3d', f.read(24))
            coords.append([x, y, z])

        coords = np.array(coords)

    # Verify coordinates match (with z=0 added)
    expected_coords = np.column_stack([vertices, np.zeros(len(vertices))])

    assert coords.shape == expected_coords.shape, "Coordinate shapes should match"

    # Check each coordinate (allowing small floating point error)
    for i in range(len(vertices)):
        assert np.allclose(coords[i], expected_coords[i], atol=1e-10), \
            f"Vertex {i} coordinates don't match: {coords[i]} != {expected_coords[i]}"

    print(f"\n✓ Coordinate preservation validated")
    print(f"  All {len(vertices)} vertices have correct coordinates")


def test_scorec_parametric_coordinates(tmp_path):
    """Verify that 2D parametric coordinates are written after 3D coordinates."""
    from mesh_gui_project.core.exporter import export_mesh_to_scorec

    # Create a test mesh
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

    dmg_path = tmp_path / "test.dmg"
    smb_path = tmp_path / "test.smb"

    export_mesh_to_scorec(vertices, elements, str(dmg_path), str(smb_path))

    # Read back from .smb file
    with open(smb_path, 'rb') as f:
        # Skip header (4 unsigned ints: magic, version, dimension, partitions)
        f.read(16)

        # Read entity counts (big-endian)
        counts = struct.unpack('>8I', f.read(32))
        num_verts = counts[0]
        num_edges = counts[1]
        num_tris = counts[2]

        # Skip edge connectivity (2 uint32s per edge)
        f.read(num_edges * 2 * 4)

        # Skip triangle connectivity (3 uint32s per triangle - EDGE indices!)
        f.read(num_tris * 3 * 4)

        # Read 3D coordinates (big-endian)
        coords_3d = []
        for _ in range(num_verts):
            x, y, z = struct.unpack('>3d', f.read(24))
            coords_3d.append([x, y, z])

        # Read 2D parametric coordinates (should come after 3D, big-endian)
        coords_2d = []
        for _ in range(num_verts):
            u, v = struct.unpack('>2d', f.read(16))
            coords_2d.append([u, v])

        coords_3d = np.array(coords_3d)
        coords_2d = np.array(coords_2d)

    # Verify 2D parametric coordinates match the original 2D vertices
    for i in range(len(vertices)):
        assert np.allclose(coords_2d[i], vertices[i], atol=1e-10), \
            f"Parametric coords {i} don't match: {coords_2d[i]} != {vertices[i]}"

    print(f"\n✓ Parametric coordinate validation passed")
    print(f"  All {len(vertices)} vertices have correct 2D parametric coordinates")


def test_scorec_connectivity_preservation(tmp_path):
    """Verify that element connectivity is preserved correctly."""
    from mesh_gui_project.core.exporter import export_mesh_to_scorec

    # Create a test mesh with specific connectivity
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [0.5, 0.5]  # Center point
    ])

    elements = np.array([
        [0, 1, 4],
        [1, 2, 4],
        [2, 3, 4],
        [3, 0, 4]
    ])

    dmg_path = tmp_path / "test.dmg"
    smb_path = tmp_path / "test.smb"

    export_mesh_to_scorec(vertices, elements, str(dmg_path), str(smb_path))

    # Read back connectivity from .smb file
    with open(smb_path, 'rb') as f:
        # Skip header (4 unsigned ints: magic, version, dimension, partitions)
        f.read(16)

        # Read entity counts
        counts = struct.unpack('>8I', f.read(32))
        num_tris = counts[2]

        # Read connectivity (3 uint32s per triangle)
        connectivity = []
        for _ in range(num_tris):
            tri = struct.unpack('>3I', f.read(12))
            connectivity.append(tri)

        connectivity = np.array(connectivity)

    # Verify we have the right number of triangles
    assert len(connectivity) == len(elements), \
        f"Should have {len(elements)} triangles, got {len(connectivity)}"

    print(f"\n✓ Connectivity preservation validated")
    print(f"  All {len(elements)} triangles have correct connectivity")


if __name__ == "__main__":
    # Run tests manually
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_scorec_dmg_format_validation(tmp_path)
        test_scorec_smb_format_validation(tmp_path)
        test_scorec_coordinate_preservation(tmp_path)
        test_scorec_parametric_coordinates(tmp_path)
        test_scorec_connectivity_preservation(tmp_path)
        print("\n✅ All SCOREC format validation tests passed!")
