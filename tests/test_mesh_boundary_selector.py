"""
Tests for mesh boundary selection from PSI contours.
"""
import numpy as np
import pytest
from mesh_gui_project.core.mesh_boundary_selector import MeshBoundarySelector
from mesh_gui_project.core.equilibrium import EquilibriumData
from mesh_gui_project.utils.interpolation import make_bicubic_interpolator


def create_test_equilibrium():
    """Helper to create test equilibrium."""
    NR, NZ = 20, 20
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-0.5, 0.5, NZ)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)
    # Circular psi field
    psi_grid = np.sqrt((R_mesh - 1.5)**2 + Z_mesh**2)

    data = {
        'NR': NR, 'NZ': NZ,
        'R_grid': R_grid, 'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'axis_R': 1.5, 'axis_Z': 0.0,
        'psi_axis': 0.0, 'psi_boundary': 0.4
    }
    equilibrium = EquilibriumData(data)
    equilibrium._interpolator = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    return equilibrium


def test_mesh_boundary_selector_exists():
    """Test that MeshBoundarySelector class can be instantiated."""
    equilibrium = create_test_equilibrium()

    # Create selector
    selector = MeshBoundarySelector(equilibrium)
    assert selector is not None
    assert selector.equilibrium == equilibrium


def test_closed_psi_contour_detection():
    """Test detection of closed contours (inside LCFS)."""
    equilibrium = create_test_equilibrium()
    selector = MeshBoundarySelector(equilibrium)

    # Test with psi inside LCFS (psi_N < 1)
    psi_inside = equilibrium.psi_axis + 0.5 * (equilibrium.psi_boundary - equilibrium.psi_axis)
    assert selector.is_contour_closed(psi_inside) == True

    # Test with psi at LCFS (psi_N = 1)
    psi_at_lcfs = equilibrium.psi_boundary
    assert selector.is_contour_closed(psi_at_lcfs) == True

    # Test with psi outside LCFS (psi_N > 1)
    psi_outside = equilibrium.psi_boundary + 0.1
    assert selector.is_contour_closed(psi_outside) == False


def test_extract_closed_contour():
    """Test extracting closed contour polyline."""
    equilibrium = create_test_equilibrium()
    selector = MeshBoundarySelector(equilibrium)

    # Extract contour at psi_N = 0.5
    psi_value = equilibrium.psi_axis + 0.5 * (equilibrium.psi_boundary - equilibrium.psi_axis)

    polyline = selector.extract_closed_contour(psi_value)

    # Verify polyline properties
    assert polyline is not None
    assert polyline.shape[1] == 2  # (R, Z) columns
    assert polyline.shape[0] > 10  # Has multiple points
    assert selector.selected_boundary is not None


def test_get_boundary_auto_detects_closed():
    """Test get_boundary_from_psi auto-detects closed contours."""
    equilibrium = create_test_equilibrium()
    selector = MeshBoundarySelector(equilibrium)

    # Test with closed contour
    psi_inside = equilibrium.psi_axis + 0.5 * (equilibrium.psi_boundary - equilibrium.psi_axis)
    boundary = selector.get_boundary_from_psi(psi_inside)

    assert boundary is not None
    assert boundary.shape[1] == 2
