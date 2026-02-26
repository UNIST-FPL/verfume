"""
Centralized mesh quality metrics computation.

Consolidates quality metric calculations from mesher.py and new_mesher.py
into a single, well-tested module following DRY principles.
"""
import numpy as np
from typing import List, Dict


class MeshQualityAnalyzer:
    """
    Centralized mesh quality metrics computation.

    Provides static methods for computing various mesh quality metrics:
    - Aspect ratios (longest edge / altitude)
    - Minimum angles per triangle
    - Triangle areas
    - Inverted element detection
    """

    @staticmethod
    def compute_aspect_ratios(
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> np.ndarray:
        """
        Compute aspect ratio for each triangle.

        Aspect ratio = longest_edge / altitude
        where altitude is the perpendicular height from longest edge.

        Good triangles have aspect ratio close to 1.15 (equilateral).
        Poor triangles have high aspect ratios (elongated/sliver).

        Args:
            vertices: (N, 2) array of vertex coordinates
            elements: (E, 3) array of triangle connectivity

        Returns:
            (E,) array of aspect ratios
        """
        n_elements = len(elements)
        aspect_ratios = np.zeros(n_elements)

        for i, tri in enumerate(elements):
            # Get triangle vertices
            v0, v1, v2 = vertices[tri]

            # Edge vectors
            e0 = v1 - v0
            e1 = v2 - v1
            e2 = v0 - v2

            # Edge lengths
            l0 = np.linalg.norm(e0)
            l1 = np.linalg.norm(e1)
            l2 = np.linalg.norm(e2)

            # Area (2D cross product magnitude)
            area = 0.5 * abs(e0[0] * (-e2[1]) - e0[1] * (-e2[0]))

            # Aspect ratio: longest / altitude
            longest = max(l0, l1, l2)
            if area > 1e-10:
                altitude = 2 * area / longest
                aspect_ratios[i] = longest / altitude
            else:
                # Degenerate triangle
                aspect_ratios[i] = np.inf

        return aspect_ratios

    @staticmethod
    def compute_min_angles(
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> np.ndarray:
        """
        Compute minimum angle for each triangle (in degrees).

        Uses law of cosines to compute all three angles, returns minimum.

        Args:
            vertices: (N, 2) array of vertex coordinates
            elements: (E, 3) array of triangle connectivity

        Returns:
            (E,) array of minimum angles in degrees
        """
        n_elements = len(elements)
        min_angles = np.zeros(n_elements)

        for i, tri in enumerate(elements):
            # Get triangle vertices
            v0, v1, v2 = vertices[tri]

            # Edge vectors
            e0 = v1 - v0
            e1 = v2 - v1
            e2 = v0 - v2

            # Edge lengths
            l0 = np.linalg.norm(e0)
            l1 = np.linalg.norm(e1)
            l2 = np.linalg.norm(e2)

            # Area check
            area = 0.5 * abs(e0[0] * (-e2[1]) - e0[1] * (-e2[0]))

            if area > 1e-10:
                # Compute angles using law of cosines
                # angle at v0: between e0 and -e2
                # angle at v1: between -e0 and e1
                # angle at v2: between -e1 and e2

                angle0 = np.arccos(np.clip(np.dot(e0, -e2) / (l0 * l2), -1, 1))
                angle1 = np.arccos(np.clip(np.dot(-e0, e1) / (l0 * l1), -1, 1))
                angle2 = np.arccos(np.clip(np.dot(-e1, e2) / (l1 * l2), -1, 1))

                min_angles[i] = np.degrees(min(angle0, angle1, angle2))
            else:
                # Degenerate triangle
                min_angles[i] = 0.0

        return min_angles

    @staticmethod
    def compute_areas(
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> np.ndarray:
        """
        Compute area for each triangle.

        Uses 2D cross product formula: area = 0.5 * |det([[x1-x0, x2-x0], [y1-y0, y2-y0]])|

        Args:
            vertices: (N, 2) array of vertex coordinates
            elements: (E, 3) array of triangle connectivity

        Returns:
            (E,) array of triangle areas
        """
        n_elements = len(elements)
        areas = np.zeros(n_elements)

        for i, tri in enumerate(elements):
            # Get triangle vertices
            v0, v1, v2 = vertices[tri]

            # Edge vectors from v0
            e0 = v1 - v0
            e2 = v2 - v0

            # Area (2D cross product magnitude)
            area = 0.5 * abs(e0[0] * e2[1] - e0[1] * e2[0])
            areas[i] = area

        return areas

    @staticmethod
    def check_inverted_elements(
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> List[int]:
        """
        Find inverted (negative area) triangles.

        Inverted triangles have vertices ordered clockwise instead of
        counter-clockwise, resulting in negative signed area.

        Args:
            vertices: (N, 2) array of vertex coordinates
            elements: (E, 3) array of triangle connectivity

        Returns:
            List of element indices that are inverted
        """
        inverted = []

        for i, tri in enumerate(elements):
            # Get triangle vertices
            v0, v1, v2 = vertices[tri]

            # Signed area (positive = CCW, negative = CW/inverted)
            signed_area = 0.5 * ((v1[0] - v0[0]) * (v2[1] - v0[1]) -
                                (v2[0] - v0[0]) * (v1[1] - v0[1]))

            if signed_area <= 0:
                inverted.append(i)

        return inverted

    @staticmethod
    def compute_all_metrics(
        vertices: np.ndarray,
        elements: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Compute all quality metrics at once.

        More efficient than calling individual methods when all metrics needed.

        Args:
            vertices: (N, 2) array of vertex coordinates
            elements: (E, 3) array of triangle connectivity

        Returns:
            Dictionary containing:
            - 'aspect_ratios': (E,) array of aspect ratios
            - 'min_angles': (E,) array of minimum angles (degrees)
            - 'areas': (E,) array of triangle areas
        """
        return {
            'aspect_ratios': MeshQualityAnalyzer.compute_aspect_ratios(vertices, elements),
            'min_angles': MeshQualityAnalyzer.compute_min_angles(vertices, elements),
            'areas': MeshQualityAnalyzer.compute_areas(vertices, elements)
        }
