"""Test flux surface extraction."""
import numpy as np
import pytest


def test_flux_surface_module_exists():
    """Test that flux_surface module can be imported."""
    from mesh_gui_project.core import flux_surface

    assert hasattr(flux_surface, 'FluxSurfaceExtractor'), \
        "flux_surface module should have FluxSurfaceExtractor class"


def test_flux_surface_extractor_can_be_instantiated():
    """Test that FluxSurfaceExtractor can be instantiated."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create simple test equilibrium
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

    # Create extractor
    extractor = FluxSurfaceExtractor(eq)

    assert extractor is not None
    assert extractor.eq is eq


def test_flux_surface_extractor_has_configurable_n_rays():
    """Test that FluxSurfaceExtractor accepts n_rays parameter."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create simple equilibrium
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

    # Create extractor with custom n_rays
    extractor = FluxSurfaceExtractor(eq, n_rays=180)

    assert extractor.n_rays == 180


def test_extract_by_psiN_method_exists():
    """Test that extract_by_psiN method exists and is callable."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create simple equilibrium
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

    extractor = FluxSurfaceExtractor(eq)

    assert hasattr(extractor, 'extract_by_psiN'), \
        "FluxSurfaceExtractor should have extract_by_psiN method"
    assert callable(extractor.extract_by_psiN), \
        "extract_by_psiN should be callable"


def test_extract_by_psiN_returns_list_of_surfaces():
    """Test that extract_by_psiN returns a list of numpy arrays."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create simple circular equilibrium: psi = (R-2)^2 + Z^2
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

    extractor = FluxSurfaceExtractor(eq, n_rays=360)

    # Extract surfaces at psi_N = [0.25, 0.5, 0.75]
    psiN_list = [0.25, 0.5, 0.75]
    surfaces = extractor.extract_by_psiN(psiN_list)

    assert isinstance(surfaces, list), "extract_by_psiN should return a list"
    assert len(surfaces) == 3, "Should return 3 surfaces for 3 psi_N values"

    # Each surface should be a numpy array with shape (M, 2)
    for i, surface in enumerate(surfaces):
        assert isinstance(surface, np.ndarray), \
            f"Surface {i} should be a numpy array"
        assert surface.ndim == 2, \
            f"Surface {i} should be 2D array"
        assert surface.shape[1] == 2, \
            f"Surface {i} should have 2 columns (R, Z)"


def test_extract_circular_flux_surface():
    """Test extraction of circular flux surfaces with known geometry."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium: psi = (R-2)^2 + Z^2
    # This has circular flux surfaces centered at (2, 0)
    R_grid = np.linspace(1.0, 3.0, 40)
    Z_grid = np.linspace(-1.5, 1.5, 40)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 40,
        'NZ': 40,
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

    extractor = FluxSurfaceExtractor(eq, n_rays=360)

    # Extract surface at psi_N = 0.5
    # For psi = (R-2)^2 + Z^2, psi_N = 0.5 means psi = 0.5
    # So (R-2)^2 + Z^2 = 0.5, which is a circle with radius sqrt(0.5)
    surfaces = extractor.extract_by_psiN([0.5])

    surface = surfaces[0]

    # Check that all points are approximately on a circle of radius sqrt(0.5)
    R_points = surface[:, 0]
    Z_points = surface[:, 1]

    # Distance from center (2, 0)
    distances = np.sqrt((R_points - 2.0)**2 + Z_points**2)

    expected_radius = np.sqrt(0.5)

    # All points should be close to the expected radius
    assert np.allclose(distances, expected_radius, rtol=0.05), \
        f"Points should form a circle of radius {expected_radius}, got distances: {distances}"


def test_extract_multiple_flux_surfaces():
    """Test extraction of multiple flux surfaces at once."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium
    R_grid = np.linspace(1.0, 3.0, 40)
    Z_grid = np.linspace(-1.5, 1.5, 40)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 40,
        'NZ': 40,
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

    extractor = FluxSurfaceExtractor(eq, n_rays=180)

    # Extract surfaces at multiple psi_N values
    psiN_list = [0.1, 0.3, 0.5, 0.7, 0.9]
    surfaces = extractor.extract_by_psiN(psiN_list)

    assert len(surfaces) == 5, "Should return 5 surfaces"

    # Check that surfaces have increasing radii
    radii = []
    for surface in surfaces:
        R_points = surface[:, 0]
        Z_points = surface[:, 1]
        avg_radius = np.mean(np.sqrt((R_points - 2.0)**2 + Z_points**2))
        radii.append(avg_radius)

    # Radii should increase with psi_N
    for i in range(len(radii) - 1):
        assert radii[i] < radii[i+1], \
            f"Radius should increase with psi_N: {radii}"


def test_flux_surface_is_closed_curve():
    """Test that extracted flux surfaces form closed curves."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium
    R_grid = np.linspace(1.0, 3.0, 30)
    Z_grid = np.linspace(-1.5, 1.5, 30)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 30,
        'NZ': 30,
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

    extractor = FluxSurfaceExtractor(eq, n_rays=360)

    surfaces = extractor.extract_by_psiN([0.5])
    surface = surfaces[0]

    # First and last points should be very close (closed curve)
    first_point = surface[0]
    last_point = surface[-1]

    distance = np.sqrt((first_point[0] - last_point[0])**2 +
                      (first_point[1] - last_point[1])**2)

    assert distance < 0.01, \
        f"First and last points should be close (closed curve), distance: {distance}"


def test_extract_by_click_method_exists():
    """Test that extract_by_click method exists."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create simple equilibrium
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

    extractor = FluxSurfaceExtractor(eq)

    assert hasattr(extractor, 'extract_by_click'), \
        "FluxSurfaceExtractor should have extract_by_click method"
    assert callable(extractor.extract_by_click), \
        "extract_by_click should be callable"


def test_extract_by_click_returns_surface():
    """Test that extract_by_click returns a flux surface array."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium
    R_grid = np.linspace(1.0, 3.0, 40)
    Z_grid = np.linspace(-1.5, 1.5, 40)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 40,
        'NZ': 40,
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

    extractor = FluxSurfaceExtractor(eq, n_rays=180)

    # Click at point (2.5, 0.0) which has psi = 0.25
    R_click = 2.5
    Z_click = 0.0

    surface = extractor.extract_by_click(R_click, Z_click)

    assert isinstance(surface, np.ndarray), "extract_by_click should return numpy array"
    assert surface.ndim == 2, "Surface should be 2D array"
    assert surface.shape[1] == 2, "Surface should have 2 columns (R, Z)"
    assert surface.shape[0] > 0, "Surface should have points"


def test_extract_by_click_passes_through_clicked_point():
    """Test that extracted surface passes through the clicked point."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium
    R_grid = np.linspace(1.0, 3.0, 40)
    Z_grid = np.linspace(-1.5, 1.5, 40)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 40,
        'NZ': 40,
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

    extractor = FluxSurfaceExtractor(eq, n_rays=360)

    # Click at point (2.5, 0.0)
    R_click = 2.5
    Z_click = 0.0

    surface = extractor.extract_by_click(R_click, Z_click)

    # Find closest point on surface to clicked point
    distances = np.sqrt((surface[:, 0] - R_click)**2 + (surface[:, 1] - Z_click)**2)
    min_distance = np.min(distances)

    # Surface should pass close to the clicked point
    assert min_distance < 0.1, \
        f"Surface should pass close to clicked point, min distance: {min_distance}"


def test_flux_surface_extractor_configurable_quality():
    """Test that FluxSurfaceExtractor can use different n_rays values."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium
    R_grid = np.linspace(1.0, 3.0, 30)
    Z_grid = np.linspace(-1.5, 1.5, 30)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 30,
        'NZ': 30,
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

    # Test with low resolution (fast preview)
    extractor_low = FluxSurfaceExtractor(eq, n_rays=36)
    surfaces_low = extractor_low.extract_by_psiN([0.5])

    # Test with high resolution (high quality)
    extractor_high = FluxSurfaceExtractor(eq, n_rays=720)
    surfaces_high = extractor_high.extract_by_psiN([0.5])

    # Low resolution should have fewer points
    assert len(surfaces_low[0]) < len(surfaces_high[0]), \
        f"Low res should have fewer points: {len(surfaces_low[0])} vs {len(surfaces_high[0])}"

    # Both should still approximate a circle
    for surface, n_rays in [(surfaces_low[0], 36), (surfaces_high[0], 720)]:
        R_points = surface[:, 0]
        Z_points = surface[:, 1]
        distances = np.sqrt((R_points - 2.0)**2 + Z_points**2)
        expected_radius = np.sqrt(0.5)

        assert np.allclose(distances, expected_radius, rtol=0.1), \
            f"Points should form a circle for n_rays={n_rays}"


def test_flux_surface_performance_different_quality_levels():
    """Test flux surface extraction at different quality levels."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create equilibrium
    R_grid = np.linspace(1.5, 2.5, 25)
    Z_grid = np.linspace(-1.0, 1.0, 25)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 25,
        'NZ': 25,
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

    # Test different quality levels
    quality_levels = {
        'preview': 60,      # Low quality for fast preview
        'medium': 180,      # Medium quality
        'high': 360,        # High quality (default)
        'very_high': 720,   # Very high quality
    }

    for quality_name, n_rays in quality_levels.items():
        extractor = FluxSurfaceExtractor(eq, n_rays=n_rays)
        surfaces = extractor.extract_by_psiN([0.25, 0.5, 0.75])

        # All should return 3 surfaces
        assert len(surfaces) == 3, f"Should return 3 surfaces for {quality_name}"

        # Each surface should have points
        for surface in surfaces:
            assert len(surface) > 0, f"Surface should have points for {quality_name}"


def test_flux_surface_point_count_consistency():
    """Test that flux surfaces have consistent point counts (T11.2)."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium
    R_grid = np.linspace(1.0, 3.0, 30)
    Z_grid = np.linspace(-1.5, 1.5, 30)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 30,
        'NZ': 30,
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

    extractor = FluxSurfaceExtractor(eq, n_rays=100)
    surfaces = extractor.extract_by_psiN([0.2, 0.4, 0.6, 0.8])

    # All surfaces should have consistent point count (n_rays + 1 for closure)
    expected_points = 101  # n_rays + 1
    for i, surface in enumerate(surfaces):
        actual_points = len(surface)
        assert actual_points == expected_points, \
            f"Surface {i} has {actual_points} points, expected {expected_points}"


def test_flux_surface_closed_curve_ordering():
    """Test that flux surface points are ordered consistently in closed curves (T11.2)."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create circular equilibrium
    R_grid = np.linspace(1.0, 3.0, 30)
    Z_grid = np.linspace(-1.5, 1.5, 30)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 30,
        'NZ': 30,
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

    extractor = FluxSurfaceExtractor(eq, n_rays=72)
    surfaces = extractor.extract_by_psiN([0.5])

    surface = surfaces[0]

    # Check that curve is closed (first == last)
    assert np.allclose(surface[0], surface[-1], atol=1e-6), \
        "Flux surface curve should be closed (first point == last point)"

    # Check that points are ordered consistently (no jumps)
    distances = []
    for i in range(len(surface) - 1):
        dist = np.linalg.norm(surface[i+1] - surface[i])
        distances.append(dist)

    distances = np.array(distances)
    mean_dist = np.mean(distances)

    # No distance should be more than 3x the mean (no large jumps)
    max_allowed = 3 * mean_dist
    assert np.all(distances < max_allowed), \
        f"Points should be consistently ordered with no large jumps. Max dist: {np.max(distances)}, mean: {mean_dist}"


# T12.1 - Low-res preview mode tests

def test_flux_surface_extractor_has_preview_mode():
    """Test that FluxSurfaceExtractor has a low-res preview mode."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create simple test equilibrium
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
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 1.0,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    # Create extractor with preview mode
    extractor = FluxSurfaceExtractor(eq, n_rays=360, preview_mode=True)

    # In preview mode, n_rays should be reduced
    assert hasattr(extractor, 'preview_mode'), \
        "FluxSurfaceExtractor should have preview_mode attribute"
    assert extractor.preview_mode is True, \
        "preview_mode should be True when set"


# T12.2 - Robust multi-intersection logic near X-point

def test_flux_surface_handles_missing_intersections_gracefully():
    """Test that flux surface extraction handles missing ray intersections gracefully."""
    from mesh_gui_project.core.equilibrium import EquilibriumData
    from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
    from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

    # Create equilibrium with limited extent (some rays may miss)
    R_grid = np.linspace(1.5, 2.5, 30)
    Z_grid = np.linspace(-0.5, 0.5, 30)

    R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid, indexing='ij')
    psi_grid = ((R_mesh - 2.0)**2 + Z_mesh**2).T

    data = {
        'NR': 30,
        'NZ': 30,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 2.0,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 0.5,
    }

    eq = EquilibriumData(data)
    interp = make_bicubic_interpolator(R_grid, Z_grid, psi_grid)
    eq.attach_interpolator(interp)

    # Extract a surface that's close to the boundary (may have missing intersections)
    extractor = FluxSurfaceExtractor(eq, n_rays=72)

    # This should not crash even if some rays don't find intersections
    surfaces = extractor.extract_by_psiN([0.45])

    # Should return a surface (even if not all rays succeeded)
    assert len(surfaces) == 1, "Should return one surface"
    surface = surfaces[0]

    # Surface should have at least some points
    assert len(surface) > 10, f"Surface should have at least 10 points, got {len(surface)}"
