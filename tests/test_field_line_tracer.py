"""
Tests for 3D magnetic field line tracing.
"""
import numpy as np
import pytest
from mesh_gui_project.core.field_line_tracer import FieldLineTracer
from mesh_gui_project.core.equilibrium import EquilibriumData
from mesh_gui_project.utils.interpolation import make_bicubic_interpolator


def create_test_equilibrium_with_fpol():
    """Helper to create test equilibrium with fpol."""
    NR, NZ = 20, 20
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-0.5, 0.5, NZ)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)
    # Circular psi field
    psi_grid = np.sqrt((R_mesh - 1.5)**2 + Z_mesh**2)

    # Create fpol (poloidal current)
    fpol = np.ones(NR) * 1.0e6  # 1 MA

    data = {
        'NR': NR, 'NZ': NZ,
        'R_grid': R_grid, 'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'axis_R': 1.5, 'axis_Z': 0.0,
        'psi_axis': 0.0, 'psi_boundary': 0.4,
        'fpol': fpol
    }
    equilibrium = EquilibriumData(data)
    equilibrium._interpolator = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    return equilibrium


def test_field_line_tracer_exists():
    """Test that FieldLineTracer can be instantiated."""
    equilibrium = create_test_equilibrium_with_fpol()

    tracer = FieldLineTracer(equilibrium, n_toroidal_steps=64)

    assert tracer is not None
    assert tracer.equilibrium == equilibrium
    assert tracer.n_toroidal_steps == 64


def test_default_toroidal_steps_is_64():
    """Test that default toroidal steps is 64."""
    equilibrium = create_test_equilibrium_with_fpol()

    tracer = FieldLineTracer(equilibrium)

    assert tracer.n_toroidal_steps == 64


def test_field_line_rhs_computation():
    """Test field line RHS computation."""
    equilibrium = create_test_equilibrium_with_fpol()
    tracer = FieldLineTracer(equilibrium, n_toroidal_steps=64)

    # Test RHS at a point
    state = [1.5, 0.0, 0.1]  # [R, phi, Z]
    rhs = tracer.field_line_rhs(0.0, state, fpol_interp=None)

    # Should return [dR/ds, dphi/ds, dZ/ds]
    assert len(rhs) == 3
    assert all(np.isfinite(rhs))


def test_trace_field_line_returns_points():
    """Test that field line tracing returns multiple points."""
    equilibrium = create_test_equilibrium_with_fpol()
    tracer = FieldLineTracer(equilibrium, n_toroidal_steps=8)  # Use fewer steps for speed

    # Trace from a starting point
    R_start, Z_start = 1.6, 0.0

    points = tracer.trace_field_line(R_start, Z_start)

    # Should return n_toroidal_steps + 1 points (including start)
    assert len(points) == 8 + 1
    assert points[0] == (R_start, Z_start)  # First point is start

    # All points should be (R, Z) tuples
    for pt in points:
        assert len(pt) == 2
        R, Z = pt
        assert np.isfinite(R) and np.isfinite(Z)


def test_generate_mesh_vertices_on_contour():
    """Test generating mesh vertices on a PSI contour."""
    equilibrium = create_test_equilibrium_with_fpol()
    tracer = FieldLineTracer(equilibrium, n_toroidal_steps=8)

    # Generate vertices at psi_N = 0.5
    psi_value = equilibrium.psi_axis + 0.5 * (equilibrium.psi_boundary - equilibrium.psi_axis)

    vertices = tracer.generate_mesh_vertices_on_contour(psi_value, n_starting_points=4)

    # Should return vertices array
    assert vertices is not None
    assert vertices.shape[1] == 2  # (R, Z) columns
    assert vertices.shape[0] > 0  # Has vertices

    # Vertices should be within grid bounds
    assert np.all(vertices[:, 0] >= 1.0)  # R >= R_min
    assert np.all(vertices[:, 0] <= 2.0)  # R <= R_max
    assert np.all(vertices[:, 1] >= -0.5)  # Z >= Z_min
    assert np.all(vertices[:, 1] <= 0.5)  # Z <= Z_max
