"""Test mesh generation for flux-aligned triangular meshes."""
import numpy as np
import pytest


def test_mesher_module_exists():
    """Test that mesher module can be imported."""
    from mesh_gui_project.core import mesher

    assert hasattr(mesher, 'FluxMesher'), \
        "mesher module should have FluxMesher class"


def test_flux_mesher_can_be_instantiated():
    """Test that FluxMesher can be instantiated."""
    from mesh_gui_project.core.mesher import FluxMesher

    mesher = FluxMesher()

    assert mesher is not None


def test_flux_mesher_has_build_structured_method():
    """Test that FluxMesher has build_structured method."""
    from mesh_gui_project.core.mesher import FluxMesher

    mesher = FluxMesher()

    assert hasattr(mesher, 'build_structured'), \
        "FluxMesher should have build_structured method"
    assert callable(mesher.build_structured), \
        "build_structured should be callable"


def test_build_structured_returns_vertices_and_elements():
    """Test that build_structured returns vertices and elements arrays."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create simple circular flux surfaces
    n_surfaces = 3
    n_points_per_surface = 36

    surfaces = []
    for i in range(n_surfaces):
        radius = 0.2 + i * 0.2  # Radii: 0.2, 0.4, 0.6
        theta = np.linspace(0, 2*np.pi, n_points_per_surface, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        # Close the curve
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces)

    assert isinstance(vertices, np.ndarray), "vertices should be numpy array"
    assert isinstance(elements, np.ndarray), "elements should be numpy array"
    assert vertices.ndim == 2, "vertices should be 2D array"
    assert elements.ndim == 2, "elements should be 2D array"
    assert vertices.shape[1] == 2, "vertices should have 2 columns (R, Z)"
    assert elements.shape[1] == 3, "elements should have 3 columns (triangle indices)"


def test_build_structured_with_axis_point():
    """Test that structured mesh includes axis point (O-point) at center."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create circular flux surfaces
    surfaces = []
    for i in range(2):
        radius = 0.3 + i * 0.3
        theta = np.linspace(0, 2*np.pi, 24, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # First vertex should be the axis point
    assert np.isclose(vertices[0, 0], 2.0, atol=1e-6), \
        f"First vertex R should be axis point R=2.0, got {vertices[0, 0]}"
    assert np.isclose(vertices[0, 1], 0.0, atol=1e-6), \
        f"First vertex Z should be axis point Z=0.0, got {vertices[0, 1]}"


def test_build_structured_creates_correct_number_of_elements():
    """Test that structured mesh has correct number of triangular elements."""
    from mesh_gui_project.core.mesher import FluxMesher

    n_surfaces = 3
    n_points = 20  # Points per surface (without closure point)

    surfaces = []
    for i in range(n_surfaces):
        radius = 0.2 + i * 0.15
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # Expected elements:
    # - Axis to first surface: n_points triangles
    # - Between each pair of surfaces: 2 * n_points triangles
    expected_elements = n_points + (n_surfaces - 1) * 2 * n_points

    assert elements.shape[0] == expected_elements, \
        f"Should have {expected_elements} elements, got {elements.shape[0]}"


def test_build_structured_elements_are_valid_indices():
    """Test that all element indices are valid."""
    from mesh_gui_project.core.mesher import FluxMesher

    surfaces = []
    for i in range(2):
        radius = 0.3 + i * 0.3
        theta = np.linspace(0, 2*np.pi, 18, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # All element indices should be within vertex array bounds
    assert np.all(elements >= 0), "All element indices should be non-negative"
    assert np.all(elements < len(vertices)), \
        f"All element indices should be < {len(vertices)}, got max {elements.max()}"


def test_build_structured_without_axis_point():
    """Test structured mesh generation without axis point."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create 2 surfaces
    n_points = 24

    surfaces = []
    for i in range(2):
        radius = 0.3 + i * 0.2
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    # Without axis point, mesh starts from first surface
    vertices, elements = mesher.build_structured(surfaces, axis_point=None)

    # Should have elements only between the two surfaces
    # Each quad between surfaces becomes 2 triangles
    expected_elements = 2 * n_points

    assert elements.shape[0] == expected_elements, \
        f"Should have {expected_elements} elements, got {elements.shape[0]}"


def test_build_structured_handles_cyclic_wrap():
    """Test that mesh correctly handles cyclic wrapping."""
    from mesh_gui_project.core.mesher import FluxMesher

    n_points = 12

    surfaces = []
    for i in range(2):
        radius = 0.2 + i * 0.2
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # Check that elements reference vertices correctly
    # The last triangles in each ring should connect back to the first points
    for elem in elements:
        # All three vertices should be different (no degenerate triangles)
        assert len(set(elem)) == 3, f"Element {elem} has duplicate vertices"


def test_build_structured_mesh_quality():
    """Test basic mesh quality - no inverted elements."""
    from mesh_gui_project.core.mesher import FluxMesher

    n_points = 30

    surfaces = []
    for i in range(3):
        radius = 0.2 + i * 0.15
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # Check winding orientation - compute signed area
    for elem_idx, elem in enumerate(elements):
        v0 = vertices[elem[0]]
        v1 = vertices[elem[1]]
        v2 = vertices[elem[2]]

        # Signed area = 0.5 * cross product
        area = 0.5 * ((v1[0] - v0[0]) * (v2[1] - v0[1]) -
                      (v2[0] - v0[0]) * (v1[1] - v0[1]))

        # All elements should have consistent (positive) orientation
        assert area > 0, f"Element {elem_idx} has negative area (inverted): {area}"


def test_mesh_quality_compute_aspect_ratios():
    """Test computation of element aspect ratios."""
    from mesh_gui_project.core.mesher import compute_mesh_quality

    # Create simple mesh with known geometry
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ])

    # Equilateral-ish triangles
    elements = np.array([
        [0, 1, 2],
        [1, 3, 2],
    ], dtype=np.int32)

    quality_dict = compute_mesh_quality(vertices, elements)

    assert 'aspect_ratios' in quality_dict, "Should compute aspect ratios"
    assert len(quality_dict['aspect_ratios']) == 2, "Should have 2 aspect ratios"
    assert all(ar > 0 for ar in quality_dict['aspect_ratios']), \
        "All aspect ratios should be positive"


def test_mesh_quality_compute_min_angles():
    """Test computation of minimum angles in elements."""
    from mesh_gui_project.core.mesher import compute_mesh_quality

    # Right triangle
    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ])

    elements = np.array([[0, 1, 2]], dtype=np.int32)

    quality_dict = compute_mesh_quality(vertices, elements)

    assert 'min_angles' in quality_dict, "Should compute minimum angles"
    assert len(quality_dict['min_angles']) == 1, "Should have 1 min angle"

    # Right triangle has 45-45-90 degrees, min angle = 45
    min_angle = quality_dict['min_angles'][0]
    assert 40 < min_angle < 50, f"Min angle should be ~45 degrees, got {min_angle}"


def test_mesh_quality_no_inverted_elements():
    """Test detection of inverted elements."""
    from mesh_gui_project.core.mesher import compute_mesh_quality

    vertices = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, 1.0],
    ])

    # Correct winding (CCW)
    elements_good = np.array([[0, 1, 2]], dtype=np.int32)

    quality_good = compute_mesh_quality(vertices, elements_good)
    assert 'n_inverted' in quality_good, "Should count inverted elements"
    assert quality_good['n_inverted'] == 0, "Should have no inverted elements"

    # Inverted winding (CW)
    elements_bad = np.array([[0, 2, 1]], dtype=np.int32)

    quality_bad = compute_mesh_quality(vertices, elements_bad)
    assert quality_bad['n_inverted'] == 1, "Should detect inverted element"


def test_mesh_quality_statistics():
    """Test that mesh quality returns summary statistics."""
    from mesh_gui_project.core.mesher import compute_mesh_quality
    from mesh_gui_project.core.mesher import FluxMesher

    # Create structured mesh
    surfaces = []
    for i in range(3):
        radius = 0.3 + i * 0.2
        theta = np.linspace(0, 2*np.pi, 24, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    quality = compute_mesh_quality(vertices, elements)

    # Should have summary statistics
    assert 'min_angle_min' in quality, "Should have min of min angles"
    assert 'min_angle_mean' in quality, "Should have mean of min angles"
    assert 'aspect_ratio_max' in quality, "Should have max aspect ratio"
    assert 'aspect_ratio_mean' in quality, "Should have mean aspect ratio"


def test_flux_mesher_has_quality_method():
    """Test that FluxMesher has convenience method for quality checks."""
    from mesh_gui_project.core.mesher import FluxMesher

    mesher = FluxMesher()

    # Should have method to check quality
    assert hasattr(mesher, 'check_quality'), \
        "FluxMesher should have check_quality method"
    assert callable(mesher.check_quality), \
        "check_quality should be callable"


# T7.1 - Boundary construction tests

def test_flux_mesher_has_create_boundary_method():
    """Test that FluxMesher has create_boundary method."""
    from mesh_gui_project.core.mesher import FluxMesher

    mesher = FluxMesher()

    assert hasattr(mesher, 'create_boundary'), \
        "FluxMesher should have create_boundary method"
    assert callable(mesher.create_boundary), \
        "create_boundary should be callable"


def test_create_boundary_from_surface():
    """Test creating boundary polyline from a flux surface."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create a simple closed surface
    n_points = 24
    theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    R = 2.0 + 0.5 * np.cos(theta)
    Z = 0.0 + 0.5 * np.sin(theta)
    surface = np.column_stack([R, Z])
    surface = np.vstack([surface, surface[0:1]])  # Close the curve

    mesher = FluxMesher()
    boundary = mesher.create_boundary(surface)

    assert isinstance(boundary, np.ndarray), "boundary should be numpy array"
    assert boundary.ndim == 2, "boundary should be 2D array"
    assert boundary.shape[1] == 2, "boundary should have 2 columns (R, Z)"
    # Boundary should include closure point
    assert len(boundary) >= n_points, f"boundary should have at least {n_points} points"


def test_create_boundary_preserves_closure():
    """Test that boundary polyline is properly closed."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create closed surface
    n_points = 20
    theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    R = 1.5 + 0.3 * np.cos(theta)
    Z = 0.0 + 0.3 * np.sin(theta)
    surface = np.column_stack([R, Z])
    surface = np.vstack([surface, surface[0:1]])

    mesher = FluxMesher()
    boundary = mesher.create_boundary(surface)

    # First and last point should be the same (or very close)
    assert np.allclose(boundary[0], boundary[-1], atol=1e-10), \
        "Boundary should be closed (first point = last point)"


def test_create_inner_outer_boundaries():
    """Test creating separate inner and outer boundaries."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Inner boundary (last closed surface)
    n_points = 30
    theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    R_inner = 2.0 + 0.4 * np.cos(theta)
    Z_inner = 0.0 + 0.4 * np.sin(theta)
    inner_surface = np.column_stack([R_inner, Z_inner])
    inner_surface = np.vstack([inner_surface, inner_surface[0:1]])

    # Outer boundary (limiter)
    n_lim = 50
    theta_lim = np.linspace(0, 2*np.pi, n_lim, endpoint=False)
    R_outer = 2.0 + 1.0 * np.cos(theta_lim)
    Z_outer = 0.0 + 1.0 * np.sin(theta_lim)
    outer_surface = np.column_stack([R_outer, Z_outer])
    outer_surface = np.vstack([outer_surface, outer_surface[0:1]])

    mesher = FluxMesher()
    inner_boundary = mesher.create_boundary(inner_surface)
    outer_boundary = mesher.create_boundary(outer_surface)

    # Both should be valid closed boundaries
    assert len(inner_boundary) >= n_points, "Inner boundary should have correct size"
    assert len(outer_boundary) >= n_lim, "Outer boundary should have correct size"
    assert np.allclose(inner_boundary[0], inner_boundary[-1]), "Inner should be closed"
    assert np.allclose(outer_boundary[0], outer_boundary[-1]), "Outer should be closed"


def test_boundary_densification_option():
    """Test optional densification of boundary near tight regions."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create simple surface
    n_points = 20
    theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    R = 2.0 + 0.5 * np.cos(theta)
    Z = 0.0 + 0.5 * np.sin(theta)
    surface = np.column_stack([R, Z])
    surface = np.vstack([surface, surface[0:1]])

    mesher = FluxMesher()

    # Without densification
    boundary_normal = mesher.create_boundary(surface, densify=False)

    # With densification
    boundary_dense = mesher.create_boundary(surface, densify=True, target_spacing=0.05)

    # Densified version should have more points
    assert len(boundary_dense) >= len(boundary_normal), \
        "Densified boundary should have at least as many points"

    # Both should still be closed
    assert np.allclose(boundary_normal[0], boundary_normal[-1])
    assert np.allclose(boundary_dense[0], boundary_dense[-1])


# T7.2 - Gmsh API integration tests

def test_flux_mesher_has_build_unstructured_SOL_method():
    """Test that FluxMesher has build_unstructured_SOL method."""
    from mesh_gui_project.core.mesher import FluxMesher

    mesher = FluxMesher()

    assert hasattr(mesher, 'build_unstructured_SOL'), \
        "FluxMesher should have build_unstructured_SOL method"
    assert callable(mesher.build_unstructured_SOL), \
        "build_unstructured_SOL should be callable"


def test_build_unstructured_SOL_returns_vertices_and_elements():
    """Test that build_unstructured_SOL returns vertices and elements."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create inner boundary (smaller circle)
    n_inner = 30
    theta = np.linspace(0, 2*np.pi, n_inner, endpoint=False)
    R_inner = 2.0 + 0.4 * np.cos(theta)
    Z_inner = 0.0 + 0.4 * np.sin(theta)
    inner_poly = np.column_stack([R_inner, Z_inner])
    inner_poly = np.vstack([inner_poly, inner_poly[0:1]])

    # Create outer boundary (larger circle)
    n_outer = 50
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    R_outer = 2.0 + 1.0 * np.cos(theta_outer)
    Z_outer = 0.0 + 1.0 * np.sin(theta_outer)
    outer_poly = np.column_stack([R_outer, Z_outer])
    outer_poly = np.vstack([outer_poly, outer_poly[0:1]])

    mesher = FluxMesher()
    vertices, elements = mesher.build_unstructured_SOL(inner_poly, outer_poly, target_size=0.1)

    assert isinstance(vertices, np.ndarray), "vertices should be numpy array"
    assert isinstance(elements, np.ndarray), "elements should be numpy array"
    assert vertices.ndim == 2, "vertices should be 2D array"
    assert elements.ndim == 2, "elements should be 2D array"
    assert vertices.shape[1] == 2, "vertices should have 2 columns (R, Z)"
    assert elements.shape[1] == 3, "elements should have 3 columns (triangle indices)"


def test_build_unstructured_SOL_elements_are_valid():
    """Test that SOL mesh has valid element indices."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Simple boundaries
    n_inner = 24
    theta = np.linspace(0, 2*np.pi, n_inner, endpoint=False)
    inner_poly = np.column_stack([2.0 + 0.3 * np.cos(theta), 0.3 * np.sin(theta)])
    inner_poly = np.vstack([inner_poly, inner_poly[0:1]])

    n_outer = 36
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    outer_poly = np.column_stack([2.0 + 0.8 * np.cos(theta_outer), 0.8 * np.sin(theta_outer)])
    outer_poly = np.vstack([outer_poly, outer_poly[0:1]])

    mesher = FluxMesher()
    vertices, elements = mesher.build_unstructured_SOL(inner_poly, outer_poly, target_size=0.1)

    # All element indices should be within vertex array bounds
    assert np.all(elements >= 0), "All element indices should be non-negative"
    assert np.all(elements < len(vertices)), \
        f"All element indices should be < {len(vertices)}, got max {elements.max()}"


def test_build_unstructured_SOL_no_inverted_elements():
    """Test that SOL mesh has no inverted elements."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create boundaries
    n_inner = 20
    theta = np.linspace(0, 2*np.pi, n_inner, endpoint=False)
    inner_poly = np.column_stack([2.0 + 0.4 * np.cos(theta), 0.4 * np.sin(theta)])
    inner_poly = np.vstack([inner_poly, inner_poly[0:1]])

    n_outer = 30
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    outer_poly = np.column_stack([2.0 + 0.9 * np.cos(theta_outer), 0.9 * np.sin(theta_outer)])
    outer_poly = np.vstack([outer_poly, outer_poly[0:1]])

    mesher = FluxMesher()
    vertices, elements = mesher.build_unstructured_SOL(inner_poly, outer_poly, target_size=0.15)

    # Check all elements have positive area
    for elem_idx, elem in enumerate(elements):
        v0 = vertices[elem[0]]
        v1 = vertices[elem[1]]
        v2 = vertices[elem[2]]

        area = 0.5 * ((v1[0] - v0[0]) * (v2[1] - v0[1]) -
                      (v2[0] - v0[0]) * (v1[1] - v0[1]))

        assert area > 0, f"Element {elem_idx} has negative area (inverted): {area}"


def test_build_unstructured_SOL_inner_boundary_vertices_match():
    """Test that inner boundary vertices are preserved in SOL mesh."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create inner boundary
    n_inner = 20
    theta = np.linspace(0, 2*np.pi, n_inner, endpoint=False)
    R_inner = 2.0 + 0.5 * np.cos(theta)
    Z_inner = 0.0 + 0.5 * np.sin(theta)
    inner_poly = np.column_stack([R_inner, Z_inner])
    inner_poly = np.vstack([inner_poly, inner_poly[0:1]])

    # Create outer boundary
    n_outer = 30
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    R_outer = 2.0 + 1.0 * np.cos(theta_outer)
    Z_outer = 0.0 + 1.0 * np.sin(theta_outer)
    outer_poly = np.column_stack([R_outer, Z_outer])
    outer_poly = np.vstack([outer_poly, outer_poly[0:1]])

    mesher = FluxMesher()
    vertices, elements = mesher.build_unstructured_SOL(inner_poly, outer_poly, target_size=0.1)

    # Inner boundary points (excluding last closure point) should appear in vertices
    inner_points = inner_poly[:-1]

    # Check that inner boundary points are in the mesh vertices
    for point in inner_points:
        # Find if this point exists in vertices (within tolerance)
        distances = np.linalg.norm(vertices - point, axis=1)
        min_distance = np.min(distances)
        assert min_distance < 1e-6, \
            f"Inner boundary point {point} not found in mesh vertices (min dist: {min_distance})"


def test_build_unstructured_SOL_handles_gmsh_errors():
    """Test that Gmsh errors are handled gracefully."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create invalid boundaries (inner larger than outer - should fail)
    n_inner = 20
    theta = np.linspace(0, 2*np.pi, n_inner, endpoint=False)
    inner_poly = np.column_stack([2.0 + 1.5 * np.cos(theta), 1.5 * np.sin(theta)])
    inner_poly = np.vstack([inner_poly, inner_poly[0:1]])

    n_outer = 20
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    outer_poly = np.column_stack([2.0 + 0.5 * np.cos(theta_outer), 0.5 * np.sin(theta_outer)])
    outer_poly = np.vstack([outer_poly, outer_poly[0:1]])

    mesher = FluxMesher()

    # Should raise an exception with clear error message
    with pytest.raises(Exception) as exc_info:
        mesher.build_unstructured_SOL(inner_poly, outer_poly, target_size=0.1)

    # Error message should mention the issue
    assert "boundary" in str(exc_info.value).lower() or "gmsh" in str(exc_info.value).lower()


# T7.3 - Merge final mesh tests

def test_flux_mesher_has_build_method():
    """Test that FluxMesher has build method to merge structured and SOL meshes."""
    from mesh_gui_project.core.mesher import FluxMesher

    mesher = FluxMesher()

    assert hasattr(mesher, 'build'), \
        "FluxMesher should have build method"
    assert callable(mesher.build), \
        "build should be callable"


def test_build_merges_structured_and_sol_meshes():
    """Test that build method merges structured and SOL meshes."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create flux surfaces for structured mesh
    n_surfaces = 3
    n_points = 20

    surfaces = []
    for i in range(n_surfaces):
        radius = 0.2 + i * 0.1
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    # Create outer boundary for SOL
    n_outer = 30
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    R_outer = 2.0 + 0.7 * np.cos(theta_outer)
    Z_outer = 0.0 + 0.7 * np.sin(theta_outer)
    outer_boundary = np.column_stack([R_outer, Z_outer])
    outer_boundary = np.vstack([outer_boundary, outer_boundary[0:1]])

    mesher = FluxMesher()

    # Build merged mesh
    vertices, elements = mesher.build(
        surfaces=surfaces,
        axis_point=(2.0, 0.0),
        outer_boundary=outer_boundary,
        target_size=0.1
    )

    assert isinstance(vertices, np.ndarray), "vertices should be numpy array"
    assert isinstance(elements, np.ndarray), "elements should be numpy array"
    assert vertices.ndim == 2, "vertices should be 2D array"
    assert elements.ndim == 2, "elements should be 2D array"
    assert vertices.shape[1] == 2, "vertices should have 2 columns (R, Z)"
    assert elements.shape[1] == 3, "elements should have 3 columns (triangle indices)"


def test_build_merged_mesh_has_valid_elements():
    """Test that merged mesh has valid element indices."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Simple test case
    n_points = 15

    surfaces = []
    for i in range(2):
        radius = 0.2 + i * 0.15
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    n_outer = 25
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    outer_boundary = np.column_stack([
        2.0 + 0.6 * np.cos(theta_outer),
        0.0 + 0.6 * np.sin(theta_outer)
    ])
    outer_boundary = np.vstack([outer_boundary, outer_boundary[0:1]])

    mesher = FluxMesher()
    vertices, elements = mesher.build(
        surfaces=surfaces,
        axis_point=(2.0, 0.0),
        outer_boundary=outer_boundary,
        target_size=0.1
    )

    # All element indices should be within vertex array bounds
    assert np.all(elements >= 0), "All element indices should be non-negative"
    assert np.all(elements < len(vertices)), \
        f"All element indices should be < {len(vertices)}, got max {elements.max()}"


def test_build_merged_mesh_no_duplicate_vertices():
    """Test that merged mesh has no duplicate vertices at boundary."""
    from mesh_gui_project.core.mesher import FluxMesher

    n_points = 18

    surfaces = []
    for i in range(2):
        radius = 0.25 + i * 0.1
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    n_outer = 24
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    outer_boundary = np.column_stack([
        2.0 + 0.55 * np.cos(theta_outer),
        0.0 + 0.55 * np.sin(theta_outer)
    ])
    outer_boundary = np.vstack([outer_boundary, outer_boundary[0:1]])

    mesher = FluxMesher()
    vertices, elements = mesher.build(
        surfaces=surfaces,
        axis_point=(2.0, 0.0),
        outer_boundary=outer_boundary,
        target_size=0.08,
        merge_tolerance=1e-6
    )

    # Check for duplicate vertices
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            dist = np.linalg.norm(vertices[i] - vertices[j])
            assert dist > 1e-7, \
                f"Vertices {i} and {j} are duplicates (distance: {dist})"


def test_build_merged_mesh_no_inverted_elements():
    """Test that merged mesh has no inverted elements."""
    from mesh_gui_project.core.mesher import FluxMesher

    n_points = 16

    surfaces = []
    for i in range(2):
        radius = 0.3 + i * 0.12
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    n_outer = 28
    theta_outer = np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    outer_boundary = np.column_stack([
        2.0 + 0.65 * np.cos(theta_outer),
        0.0 + 0.65 * np.sin(theta_outer)
    ])
    outer_boundary = np.vstack([outer_boundary, outer_boundary[0:1]])

    mesher = FluxMesher()
    vertices, elements = mesher.build(
        surfaces=surfaces,
        axis_point=(2.0, 0.0),
        outer_boundary=outer_boundary,
        target_size=0.1
    )

    # Check all elements have positive area
    for elem_idx, elem in enumerate(elements):
        v0 = vertices[elem[0]]
        v1 = vertices[elem[1]]
        v2 = vertices[elem[2]]

        area = 0.5 * ((v1[0] - v0[0]) * (v2[1] - v0[1]) -
                      (v2[0] - v0[0]) * (v1[1] - v0[1]))

        assert area > 0, f"Element {elem_idx} has negative area (inverted): {area}"


def test_build_structured_only_without_sol():
    """Test that build can create structured mesh only (no SOL)."""
    from mesh_gui_project.core.mesher import FluxMesher

    n_points = 20

    surfaces = []
    for i in range(3):
        radius = 0.2 + i * 0.15
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()

    # Build with no outer boundary (structured only)
    vertices, elements = mesher.build(
        surfaces=surfaces,
        axis_point=(2.0, 0.0),
        outer_boundary=None
    )

    # Should still work
    assert len(vertices) > 0, "Should have vertices"
    assert len(elements) > 0, "Should have elements"

    # Expected elements: n_points + (n_surfaces - 1) * 2 * n_points
    expected_elements = n_points + (3 - 1) * 2 * n_points
    assert elements.shape[0] == expected_elements, \
        f"Should have {expected_elements} elements, got {elements.shape[0]}"


def test_mesh_has_no_duplicate_nodes():
    """Test that generated mesh has no duplicate nodes (T11.2)."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create circular flux surfaces
    n_surfaces = 3
    n_points = 24

    surfaces = []
    for i in range(n_surfaces):
        radius = 0.2 + i * 0.2
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # Check for duplicate vertices (within tolerance)
    tolerance = 1e-10
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            dist = np.linalg.norm(vertices[i] - vertices[j])
            assert dist > tolerance, \
                f"Duplicate nodes found at indices {i} and {j}: distance {dist} < {tolerance}"


def test_mesh_has_no_inverted_elements():
    """Test that generated mesh has no inverted triangular elements (T11.2)."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create circular flux surfaces
    n_surfaces = 4
    n_points = 36

    surfaces = []
    for i in range(n_surfaces):
        radius = 0.15 + i * 0.15
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # Check each triangle for positive signed area
    for i, elem in enumerate(elements):
        v0 = vertices[elem[0]]
        v1 = vertices[elem[1]]
        v2 = vertices[elem[2]]

        # Signed area = 0.5 * ((x1-x0)*(y2-y0) - (x2-x0)*(y1-y0))
        signed_area = 0.5 * ((v1[0]-v0[0])*(v2[1]-v0[1]) - (v2[0]-v0[0])*(v1[1]-v0[1]))

        assert signed_area > 0, \
            f"Element {i} is inverted: signed area = {signed_area}"


def test_mesh_quality_metrics():
    """Test that mesh quality metrics are within acceptable ranges (T11.2)."""
    from mesh_gui_project.core.mesher import FluxMesher

    # Create circular flux surfaces
    n_surfaces = 3
    n_points = 48

    surfaces = []
    for i in range(n_surfaces):
        radius = 0.2 + i * 0.2
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        R = 2.0 + radius * np.cos(theta)
        Z = 0.0 + radius * np.sin(theta)
        surface = np.column_stack([R, Z])
        surface = np.vstack([surface, surface[0:1]])
        surfaces.append(surface)

    mesher = FluxMesher()
    vertices, elements = mesher.build_structured(surfaces, axis_point=(2.0, 0.0))

    # Check aspect ratios
    aspect_ratios = []
    for elem in elements:
        v0 = vertices[elem[0]]
        v1 = vertices[elem[1]]
        v2 = vertices[elem[2]]

        # Edge lengths
        e0 = np.linalg.norm(v1 - v0)
        e1 = np.linalg.norm(v2 - v1)
        e2 = np.linalg.norm(v0 - v2)

        # Aspect ratio = max_edge / min_edge
        aspect_ratio = max(e0, e1, e2) / min(e0, e1, e2)
        aspect_ratios.append(aspect_ratio)

    # Most elements should have reasonable aspect ratios (< 5)
    aspect_ratios = np.array(aspect_ratios)
    median_ar = np.median(aspect_ratios)
    assert median_ar < 5.0, \
        f"Median aspect ratio should be < 5.0, got {median_ar}"
