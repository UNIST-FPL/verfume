"""
Tests for SCOREC exporter classes (DMG and SMB writers).

This module tests the DMGWriter and SMBWriter classes used to export
meshes in SCOREC PUMI formats.
"""
import numpy as np
import pytest
import os
import tempfile
import struct
from mesh_gui_project.core.scorec_exporter import DMGWriter, SMBWriter


class TestDMGWriter:
    """Tests for DMGWriter class."""

    def test_dmg_writer_exists(self):
        """Test that DMGWriter class exists."""
        writer = DMGWriter()
        assert writer is not None

    def test_dmg_writer_creates_file(self):
        """Test that write_dmg creates .dmg file."""
        writer = DMGWriter()

        # Simple model entities
        model_entities = {
            'model_vertices': [(0, 0.0, 0.0, 0.0)],
            'model_edges': [],
            'model_faces': [],
            'model_regions': [],
            'bbox': (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dmg', delete=False) as f:
            temp_path = f.name

        try:
            writer.write_dmg(model_entities, temp_path)
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_dmg_writer_header_counts(self):
        """Test header contains correct entity counts."""
        writer = DMGWriter()

        # Model with 2 vertices, 1 edge
        model_entities = {
            'model_vertices': [
                (0, 0.0, 0.0, 0.0),
                (1, 1.0, 0.0, 0.0)
            ],
            'model_edges': [(0, 0, 1)],
            'model_faces': [],
            'model_regions': [],
            'bbox': (0.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dmg', delete=False) as f:
            temp_path = f.name

        try:
            writer.write_dmg(model_entities, temp_path)

            # Read first line
            with open(temp_path, 'r') as f:
                first_line = f.readline().strip()
                # Format: n_regions n_faces n_edges n_vertices
                parts = first_line.split()
                assert len(parts) == 4
                assert parts[0] == '0'  # n_regions
                assert parts[1] == '0'  # n_faces
                assert parts[2] == '1'  # n_edges
                assert parts[3] == '2'  # n_vertices
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestSMBWriter:
    """Tests for SMBWriter class."""

    def test_smb_writer_exists(self):
        """Test that SMBWriter class exists."""
        writer = SMBWriter()
        assert writer is not None

    def test_smb_writer_creates_binary_file(self):
        """Test that write_smb creates binary .smb file."""
        writer = SMBWriter()

        # Simple mesh: single triangle
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]], dtype=np.int32)
        classification = {
            'vertex_class': {0: (2, 0), 1: (2, 0), 2: (2, 0)},
            'triangle_class': {0: (2, 0)}
        }

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.smb', delete=False) as f:
            temp_path = f.name

        try:
            writer.write_smb(vertices, elements, classification, temp_path)
            assert os.path.exists(temp_path)

            # File should be binary and non-empty
            file_size = os.path.getsize(temp_path)
            assert file_size > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_smb_writer_header_magic(self):
        """Test header contains magic=0 (unsigned int, big-endian)."""
        writer = SMBWriter()

        vertices = np.array([[0.0, 0.0]])
        elements = np.array([], dtype=np.int32).reshape(0, 3)
        classification = {'vertex_class': {}, 'edge_class': {}, 'triangle_class': {}}

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.smb', delete=False) as f:
            temp_path = f.name

        try:
            writer.write_smb(vertices, elements, classification, temp_path)

            # Read magic number (unsigned int, big-endian)
            with open(temp_path, 'rb') as f:
                magic = struct.unpack('>I', f.read(4))[0]
                assert magic == 0, f"Magic should be 0 (per PUMI spec), got {magic}"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_smb_writer_header_version(self):
        """Test header version is 6 (uint32, big-endian)."""
        writer = SMBWriter()

        vertices = np.array([[0.0, 0.0]])
        elements = np.array([], dtype=np.int32).reshape(0, 3)
        classification = {'vertex_class': {}, 'edge_class': {}, 'triangle_class': {}}

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.smb', delete=False) as f:
            temp_path = f.name

        try:
            writer.write_smb(vertices, elements, classification, temp_path)

            # Read header (big-endian)
            with open(temp_path, 'rb') as f:
                magic, version, dim, partitions = struct.unpack('>4I', f.read(16))
                assert magic == 0, "Magic should be 0"
                assert version == 6, f"Version should be 6, got {version}"
                assert dim == 2, "Dimension should be 2"
                assert partitions == 1, "Partitions should be 1"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestBoundaryExtractorIntegration:
    """Integration tests for complete SCOREC export workflow."""

    def test_boundary_extractor_with_simple_triangle(self):
        """Test BoundaryExtractor with minimal mesh."""
        from mesh_gui_project.core.scorec_exporter import BoundaryExtractor

        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]], dtype=np.int32)

        extractor = BoundaryExtractor()
        model_entities, classification = extractor.extract_model(vertices, elements)

        # Verify model entities structure
        assert 'model_vertices' in model_entities
        assert 'model_edges' in model_entities
        assert 'model_faces' in model_entities
        assert 'bbox' in model_entities

        # Triangle has 3 corners
        assert len(model_entities['model_vertices']) == 3

        # Classification should cover all vertices
        assert 'vertex_class' in classification
        assert 'triangle_class' in classification
        assert len(classification['triangle_class']) == 1

    def test_export_scorec_roundtrip(self):
        """Test complete export creates both files with correct content."""
        from mesh_gui_project.core.exporter import export_mesh_to_scorec

        # Create test mesh
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ])
        elements = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)

        with tempfile.NamedTemporaryFile(suffix='.dmg', delete=False) as f:
            dmg_path = f.name
        with tempfile.NamedTemporaryFile(suffix='.smb', delete=False) as f:
            smb_path = f.name

        try:
            export_mesh_to_scorec(vertices, elements, dmg_path, smb_path)

            # Verify both files exist
            assert os.path.exists(dmg_path)
            assert os.path.exists(smb_path)

            # Verify DMG is ASCII and readable
            with open(dmg_path, 'r') as f:
                first_line = f.readline()
                assert len(first_line.split()) == 4  # n_regions n_faces n_edges n_vertices

            # Verify SMB is binary with correct header
            with open(smb_path, 'rb') as f:
                magic = struct.unpack('>I', f.read(4))[0]
                assert magic == 0, "PUMI SMB magic should be 0"

        finally:
            if os.path.exists(dmg_path):
                os.unlink(dmg_path)
            if os.path.exists(smb_path):
                os.unlink(smb_path)

    def test_export_preserves_vertex_coordinates(self):
        """Test that vertex coordinates are preserved in SMB export."""
        from mesh_gui_project.core.scorec_exporter import SMBWriter

        # Specific coordinates to verify
        vertices = np.array([
            [1.5, 2.5],
            [3.7, 4.2],
            [5.1, 6.9]
        ])
        elements = np.array([[0, 1, 2]], dtype=np.int32)
        classification = {
            'vertex_class': {i: (2, 0) for i in range(3)},
            'edge_class': {i: (2, 0) for i in range(3)},  # Triangle generates 3 edges
            'triangle_class': {0: (2, 0)}
        }

        with tempfile.NamedTemporaryFile(suffix='.smb', delete=False) as f:
            temp_path = f.name

        try:
            writer = SMBWriter()
            writer.write_smb(vertices, elements, classification, temp_path)

            # Read back coordinates from binary file
            with open(temp_path, 'rb') as f:
                # Skip header: 4 uint32s = 16 bytes
                f.read(16)

                # Read entity counts (big-endian)
                counts = struct.unpack('>8I', f.read(32))
                num_verts = counts[0]
                num_edges = counts[1]
                num_tris = counts[2]

                # Skip edge connectivity: num_edges * 2 vertices * 4 bytes
                f.read(num_edges * 2 * 4)

                # Skip triangle connectivity: num_tris * 3 edges * 4 bytes
                f.read(num_tris * 3 * 4)

                # Read coordinates: 3 vertices * 3 doubles * 8 bytes = 72 bytes (big-endian)
                for i in range(3):
                    x = struct.unpack('>d', f.read(8))[0]
                    y = struct.unpack('>d', f.read(8))[0]
                    z = struct.unpack('>d', f.read(8))[0]

                    # Verify coordinates match (with floating point tolerance)
                    assert abs(x - vertices[i, 0]) < 1e-10
                    assert abs(y - vertices[i, 1]) < 1e-10
                    assert abs(z - 0.0) < 1e-10  # Should be at z=0

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_validates_input_shapes(self):
        """Test that export functions validate input array shapes."""
        from mesh_gui_project.core.exporter import export_mesh_to_scorec

        # Invalid vertices shape (3D instead of 2D)
        bad_vertices = np.array([[0, 0, 0], [1, 1, 1]])
        elements = np.array([[0, 1, 2]], dtype=np.int32)

        with pytest.raises(ValueError, match="vertices must have shape"):
            export_mesh_to_scorec(bad_vertices, elements, "test.dmg", "test.smb")

        # Invalid elements shape (quads instead of triangles)
        vertices = np.array([[0, 0], [1, 0]])
        bad_elements = np.array([[0, 1, 2, 3]], dtype=np.int32)

        with pytest.raises(ValueError, match="elements must have shape"):
            export_mesh_to_scorec(vertices, bad_elements, "test.dmg", "test.smb")
