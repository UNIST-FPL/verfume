"""
Interactive mesh editor for vertex manipulation.

Provides tools for selecting, dragging, adding, and deleting mesh vertices.
"""
import numpy as np
from typing import Optional, List, Tuple, Set


class MeshEditor:
    """
    Interactive editor for mesh vertex manipulation.
    """

    def __init__(self, vertices: np.ndarray, elements: np.ndarray):
        """
        Initialize mesh editor.

        Args:
            vertices: (N, 2) array of vertex coordinates (R, Z)
            elements: (E, 3) array of triangle connectivity
        """
        self.vertices = vertices.copy()
        self.elements = elements.copy()
        self.selected_vertices = set()
        self.contour_constraints = {}  # Maps vertex index -> contour polyline
        self.manually_moved_vertices = set()  # Track vertices that user has manually moved

    def select_vertex(self, R_click: float, Z_click: float, threshold: float = 0.05) -> Optional[int]:
        """
        Select vertex nearest to click location.

        Args:
            R_click: R coordinate of click
            Z_click: Z coordinate of click
            threshold: Maximum distance for selection

        Returns:
            Index of selected vertex, or None
        """
        click_point = np.array([R_click, Z_click])
        distances = np.linalg.norm(self.vertices - click_point, axis=1)

        min_idx = np.argmin(distances)
        if distances[min_idx] < threshold:
            self.selected_vertices = {min_idx}
            return min_idx

        return None

    def select_vertices_in_rectangle(
        self,
        R_min: float, R_max: float,
        Z_min: float, Z_max: float
    ) -> Set[int]:
        """
        Select all vertices within rectangle.

        Args:
            R_min, R_max: R coordinate range
            Z_min, Z_max: Z coordinate range

        Returns:
            Set of selected vertex indices
        """
        mask = (
            (self.vertices[:, 0] >= R_min) &
            (self.vertices[:, 0] <= R_max) &
            (self.vertices[:, 1] >= Z_min) &
            (self.vertices[:, 1] <= Z_max)
        )

        selected = set(np.where(mask)[0])
        self.selected_vertices = selected
        return selected

    def move_vertex(self, vertex_idx: int, R_new: float, Z_new: float):
        """
        Move vertex to new position (respecting constraints).

        Args:
            vertex_idx: Index of vertex to move
            R_new: New R coordinate
            Z_new: New Z coordinate
        """
        # Mark this vertex as manually moved
        self.manually_moved_vertices.add(vertex_idx)

        if vertex_idx in self.contour_constraints:
            # Vertex is constrained to contour - project to nearest point on contour
            contour = self.contour_constraints[vertex_idx]
            new_point = np.array([R_new, Z_new])

            # Find nearest point on contour (checking both points and edges)
            min_dist = float('inf')
            nearest_point = contour[0]

            # Check distance to each contour edge (line segment)
            for i in range(len(contour)):
                p1 = contour[i]
                p2 = contour[(i + 1) % len(contour)]

                # Project new_point onto edge p1-p2
                edge = p2 - p1
                edge_length_sq = np.dot(edge, edge)

                if edge_length_sq < 1e-10:
                    # Degenerate edge, just use p1
                    projected = p1
                else:
                    # Project onto line, then clamp to segment
                    t = np.dot(new_point - p1, edge) / edge_length_sq
                    t = np.clip(t, 0, 1)  # Clamp to [0, 1] to stay on segment
                    projected = p1 + t * edge

                dist = np.linalg.norm(new_point - projected)
                if dist < min_dist:
                    min_dist = dist
                    nearest_point = projected

            self.vertices[vertex_idx] = nearest_point
        else:
            # Free vertex - move directly
            self.vertices[vertex_idx] = [R_new, Z_new]

    def move_selected_vertices(self, dR: float, dZ: float):
        """
        Move all selected vertices by offset.

        Args:
            dR: R offset
            dZ: Z offset
        """
        for idx in self.selected_vertices:
            current = self.vertices[idx]
            self.move_vertex(idx, current[0] + dR, current[1] + dZ)

    def delete_vertex(self, vertex_idx: int):
        """
        Delete vertex and update triangulation.

        Args:
            vertex_idx: Index of vertex to delete
        """
        # Remove triangles containing this vertex
        mask = ~np.any(self.elements == vertex_idx, axis=1)
        self.elements = self.elements[mask]

        # Note: This leaves a hole - would need retriangulation
        # For now, just mark as deleted
        self.vertices[vertex_idx] = np.array([np.nan, np.nan])

    def add_vertex_on_edge(
        self,
        elem_idx: int,
        edge_idx: int
    ) -> int:
        """
        Add vertex at midpoint of edge.

        Args:
            elem_idx: Triangle index
            edge_idx: Edge index (0, 1, or 2)

        Returns:
            Index of new vertex
        """
        tri = self.elements[elem_idx]

        # Get edge vertices
        v0_idx = tri[edge_idx]
        v1_idx = tri[(edge_idx + 1) % 3]

        v0 = self.vertices[v0_idx]
        v1 = self.vertices[v1_idx]

        # Midpoint
        midpoint = (v0 + v1) / 2.0

        # Add new vertex
        new_idx = len(self.vertices)
        self.vertices = np.vstack([self.vertices, midpoint])

        return new_idx

    def set_contour_constraint(self, vertex_idx: int, contour: np.ndarray):
        """
        Constrain vertex to move only along contour.

        Args:
            vertex_idx: Index of vertex
            contour: (M, 2) array of contour points
        """
        self.contour_constraints[vertex_idx] = contour

    def clear_selection(self):
        """Clear all selected vertices."""
        self.selected_vertices.clear()

    def get_mesh(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get current mesh state.

        Returns:
            Tuple (vertices, elements)
        """
        # Filter out deleted vertices (NaN)
        valid_mask = ~np.isnan(self.vertices[:, 0])
        valid_vertices = self.vertices[valid_mask]

        # Remap element indices
        idx_map = {old: new for new, old in enumerate(np.where(valid_mask)[0])}

        valid_elements = []
        for tri in self.elements:
            if all(v in idx_map for v in tri):
                valid_elements.append([idx_map[v] for v in tri])

        valid_elements = np.array(valid_elements, dtype=np.int32) if valid_elements else np.zeros((0, 3), dtype=np.int32)

        return valid_vertices, valid_elements
