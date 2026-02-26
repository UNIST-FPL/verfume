"""Test critical points detection (O-point and X-point)."""
import numpy as np
import pytest


def test_critical_points_module_exists():
    """Test that critical_points module can be imported."""
    from mesh_gui_project.core import critical_points

    assert hasattr(critical_points, 'find_o_point'), \
        "critical_points module should have find_o_point function"


def test_find_o_point_function_exists():
    """Test that find_o_point function exists and is callable."""
    from mesh_gui_project.core.critical_points import find_o_point

    assert callable(find_o_point), "find_o_point should be callable"


def test_find_o_point_with_simple_equilibrium():
    """Test O-point finding with a simple known equilibrium."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_o_point

    # Create test data with O-point at (2.0, 0.0)
    # Use psi = (R-2)^2 + Z^2, so minimum at (2, 0)
    R_grid = np.linspace(1.5, 2.5, 20)
    Z_grid = np.linspace(-1.0, 1.0, 20)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 20,
        'NZ': 20,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,  # Initial guess
        'Zmag': 0.0,  # Initial guess
        'psi_axis': 0.0,  # Minimum value
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    # Find O-point
    R_o, Z_o = find_o_point(eq)

    # Should find O-point at (2.0, 0.0)
    assert np.isclose(R_o, 2.0, atol=1e-4), f"O-point R should be 2.0, got {R_o}"
    assert np.isclose(Z_o, 0.0, atol=1e-4), f"O-point Z should be 0.0, got {Z_o}"


def test_find_o_point_verifies_gradient_is_zero():
    """Test that found O-point has gradient near zero."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_o_point

    # Create test data
    R_grid = np.linspace(1.5, 2.5, 20)
    Z_grid = np.linspace(-1.0, 1.0, 20)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 20,
        'NZ': 20,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 1.95,  # Slightly off initial guess
        'Zmag': 0.05,
        'psi_axis': 0.0,
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    R_o, Z_o = find_o_point(eq)

    # Verify gradient is near zero
    grad_R, grad_Z = eq.grad_psi(R_o, Z_o)
    grad_norm = np.sqrt(grad_R**2 + grad_Z**2)

    assert grad_norm < 1e-6, f"Gradient norm at O-point should be near zero, got {grad_norm}"


def test_find_o_point_verifies_extremum():
    """Test that O-point is an extremum (same sign Hessian eigenvalues)."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_o_point

    R_grid = np.linspace(1.5, 2.5, 20)
    Z_grid = np.linspace(-1.0, 1.0, 20)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 20,
        'NZ': 20,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    R_o, Z_o = find_o_point(eq)

    # Get Hessian
    d2_dR2, d2_dZ2, d2_dRdZ = eq.hessian_psi(R_o, Z_o)

    # For extremum, both eigenvalues should have same sign
    # Eigenvalues of 2x2 symmetric matrix:
    # λ = (trace ± sqrt(trace^2 - 4*det)) / 2
    trace = d2_dR2 + d2_dZ2
    det = d2_dR2 * d2_dZ2 - d2_dRdZ**2

    # For same sign eigenvalues, det > 0
    assert det > 0, f"Hessian determinant should be positive for extremum, got {det}"


def test_find_o_point_with_initial_guess():
    """Test that find_o_point uses initial guess from header."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_o_point

    R_grid = np.linspace(1.5, 2.5, 15)
    Z_grid = np.linspace(-1.0, 1.0, 15)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.1)**2 + (Z_mesh - 0.2)**2).T

    data = {
        'NR': 15,
        'NZ': 15,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,  # Initial guess (slightly off)
        'Zmag': 0.1,  # Initial guess (slightly off)
        'psi_axis': 0.0,
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    R_o, Z_o = find_o_point(eq)

    # Should converge to true O-point at (2.1, 0.2)
    assert np.isclose(R_o, 2.1, atol=1e-3), f"O-point R should be 2.1, got {R_o}"
    assert np.isclose(Z_o, 0.2, atol=1e-3), f"O-point Z should be 0.2, got {Z_o}"


def test_find_x_points_function_exists():
    """Test that find_x_points function exists and is callable."""
    from mesh_gui_project.core.critical_points import find_x_points

    assert callable(find_x_points), "find_x_points should be callable"


def test_find_x_points_with_saddle():
    """Test X-point finding with a simple saddle point."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_x_points

    # Create test data with saddle point at (2.0, 0.5)
    # Use psi = (R-2)^2 - (Z-0.5)^2 (saddle at (2, 0.5))
    R_grid = np.linspace(1.5, 2.5, 25)
    Z_grid = np.linspace(-0.5, 1.5, 25)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 - (Z_mesh - 0.5)**2).T

    data = {
        'NR': 25,
        'NZ': 25,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 0.25,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    # Find X-points
    x_points = find_x_points(eq)

    # Should find at least one X-point near (2.0, 0.5)
    assert len(x_points) >= 1, "Should find at least one X-point"

    # Check if any X-point is near the expected location
    found = False
    for R_x, Z_x in x_points:
        if np.isclose(R_x, 2.0, atol=0.1) and np.isclose(Z_x, 0.5, atol=0.1):
            found = True
            break

    assert found, f"Should find X-point near (2.0, 0.5), got {x_points}"


def test_find_x_points_verifies_saddle():
    """Test that found X-points have saddle-type Hessian."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_x_points

    # Create saddle
    R_grid = np.linspace(1.5, 2.5, 25)
    Z_grid = np.linspace(-0.5, 1.5, 25)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 - (Z_mesh - 0.5)**2).T

    data = {
        'NR': 25,
        'NZ': 25,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 0.25,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    x_points = find_x_points(eq)

    # Verify each X-point has saddle Hessian (det < 0)
    for R_x, Z_x in x_points:
        d2_dR2, d2_dZ2, d2_dRdZ = eq.hessian_psi(R_x, Z_x)
        det = d2_dR2 * d2_dZ2 - d2_dRdZ**2

        assert det < 0, f"X-point at ({R_x}, {Z_x}) should have negative Hessian det, got {det}"


def test_find_x_points_returns_list():
    """Test that find_x_points returns a list of tuples."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_x_points

    R_grid = np.linspace(1.5, 2.5, 15)
    Z_grid = np.linspace(-1.0, 1.0, 15)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 15,
        'NZ': 15,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    x_points = find_x_points(eq)

    assert isinstance(x_points, list), "find_x_points should return a list"


def test_o_point_convergence_accuracy():
    """Test O-point finding meets accuracy threshold (T11.1)."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_o_point

    # Create test data with known O-point at (2.0, 0.0)
    R_grid = np.linspace(1.5, 2.5, 30)
    Z_grid = np.linspace(-1.0, 1.0, 30)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 30,
        'NZ': 30,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.05,  # Intentionally off
        'Zmag': 0.05,  # Intentionally off
        'psi_axis': 0.0,
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    R_o, Z_o = find_o_point(eq)

    # Accuracy threshold: within 1e-4 of true O-point
    assert np.isclose(R_o, 2.0, atol=1e-4), \
        f"O-point R accuracy threshold failed: got {R_o}, expected 2.0"
    assert np.isclose(Z_o, 0.0, atol=1e-4), \
        f"O-point Z accuracy threshold failed: got {Z_o}, expected 0.0"

    # Convergence check: gradient should be < 1e-6
    grad_R, grad_Z = eq.grad_psi(R_o, Z_o)
    grad_norm = np.sqrt(grad_R**2 + grad_Z**2)
    assert grad_norm < 1e-6, \
        f"O-point convergence threshold failed: gradient norm {grad_norm} > 1e-6"


def test_x_point_convergence_accuracy():
    """Test X-point finding meets accuracy threshold (T11.1)."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_x_points

    # Create test data with known X-point at (2.0, 0.5)
    R_grid = np.linspace(1.5, 2.5, 30)
    Z_grid = np.linspace(-0.5, 1.5, 30)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 - (Z_mesh - 0.5)**2).T

    data = {
        'NR': 30,
        'NZ': 30,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 0.25,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    x_points = find_x_points(eq)

    # Should find X-point near (2.0, 0.5) with accuracy threshold 1e-3
    found = False
    for R_x, Z_x in x_points:
        if np.isclose(R_x, 2.0, atol=1e-3) and np.isclose(Z_x, 0.5, atol=1e-3):
            # Convergence check: gradient should be < 1e-5
            grad_R, grad_Z = eq.grad_psi(R_x, Z_x)
            grad_norm = np.sqrt(grad_R**2 + grad_Z**2)
            assert grad_norm < 1e-5, \
                f"X-point convergence threshold failed: gradient norm {grad_norm} > 1e-5"
            found = True
            break

    assert found, f"X-point accuracy threshold failed: no X-point found within 1e-3 of (2.0, 0.5)"


def test_find_o_point_with_real_kstar_data():
    """Test O-point finding with real KSTAR equilibrium data."""
    from mesh_gui_project.data.geqdsk_parser import parse_geqdsk
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.critical_points import find_o_point

    # Load real KSTAR equilibrium
    data = parse_geqdsk('examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk')

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(data['R_grid'], data['Z_grid'], data['psi_grid'])
    eq.attach_interpolator(interp)

    # Should successfully find O-point without raising error
    R_o, Z_o = find_o_point(eq)

    # Verify O-point is reasonable (within plasma domain)
    assert data['R_grid'][0] <= R_o <= data['R_grid'][-1], \
        f"O-point R={R_o} outside domain [{data['R_grid'][0]}, {data['R_grid'][-1]}]"
    assert data['Z_grid'][0] <= Z_o <= data['Z_grid'][-1], \
        f"O-point Z={Z_o} outside domain [{data['Z_grid'][0]}, {data['Z_grid'][-1]}]"

    # Verify gradient is reasonably small (relaxed for real data)
    grad_R, grad_Z = eq.grad_psi(R_o, Z_o)
    grad_norm = np.sqrt(grad_R**2 + grad_Z**2)
    assert grad_norm < 0.1, \
        f"O-point gradient norm {grad_norm} too large (should be < 0.1)"

    # Verify it's an extremum (positive Hessian determinant)
    d2_dR2, d2_dZ2, d2_dRdZ = eq.hessian_psi(R_o, Z_o)
    det = d2_dR2 * d2_dZ2 - d2_dRdZ**2
    assert det > -1e-8, \
        f"O-point should be an extremum (det > 0), got det={det}"
