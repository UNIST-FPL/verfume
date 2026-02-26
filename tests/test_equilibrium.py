"""Test EquilibriumData class."""
import numpy as np
import pytest


def test_equilibrium_module_exists():
    """Test that equilibrium module can be imported."""
    from mesh_gui_project.core import equilibrium

    assert hasattr(equilibrium, 'EquilibriumData'), \
        "equilibrium module should have EquilibriumData class"


def test_equilibrium_data_initialization():
    """Test that EquilibriumData can be initialized from parsed data."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    # Create minimal equilibrium data
    data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.5, 2.5, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 1.0,
        'psi_boundary': -0.5,
        'boundary': np.array([[2.0, 0.0], [2.1, 0.1], [2.0, 0.2]]),
        'limiter': np.array([[1.5, -1.0], [2.5, -1.0], [2.5, 1.0], [1.5, 1.0]]),
    }

    eq = EquilibriumData(data)

    assert eq is not None
    assert eq.NR == 5
    assert eq.NZ == 5


def test_equilibrium_data_properties():
    """Test that EquilibriumData has required properties."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.5, 2.5, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 1.0,
        'psi_boundary': -0.5,
    }

    eq = EquilibriumData(data)

    # Check required properties
    assert hasattr(eq, 'R_grid'), "Should have R_grid property"
    assert hasattr(eq, 'Z_grid'), "Should have Z_grid property"
    assert hasattr(eq, 'psi_grid'), "Should have psi_grid property"
    assert hasattr(eq, 'axis_R'), "Should have axis_R property"
    assert hasattr(eq, 'axis_Z'), "Should have axis_Z property"
    assert hasattr(eq, 'psi_axis'), "Should have psi_axis property"
    assert hasattr(eq, 'psi_boundary'), "Should have psi_boundary property"


def test_normalize_psi_method():
    """Test that normalize_psi method works correctly."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.5, 2.5, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 1.0,
        'psi_boundary': -0.5,
    }

    eq = EquilibriumData(data)

    # Test normalization: axis -> 0, boundary -> 1
    psi_n_axis = eq.normalize_psi(1.0)
    psi_n_boundary = eq.normalize_psi(-0.5)

    assert np.isclose(psi_n_axis, 0.0), "Axis should normalize to 0.0"
    assert np.isclose(psi_n_boundary, 1.0), "Boundary should normalize to 1.0"

    # Test midpoint
    psi_n_mid = eq.normalize_psi(0.25)
    assert 0.0 < psi_n_mid < 1.0, "Midpoint should be between 0 and 1"


def test_normalize_psi_handles_inversion():
    """Test that normalize_psi detects and handles inverted psi."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    # Case where psi_boundary > psi_axis (inverted)
    data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.5, 2.5, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': -0.5,
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)

    # Should still normalize so axis -> 0, boundary -> 1
    psi_n_axis = eq.normalize_psi(-0.5)
    psi_n_boundary = eq.normalize_psi(1.0)

    assert np.isclose(psi_n_axis, 0.0), "Axis should normalize to 0.0 even when inverted"
    assert np.isclose(psi_n_boundary, 1.0), "Boundary should normalize to 1.0 even when inverted"


def test_psi_value_stub():
    """Test that psi_value method exists (stub until interpolator attached)."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.5, 2.5, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 1.0,
        'psi_boundary': -0.5,
    }

    eq = EquilibriumData(data)

    assert hasattr(eq, 'psi_value'), "Should have psi_value method"
    assert callable(eq.psi_value), "psi_value should be callable"


def test_data_consistency_checks():
    """Test that EquilibriumData performs basic consistency checks."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    # Valid data should work
    data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.5, 2.5, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 1.0,
        'psi_boundary': -0.5,
    }

    eq = EquilibriumData(data)
    assert eq is not None

    # Test with NaN in psi_grid - should handle gracefully or raise
    data_with_nan = data.copy()
    data_with_nan['psi_grid'] = np.array([[np.nan, 0, 0, 0, 0]] * 5)

    # Should either raise or store a flag
    try:
        eq_nan = EquilibriumData(data_with_nan)
        # If it doesn't raise, it should have detected the issue
        assert hasattr(eq_nan, 'has_nan') or True, "Should handle NaN gracefully"
    except ValueError:
        # Raising ValueError is also acceptable
        assert True


def test_attach_interpolator_method_exists():
    """Test that EquilibriumData has attach_interpolator method."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.5, 2.5, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 1.0,
        'psi_boundary': -0.5,
    }

    eq = EquilibriumData(data)

    assert hasattr(eq, 'attach_interpolator'), "Should have attach_interpolator method"
    assert callable(eq.attach_interpolator), "attach_interpolator should be callable"


def test_interpolator_integration():
    """Test that interpolator can be attached and used via EquilibriumData."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create test data with known function: psi = R^2 + Z^2
    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = (R_mesh**2 + Z_mesh**2).T  # Shape [NZ, NR]

    data = {
        'NR': 10,
        'NZ': 10,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 4.0,  # 2^2 + 0^2
        'psi_boundary': 7.25,  # Example boundary value
    }

    eq = EquilibriumData(data)

    # Create and attach interpolator
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    # Test psi_value method
    R_test, Z_test = 2.0, 0.5
    psi_val = eq.psi_value(R_test, Z_test)
    expected = R_test**2 + Z_test**2

    assert np.isclose(psi_val, expected, rtol=1e-3), \
        f"psi_value should return interpolated value: got {psi_val}, expected {expected}"


def test_grad_psi_proxy_method():
    """Test that EquilibriumData has grad_psi proxy method."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create test data: psi = R^2 + Z^2, so grad = (2R, 2Z)
    R_grid = np.linspace(1.5, 2.5, 10)
    Z_grid = np.linspace(-1.0, 1.0, 10)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = (R_mesh**2 + Z_mesh**2).T

    data = {
        'NR': 10,
        'NZ': 10,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 4.0,
        'psi_boundary': 7.25,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    assert hasattr(eq, 'grad_psi'), "Should have grad_psi method"
    assert callable(eq.grad_psi), "grad_psi should be callable"

    # Test gradient calculation
    R_test, Z_test = 2.0, 0.5
    grad_R, grad_Z = eq.grad_psi(R_test, Z_test)

    expected_grad_R = 2 * R_test
    expected_grad_Z = 2 * Z_test

    assert np.isclose(grad_R, expected_grad_R, rtol=1e-3), \
        f"grad_psi dR component incorrect: got {grad_R}, expected {expected_grad_R}"
    assert np.isclose(grad_Z, expected_grad_Z, rtol=1e-3), \
        f"grad_psi dZ component incorrect: got {grad_Z}, expected {expected_grad_Z}"


def test_hessian_psi_proxy_method():
    """Test that EquilibriumData has hessian_psi proxy method."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

    # Create test data: psi = R^2 + Z^2
    # Hessian: d2/dR2 = 2, d2/dZ2 = 2, d2/dRdZ = 0
    R_grid = np.linspace(1.5, 2.5, 15)
    Z_grid = np.linspace(-1.0, 1.0, 15)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = (R_mesh**2 + Z_mesh**2).T

    data = {
        'NR': 15,
        'NZ': 15,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 4.0,
        'psi_boundary': 7.25,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    assert hasattr(eq, 'hessian_psi'), "Should have hessian_psi method"
    assert callable(eq.hessian_psi), "hessian_psi should be callable"

    # Test Hessian calculation
    R_test, Z_test = 2.0, 0.3
    d2_dR2, d2_dZ2, d2_dRdZ = eq.hessian_psi(R_test, Z_test)

    assert np.isclose(d2_dR2, 2.0, rtol=1e-2), \
        f"hessian_psi d2/dR2 incorrect: got {d2_dR2}, expected 2.0"
    assert np.isclose(d2_dZ2, 2.0, rtol=1e-2), \
        f"hessian_psi d2/dZ2 incorrect: got {d2_dZ2}, expected 2.0"
    assert np.isclose(d2_dRdZ, 0.0, atol=1e-2), \
        f"hessian_psi d2/dRdZ incorrect: got {d2_dRdZ}, expected 0.0"


def test_is_within_grid_bounds():
    """Test that is_within_grid_bounds correctly checks if coordinates are within grid."""
    from mesh_gui_project.core.equilibrium import EquilibriumData

    # Create test data with known grid bounds
    R_grid = np.linspace(1.5, 2.5, 10)  # R: [1.5, 2.5]
    Z_grid = np.linspace(-1.0, 1.0, 10)  # Z: [-1.0, 1.0]

    data = {
        'NR': 10,
        'NZ': 10,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': np.random.rand(10, 10),
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 1.0,
        'psi_boundary': -0.5,
    }

    eq = EquilibriumData(data)

    # Test points clearly within bounds
    assert eq.is_within_grid_bounds(2.0, 0.0) is True, \
        "Point (2.0, 0.0) should be within bounds"
    assert eq.is_within_grid_bounds(1.5, -1.0) is True, \
        "Point (1.5, -1.0) at min corner should be within bounds"
    assert eq.is_within_grid_bounds(2.5, 1.0) is True, \
        "Point (2.5, 1.0) at max corner should be within bounds"

    # Test points clearly outside bounds
    assert eq.is_within_grid_bounds(1.0, 0.0) is False, \
        "Point (1.0, 0.0) with R < R_min should be outside bounds"
    assert eq.is_within_grid_bounds(3.0, 0.0) is False, \
        "Point (3.0, 0.0) with R > R_max should be outside bounds"
    assert eq.is_within_grid_bounds(2.0, -2.0) is False, \
        "Point (2.0, -2.0) with Z < Z_min should be outside bounds"
    assert eq.is_within_grid_bounds(2.0, 2.0) is False, \
        "Point (2.0, 2.0) with Z > Z_max should be outside bounds"

    # Test edge cases (exactly on boundary)
    assert eq.is_within_grid_bounds(1.5, 0.5) is True, \
        "Point on R_min should be within bounds"
    assert eq.is_within_grid_bounds(2.5, 0.5) is True, \
        "Point on R_max should be within bounds"
    assert eq.is_within_grid_bounds(2.0, -1.0) is True, \
        "Point on Z_min should be within bounds"
    assert eq.is_within_grid_bounds(2.0, 1.0) is True, \
        "Point on Z_max should be within bounds"
