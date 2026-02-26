"""
Mesh quality optimization algorithms.

Implements edge flipping and Laplacian smoothing for mesh improvement.
"""
import numpy as np
from typing import Tuple, Set


class MeshOptimizer:
    """
    Optimize mesh quality through edge flipping and smoothing.
    """

    def __init__(self):
        """Initialize optimizer."""
        self.constrained_vertices = set()

    def set_constrained_vertices(self, vertex_indices: Set[int]):
        """
        Set which vertices are constrained (e.g., on contours).

        Args:
            vertex_indices: Set of vertex indices that should not move
        """
        self.constrained_vertices = vertex_indices

    def optimize(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        n_iterations: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Optimize mesh quality.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
            n_iterations: Number of smoothing iterations

        Returns:
            Tuple (optimized_vertices, elements)
        """
        vertices_opt = vertices.copy()

        # Perform Laplacian smoothing
        for _ in range(n_iterations):
            vertices_opt = self.laplacian_smoothing(vertices_opt, elements)

        return vertices_opt, elements

    def laplacian_smoothing(
        self,
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> np.ndarray:
        """
        Apply one iteration of Laplacian smoothing.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity

        Returns:
            Smoothed vertices
        """
        n_vertices = len(vertices)
        vertices_new = vertices.copy()

        # Build vertex neighbors
        neighbors = [set() for _ in range(n_vertices)]
        for tri in elements:
            v0, v1, v2 = tri
            neighbors[v0].update([v1, v2])
            neighbors[v1].update([v0, v2])
            neighbors[v2].update([v0, v1])

        # Smooth each unconstrained vertex
        for i in range(n_vertices):
            if i in self.constrained_vertices:
                continue  # Skip constrained vertices

            if len(neighbors[i]) == 0:
                continue

            # Compute centroid of neighbors
            neighbor_coords = vertices[list(neighbors[i])]
            centroid = np.mean(neighbor_coords, axis=0)

            # Move vertex toward centroid
            vertices_new[i] = centroid

        return vertices_new

