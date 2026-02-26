"""Test interpolation module."""
import numpy as np
import pytest


def test_interpolation_module_exists():
    """Test that interpolation module can be imported."""
    from mesh_gui_project.utils import interpolation

    assert hasattr(interpolation, 'make_bicubic_interpolator'), \
        "interpolation module should have make_bicubic_interpolator function"


def test_make_bicubic_interpolator_returns_callable():
    """Test that make_bicubic_interpolator returns a callable interpolator."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create simple test grid
    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    assert interp is not None
    assert hasattr(interp, 'psi'), "Interpolator should have psi method"
    assert callable(interp.psi), "psi should be callable"


def test_interpolator_evaluates_at_grid_points():
    """Test that interpolator returns correct values at grid points."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create known grid
    R_grid = np.linspace(1.5, 2.5, 5)
    Z_grid = np.linspace(-1.0, 1.0, 5)

    # Create simple function: psi = R^2 + Z^2
    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = (R_mesh**2 + Z_mesh**2).T  # Shape [NZ, NR]

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    # Test at a grid point
    R_test, Z_test = R_grid[2], Z_grid[2]
    expected = R_test**2 + Z_test**2
    result = interp.psi(R_test, Z_test)

    assert np.isclose(result, expected, rtol=1e-6), \
        f"Interpolator should match at grid points: got {result}, expected {expected}"


def test_interpolator_has_derivative_methods():
    """Test that interpolator has dpsi_dR and dpsi_dZ methods."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    assert hasattr(interp, 'dpsi_dR'), "Should have dpsi_dR method"
    assert hasattr(interp, 'dpsi_dZ'), "Should have dpsi_dZ method"
    assert callable(interp.dpsi_dR), "dpsi_dR should be callable"
    assert callable(interp.dpsi_dZ), "dpsi_dZ should be callable"


def test_derivatives_are_correct():
    """Test that derivatives are computed correctly for a known function."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create grid for psi = R^2 + Z^2
    # dpsi/dR = 2*R, dpsi/dZ = 2*Z
    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = (R_mesh**2 + Z_mesh**2).T

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    # Test derivatives at a point
    R_test, Z_test = 2.0, 0.5
    expected_dR = 2 * R_test
    expected_dZ = 2 * Z_test

    result_dR = interp.dpsi_dR(R_test, Z_test)
    result_dZ = interp.dpsi_dZ(R_test, Z_test)

    assert np.isclose(result_dR, expected_dR, rtol=1e-3), \
        f"dpsi/dR incorrect: got {result_dR}, expected {expected_dR}"
    assert np.isclose(result_dZ, expected_dZ, rtol=1e-3), \
        f"dpsi/dZ incorrect: got {result_dZ}, expected {expected_dZ}"


def test_out_of_bounds_handling():
    """Test that interpolator handles out-of-bounds queries gracefully."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    # Test slightly out of bounds (should extrapolate or warn)
    R_out = 3.0  # Beyond R_grid
    Z_out = 0.0

    # Should not raise an error (either extrapolates or clamps)
    try:
        result = interp.psi(R_out, Z_out)
        assert result is not None
    except ValueError:
        # Raising ValueError for out-of-bounds is also acceptable
        assert True


def test_interpolator_works_with_arrays():
    """Test that interpolator can handle array inputs."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    # Test with arrays
    R_array = np.array([1.7, 2.0, 2.3])
    Z_array = np.array([-0.5, 0.0, 0.5])

    result = interp.psi(R_array, Z_array)

    assert isinstance(result, (np.ndarray, float))
    if isinstance(result, np.ndarray):
        assert result.shape == R_array.shape


def test_second_derivatives_exist():
    """Test that interpolator has second derivative methods."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    assert hasattr(interp, 'd2psi_dR2'), "Should have d2psi_dR2 method"
    assert hasattr(interp, 'd2psi_dZ2'), "Should have d2psi_dZ2 method"
    assert hasattr(interp, 'd2psi_dRdZ'), "Should have d2psi_dRdZ method"
    assert callable(interp.d2psi_dR2)
    assert callable(interp.d2psi_dZ2)
    assert callable(interp.d2psi_dRdZ)


def test_second_derivatives_correctness():
    """Test that second derivatives are computed correctly for a known function."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Use psi = R^2 + Z^2
    # d2psi/dR2 = 2, d2psi/dZ2 = 2, d2psi/dRdZ = 0
    R_grid = np.linspace(1.5, 2.5, 15)
    Z_grid = np.linspace(-1.0, 1.0, 15)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = (R_mesh**2 + Z_mesh**2).T

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    R_test, Z_test = 2.0, 0.3
    d2_dR2 = interp.d2psi_dR2(R_test, Z_test)
    d2_dZ2 = interp.d2psi_dZ2(R_test, Z_test)
    d2_dRdZ = interp.d2psi_dRdZ(R_test, Z_test)

    assert np.isclose(d2_dR2, 2.0, rtol=1e-2), f"d2psi/dR2 should be 2.0, got {d2_dR2}"
    assert np.isclose(d2_dZ2, 2.0, rtol=1e-2), f"d2psi/dZ2 should be 2.0, got {d2_dZ2}"
    assert np.isclose(d2_dRdZ, 0.0, atol=1e-2), f"d2psi/dRdZ should be 0.0, got {d2_dRdZ}"


def test_hessian_method_exists():
    """Test that interpolator has a hessian method."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    assert hasattr(interp, 'hessian'), "Should have hessian method"
    assert callable(interp.hessian)


def test_hessian_returns_correct_tuple():
    """Test that hessian method returns (d2/dR2, d2/dZ2, d2/dRdZ)."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    result = interp.hessian(2.0, 0.0)

    assert isinstance(result, tuple), "hessian should return a tuple"
    assert len(result) == 3, "hessian should return 3 values"

    d2_dR2, d2_dZ2, d2_dRdZ = result
    assert isinstance(d2_dR2, (float, np.floating))
    assert isinstance(d2_dZ2, (float, np.floating))
    assert isinstance(d2_dRdZ, (float, np.floating))


def test_gradient_method_exists():
    """Test that interpolator has a gradient method."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    assert hasattr(interp, 'gradient'), "Should have gradient method"
    assert callable(interp.gradient)


def test_gradient_returns_correct_tuple():
    """Test that gradient method returns (dpsi/dR, dpsi/dZ)."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Use psi = R^2 + Z^2, so grad = (2R, 2Z)
    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = (R_mesh**2 + Z_mesh**2).T

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    R_test, Z_test = 2.0, 0.5
    grad_R, grad_Z = interp.gradient(R_test, Z_test)

    assert np.isclose(grad_R, 2 * R_test, rtol=1e-3)
    assert np.isclose(grad_Z, 2 * Z_test, rtol=1e-3)


# T12.2 - Numerical guards and extrapolation warnings

def test_interpolator_warns_on_extrapolation(caplog):
    """Test that interpolator warns when queried outside grid bounds."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    import logging

    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    # Query outside bounds
    with caplog.at_level(logging.WARNING):
        result = interp.psi(3.0, 0.0)  # R=3.0 is outside [1.5, 2.5]

    # Should log a warning
    assert len(caplog.records) > 0, "Should log a warning for out-of-bounds query"
    assert any("out of bounds" in record.message.lower() or "extrapolat" in record.message.lower()
               for record in caplog.records), \
        f"Warning should mention out-of-bounds or extrapolation, got: {[r.message for r in caplog.records]}"


def test_is_within_bounds_for_scalar_coordinates():
    """Test is_within_bounds method with scalar coordinates."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create grid with bounds R=[1.0, 2.0], Z=[-1.0, 1.0]
    R_grid = np.linspace(1.0, 2.0, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    # Test points inside bounds
    assert interp.is_within_bounds(1.5, 0.0), "Center point should be within bounds"
    assert interp.is_within_bounds(1.0, -1.0), "Lower left corner should be within bounds"
    assert interp.is_within_bounds(2.0, 1.0), "Upper right corner should be within bounds"
    assert interp.is_within_bounds(1.0, 0.0), "Left edge should be within bounds"
    assert interp.is_within_bounds(2.0, 0.0), "Right edge should be within bounds"

    # Test points outside bounds - R coordinate
    assert not interp.is_within_bounds(0.5, 0.0), "R < R_min should be outside bounds"
    assert not interp.is_within_bounds(2.5, 0.0), "R > R_max should be outside bounds"

    # Test points outside bounds - Z coordinate
    assert not interp.is_within_bounds(1.5, -1.5), "Z < Z_min should be outside bounds"
    assert not interp.is_within_bounds(1.5, 1.5), "Z > Z_max should be outside bounds"

    # Test points outside bounds - both coordinates
    assert not interp.is_within_bounds(0.5, -1.5), "Both R and Z too small should be outside bounds"
    assert not interp.is_within_bounds(2.5, 1.5), "Both R and Z too large should be outside bounds"


def test_is_within_bounds_for_array_coordinates():
    """Test is_within_bounds method with array coordinates."""
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create grid with bounds R=[1.0, 2.0], Z=[-1.0, 1.0]
    R_grid = np.linspace(1.0, 2.0, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)
    psi_grid = np.random.rand(10, 10)

    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)

    # Test arrays where all points are inside bounds
    R_inside = np.array([1.2, 1.5, 1.8])
    Z_inside = np.array([0.0, 0.5, -0.5])
    assert interp.is_within_bounds(R_inside, Z_inside), \
        "All points inside should return True"

    # Test arrays where at least one point is outside bounds
    R_mixed = np.array([1.2, 1.5, 2.5])  # Last point R > R_max
    Z_mixed = np.array([0.0, 0.5, 0.0])
    assert not interp.is_within_bounds(R_mixed, Z_mixed), \
        "Any point outside should return False"

    # Test arrays where all points are outside bounds
    R_outside = np.array([0.5, 0.8, 2.5])  # All R outside
    Z_outside = np.array([0.0, 0.0, 0.0])
    assert not interp.is_within_bounds(R_outside, Z_outside), \
        "All points outside should return False"
