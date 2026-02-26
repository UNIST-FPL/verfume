"""
Tests for EquilibriumVisualizationController.

This module tests the equilibrium visualization controller which handles
plotting of critical points (O-point, X-points) and flux surfaces.
"""
import pytest
from unittest.mock import Mock, patch, call
from mesh_gui_project.ui.equilibrium_visualization_controller import EquilibriumVisualizationController


class TestEquilibriumVisualizationControllerConstruction:
    """Test EquilibriumVisualizationController construction."""

    def test_controller_can_be_instantiated(self):
        """EquilibriumVisualizationController should be instantiable with ax and canvas_controller."""
        mock_ax = Mock()
        mock_canvas_controller = Mock()
        controller = EquilibriumVisualizationController(mock_ax, mock_canvas_controller)
        assert controller is not None
        assert controller.ax == mock_ax
        assert controller.canvas_controller == mock_canvas_controller


class TestPlotCriticalPoints:
    """Test critical points plotting."""

    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_o_point')
    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_x_points')
    def test_plot_critical_points_with_o_and_x_points(self, mock_find_x, mock_find_o):
        """Should plot O-point and X-points when both are found."""
        # Setup mocks
        mock_ax = Mock()
        mock_canvas_controller = Mock()
        mock_equilibrium = Mock()

        # O-point at (1.8, 0.0)
        mock_find_o.return_value = (1.8, 0.0)

        # Two X-points
        mock_find_x.return_value = [(1.2, -0.5), (1.2, 0.5)]

        controller = EquilibriumVisualizationController(mock_ax, mock_canvas_controller)
        controller.plot_critical_points(mock_equilibrium)

        # Verify O-point finding was called
        mock_find_o.assert_called_once_with(mock_equilibrium)

        # Verify O-point was plotted (plot called with O-point coords)
        o_point_plot_calls = [c for c in mock_ax.plot.call_args_list
                             if len(c[0]) >= 2 and c[0][0] == 1.8 and c[0][1] == 0.0]
        assert len(o_point_plot_calls) > 0, "O-point should be plotted"

        # Verify O-point annotation
        o_annotations = [c for c in mock_ax.annotate.call_args_list
                        if c[0][0] == 'O']
        assert len(o_annotations) > 0, "O-point should be annotated"

        # Verify X-points finding was called
        mock_find_x.assert_called_once_with(mock_equilibrium)

        # Verify X-points were plotted (2 X-points)
        assert mock_ax.plot.call_count >= 3  # At least O + 2 X-points

        # Verify X-point annotations (X1, X2)
        x_annotations = [c for c in mock_ax.annotate.call_args_list
                        if 'X' in c[0][0]]
        assert len(x_annotations) == 2, "Should have 2 X-point annotations"

        # Verify canvas was refreshed
        mock_canvas_controller.draw.assert_called_once()

    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_o_point')
    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_x_points')
    def test_plot_critical_points_handles_o_point_error(self, mock_find_x, mock_find_o):
        """Should continue if O-point finding fails."""
        mock_ax = Mock()
        mock_canvas_controller = Mock()
        mock_equilibrium = Mock()

        # O-point finding fails
        mock_find_o.side_effect = Exception("O-point not found")

        # X-points succeed
        mock_find_x.return_value = [(1.2, -0.5)]

        controller = EquilibriumVisualizationController(mock_ax, mock_canvas_controller)

        # Should not raise exception
        controller.plot_critical_points(mock_equilibrium)

        # O-point should not be plotted
        o_annotations = [c for c in mock_ax.annotate.call_args_list
                        if c[0][0] == 'O']
        assert len(o_annotations) == 0, "O-point should not be annotated when finding fails"

        # X-points should still be plotted
        x_annotations = [c for c in mock_ax.annotate.call_args_list
                        if 'X' in c[0][0]]
        assert len(x_annotations) > 0, "X-points should still be plotted"

        # Canvas should still be refreshed
        mock_canvas_controller.draw.assert_called_once()

    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_o_point')
    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_x_points')
    def test_plot_critical_points_handles_x_points_error(self, mock_find_x, mock_find_o):
        """Should continue if X-points finding fails."""
        mock_ax = Mock()
        mock_canvas_controller = Mock()
        mock_equilibrium = Mock()

        # O-point succeeds
        mock_find_o.return_value = (1.8, 0.0)

        # X-points finding fails
        mock_find_x.side_effect = Exception("X-points not found")

        controller = EquilibriumVisualizationController(mock_ax, mock_canvas_controller)

        # Should not raise exception
        controller.plot_critical_points(mock_equilibrium)

        # O-point should be plotted
        o_annotations = [c for c in mock_ax.annotate.call_args_list
                        if c[0][0] == 'O']
        assert len(o_annotations) > 0, "O-point should be annotated"

        # X-points should not be plotted
        x_annotations = [c for c in mock_ax.annotate.call_args_list
                        if 'X' in c[0][0]]
        assert len(x_annotations) == 0, "X-points should not be annotated when finding fails"

        # Canvas should still be refreshed
        mock_canvas_controller.draw.assert_called_once()

    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_o_point')
    @patch('mesh_gui_project.ui.equilibrium_visualization_controller.find_x_points')
    def test_plot_critical_points_with_no_x_points(self, mock_find_x, mock_find_o):
        """Should handle case with O-point but no X-points."""
        mock_ax = Mock()
        mock_canvas_controller = Mock()
        mock_equilibrium = Mock()

        # O-point succeeds
        mock_find_o.return_value = (1.8, 0.0)

        # No X-points found (empty list)
        mock_find_x.return_value = []

        controller = EquilibriumVisualizationController(mock_ax, mock_canvas_controller)
        controller.plot_critical_points(mock_equilibrium)

        # O-point should be plotted
        o_annotations = [c for c in mock_ax.annotate.call_args_list
                        if c[0][0] == 'O']
        assert len(o_annotations) > 0, "O-point should be annotated"

        # No X-point annotations
        x_annotations = [c for c in mock_ax.annotate.call_args_list
                        if 'X' in c[0][0]]
        assert len(x_annotations) == 0, "No X-point annotations when none found"

        # Canvas should still be refreshed
        mock_canvas_controller.draw.assert_called_once()
