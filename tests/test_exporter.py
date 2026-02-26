"""Test mesh export functionality for .msh and .vtk formats."""
import numpy as np
import pytest
import os
import tempfile


def test_exporter_module_exists():
    """Test that exporter module can be imported."""
    from mesh_gui_project.core import exporter

    assert hasattr(exporter, 'export_mesh_to_msh'), \
        "exporter module should have export_mesh_to_msh function"
    assert hasattr(exporter, 'export_mesh_to_vtk'), \
        "exporter module should have export_mesh_to_vtk function"


def test_export_mesh_to_msh_function_exists():
    """Test that export_mesh_to_msh function exists."""
    from mesh_gui_project.core.exporter import export_mesh_to_msh

    assert callable(export_mesh_to_msh), "export_mesh_to_msh should be callable"


def test_export_mesh_to_vtk_function_exists():
    """Test that export_mesh_to_vtk function exists."""
    from mesh_gui_project.core.exporter import export_mesh_to_vtk

    assert callable(export_mesh_to_vtk), "export_mesh_to_vtk should be callable"


def test_export_mesh_to_msh_creates_file():
    """Test that export_mesh_to_msh creates a .msh file."""
    from mesh_gui_project.core.exporter import export_mesh_to_msh

    # Create simple mesh
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ])

    elements = np.array([
        [0, 1, 2],
        [1, 3, 2],
    ], dtype=np.int32)

    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.msh', delete=False) as f:
        temp_path = f.name

    try:
        export_mesh_to_msh(vertices, elements, temp_path)

        # File should exist
        assert os.path.exists(temp_path), f"File {temp_path} should be created"
        assert os.path.getsize(temp_path) > 0, "File should not be empty"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_mesh_to_vtk_creates_file():
    """Test that export_mesh_to_vtk creates a .vtk file."""
    from mesh_gui_project.core.exporter import export_mesh_to_vtk

    # Create simple mesh
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ])

    elements = np.array([
        [0, 1, 2],
        [1, 3, 2],
    ], dtype=np.int32)

    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as f:
        temp_path = f.name

    try:
        export_mesh_to_vtk(vertices, elements, temp_path)

        # File should exist
        assert os.path.exists(temp_path), f"File {temp_path} should be created"
        assert os.path.getsize(temp_path) > 0, "File should not be empty"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_mesh_to_msh_with_metadata():
    """Test exporting mesh with optional metadata."""
    from mesh_gui_project.core.exporter import export_mesh_to_msh

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ])

    elements = np.array([[0, 1, 2]], dtype=np.int32)

    # Metadata: psi_N values at vertices
    metadata = {
        'node_data': {
            'psi_N': np.array([0.0, 0.5, 1.0])
        }
    }

    with tempfile.NamedTemporaryFile(suffix='.msh', delete=False) as f:
        temp_path = f.name

    try:
        export_mesh_to_msh(vertices, elements, temp_path, metadata=metadata)

        assert os.path.exists(temp_path), "File should be created with metadata"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_mesh_to_vtk_with_metadata():
    """Test exporting VTK mesh with optional metadata."""
    from mesh_gui_project.core.exporter import export_mesh_to_vtk

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ])

    elements = np.array([[0, 1, 2]], dtype=np.int32)

    # Metadata: psi_N values at vertices
    metadata = {
        'node_data': {
            'psi_N': np.array([0.0, 0.5, 1.0])
        }
    }

    with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as f:
        temp_path = f.name

    try:
        export_mesh_to_vtk(vertices, elements, temp_path, metadata=metadata)

        assert os.path.exists(temp_path), "File should be created with metadata"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_mesh_validates_input():
    """Test that export functions validate input."""
    from mesh_gui_project.core.exporter import export_mesh_to_msh, export_mesh_to_vtk

    # Invalid vertices (wrong shape)
    invalid_vertices = np.array([0.0, 1.0, 2.0])
    elements = np.array([[0, 1, 2]], dtype=np.int32)

    with tempfile.NamedTemporaryFile(suffix='.msh', delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(ValueError):
            export_mesh_to_msh(invalid_vertices, elements, temp_path)

        with pytest.raises(ValueError):
            export_mesh_to_vtk(invalid_vertices, elements, temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_mesh_logs_counts():
    """Test that export functions log vertex and element counts."""
    from mesh_gui_project.core.exporter import export_mesh_to_msh
    import logging

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ])

    elements = np.array([
        [0, 1, 2],
        [1, 3, 2],
    ], dtype=np.int32)

    with tempfile.NamedTemporaryFile(suffix='.msh', delete=False) as f:
        temp_path = f.name

    # Capture log messages
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, 'test.log')
        handler = logging.FileHandler(log_file)
        logger = logging.getLogger('mesh_gui_project.core.exporter')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            export_mesh_to_msh(vertices, elements, temp_path)

            # Check log file contains count information
            handler.flush()
            with open(log_file, 'r') as f:
                log_content = f.read()

            # Log should mention vertices and elements counts
            assert '4' in log_content or 'vertices' in log_content.lower(), \
                "Log should mention vertex count"
        finally:
            logger.removeHandler(handler)
            handler.close()
            if os.path.exists(temp_path):
                os.remove(temp_path)


def test_export_mesh_roundtrip_msh():
    """Test that exported .msh file can be read back."""
    from mesh_gui_project.core.exporter import export_mesh_to_msh

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, 1.0],
    ])

    elements = np.array([[0, 1, 2]], dtype=np.int32)

    with tempfile.NamedTemporaryFile(suffix='.msh', delete=False) as f:
        temp_path = f.name

    try:
        export_mesh_to_msh(vertices, elements, temp_path)

        # Try to read it back with meshio
        import meshio
        mesh = meshio.read(temp_path)

        # Check vertices count
        assert len(mesh.points) == 3, "Should have 3 vertices"

        # Check elements count (triangles)
        assert 'triangle' in mesh.cells_dict, "Should have triangle cells"
        assert len(mesh.cells_dict['triangle']) == 1, "Should have 1 triangle"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_mesh_roundtrip_vtk():
    """Test that exported .vtk file can be read back."""
    from mesh_gui_project.core.exporter import export_mesh_to_vtk

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, 1.0],
    ])

    elements = np.array([[0, 1, 2]], dtype=np.int32)

    with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as f:
        temp_path = f.name

    try:
        export_mesh_to_vtk(vertices, elements, temp_path)

        # Try to read it back with meshio
        import meshio
        mesh = meshio.read(temp_path)

        # Check vertices count
        assert len(mesh.points) == 3, "Should have 3 vertices"

        # Check elements count (triangles)
        assert 'triangle' in mesh.cells_dict, "Should have triangle cells"
        assert len(mesh.cells_dict['triangle']) == 1, "Should have 1 triangle"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
