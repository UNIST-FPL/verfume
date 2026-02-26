"""
Flux surface extraction using radial ray shooting and root finding.

This module provides tools to extract flux surfaces (contours of constant psi)
from magnetic equilibria using a ray-based approach.
"""
import numpy as np
from typing import List, Tuple, Optional
from scipy.optimize import brentq
import logging

logger = logging.getLogger(__name__)


class FluxSurfaceExtractor:
    """
    Extract flux surfaces from equilibrium data using radial ray shooting.

    This class shoots rays from the O-point (magnetic axis) at various angles
    and uses root-finding to locate points where psi equals the target value.
    """

    def __init__(self, eq, *, n_rays: int = 360, ray_extent_policy: str = 'limiter', preview_mode: bool = False):
        """
        Initialize flux surface extractor.

        Args:
            eq: EquilibriumData instance with attached interpolator
            n_rays: Number of rays to shoot (default 360)
            ray_extent_policy: Policy for ray extent ('limiter' or 'boundary')
            preview_mode: If True, use reduced resolution for faster preview (default False)
        """
        self.eq = eq
        self.preview_mode = preview_mode

        # In preview mode, use fewer rays for better performance
        if self.preview_mode:
            self.n_rays = max(72, n_rays // 5)  # Use 1/5 of requested rays, min 72
        else:
            self.n_rays = n_rays

        self.ray_extent_policy = ray_extent_policy

        # Find O-point for ray origin
        from mesh_gui_project.core.critical_points import find_o_point
        self.R_o, self.Z_o = find_o_point(eq)

        # Determine maximum ray extent
        self._compute_ray_extent()

    def _compute_ray_extent(self):
        """Compute maximum extent for rays based on grid boundaries."""
        # Use grid boundaries as maximum extent
        R_min, R_max = self.eq.R_grid[0], self.eq.R_grid[-1]
        Z_min, Z_max = self.eq.Z_grid[0], self.eq.Z_grid[-1]

        # Maximum distance from O-point to any corner
        corners = [
            (R_min, Z_min),
            (R_min, Z_max),
            (R_max, Z_min),
            (R_max, Z_max)
        ]

        max_dist = 0.0
        for R_c, Z_c in corners:
            dist = np.sqrt((R_c - self.R_o)**2 + (Z_c - self.Z_o)**2)
            max_dist = max(max_dist, dist)

        self.max_ray_extent = max_dist

    def _ray_point(self, angle: float, distance: float) -> Tuple[float, float]:
        """
        Compute (R, Z) point along a ray.

        Args:
            angle: Ray angle in radians
            distance: Distance from O-point along ray

        Returns:
            (R, Z) coordinates
        """
        R = self.R_o + distance * np.cos(angle)
        Z = self.Z_o + distance * np.sin(angle)
        return R, Z

    def _find_intersection(self, angle: float, psi_target: float) -> Optional[Tuple[float, float]]:
        """
        Find intersection of ray with target psi surface.

        Args:
            angle: Ray angle in radians
            psi_target: Target psi value to find

        Returns:
            (R, Z) intersection point, or None if not found
        """
        # Define function: f(distance) = psi(R(d), Z(d)) - psi_target
        def psi_difference(distance):
            R, Z = self._ray_point(angle, distance)

            # Check if point is within grid bounds
            if not (self.eq.R_grid[0] <= R <= self.eq.R_grid[-1] and
                    self.eq.Z_grid[0] <= Z <= self.eq.Z_grid[-1]):
                # Return large value to indicate out of bounds
                return 1e10

            try:
                psi = self.eq.psi_value(R, Z)
                return psi - psi_target
            except Exception:
                return 1e10

        # Check endpoints
        f_start = psi_difference(0.0)
        f_end = psi_difference(self.max_ray_extent)

        # If signs don't change, no intersection
        if f_start * f_end > 0:
            return None

        # Use Brent's method to find root
        try:
            distance = brentq(
                psi_difference,
                0.0,
                self.max_ray_extent,
                xtol=1e-6,
                maxiter=100
            )

            R, Z = self._ray_point(angle, distance)
            return R, Z

        except (ValueError, RuntimeError):
            # No intersection found
            return None

    def extract_by_psiN(self, psiN_list: List[float]) -> List[np.ndarray]:
        """
        Extract flux surfaces for given normalized psi values.

        Args:
            psiN_list: List of normalized psi values (0 = axis, 1 = boundary)

        Returns:
            List of numpy arrays, each with shape (M, 2) containing (R, Z) points
            for the flux surface
        """
        surfaces = []

        for psi_n in psiN_list:
            # Convert normalized psi to actual psi value
            psi_target = self.eq.psi_axis + psi_n * (self.eq.psi_boundary - self.eq.psi_axis)

            # Shoot rays at different angles
            angles = np.linspace(0, 2 * np.pi, self.n_rays, endpoint=False)
            points = []

            for angle in angles:
                intersection = self._find_intersection(angle, psi_target)
                if intersection is not None:
                    points.append(intersection)
                else:
                    # Failed to find intersection - try to interpolate from neighbors
                    # For now, skip this point
                    logger.debug(f"No intersection found for angle {np.degrees(angle):.1f}°")

            if len(points) == 0:
                logger.warning(f"No points found for psi_N = {psi_n}")
                # Return empty array
                surfaces.append(np.array([]).reshape(0, 2))
                continue

            # Convert to numpy array
            surface = np.array(points)

            # Close the curve by appending the first point
            if len(surface) > 0:
                surface = np.vstack([surface, surface[0:1]])

            surfaces.append(surface)

        return surfaces

    def extract_by_click(self, R_click: float, Z_click: float) -> np.ndarray:
        """
        Extract flux surface passing through clicked point.

        Args:
            R_click: R coordinate of clicked point
            Z_click: Z coordinate of clicked point

        Returns:
            Numpy array with shape (M, 2) containing (R, Z) points for flux surface
        """
        # Get psi value at clicked point
        psi_target = self.eq.psi_value(R_click, Z_click)

        # Compute normalized psi
        psi_n = self.eq.normalize_psi(psi_target)

        # Extract surface using extract_by_psiN
        surfaces = self.extract_by_psiN([psi_n])

        return surfaces[0]
