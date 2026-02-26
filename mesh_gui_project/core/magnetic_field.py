"""
Magnetic field computation from equilibrium data.

Computes B_R, B_Z, and B_phi from poloidal flux (psi) and poloidal current (I).
"""
import numpy as np


class MagneticFieldCalculator:
    """
    Computes magnetic field components from equilibrium data.

    Uses Grad-Shafranov equilibrium:
        B_R = -(1/R) * ∂psi/∂Z
        B_Z = (1/R) * ∂psi/∂R
        B_phi = μ₀ * I / (2π * R)

    where psi is the poloidal flux and I is the poloidal current function.
    """

    def __init__(self, equilibrium=None):
        """
        Initialize the calculator.

        Args:
            equilibrium: EquilibriumData object with attached interpolator
        """
        self.equilibrium = equilibrium

    def compute_B_R(self, R, Z):
        """
        Compute B_R = -(1/R) * dpsi/dZ.

        Args:
            R: Major radius coordinate(s)
            Z: Vertical coordinate(s)

        Returns:
            B_R: Radial magnetic field component
        """
        # Get gradient from interpolator
        dpsi_dR, dpsi_dZ = self.equilibrium._interpolator.gradient(R, Z)

        # B_R = -(1/R) * dpsi/dZ
        B_R = -(1.0 / R) * dpsi_dZ

        return B_R

    def compute_B_Z(self, R, Z):
        """
        Compute B_Z = (1/R) * dpsi/dR.

        Args:
            R: Major radius coordinate(s)
            Z: Vertical coordinate(s)

        Returns:
            B_Z: Vertical magnetic field component
        """
        # Get gradient from interpolator
        dpsi_dR, dpsi_dZ = self.equilibrium._interpolator.gradient(R, Z)

        # B_Z = (1/R) * dpsi/dR
        B_Z = (1.0 / R) * dpsi_dR

        return B_Z

    def compute_B_phi(self, R, I):
        """
        Compute B_phi = μ₀ * I / (2π * R).

        Args:
            R: Major radius coordinate(s)
            I: Poloidal current function value

        Returns:
            B_phi: Toroidal magnetic field component
        """
        # Vacuum permeability
        mu_0 = 4 * np.pi * 1e-7  # T·m/A

        # B_phi = μ₀ * I / (2π * R)
        B_phi = mu_0 * I / (2 * np.pi * R)

        return B_phi

    def compute_B_vector(self, R, Z, I):
        """
        Compute full magnetic field vector (B_R, B_Z, B_phi).

        Args:
            R: Major radius coordinate(s)
            Z: Vertical coordinate(s)
            I: Poloidal current function value

        Returns:
            tuple: (B_R, B_Z, B_phi)
        """
        B_R = self.compute_B_R(R, Z)
        B_Z = self.compute_B_Z(R, Z)
        B_phi = self.compute_B_phi(R, I)

        return B_R, B_Z, B_phi
