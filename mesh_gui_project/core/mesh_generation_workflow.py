"""
MeshGenerationWorkflow: Coordinates mesh generation from boundary to optimization.

Extracted from MainWindow to separate mesh generation workflow logic.
This class handles:
- Mesh generation from PSI contours or limiter boundaries
- Boundary vertex identification
- Mesh quality computation
- Remeshing and optimization with constraints
"""
import numpy as np
from typing import Dict, Optional, Set, Tuple, Any


class MeshGenerationWorkflow:
    """
    Coordinates mesh generation from boundary selection to optimization.

    This class extracts complex mesh generation workflow logic from MainWindow,
    providing a clean API for mesh generation operations.
    """

    def __init__(self):
        """Initialize MeshGenerationWorkflow."""
        pass

    def generate_mesh_from_psi(
        self,
        equilibrium,
        psi_value: float,
        target_element_size: float
    ) -> Dict[str, Any]:
        """
        Generate mesh from PSI boundary contour.

        Steps:
        1. Extract boundary contour at specified PSI value
        2. Generate vertices via triangulation
        3. Identify boundary vertices
        4. Compute quality metrics

        Args:
            equilibrium: EquilibriumData object with PSI grid
            psi_value: PSI value for boundary contour
            target_element_size: Target size for mesh elements

        Returns:
            Dictionary with keys:
                - vertices: (N, 2) array of vertex coordinates
                - elements: (M, 3) array of triangle connectivity
                - boundary: (K, 2) array of boundary points
                - boundary_vertex_indices: Set of vertex indices on boundary
                - metrics: Dictionary of quality metrics

        Raises:
            ValueError: If equilibrium is None or target_element_size <= 0
        """
        # Validate inputs
        if equilibrium is None:
            raise ValueError("equilibrium is required")

        if target_element_size <= 0:
            raise ValueError("element_size must be positive")

        # Import required modules
        from mesh_gui_project.core.mesh_boundary_selector import MeshBoundarySelector
        from mesh_gui_project.core.new_mesher import ContourMesher

        # Step 1: Extract boundary contour
        boundary_selector = MeshBoundarySelector(equilibrium)
        boundary = boundary_selector.get_boundary_from_psi(psi_value)

        # Step 2: Generate mesh
        mesher = ContourMesher()
        vertices, elements = mesher.generate_mesh(
            boundary,
            target_element_size=target_element_size
        )

        # Step 3: Identify boundary vertices
        boundary_vertex_indices = self.identify_boundary_vertices(vertices, boundary)

        # Step 4: Compute quality metrics
        metrics = self.compute_mesh_quality(vertices, elements)

        return {
            'vertices': vertices,
            'elements': elements,
            'boundary': boundary,
            'boundary_vertex_indices': boundary_vertex_indices,
            'metrics': metrics
        }

    def generate_mesh_from_limiter(
        self,
        equilibrium,
        target_element_size: float
    ) -> Dict[str, Any]:
        """
        Generate mesh using limiter as boundary.

        Args:
            equilibrium: EquilibriumData object with limiter_curve
            target_element_size: Target size for mesh elements

        Returns:
            Dictionary with mesh data (same format as generate_mesh_from_psi)

        Raises:
            ValueError: If equilibrium is None or target_element_size <= 0
        """
        # Validate inputs
        if equilibrium is None:
            raise ValueError("equilibrium is required")

        if target_element_size <= 0:
            raise ValueError("element_size must be positive")

        # Import required modules
        from mesh_gui_project.core.new_mesher import ContourMesher

        # Use limiter as boundary
        boundary = equilibrium.limiter_curve

        # Generate mesh
        mesher = ContourMesher()
        vertices, elements = mesher.generate_mesh(
            boundary,
            target_element_size=target_element_size
        )

        # Identify boundary vertices
        boundary_vertex_indices = self.identify_boundary_vertices(vertices, boundary)

        # Compute quality metrics
        metrics = self.compute_mesh_quality(vertices, elements)

        return {
            'vertices': vertices,
            'elements': elements,
            'boundary': boundary,
            'boundary_vertex_indices': boundary_vertex_indices,
            'metrics': metrics
        }

    def identify_boundary_vertices(
        self,
        vertices: np.ndarray,
        boundary: np.ndarray,
        tolerance: float = 0.001
    ) -> Set[int]:
        """
        Identify which vertices lie on the boundary.

        Checks if each vertex is close to ANY point on the boundary contour.
        Also checks if vertex lies on any boundary edge (between consecutive points).

        Args:
            vertices: (N, 2) array of all mesh vertices
            boundary: (M, 2) array of boundary points
            tolerance: Distance tolerance for matching (default: 0.001 = 1mm)

        Returns:
            Set of vertex indices that are on the boundary
        """
        boundary_indices = set()

        # For each mesh vertex
        for i, vertex in enumerate(vertices):
            # Check distance to boundary points
            for boundary_point in boundary:
                dist = np.linalg.norm(vertex - boundary_point)
                if dist < tolerance:
                    boundary_indices.add(i)
                    break

            if i in boundary_indices:
                continue

            # Also check distance to boundary edges (lines between consecutive points)
            for j in range(len(boundary)):
                p1 = boundary[j]
                p2 = boundary[(j + 1) % len(boundary)]

                # Calculate distance from vertex to line segment p1-p2
                edge = p2 - p1
                edge_length = np.linalg.norm(edge)
                if edge_length < 1e-10:
                    continue

                # Project vertex onto line
                t = np.dot(vertex - p1, edge) / (edge_length ** 2)
                t = np.clip(t, 0, 1)  # Clamp to segment
                projection = p1 + t * edge

                dist = np.linalg.norm(vertex - projection)
                if dist < tolerance:
                    boundary_indices.add(i)
                    break

        return boundary_indices

    def remesh_and_optimize(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        constrained_vertices: Optional[Set[int]] = None,
        n_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Remesh and optimize existing mesh.

        Steps:
        1. Validate constraints
        2. Apply optimization (smoothing, edge flipping)
        3. Preserve constrained vertices
        4. Compute quality metrics

        Args:
            vertices: (N, 2) array of current mesh vertices
            elements: (M, 3) array of current mesh elements
            constrained_vertices: Set of vertex indices that should not move
            n_iterations: Number of optimization iterations

        Returns:
            Dictionary with optimized mesh data
        """
        from mesh_gui_project.core.mesh_optimizer import MeshOptimizer

        # Create optimizer
        optimizer = MeshOptimizer()

        # Set constrained vertices
        if constrained_vertices:
            optimizer.set_constrained_vertices(constrained_vertices)

        # Optimize mesh
        optimized_vertices, optimized_elements = optimizer.optimize(
            vertices,
            elements,
            n_iterations=n_iterations
        )

        # Compute quality metrics
        metrics = self.compute_mesh_quality(optimized_vertices, optimized_elements)

        return {
            'vertices': optimized_vertices,
            'elements': optimized_elements,
            'metrics': metrics
        }

    def compute_mesh_quality(
        self,
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Compute quality metrics for mesh.

        Args:
            vertices: (N, 2) array of vertex coordinates
            elements: (M, 3) array of triangle connectivity

        Returns:
            Dictionary with quality metrics:
                - aspect_ratios: Array of aspect ratios
                - min_angles: Array of minimum angles (degrees)
                - areas: Array of triangle areas
        """
        from mesh_gui_project.core.new_mesher import ContourMesher

        mesher = ContourMesher()
        metrics = mesher.compute_quality_metrics(vertices, elements)

        return metrics

    def estimate_triangle_count(
        self,
        boundary: np.ndarray,
        target_element_size: float
    ) -> int:
        """
        Estimate number of triangles for given mesh size.

        Calculates approximate area of boundary and divides by
        expected triangle area.

        Args:
            boundary: (N, 2) array of boundary points
            target_element_size: Target size for mesh elements

        Returns:
            Estimated number of triangles
        """
        # Calculate area using shoelace formula
        area = 0
        for i in range(len(boundary)):
            j = (i + 1) % len(boundary)
            area += boundary[i, 0] * boundary[j, 1]
            area -= boundary[j, 0] * boundary[i, 1]
        area = abs(area) / 2

        # Estimate triangle area (equilateral triangle)
        triangle_area = (target_element_size ** 2) * np.sqrt(3) / 4

        # Estimate number of triangles
        if triangle_area > 0:
            estimated_triangles = int(area / triangle_area)
        else:
            estimated_triangles = int(1e10)

        return estimated_triangles

    def validate_mesh_size(
        self,
        boundary: np.ndarray,
        target_element_size: float,
        max_triangles: int = 50000
    ) -> Dict[str, Any]:
        """
        Validate mesh size and warn if too fine.

        Args:
            boundary: (N, 2) array of boundary points
            target_element_size: Target size for mesh elements
            max_triangles: Maximum acceptable triangle count

        Returns:
            Dictionary with validation results:
                - warning: True if mesh will be too large
                - estimated_triangles: Estimated triangle count
                - recommended_size: Recommended mesh size (if warning)
        """
        # Estimate triangle count
        estimated_triangles = self.estimate_triangle_count(boundary, target_element_size)

        # Check if too large
        warning = estimated_triangles > max_triangles

        # Calculate recommended size if warning
        recommended_size = None
        if warning:
            # Calculate area
            area = 0
            for i in range(len(boundary)):
                j = (i + 1) % len(boundary)
                area += boundary[i, 0] * boundary[j, 1]
                area -= boundary[j, 0] * boundary[i, 1]
            area = abs(area) / 2

            # Recommended size for max_triangles triangles
            recommended_size = np.sqrt(area / max_triangles * 4 / np.sqrt(3))

        return {
            'warning': warning,
            'estimated_triangles': estimated_triangles,
            'recommended_size': recommended_size
        }
