"""
Mesh export functionality for .msh and .vtk formats.

This module provides functions to export triangular meshes to Gmsh (.msh)
and VTK (.vtk) formats using meshio.
"""
import numpy as np
from typing import Optional, Dict, Any
import logging

try:
    import meshio
except ImportError:
    meshio = None

logger = logging.getLogger(__name__)


def export_mesh_to_msh(
    vertices: np.ndarray,
    elements: np.ndarray,
    path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Export mesh to Gmsh .msh format.

    Args:
        vertices: np.ndarray shape (N, 2) - (R, Z) vertex coordinates
        elements: np.ndarray shape (E, 3) - triangle vertex indices
        path: Output file path (should end with .msh)
        metadata: Optional dictionary with mesh metadata
                  Format: {'node_data': {'field_name': np.ndarray}, ...}

    Raises:
        RuntimeError: If meshio is not installed
        ValueError: If input arrays have invalid shapes
    """
    if meshio is None:
        raise RuntimeError("meshio is not installed. Install with: pip install meshio")

    # Validate input
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        raise ValueError(f"vertices must have shape (N, 2), got {vertices.shape}")

    if elements.ndim != 2 or elements.shape[1] != 3:
        raise ValueError(f"elements must have shape (E, 3), got {elements.shape}")

    n_vertices = len(vertices)
    n_elements = len(elements)

    logger.info(f"Exporting mesh to {path}: {n_vertices} vertices, {n_elements} triangles")

    # Convert 2D vertices to 3D (add z=0)
    vertices_3d = np.column_stack([vertices, np.zeros(n_vertices)])

    # Create meshio mesh object
    cells = [("triangle", elements)]

    # Prepare point and cell data
    point_data = {}
    cell_data = {}

    if metadata is not None:
        if 'node_data' in metadata:
            point_data = metadata['node_data']
        if 'cell_data' in metadata:
            cell_data = metadata['cell_data']

    mesh = meshio.Mesh(
        points=vertices_3d,
        cells=cells,
        point_data=point_data,
        cell_data=cell_data
    )

    # Write to file
    mesh.write(path)

    logger.info(f"Successfully exported mesh to {path}")


def export_mesh_to_vtk(
    vertices: np.ndarray,
    elements: np.ndarray,
    path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Export mesh to VTK UnstructuredGrid format.

    Args:
        vertices: np.ndarray shape (N, 2) - (R, Z) vertex coordinates
        elements: np.ndarray shape (E, 3) - triangle vertex indices
        path: Output file path (should end with .vtk or .vtu)
        metadata: Optional dictionary with mesh metadata
                  Format: {'node_data': {'field_name': np.ndarray}, ...}

    Raises:
        RuntimeError: If meshio is not installed
        ValueError: If input arrays have invalid shapes
    """
    if meshio is None:
        raise RuntimeError("meshio is not installed. Install with: pip install meshio")

    # Validate input
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        raise ValueError(f"vertices must have shape (N, 2), got {vertices.shape}")

    if elements.ndim != 2 or elements.shape[1] != 3:
        raise ValueError(f"elements must have shape (E, 3), got {elements.shape}")

    n_vertices = len(vertices)
    n_elements = len(elements)

    logger.info(f"Exporting mesh to {path}: {n_vertices} vertices, {n_elements} triangles")

    # Convert 2D vertices to 3D (add z=0)
    vertices_3d = np.column_stack([vertices, np.zeros(n_vertices)])

    # Create meshio mesh object
    cells = [("triangle", elements)]

    # Prepare point and cell data
    point_data = {}
    cell_data = {}

    if metadata is not None:
        if 'node_data' in metadata:
            point_data = metadata['node_data']
        if 'cell_data' in metadata:
            cell_data = metadata['cell_data']

    mesh = meshio.Mesh(
        points=vertices_3d,
        cells=cells,
        point_data=point_data,
        cell_data=cell_data
    )

    # Write to file
    mesh.write(path)

    logger.info(f"Successfully exported mesh to {path}")


def export_mesh_to_scorec(
    vertices: np.ndarray,
    elements: np.ndarray,
    path_dmg: str,
    path_smb: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Export mesh to SCOREC .dmg (model) and .smb (mesh) formats.

    Args:
        vertices: np.ndarray shape (N, 2) - (R, Z) vertex coordinates
        elements: np.ndarray shape (E, 3) - triangle vertex indices
        path_dmg: Output .dmg file path
        path_smb: Output .smb file path
        metadata: Optional mesh metadata (currently unused)

    Raises:
        ValueError: If input arrays have invalid shapes
    """
    # Validate input
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        raise ValueError(f"vertices must have shape (N, 2), got {vertices.shape}")

    if elements.ndim != 2 or elements.shape[1] != 3:
        raise ValueError(f"elements must have shape (E, 3), got {elements.shape}")

    from mesh_gui_project.core.scorec_exporter import (
        BoundaryExtractor, DMGWriter, SMBWriter
    )

    # Extract geometric model from mesh
    extractor = BoundaryExtractor()
    model_entities, classification = extractor.extract_model(vertices, elements)

    # Write .dmg file
    dmg_writer = DMGWriter()
    dmg_writer.write_dmg(model_entities, path_dmg)

    # Write .smb file
    smb_writer = SMBWriter()
    smb_writer.write_smb(vertices, elements, classification, path_smb)

    logger.info(f"Successfully exported SCOREC files: {path_dmg}, {path_smb}")


def export_mesh_to_dmg(
    vertices: np.ndarray,
    elements: np.ndarray,
    path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Export mesh to SCOREC .dmg geometric model format only.

    Args:
        vertices: np.ndarray shape (N, 2) - (R, Z) vertex coordinates
        elements: np.ndarray shape (E, 3) - triangle vertex indices
        path: Output file path (should end with .dmg)
        metadata: Optional mesh metadata (currently unused)

    Raises:
        ValueError: If input arrays have invalid shapes
    """
    # Validate input
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        raise ValueError(f"vertices must have shape (N, 2), got {vertices.shape}")

    if elements.ndim != 2 or elements.shape[1] != 3:
        raise ValueError(f"elements must have shape (E, 3), got {elements.shape}")

    from mesh_gui_project.core.scorec_exporter import BoundaryExtractor, DMGWriter

    # Extract geometric model from mesh
    extractor = BoundaryExtractor()
    model_entities, _ = extractor.extract_model(vertices, elements)

    # Write .dmg file
    dmg_writer = DMGWriter()
    dmg_writer.write_dmg(model_entities, path)

    logger.info(f"Successfully exported mesh to {path}")


def export_mesh_to_smb(
    vertices: np.ndarray,
    elements: np.ndarray,
    path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Export mesh to SCOREC .smb mesh format only.

    Args:
        vertices: np.ndarray shape (N, 2) - (R, Z) vertex coordinates
        elements: np.ndarray shape (E, 3) - triangle vertex indices
        path: Output file path (should end with .smb)
        metadata: Optional mesh metadata (currently unused)

    Raises:
        ValueError: If input arrays have invalid shapes
    """
    # Validate input
    if vertices.ndim != 2 or vertices.shape[1] != 2:
        raise ValueError(f"vertices must have shape (N, 2), got {vertices.shape}")

    if elements.ndim != 2 or elements.shape[1] != 3:
        raise ValueError(f"elements must have shape (E, 3), got {elements.shape}")

    from mesh_gui_project.core.scorec_exporter import BoundaryExtractor, SMBWriter

    # Extract geometric model from mesh
    extractor = BoundaryExtractor()
    _, classification = extractor.extract_model(vertices, elements)

    # Write .smb file
    smb_writer = SMBWriter()
    smb_writer.write_smb(vertices, elements, classification, path)

    logger.info(f"Successfully exported mesh to {path}")
