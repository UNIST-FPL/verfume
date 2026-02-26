"""
New mesh generation with contour constraints using Gmsh.

Generates triangular meshes with vertices constrained to PSI contours,
supporting both field-line-traced vertices and user-adjustable meshes.
"""
import numpy as np
from typing import List, Tuple, Optional, Dict
from mesh_gui_project.core.mesh_quality import MeshQualityAnalyzer

try:
    import gmsh
except ImportError:
    gmsh = None


class ContourMesher:
    """
    Generate meshes with vertices constrained to contours.

    Uses Gmsh Python API for constrained Delaunay triangulation.
    """

    def __init__(self):
        """Initialize the contour mesher."""
        self.mesh_data = None

    def generate_mesh(
        self,
        boundary: np.ndarray,
        interior_contours: Optional[List[np.ndarray]] = None,
        target_element_size: float = 0.05
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate mesh from boundary and interior contours.

        Args:
            boundary: (N, 2) array of boundary vertices (R, Z)
            interior_contours: List of interior contour polylines
            target_element_size: Target mesh element size

        Returns:
            Tuple (vertices, elements):
            - vertices: np.ndarray (N, 2) - (R, Z) coordinates
            - elements: np.ndarray (E, 3) - triangle vertex indices
        """
        if gmsh is None:
            raise ImportError("Gmsh is required for mesh generation")

        # Initialize Gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)  # Suppress output
        gmsh.option.setNumber("General.Verbosity", 1)  # Minimal verbosity
        gmsh.model.add("contour_mesh")

        try:
            # Check if boundary is closed (first point == last point)
            # If so, skip the last point to avoid zero-length line segment
            if len(boundary) > 1 and np.allclose(boundary[0], boundary[-1], atol=1e-10):
                boundary_points = boundary[:-1]
            else:
                boundary_points = boundary

            # Add boundary points
            # NOTE: Do NOT set mesh size per-point as it can cause over-refinement
            # We'll set global mesh size constraints later
            boundary_tags = []
            for i, (R, Z) in enumerate(boundary_points):
                tag = gmsh.model.geo.addPoint(R, Z, 0.0)
                boundary_tags.append(tag)

            # Create boundary curve
            boundary_lines = []
            for i in range(len(boundary_tags)):
                i_next = (i + 1) % len(boundary_tags)
                line = gmsh.model.geo.addLine(boundary_tags[i], boundary_tags[i_next])
                boundary_lines.append(line)

            # Create curve loop and surface
            boundary_loop = gmsh.model.geo.addCurveLoop(boundary_lines)
            surface = gmsh.model.geo.addPlaneSurface([boundary_loop])

            # Add interior contours if provided
            all_contour_lines = []  # Collect all contour lines to embed after synchronize
            if interior_contours:
                for contour in interior_contours:
                    contour_tags = []
                    for R, Z in contour:
                        # NOTE: Do NOT set mesh size per-point
                        tag = gmsh.model.geo.addPoint(R, Z, 0.0)
                        contour_tags.append(tag)

                    # Create embedded curve
                    contour_lines = []
                    for i in range(len(contour_tags) - 1):
                        line = gmsh.model.geo.addLine(contour_tags[i], contour_tags[i+1])
                        contour_lines.append(line)
                        all_contour_lines.append(line)

            # Synchronize ONCE before embedding
            gmsh.model.geo.synchronize()

            # Embed all contour lines after synchronization
            if all_contour_lines:
                for line in all_contour_lines:
                    gmsh.model.mesh.embed(1, [line], 2, surface)

            # Set mesh size constraints
            gmsh.option.setNumber("Mesh.CharacteristicLengthMin", target_element_size * 0.5)
            gmsh.option.setNumber("Mesh.CharacteristicLengthMax", target_element_size * 2.0)

            # Generate 2D mesh
            gmsh.model.mesh.generate(2)

            # Extract mesh
            node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
            elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(2)

            # Process nodes
            vertices = np.array(node_coords).reshape(-1, 3)[:, :2]  # (R, Z) only

            # Create node tag mapping
            node_map = {tag: i for i, tag in enumerate(node_tags)}

            # Process elements (triangles)
            elements = []
            for elem_type, tags, nodes in zip(elem_types, elem_tags, elem_node_tags):
                if elem_type == 2:  # Triangle
                    nodes_array = np.array(nodes).reshape(-1, 3)
                    for tri_nodes in nodes_array:
                        # Map to vertex indices
                        tri = [node_map[int(n)] for n in tri_nodes]
                        elements.append(tri)

            elements = np.array(elements, dtype=np.int32)

            # Remove duplicate vertices and update element connectivity
            vertices, elements = self._remove_duplicate_vertices(vertices, elements)

            # Remove degenerate triangles (zero area or duplicate vertices in triangle)
            elements = self._remove_degenerate_triangles(vertices, elements)

            self.mesh_data = {
                'vertices': vertices,
                'elements': elements
            }

            return vertices, elements

        finally:
            gmsh.finalize()

    def _remove_duplicate_vertices(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        tolerance: float = 1e-10
    ) -> tuple:
        """
        Remove duplicate vertices and update element connectivity.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
            tolerance: Distance threshold for considering vertices duplicates

        Returns:
            Tuple of (unique_vertices, updated_elements)
        """
        # Find unique vertices
        unique_vertices, inverse_indices = np.unique(
            np.round(vertices / tolerance) * tolerance,
            axis=0,
            return_inverse=True
        )

        # Update element connectivity to use unique vertex indices
        updated_elements = inverse_indices[elements]

        return unique_vertices, updated_elements

    def _remove_degenerate_triangles(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        area_tolerance: float = 1e-10
    ) -> np.ndarray:
        """
        Remove degenerate triangles (zero area or repeated vertices).

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
            area_tolerance: Minimum triangle area threshold

        Returns:
            Filtered elements array without degenerate triangles
        """
        valid_triangles = []

        for tri in elements:
            # Check for repeated vertex indices
            if len(set(tri)) < 3:
                continue  # Skip triangle with repeated vertices

            # Check triangle area
            v0, v1, v2 = vertices[tri]
            # Area using cross product
            e0 = v1 - v0
            e2 = v0 - v2
            area = 0.5 * abs(e0[0] * (-e2[1]) - e0[1] * (-e2[0]))

            if area > area_tolerance:
                valid_triangles.append(tri)

        return np.array(valid_triangles, dtype=np.int32)

    def compute_quality_metrics(
        self,
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Compute mesh quality metrics.

        Delegates to MeshQualityAnalyzer for centralized quality computation.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity

        Returns:
            Dictionary with quality metrics:
            - aspect_ratios: (E,) aspect ratio for each triangle
            - min_angles: (E,) minimum angle in degrees
            - areas: (E,) triangle areas
        """
        return MeshQualityAnalyzer.compute_all_metrics(vertices, elements)
