"""
Interpolation utilities for poloidal flux fields.

Provides bicubic interpolation with derivative support using SciPy.
"""
import numpy as np
from scipy.interpolate import RectBivariateSpline
import warnings
import logging

logger = logging.getLogger(__name__)


class BicubicInterpolator:
    """
    Bicubic interpolator for 2D scalar fields with derivative support.

    Wraps SciPy RectBivariateSpline to provide convenient access to
    function values and derivatives.
    """

    def __init__(self, R_grid, Z_grid, psi_grid):
        """
        Initialize bicubic interpolator.

        Args:
            R_grid: 1D array of R coordinates (strictly increasing)
            Z_grid: 1D array of Z coordinates (strictly increasing)
            psi_grid: 2D array of psi values, shape [NZ, NR]
        """
        self.R_grid = np.asarray(R_grid)
        self.Z_grid = np.asarray(Z_grid)
        self.psi_grid = np.asarray(psi_grid)

        # Validate inputs
        if len(self.R_grid.shape) != 1 or len(self.Z_grid.shape) != 1:
            raise ValueError("R_grid and Z_grid must be 1D arrays")

        expected_shape = (len(Z_grid), len(R_grid))
        if self.psi_grid.shape != expected_shape:
            raise ValueError(
                f"psi_grid shape {self.psi_grid.shape} doesn't match "
                f"expected shape {expected_shape} from grid dimensions"
            )

        # Create RectBivariateSpline
        # Note: RectBivariateSpline expects (x, y, z) where z[i,j] = f(x[i], y[j])
        # Our convention: psi_grid[j, i] = psi(R_grid[i], Z_grid[j])
        # So we need to transpose or reorder
        self._spline = RectBivariateSpline(
            self.Z_grid,  # y-axis (Z)
            self.R_grid,  # x-axis (R)
            self.psi_grid,  # z values: psi_grid[j, i] = psi(R[i], Z[j])
            kx=3,  # Cubic in x (R)
            ky=3,  # Cubic in y (Z)
        )

        # Store bounds for checking
        self.R_min, self.R_max = self.R_grid[0], self.R_grid[-1]
        self.Z_min, self.Z_max = self.Z_grid[0], self.Z_grid[-1]

    def psi(self, R, Z, warn_extrapolate=True):
        """
        Evaluate psi at (R, Z).

        Args:
            R: R coordinate(s) - scalar or array
            Z: Z coordinate(s) - scalar or array
            warn_extrapolate: If True, warn when extrapolating

        Returns:
            Psi value(s) at (R, Z)
        """
        R = np.asarray(R)
        Z = np.asarray(Z)

        # Check bounds and warn if extrapolating
        if warn_extrapolate:
            if np.any(R < self.R_min) or np.any(R > self.R_max) or \
               np.any(Z < self.Z_min) or np.any(Z > self.Z_max):
                logger.warning(
                    "Interpolation outside grid bounds - extrapolating (R: [%.3f, %.3f], Z: [%.3f, %.3f])",
                    self.R_min, self.R_max, self.Z_min, self.Z_max
                )
                warnings.warn(
                    "Interpolation outside grid bounds - extrapolating",
                    RuntimeWarning
                )

        # RectBivariateSpline uses (y, x) order: spline(Z, R)
        result = self._spline(Z, R, grid=False)

        # Return scalar if inputs were scalar
        if result.shape == ():
            return float(result)
        return result

    def dpsi_dR(self, R, Z):
        """
        Evaluate dpsi/dR at (R, Z).

        Args:
            R: R coordinate(s)
            Z: Z coordinate(s)

        Returns:
            Derivative dpsi/dR at (R, Z)
        """
        R = np.asarray(R)
        Z = np.asarray(Z)

        # Derivative with respect to R (second argument, dx=1)
        result = self._spline(Z, R, dx=0, dy=1, grid=False)

        if result.shape == ():
            return float(result)
        return result

    def dpsi_dZ(self, R, Z):
        """
        Evaluate dpsi/dZ at (R, Z).

        Args:
            R: R coordinate(s)
            Z: Z coordinate(s)

        Returns:
            Derivative dpsi/dZ at (R, Z)
        """
        R = np.asarray(R)
        Z = np.asarray(Z)

        # Derivative with respect to Z (first argument, dx=1)
        result = self._spline(Z, R, dx=1, dy=0, grid=False)

        if result.shape == ():
            return float(result)
        return result

    def d2psi_dR2(self, R, Z):
        """
        Evaluate d²psi/dR² at (R, Z).

        Args:
            R: R coordinate(s)
            Z: Z coordinate(s)

        Returns:
            Second derivative d²psi/dR² at (R, Z)
        """
        R = np.asarray(R)
        Z = np.asarray(Z)

        # Second derivative with respect to R (dy=2)
        result = self._spline(Z, R, dx=0, dy=2, grid=False)

        if result.shape == ():
            return float(result)
        return result

    def d2psi_dZ2(self, R, Z):
        """
        Evaluate d²psi/dZ² at (R, Z).

        Args:
            R: R coordinate(s)
            Z: Z coordinate(s)

        Returns:
            Second derivative d²psi/dZ² at (R, Z)
        """
        R = np.asarray(R)
        Z = np.asarray(Z)

        # Second derivative with respect to Z (dx=2)
        result = self._spline(Z, R, dx=2, dy=0, grid=False)

        if result.shape == ():
            return float(result)
        return result

    def d2psi_dRdZ(self, R, Z):
        """
        Evaluate d²psi/dRdZ (mixed derivative) at (R, Z).

        Args:
            R: R coordinate(s)
            Z: Z coordinate(s)

        Returns:
            Mixed second derivative d²psi/dRdZ at (R, Z)
        """
        R = np.asarray(R)
        Z = np.asarray(Z)

        # Mixed derivative (dx=1, dy=1)
        result = self._spline(Z, R, dx=1, dy=1, grid=False)

        if result.shape == ():
            return float(result)
        return result

    def gradient(self, R, Z):
        """
        Compute gradient of psi at (R, Z).

        Args:
            R: R coordinate(s)
            Z: Z coordinate(s)

        Returns:
            Tuple (dpsi/dR, dpsi/dZ) - gradient vector
        """
        return (self.dpsi_dR(R, Z), self.dpsi_dZ(R, Z))

    def hessian(self, R, Z):
        """
        Compute Hessian (second derivatives) of psi at (R, Z).

        Args:
            R: R coordinate(s)
            Z: Z coordinate(s)

        Returns:
            Tuple (d²psi/dR², d²psi/dZ², d²psi/dRdZ)
        """
        return (
            self.d2psi_dR2(R, Z),
            self.d2psi_dZ2(R, Z),
            self.d2psi_dRdZ(R, Z)
        )

    def is_within_bounds(self, R, Z):
        """
        Check if (R, Z) coordinates are within the interpolation grid bounds.

        Args:
            R: R coordinate(s) - scalar or array
            Z: Z coordinate(s) - scalar or array

        Returns:
            True if all coordinates are within bounds, False otherwise
        """
        R = np.asarray(R)
        Z = np.asarray(Z)

        # Check if all R and Z values are within bounds
        r_ok = np.all((R >= self.R_min) & (R <= self.R_max))
        z_ok = np.all((Z >= self.Z_min) & (Z <= self.Z_max))

        return r_ok and z_ok


def make_bicubic_interpolator(R_grid, Z_grid, psi_grid):
    """
    Create a bicubic interpolator for psi(R, Z).

    Uses SciPy RectBivariateSpline for smooth interpolation with
    continuous first and second derivatives.

    Args:
        R_grid: 1D array of R coordinates (strictly increasing)
        Z_grid: 1D array of Z coordinates (strictly increasing)
        psi_grid: 2D array of psi values, shape [NZ, NR]

    Returns:
        BicubicInterpolator instance with methods:
            - psi(R, Z): Evaluate psi
            - dpsi_dR(R, Z): Evaluate dpsi/dR
            - dpsi_dZ(R, Z): Evaluate dpsi/dZ

    Example:
        >>> interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
        >>> psi_val = interp.psi(2.0, 0.0)
        >>> grad_R = interp.dpsi_dR(2.0, 0.0)
    """
    return BicubicInterpolator(R_grid, Z_grid, psi_grid)
