"""
EquilibriumData class for managing EFIT equilibrium data.

This module provides a container for equilibrium data with normalization,
interpolation support, and plotting helpers.
"""
import numpy as np
from typing import Optional


class EquilibriumData:
    """
    Container for equilibrium data from gEQDSK files.

    Stores grid data, magnetic axis and boundary information, and provides
    normalization and interpolation methods.
    """

    def __init__(self, data: dict):
        """
        Initialize EquilibriumData from parsed gEQDSK data.

        Args:
            data: Dictionary from parse_geqdsk() containing:
                - NR, NZ: Grid dimensions
                - R_grid, Z_grid: 1D coordinate arrays
                - psi_grid: 2D poloidal flux array (shape [NZ, NR])
                - Rmag, Zmag: Magnetic axis location (or axis_R, axis_Z)
                - psi_axis, psi_boundary: Psi at axis and boundary (or simag, sibry)
                - boundary: Boundary curve points (optional)
                - limiter: Limiter curve points (optional)
        """
        # Grid dimensions
        self.NR = data['NR']
        self.NZ = data['NZ']

        # Grid arrays
        self.R_grid = np.array(data['R_grid'])
        self.Z_grid = np.array(data['Z_grid'])
        self.psi_grid = np.array(data['psi_grid'])

        # Magnetic axis location
        self.axis_R = data.get('Rmag', data.get('axis_R'))
        self.axis_Z = data.get('Zmag', data.get('axis_Z'))

        # Psi at axis and boundary
        self.psi_axis = data.get('psi_axis', data.get('simag'))
        self.psi_boundary = data.get('psi_boundary', data.get('sibry'))

        # Boundary and limiter curves (optional)
        self.boundary_curve = data.get('boundary')
        self.limiter_curve = data.get('limiter')

        # Interpolator (to be attached later)
        self._interpolator = None

        # Perform data consistency checks
        self._check_consistency()

    def _check_consistency(self):
        """Perform basic data consistency checks."""
        # Check for NaN values in psi_grid
        if np.isnan(self.psi_grid).any():
            # Store flag but don't raise - allow loading of imperfect data
            self.has_nan = True
        else:
            self.has_nan = False

        # Check grid dimensions match psi_grid shape
        expected_shape = (self.NZ, self.NR)
        if self.psi_grid.shape != expected_shape:
            raise ValueError(
                f"psi_grid shape {self.psi_grid.shape} doesn't match "
                f"expected shape {expected_shape} from NR={self.NR}, NZ={self.NZ}"
            )

        # Check that psi_axis and psi_boundary are different
        if np.isclose(self.psi_axis, self.psi_boundary):
            raise ValueError(
                f"psi_axis ({self.psi_axis}) and psi_boundary ({self.psi_boundary}) "
                f"are too close - cannot normalize"
            )

    def normalize_psi(self, psi):
        """
        Normalize psi value to psi_N in [0, 1].

        Convention: axis -> 0, boundary -> 1
        Handles both normal and inverted cases automatically.

        Args:
            psi: Poloidal flux value (scalar or array)

        Returns:
            Normalized psi_N (scalar or array)
        """
        # Calculate normalized psi: (psi - psi_axis) / (psi_boundary - psi_axis)
        # This automatically handles inversion:
        # - If psi_boundary > psi_axis: normal case
        # - If psi_boundary < psi_axis: inverted case (denominator is negative)
        psi_n = (psi - self.psi_axis) / (self.psi_boundary - self.psi_axis)
        return psi_n

    def is_within_grid_bounds(self, R, Z):
        """
        Check if (R, Z) coordinates are within the equilibrium grid bounds.

        This method checks against the R and Z grid extents, not the
        interpolation domain. It's useful for validating coordinates before
        interpolation or when the interpolator is not yet attached.

        Args:
            R: R coordinate (scalar)
            Z: Z coordinate (scalar)

        Returns:
            bool: True if coordinates are within grid bounds, False otherwise
        """
        R_min, R_max = self.R_grid.min(), self.R_grid.max()
        Z_min, Z_max = self.Z_grid.min(), self.Z_grid.max()
        return bool(R_min <= R <= R_max and Z_min <= Z <= Z_max)

    def psi_value(self, R, Z):
        """
        Get psi value at (R, Z) coordinates.

        Args:
            R: R coordinate (scalar or array)
            Z: Z coordinate (scalar or array)

        Returns:
            Psi value at (R, Z)

        Raises:
            RuntimeError: If interpolator not attached
        """
        if self._interpolator is None:
            raise RuntimeError(
                "No interpolator attached. Use attach_interpolator() first."
            )
        return self._interpolator.psi(R, Z)

    def attach_interpolator(self, interpolator):
        """
        Attach an interpolator for psi evaluation.

        Args:
            interpolator: BicubicInterpolator instance with psi, gradient, and hessian methods
        """
        self._interpolator = interpolator

    def grad_psi(self, R, Z):
        """
        Compute gradient of psi at (R, Z).

        Args:
            R: R coordinate (scalar or array)
            Z: Z coordinate (scalar or array)

        Returns:
            Tuple (dpsi/dR, dpsi/dZ)

        Raises:
            RuntimeError: If interpolator not attached
        """
        if self._interpolator is None:
            raise RuntimeError(
                "No interpolator attached. Use attach_interpolator() first."
            )
        return self._interpolator.gradient(R, Z)

    def hessian_psi(self, R, Z):
        """
        Compute Hessian (second derivatives) of psi at (R, Z).

        Args:
            R: R coordinate (scalar or array)
            Z: Z coordinate (scalar or array)

        Returns:
            Tuple (d²psi/dR², d²psi/dZ², d²psi/dRdZ)

        Raises:
            RuntimeError: If interpolator not attached
        """
        if self._interpolator is None:
            raise RuntimeError(
                "No interpolator attached. Use attach_interpolator() first."
            )
        return self._interpolator.hessian(R, Z)

    def is_within_psi_domain(self, R, Z):
        """
        Check if (R, Z) coordinates are within the psi interpolation domain.

        Args:
            R: R coordinate (scalar or array)
            Z: Z coordinate (scalar or array)

        Returns:
            True if all coordinates are within domain bounds, False otherwise

        Raises:
            RuntimeError: If interpolator not attached
        """
        if self._interpolator is None:
            raise RuntimeError(
                "No interpolator attached. Use attach_interpolator() first."
            )
        return self._interpolator.is_within_bounds(R, Z)

    def plot_boundary(self, ax, **kwargs):
        """
        Plot boundary curve on given axes.

        Args:
            ax: Matplotlib axes
            kwargs: Style arguments passed to ax.plot()
        """
        if self.boundary_curve is None:
            return

        # Set default style
        style = {'color': 'red', 'linewidth': 2, 'label': 'LCFS'}
        style.update(kwargs)

        # Close the curve by appending first point
        r = self.boundary_curve[:, 0]
        z = self.boundary_curve[:, 1]
        r = np.append(r, r[0])
        z = np.append(z, z[0])

        ax.plot(r, z, **style)

    def plot_limiter(self, ax, **kwargs):
        """
        Plot limiter curve on given axes.

        Args:
            ax: Matplotlib axes
            kwargs: Style arguments passed to ax.plot()
        """
        if self.limiter_curve is None:
            return

        # Set default style
        style = {'color': 'black', 'linewidth': 2, 'linestyle': '--', 'label': 'Limiter'}
        style.update(kwargs)

        # Close the curve
        r = self.limiter_curve[:, 0]
        z = self.limiter_curve[:, 1]
        r = np.append(r, r[0])
        z = np.append(z, z[0])

        ax.plot(r, z, **style)
