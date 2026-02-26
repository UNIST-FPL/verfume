"""
SCOREC utility classes for topology extraction and entity classification.

This module provides classes to extract discrete geometric models from
triangular meshes for SCOREC PUMI export.
"""
import numpy as np
from typing import Dict, List, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class TopologyBuilder:
    """Build topological relationships from mesh connectivity."""

    def __init__(self):
        """Initialize TopologyBuilder."""
        pass

    def build_edge_to_triangles_map(
        self, elements: np.ndarray
    ) -> Dict[Tuple[int, int], List[int]]:
        """
        Build edge to triangles adjacency map.

        Args:
            elements: np.ndarray shape (E, 3) - triangle vertex indices

        Returns:
            Dictionary mapping edge (v1, v2) tuple to list of triangle indices
        """
        edge_to_triangles = {}

        for tri_idx, triangle in enumerate(elements):
            # Each triangle has 3 edges
            edges = [
                tuple(sorted([triangle[0], triangle[1]])),
                tuple(sorted([triangle[1], triangle[2]])),
                tuple(sorted([triangle[2], triangle[0]]))
            ]

            for edge in edges:
                if edge not in edge_to_triangles:
                    edge_to_triangles[edge] = []
                edge_to_triangles[edge].append(tri_idx)

        return edge_to_triangles

    def find_boundary_edges(
        self, edge_to_triangles: Dict[Tuple[int, int], List[int]]
    ) -> Set[Tuple[int, int]]:
        """
        Find edges with exactly one adjacent triangle (boundary edges).

        Args:
            edge_to_triangles: Dictionary mapping edges to triangle indices

        Returns:
            Set of boundary edge tuples
        """
        boundary_edges = set()

        for edge, triangles in edge_to_triangles.items():
            if len(triangles) == 1:
                boundary_edges.add(edge)

        return boundary_edges

    def build_edge_chains(
        self,
        boundary_edges: Set[Tuple[int, int]],
        vertices: np.ndarray,
        angle_threshold: float = 30.0
    ) -> List[List[int]]:
        """
        Chain boundary edges between corner vertices.

        Corner vertices are identified by angle changes in the boundary.
        Edges are chained between consecutive corners to form model edges.

        Args:
            boundary_edges: Set of (v1, v2) boundary edge tuples
            vertices: Vertex coordinates
            angle_threshold: Angle change threshold in degrees for corner detection

        Returns:
            List of edge chains (vertex index sequences)
        """
        # Build adjacency list for boundary vertices
        boundary_graph = {}
        for v1, v2 in boundary_edges:
            if v1 not in boundary_graph:
                boundary_graph[v1] = []
            if v2 not in boundary_graph:
                boundary_graph[v2] = []
            boundary_graph[v1].append(v2)
            boundary_graph[v2].append(v1)

        # Find corner vertices
        corners = set()
        for vertex, neighbors in boundary_graph.items():
            if len(neighbors) != 2:
                # Junction or endpoint - always a corner
                corners.add(vertex)
                continue

            # Compute angle between edges
            v0, v2 = neighbors
            edge1 = vertices[v0] - vertices[vertex]
            edge2 = vertices[v2] - vertices[vertex]

            # Normalize
            edge1_norm = edge1 / np.linalg.norm(edge1)
            edge2_norm = edge2 / np.linalg.norm(edge2)

            # Angle
            cos_angle = np.dot(edge1_norm, edge2_norm)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle_deg = np.degrees(np.arccos(cos_angle))

            # Angle change from 180° (straight)
            angle_change = abs(180.0 - angle_deg)

            if angle_change > angle_threshold:
                corners.add(vertex)

        # Build chains between corners
        chains = []
        visited_edges = set()

        for corner in corners:
            for neighbor in boundary_graph[corner]:
                edge = tuple(sorted([corner, neighbor]))
                if edge in visited_edges:
                    continue

                # Walk from corner until next corner
                chain = [corner, neighbor]
                current = neighbor

                while current not in corners:
                    visited_edges.add(tuple(sorted([chain[-2], current])))

                    # Find next vertex
                    next_vertices = [v for v in boundary_graph[current]
                                   if v != chain[-2]]
                    if not next_vertices:
                        break

                    next_vertex = next_vertices[0]
                    chain.append(next_vertex)
                    current = next_vertex

                visited_edges.add(tuple(sorted([chain[-2], chain[-1]])))
                chains.append(chain)

        return chains


class EntityClassifier:
    """Classify mesh entities to geometric model entities."""

    def __init__(self):
        """Initialize EntityClassifier."""
        pass

    def classify_vertices(
        self,
        vertices: np.ndarray,
        boundary_edges: Set[Tuple[int, int]],
        edge_chains: List[List[int]],
        vertex_to_tag: Dict[int, int]
    ) -> Dict[int, Tuple[int, int]]:
        """
        Classify each vertex to a model entity.

        Args:
            vertices: Vertex coordinates
            boundary_edges: Set of boundary edge tuples
            edge_chains: List of edge chains (from build_edge_chains)
            vertex_to_tag: Mapping from mesh vertex index to model vertex tag

        Returns:
            Dictionary mapping vertex index to (model_dim, model_tag)
            - dim=0: model vertex (corner)
            - dim=1: model edge
            - dim=2: model face (interior)
        """
        vertex_class = {}

        # Find all boundary vertices
        boundary_vertices = set()
        for v1, v2 in boundary_edges:
            boundary_vertices.add(v1)
            boundary_vertices.add(v2)

        # Find corner vertices (chain endpoints)
        corner_vertices = set()
        for chain in edge_chains:
            corner_vertices.add(chain[0])
            corner_vertices.add(chain[-1])

        # Classify vertices
        for v_idx in range(len(vertices)):
            if v_idx in corner_vertices:
                # Corner vertex - model vertex (dim=0)
                # Use model tag from vertex_to_tag mapping, NOT mesh index!
                model_tag = vertex_to_tag[v_idx]
                vertex_class[v_idx] = (0, model_tag)
            elif v_idx in boundary_vertices:
                # Boundary vertex on edge - model edge (dim=1)
                # Find which chain this vertex belongs to
                chain_idx = 0
                for i, chain in enumerate(edge_chains):
                    if v_idx in chain:
                        chain_idx = i
                        break
                vertex_class[v_idx] = (1, chain_idx)
            else:
                # Interior vertex - model face (dim=2)
                vertex_class[v_idx] = (2, 0)

        return vertex_class
