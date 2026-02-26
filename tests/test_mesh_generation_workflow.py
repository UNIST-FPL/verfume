"""
Tests for MeshGenerationWorkflow class.

Following TDD approach: write tests first, then implement.
The MeshGenerationWorkflow coordinates mesh generation from boundary selection
to optimization, extracting complex workflow logic from MainWindow.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch


class TestMeshGenerationWorkflowConstruction:
    """Test MeshGenerationWorkflow construction and initialization."""

    def test_workflow_can_be_instantiated(self):
        """MeshGenerationWorkflow should be instantiable."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        assert workflow is not None


class TestGenerateMeshFromBoundary:
    """Test mesh generation from boundary contour."""

    @pytest.mark.slow
    def test_generate_mesh_with_psi_boundary(self):
        """Should generate mesh from PSI boundary contour."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow
        from mesh_gui_project.data.geqdsk_parser import parse_geqdsk
        from mesh_gui_project.core.equilibrium import EquilibriumData
        from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
        import os

        # Load real equilibrium file for this test
        test_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            'examples',
            'kstar_EFIT01_35582_010000.esy_headerMod.geqdsk'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test GEQDSK file not found")

        data = parse_geqdsk(test_file)
        equilibrium = EquilibriumData(data)
        # Attach interpolator for PSI gradient calculations
        interp = make_bicubic_interpolator(data['R_grid'], data['Z_grid'], data['psi_grid'])
        equilibrium.attach_interpolator(interp)

        workflow = MeshGenerationWorkflow()

        # Generate mesh from PSI value
        psi_value = 0.95  # Use normalized PSI near edge
        mesh_size = 0.05

        result = workflow.generate_mesh_from_psi(
            equilibrium=equilibrium,
            psi_value=psi_value,
            target_element_size=mesh_size
        )

        # Should return mesh data
        assert result is not None
        assert 'vertices' in result
        assert 'elements' in result
        assert 'boundary' in result
        assert 'boundary_vertex_indices' in result
        assert 'metrics' in result

        # Verify mesh structure
        assert result['vertices'].shape[1] == 2  # 2D vertices
        assert result['elements'].shape[1] == 3  # Triangular elements
        assert len(result['vertices']) > 0
        assert len(result['elements']) > 0

    def test_generate_mesh_with_limiter_boundary(self):
        """Should generate mesh using limiter as boundary."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow
        from mesh_gui_project.core.equilibrium import EquilibriumData

        # Create mock equilibrium with limiter
        equilibrium = Mock(spec=EquilibriumData)
        limiter = np.array([
            [1.0, 0.5],
            [1.5, 0.5],
            [1.5, -0.5],
            [1.0, -0.5]
        ])
        equilibrium.limiter_curve = limiter

        workflow = MeshGenerationWorkflow()

        # Generate mesh from limiter
        mesh_size = 0.05

        result = workflow.generate_mesh_from_limiter(
            equilibrium=equilibrium,
            target_element_size=mesh_size
        )

        # Should return mesh data
        assert result is not None
        assert 'vertices' in result
        assert 'elements' in result
        assert 'boundary' in result
        assert np.allclose(result['boundary'], limiter)

    def test_generate_mesh_validates_parameters(self):
        """Should validate mesh generation parameters."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Test with invalid mesh size (too small)
        with pytest.raises(ValueError, match="element_size must be positive"):
            workflow.generate_mesh_from_psi(
                equilibrium=Mock(),
                psi_value=0.5,
                target_element_size=-0.01
            )

        # Test with invalid mesh size (zero)
        with pytest.raises(ValueError, match="element_size must be positive"):
            workflow.generate_mesh_from_psi(
                equilibrium=Mock(),
                psi_value=0.5,
                target_element_size=0.0
            )

    def test_generate_mesh_without_equilibrium(self):
        """Should raise error if no equilibrium provided."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        with pytest.raises(ValueError, match="equilibrium is required"):
            workflow.generate_mesh_from_psi(
                equilibrium=None,
                psi_value=0.5,
                target_element_size=0.05
            )


class TestBoundaryVertexIdentification:
    """Test identification of boundary vertices."""

    def test_identify_boundary_vertices_exact_match(self):
        """Should identify vertices that exactly match boundary points."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Create simple mesh with some vertices on boundary
        vertices = np.array([
            [0.0, 0.0],  # On boundary
            [1.0, 0.0],  # On boundary
            [0.5, 0.5],  # Interior
            [1.0, 1.0],  # On boundary
            [0.0, 1.0],  # On boundary
        ])

        boundary = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ])

        boundary_indices = workflow.identify_boundary_vertices(vertices, boundary)

        # Should identify vertices 0, 1, 3, 4 as boundary vertices
        assert 0 in boundary_indices
        assert 1 in boundary_indices
        assert 2 not in boundary_indices  # Interior vertex
        assert 3 in boundary_indices
        assert 4 in boundary_indices

    def test_identify_boundary_vertices_with_tolerance(self):
        """Should identify vertices near boundary within tolerance."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Create vertices slightly off boundary (within tolerance)
        vertices = np.array([
            [0.0005, 0.0],    # Near boundary point
            [1.0, 0.0003],    # Near boundary point
            [0.5, 0.5],       # Interior
        ])

        boundary = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ])

        tolerance = 0.001
        boundary_indices = workflow.identify_boundary_vertices(
            vertices, boundary, tolerance=tolerance
        )

        # Should identify vertices 0, 1 (within tolerance)
        assert 0 in boundary_indices
        assert 1 in boundary_indices
        assert 2 not in boundary_indices

    def test_identify_boundary_vertices_on_edges(self):
        """Should identify vertices on boundary edges (between points)."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Create vertices on edges
        vertices = np.array([
            [0.5, 0.0],   # On edge between (0,0) and (1,0)
            [1.0, 0.5],   # On edge between (1,0) and (1,1)
            [0.5, 0.5],   # Interior
        ])

        boundary = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ])

        boundary_indices = workflow.identify_boundary_vertices(vertices, boundary)

        # Should identify vertices on edges
        assert 0 in boundary_indices
        assert 1 in boundary_indices
        assert 2 not in boundary_indices


class TestRemeshAndOptimize:
    """Test remeshing and optimization workflow."""

    def test_remesh_and_optimize_basic(self):
        """Should remesh and optimize existing mesh."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Create simple mesh
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
            [0.5, 0.5]
        ])

        elements = np.array([
            [0, 1, 4],
            [1, 2, 4],
            [2, 3, 4],
            [3, 0, 4]
        ])

        result = workflow.remesh_and_optimize(
            vertices=vertices,
            elements=elements,
            n_iterations=5
        )

        # Should return optimized mesh
        assert result is not None
        assert 'vertices' in result
        assert 'elements' in result
        assert 'metrics' in result

        # Should have same or similar number of vertices/elements
        assert len(result['vertices']) > 0
        assert len(result['elements']) > 0

    def test_remesh_preserves_constrained_vertices(self):
        """Should preserve boundary and manually moved vertices during optimization."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Create mesh with constrained vertices
        vertices = np.array([
            [0.0, 0.0],  # Boundary
            [1.0, 0.0],  # Boundary
            [1.0, 1.0],  # Boundary
            [0.0, 1.0],  # Boundary
            [0.5, 0.5]   # Interior (manually moved)
        ])

        elements = np.array([
            [0, 1, 4],
            [1, 2, 4],
            [2, 3, 4],
            [3, 0, 4]
        ])

        # Mark boundary vertices (0, 1, 2, 3) and manually moved (4)
        constrained_vertices = {0, 1, 2, 3, 4}

        result = workflow.remesh_and_optimize(
            vertices=vertices,
            elements=elements,
            constrained_vertices=constrained_vertices,
            n_iterations=5
        )

        # Constrained vertices should not move
        for idx in constrained_vertices:
            if idx < len(result['vertices']):
                assert np.allclose(result['vertices'][idx], vertices[idx], atol=1e-10)


class TestMeshQualityComputation:
    """Test mesh quality metrics computation."""

    def test_compute_mesh_quality_metrics(self):
        """Should compute quality metrics for generated mesh."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Create simple triangular mesh
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.5, np.sqrt(3)/2]  # Equilateral triangle
        ])

        elements = np.array([[0, 1, 2]])

        metrics = workflow.compute_mesh_quality(vertices, elements)

        # Should return metrics
        assert 'aspect_ratios' in metrics
        assert 'min_angles' in metrics
        assert 'areas' in metrics

        # Equilateral triangle should have aspect ratio ~1.15 and min angle 60°
        assert len(metrics['aspect_ratios']) == 1
        assert metrics['aspect_ratios'][0] == pytest.approx(1.15, abs=0.2)
        assert metrics['min_angles'][0] == pytest.approx(60.0, abs=1.0)


class TestMeshSizeValidation:
    """Test mesh size warnings and validation."""

    def test_estimate_triangle_count(self):
        """Should estimate number of triangles for given mesh size."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Square boundary 1m x 1m (area = 1)
        boundary = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ])

        mesh_size = 0.1

        estimate = workflow.estimate_triangle_count(boundary, mesh_size)

        # For 1 m² area and 0.1m mesh size:
        # Triangle area = (0.1)² * sqrt(3) / 4 ≈ 0.00433
        # Expected triangles ≈ 1 / 0.00433 ≈ 231
        assert estimate > 0
        assert estimate == pytest.approx(231, rel=0.5)  # Allow 50% tolerance

    def test_validate_mesh_size_too_fine(self):
        """Should warn if mesh size will create too many triangles."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        # Large boundary with very fine mesh
        boundary = np.array([
            [0.0, 0.0],
            [10.0, 0.0],
            [10.0, 10.0],
            [0.0, 10.0]
        ])

        mesh_size = 0.001  # Very fine mesh -> many triangles

        validation = workflow.validate_mesh_size(boundary, mesh_size)

        # Should warn about large mesh
        assert validation['warning'] is True
        assert validation['estimated_triangles'] > 50000
        assert 'recommended_size' in validation

    def test_validate_mesh_size_acceptable(self):
        """Should not warn for reasonable mesh size."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow

        workflow = MeshGenerationWorkflow()

        boundary = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ])

        mesh_size = 0.1  # Reasonable size

        validation = workflow.validate_mesh_size(boundary, mesh_size)

        # Should not warn
        assert validation['warning'] is False
        assert validation['estimated_triangles'] < 50000


class TestWorkflowIntegration:
    """Integration tests for complete workflow."""

    @pytest.mark.slow
    def test_complete_mesh_generation_workflow(self):
        """Should execute complete mesh generation workflow."""
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow
        from mesh_gui_project.data.geqdsk_parser import parse_geqdsk
        from mesh_gui_project.core.equilibrium import EquilibriumData
        from mesh_gui_project.utils.interpolation import make_bicubic_interpolator
        import os

        # Load real equilibrium file
        test_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            'examples',
            'kstar_EFIT01_35582_010000.esy_headerMod.geqdsk'
        )

        if not os.path.exists(test_file):
            pytest.skip("Test GEQDSK file not found")

        data = parse_geqdsk(test_file)
        equilibrium = EquilibriumData(data)
        # Attach interpolator for PSI gradient calculations
        interp = make_bicubic_interpolator(data['R_grid'], data['Z_grid'], data['psi_grid'])
        equilibrium.attach_interpolator(interp)

        workflow = MeshGenerationWorkflow()

        # Generate mesh from PSI contour
        psi_value = 0.95
        mesh_size = 0.05

        result = workflow.generate_mesh_from_psi(
            equilibrium=equilibrium,
            psi_value=psi_value,
            target_element_size=mesh_size
        )

        # Should produce valid mesh
        assert len(result['vertices']) > 10
        assert len(result['elements']) > 10
        assert len(result['boundary_vertex_indices']) > 0

        # Metrics should be computed
        assert 'aspect_ratios' in result['metrics']
        assert len(result['metrics']['aspect_ratios']) == len(result['elements'])

        # Now optimize the mesh
        optimized = workflow.remesh_and_optimize(
            vertices=result['vertices'],
            elements=result['elements'],
            constrained_vertices=result['boundary_vertex_indices'],
            n_iterations=3
        )

        # Optimized mesh should have similar size
        assert len(optimized['vertices']) > 0
        assert len(optimized['elements']) > 0
