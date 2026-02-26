"""
Mesh boundary selection from PSI contours.

Allows user to select PSI contours via mouse interaction and constructs
mesh boundaries from selected contours, optionally combined with limiter geometry.
"""
import numpy as np
from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor


class MeshBoundarySelector:
    """
    Handles selection of PSI contours for mesh boundary definition.

    Supports:
    - Mouse-based PSI contour selection
    - Closed contour boundaries (inside LCFS)
    - Combined PSI+limiter boundaries (outside LCFS)
    """

    def __init__(self, equilibrium):
        """
        Initialize the boundary selector.

        Args:
            equilibrium: EquilibriumData object with psi field
        """
        self.equilibrium = equilibrium
        self.selected_boundary = None
        self.flux_extractor = FluxSurfaceExtractor(equilibrium, n_rays=360)

    def is_contour_closed(self, psi_value):
        """
        Determine if a PSI contour is closed (inside LCFS).

        Args:
            psi_value: PSI value to check

        Returns:
            bool: True if contour is closed, False if open
        """
        # Normalize psi
        psi_N = (psi_value - self.equilibrium.psi_axis) / \
                (self.equilibrium.psi_boundary - self.equilibrium.psi_axis)

        # Contour is closed if psi_N <= 1.0 (inside or at LCFS)
        return psi_N <= 1.0

    def extract_closed_contour(self, psi_value):
        """
        Extract closed contour polyline for given PSI value.

        Args:
            psi_value: PSI value

        Returns:
            polyline: np.ndarray (N, 2) of (R, Z) points forming closed curve
        """
        # Normalize psi
        psi_N = (psi_value - self.equilibrium.psi_axis) / \
                (self.equilibrium.psi_boundary - self.equilibrium.psi_axis)

        # Extract flux surface using ray-tracing
        surfaces = self.flux_extractor.extract_by_psiN([psi_N])

        if len(surfaces) == 0 or surfaces[0] is None:
            raise ValueError(f"Could not extract contour for psi={psi_value}")

        polyline = surfaces[0]
        self.selected_boundary = polyline

        return polyline

    def combine_with_limiter(self, psi_value):
        """
        Combine open PSI contour with limiter to form closed boundary.

        Args:
            psi_value: PSI value (outside LCFS)

        Returns:
            polyline: np.ndarray (N, 2) of (R, Z) forming closed loop
        """
        # Extract PSI contour segment (will be open)
        psi_N = (psi_value - self.equilibrium.psi_axis) / \
                (self.equilibrium.psi_boundary - self.equilibrium.psi_axis)

        # Get PSI contour polyline
        surfaces = self.flux_extractor.extract_by_psiN([psi_N])

        if len(surfaces) == 0 or surfaces[0] is None:
            # If extraction fails, just use limiter
            if self.equilibrium.limiter_curve is not None:
                self.selected_boundary = self.equilibrium.limiter_curve
                return self.equilibrium.limiter_curve
            else:
                raise ValueError("No limiter available and PSI extraction failed")

        psi_contour = surfaces[0]

        # Get limiter
        if self.equilibrium.limiter_curve is None:
            # No limiter, just return PSI contour (might not be fully closed)
            self.selected_boundary = psi_contour
            return psi_contour

        limiter = self.equilibrium.limiter_curve

        # Find intersection points between PSI contour and limiter
        # For simplicity, find closest points on each curve to connect them
        # More sophisticated: find actual geometric intersections

        # Find endpoints of PSI contour (if not closed)
        psi_start = psi_contour[0]
        psi_end = psi_contour[-1]

        # Check if already closed
        dist_closure = np.linalg.norm(psi_start - psi_end)
        if dist_closure < 1e-3:
            # Already closed
            self.selected_boundary = psi_contour
            return psi_contour

        # Find closest limiter points to PSI endpoints
        dist_to_start = np.linalg.norm(limiter - psi_start, axis=1)
        dist_to_end = np.linalg.norm(limiter - psi_end, axis=1)

        idx_start = np.argmin(dist_to_start)
        idx_end = np.argmin(dist_to_end)

        # Extract limiter segment between these points
        if idx_start <= idx_end:
            limiter_segment = limiter[idx_start:idx_end+1]
        else:
            # Wrap around
            limiter_segment = np.vstack([
                limiter[idx_start:],
                limiter[:idx_end+1]
            ])

        # Combine: psi_contour + limiter_segment
        combined = np.vstack([psi_contour, limiter_segment])

        self.selected_boundary = combined
        return combined

    def get_boundary_from_psi(self, psi_value):
        """
        Get mesh boundary from PSI value (auto-detect closed vs combined).

        Args:
            psi_value: PSI value

        Returns:
            polyline: np.ndarray (N, 2) forming closed boundary
        """
        if self.is_contour_closed(psi_value):
            return self.extract_closed_contour(psi_value)
        else:
            return self.combine_with_limiter(psi_value)
