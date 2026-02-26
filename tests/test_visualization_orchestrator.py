"""Tests for VisualizationOrchestrator class."""
import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np


def test_visualization_orchestrator_exists():
    """Test that VisualizationOrchestrator class can be instantiated."""
    from mesh_gui_project.ui.visualization_orchestrator import VisualizationOrchestrator

    # Create mock controllers
    canvas_ctrl = Mock()
    psi_viz_ctrl = Mock()
    mesh_viz_ctrl = Mock()
    eq_viz_ctrl = Mock()

    # Should be able to instantiate
    orchestrator = VisualizationOrchestrator(
        canvas_ctrl=canvas_ctrl,
        psi_viz_ctrl=psi_viz_ctrl,
        mesh_viz_ctrl=mesh_viz_ctrl,
        eq_viz_ctrl=eq_viz_ctrl
    )

    assert orchestrator is not None
    assert orchestrator.canvas == canvas_ctrl
    assert orchestrator.psi_viz == psi_viz_ctrl
    assert orchestrator.mesh_viz == mesh_viz_ctrl
    assert orchestrator.eq_viz == eq_viz_ctrl


def test_update_psi_range_display():
    """Test updating PSI range display widgets."""
    from mesh_gui_project.ui.visualization_orchestrator import VisualizationOrchestrator

    # Create mock controllers
    canvas_ctrl = Mock()
    psi_viz_ctrl = Mock()
    mesh_viz_ctrl = Mock()
    eq_viz_ctrl = Mock()

    # Create mock display widgets
    psi_min_display = Mock()
    psi_max_display = Mock()

    orchestrator = VisualizationOrchestrator(
        canvas_ctrl=canvas_ctrl,
        psi_viz_ctrl=psi_viz_ctrl,
        mesh_viz_ctrl=mesh_viz_ctrl,
        eq_viz_ctrl=eq_viz_ctrl
    )

    # Test with equilibrium data
    psi_min = 0.15
    psi_max = 0.95

    orchestrator.update_psi_range_display(
        psi_min_display=psi_min_display,
        psi_max_display=psi_max_display,
        psi_min=psi_min,
        psi_max=psi_max
    )

    # Check that widgets were updated
    psi_min_display.setText.assert_called_once_with("0.1500")
    psi_max_display.setText.assert_called_once_with("0.9500")


def test_update_psi_range_display_no_data():
    """Test updating PSI range display when no equilibrium is loaded."""
    from mesh_gui_project.ui.visualization_orchestrator import VisualizationOrchestrator

    # Create mock controllers
    canvas_ctrl = Mock()
    psi_viz_ctrl = Mock()
    mesh_viz_ctrl = Mock()
    eq_viz_ctrl = Mock()

    # Create mock display widgets
    psi_min_display = Mock()
    psi_max_display = Mock()

    orchestrator = VisualizationOrchestrator(
        canvas_ctrl=canvas_ctrl,
        psi_viz_ctrl=psi_viz_ctrl,
        mesh_viz_ctrl=mesh_viz_ctrl,
        eq_viz_ctrl=eq_viz_ctrl
    )

    # Test with None
    orchestrator.update_psi_range_display(
        psi_min_display=psi_min_display,
        psi_max_display=psi_max_display,
        psi_min=None,
        psi_max=None
    )

    # Check that widgets were cleared
    psi_min_display.setText.assert_called_once_with("")
    psi_max_display.setText.assert_called_once_with("")


def test_update_psi_visualization():
    """Test updating PSI field visualization."""
    from mesh_gui_project.ui.visualization_orchestrator import VisualizationOrchestrator

    # Create mock controllers
    canvas_ctrl = Mock()
    psi_viz_ctrl = Mock()
    mesh_viz_ctrl = Mock()
    eq_viz_ctrl = Mock()

    orchestrator = VisualizationOrchestrator(
        canvas_ctrl=canvas_ctrl,
        psi_viz_ctrl=psi_viz_ctrl,
        mesh_viz_ctrl=mesh_viz_ctrl,
        eq_viz_ctrl=eq_viz_ctrl
    )

    # Mock equilibrium
    equilibrium = Mock()

    # Test updating PSI visualization
    orchestrator.update_psi_visualization(
        equilibrium=equilibrium,
        show_contour=True,
        show_contourf=False,
        added_psi_values=[0.5, 0.7],
        disabled_psi_levels=[0.3]
    )

    # Check that setter methods were called (proper encapsulation)
    psi_viz_ctrl.set_added_psi_values.assert_called_once_with([0.5, 0.7])
    psi_viz_ctrl.set_disabled_psi_levels.assert_called_once_with([0.3])
    psi_viz_ctrl.plot_psi_field.assert_called_once_with(
        equilibrium,
        True,  # show_contour
        False  # show_contourf
    )


def test_clear_psi_visualization():
    """Test clearing PSI field visualization."""
    from mesh_gui_project.ui.visualization_orchestrator import VisualizationOrchestrator

    # Create mock controllers
    canvas_ctrl = Mock()
    psi_viz_ctrl = Mock()
    mesh_viz_ctrl = Mock()
    eq_viz_ctrl = Mock()

    orchestrator = VisualizationOrchestrator(
        canvas_ctrl=canvas_ctrl,
        psi_viz_ctrl=psi_viz_ctrl,
        mesh_viz_ctrl=mesh_viz_ctrl,
        eq_viz_ctrl=eq_viz_ctrl
    )

    # Test clearing PSI visualization
    orchestrator.clear_psi_visualization()

    # Check that psi_viz controller was called
    psi_viz_ctrl.clear_psi_field.assert_called_once()


def test_update_mesh_visualization():
    """Test updating mesh visualization."""
    from mesh_gui_project.ui.visualization_orchestrator import VisualizationOrchestrator

    # Create mock controllers
    canvas_ctrl = Mock()
    psi_viz_ctrl = Mock()
    mesh_viz_ctrl = Mock()
    eq_viz_ctrl = Mock()

    orchestrator = VisualizationOrchestrator(
        canvas_ctrl=canvas_ctrl,
        psi_viz_ctrl=psi_viz_ctrl,
        mesh_viz_ctrl=mesh_viz_ctrl,
        eq_viz_ctrl=eq_viz_ctrl
    )

    # Mock mesh data
    vertices = np.array([[0, 0], [1, 0], [0, 1]])
    elements = np.array([[0, 1, 2]])

    # Test updating mesh visualization
    orchestrator.update_mesh_visualization(
        vertices=vertices,
        elements=elements,
        psi_colorbar_exists=True
    )

    # Check that mesh_viz controller was called
    mesh_viz_ctrl.visualize_mesh.assert_called_once_with(
        vertices,
        elements,
        True  # psi_colorbar_exists
    )

    # Check that canvas was redrawn
    canvas_ctrl.draw.assert_called_once()
