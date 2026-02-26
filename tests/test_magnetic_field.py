"""
Tests for magnetic field computation from equilibrium data.
"""
import numpy as np
import pytest
from mesh_gui_project.core.magnetic_field import MagneticFieldCalculator
from mesh_gui_project.core.equilibrium import EquilibriumData
from mesh_gui_project.utils.interpolation import make_bicubic_interpolator


def test_magnetic_field_calculator_exists():
    """Test that MagneticFieldCalculator class can be instantiated."""
    # This test will fail until we create the class
    calc = MagneticFieldCalculator()
    assert calc is not None


def test_compute_B_R_from_psi():
    """Test that B_R = -(1/R) * dpsi/dZ is computed correctly."""
    # Create simple equilibrium with known psi gradient
    # psi = Z (linear in Z), so dpsi/dZ = 1
    NR, NZ = 10, 10
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-0.5, 0.5, NZ)

    # Create psi field: psi(R, Z) = Z (linear in Z)
    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)
    psi_grid = Z_mesh

    # Create equilibrium data dict
    data = {
        'NR': NR, 'NZ': NZ,
        'R_grid': R_grid, 'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'axis_R': 1.5, 'axis_Z': 0.0,
        'psi_axis': 0.0, 'psi_boundary': 0.5
    }
    equilibrium = EquilibriumData(data)

    # Attach interpolator
    equilibrium._interpolator = make_bicubic_interpolator(
        R_grid, Z_grid, psi_grid
    )

    # Create calculator
    calc = MagneticFieldCalculator(equilibrium)

    # Test B_R at a point
    # For psi = Z, dpsi/dZ = 1, so B_R = -(1/R) * 1 = -1/R
    R_test, Z_test = 1.5, 0.0
    B_R = calc.compute_B_R(R_test, Z_test)

    expected_B_R = -1.0 / R_test  # = -1/1.5 = -0.6667
    assert np.abs(B_R - expected_B_R) < 1e-6


def test_compute_B_Z_from_psi():
    """Test that B_Z = (1/R) * dpsi/dR is computed correctly."""
    # Create simple equilibrium with known psi gradient
    # psi = R (linear in R), so dpsi/dR = 1
    NR, NZ = 10, 10
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-0.5, 0.5, NZ)

    # Create psi field: psi(R, Z) = R (linear in R)
    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)
    psi_grid = R_mesh

    # Create equilibrium data dict
    data = {
        'NR': NR, 'NZ': NZ,
        'R_grid': R_grid, 'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'axis_R': 1.5, 'axis_Z': 0.0,
        'psi_axis': 1.5, 'psi_boundary': 2.0
    }
    equilibrium = EquilibriumData(data)

    # Attach interpolator
    equilibrium._interpolator = make_bicubic_interpolator(
        R_grid, Z_grid, psi_grid
    )

    # Create calculator
    calc = MagneticFieldCalculator(equilibrium)

    # Test B_Z at a point
    # For psi = R, dpsi/dR = 1, so B_Z = (1/R) * 1 = 1/R
    R_test, Z_test = 1.5, 0.0
    B_Z = calc.compute_B_Z(R_test, Z_test)

    expected_B_Z = 1.0 / R_test  # = 1/1.5 = 0.6667
    assert np.abs(B_Z - expected_B_Z) < 1e-6


def test_compute_B_phi_from_I():
    """Test that B_phi = μ₀ * I / (2π * R) is computed correctly."""
    # Create simple equilibrium with constant I (fpol)
    NR, NZ = 10, 10
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-0.5, 0.5, NZ)

    # Create psi field (arbitrary)
    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)
    psi_grid = R_mesh * 0.0  # Zeros

    # Create fpol (poloidal current function) - constant value
    I_value = 1.0e6  # 1 MA
    fpol = np.ones(NR) * I_value

    # Create equilibrium data dict
    data = {
        'NR': NR, 'NZ': NZ,
        'R_grid': R_grid, 'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'axis_R': 1.5, 'axis_Z': 0.0,
        'psi_axis': 0.0, 'psi_boundary': 1.0,  # Different values to pass consistency check
        'fpol': fpol
    }
    equilibrium = EquilibriumData(data)

    # Create calculator
    calc = MagneticFieldCalculator(equilibrium)

    # Test B_phi at a point
    # B_phi = μ₀ * I / (2π * R)
    R_test = 1.5
    mu_0 = 4 * np.pi * 1e-7  # T·m/A
    expected_B_phi = mu_0 * I_value / (2 * np.pi * R_test)

    B_phi = calc.compute_B_phi(R_test, I_value)

    assert np.abs(B_phi - expected_B_phi) < 1e-10


def test_magnetic_field_at_grid_points():
    """Test computing full B vector (B_R, B_Z, B_phi) at arbitrary points."""
    # Create simple equilibrium
    NR, NZ = 10, 10
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-0.5, 0.5, NZ)

    # psi = R + Z (mixed gradients)
    # dpsi/dR = 1, dpsi/dZ = 1
    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)
    psi_grid = R_mesh + Z_mesh

    # Create fpol
    I_value = 1.0e6
    fpol = np.ones(NR) * I_value

    # Create equilibrium
    data = {
        'NR': NR, 'NZ': NZ,
        'R_grid': R_grid, 'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'axis_R': 1.5, 'axis_Z': 0.0,
        'psi_axis': 1.5, 'psi_boundary': 2.5,
        'fpol': fpol
    }
    equilibrium = EquilibriumData(data)

    # Attach interpolator
    equilibrium._interpolator = make_bicubic_interpolator(
        R_grid, Z_grid, psi_grid
    )

    # Create calculator
    calc = MagneticFieldCalculator(equilibrium)

    # Test at a point
    R_test, Z_test = 1.5, 0.0

    # Compute full field vector
    B_R, B_Z, B_phi = calc.compute_B_vector(R_test, Z_test, I_value)

    # Expected values:
    # dpsi/dR = 1, dpsi/dZ = 1
    # B_R = -(1/R) * 1 = -1/1.5
    # B_Z = (1/R) * 1 = 1/1.5
    # B_phi = μ₀ * I / (2π * R)
    expected_B_R = -1.0 / R_test
    expected_B_Z = 1.0 / R_test
    mu_0 = 4 * np.pi * 1e-7
    expected_B_phi = mu_0 * I_value / (2 * np.pi * R_test)

    assert np.abs(B_R - expected_B_R) < 1e-6
    assert np.abs(B_Z - expected_B_Z) < 1e-6
    assert np.abs(B_phi - expected_B_phi) < 1e-10
