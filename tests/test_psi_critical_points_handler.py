"""
Tests for PsiCriticalPointsHandler class.

Following TDD approach: write tests first, then implement.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch


class TestPsiCriticalPointsHandlerConstruction:
    """Test PsiCriticalPointsHandler construction and initialization."""

    def test_handler_can_be_instantiated(self):
        """PsiCriticalPointsHandler should be instantiable with required dependencies."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        # Mock dependencies
        ax = Mock()
        canvas_controller = Mock()
        application_state = Mock()
        equilibrium_provider = Mock(return_value=Mock())

        handler = PsiCriticalPointsHandler(
            ax=ax,
            canvas_controller=canvas_controller,
            application_state=application_state,
            equilibrium_provider=equilibrium_provider
        )

        assert handler is not None


class TestCriticalPointsComputation:
    """Test critical points finding functionality."""

    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_o_point')
    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_x_points')
    def test_find_critical_points_calls_core_functions(self, mock_find_x, mock_find_o):
        """find_critical_points should call find_o_point and find_x_points."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        # Setup mocks
        mock_find_o.return_value = (1.85, 0.0)
        mock_find_x.return_value = [(1.2, -0.45), (1.2, 0.45)]

        equilibrium = Mock()
        equilibrium_provider = Mock(return_value=equilibrium)

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=Mock(),
            equilibrium_provider=equilibrium_provider
        )

        result = handler.find_critical_points()

        assert result is True
        mock_find_o.assert_called_once_with(equilibrium)
        mock_find_x.assert_called_once_with(equilibrium)

    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_o_point')
    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_x_points')
    def test_find_critical_points_stores_results_in_state(self, mock_find_x, mock_find_o):
        """find_critical_points should store results in ApplicationState."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        # Setup mocks
        o_point = (1.85, 0.0)
        x_points = [(1.2, -0.45), (1.2, 0.45)]
        mock_find_o.return_value = o_point
        mock_find_x.return_value = x_points

        equilibrium = Mock()
        equilibrium_provider = Mock(return_value=equilibrium)
        application_state = Mock()

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=equilibrium_provider
        )

        handler.find_critical_points()

        # Should call set_critical_points with the found points
        application_state.set_critical_points.assert_called_once_with(o_point, x_points)

    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_o_point')
    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_x_points')
    def test_find_critical_points_handles_no_equilibrium(self, mock_find_x, mock_find_o):
        """find_critical_points should return False when no equilibrium is loaded."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        equilibrium_provider = Mock(return_value=None)

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=Mock(),
            equilibrium_provider=equilibrium_provider
        )

        result = handler.find_critical_points()

        assert result is False
        mock_find_o.assert_not_called()
        mock_find_x.assert_not_called()

    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_o_point')
    @patch('mesh_gui_project.ui.psi_critical_points_handler.find_x_points')
    def test_find_critical_points_handles_o_point_failure(self, mock_find_x, mock_find_o):
        """find_critical_points should continue with X-points if O-point finding fails."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        # O-point fails, X-points succeed
        mock_find_o.return_value = None
        mock_find_x.return_value = [(1.2, -0.45)]

        equilibrium = Mock()
        equilibrium_provider = Mock(return_value=equilibrium)
        application_state = Mock()

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=equilibrium_provider
        )

        result = handler.find_critical_points()

        # Should still return True and store partial results
        assert result is True
        application_state.set_critical_points.assert_called_once_with(None, [(1.2, -0.45)])


class TestDisplayTextFormatting:
    """Test display text formatting functionality."""

    def test_format_display_text_groups_by_type(self):
        """format_display_text should group O-points and X-points separately."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.85, 0.0),
            'x_points': [(1.2, -0.45), (1.2, 0.45)]
        }

        equilibrium = Mock()
        equilibrium.axis_R = 1.849
        equilibrium.axis_Z = 0.001
        equilibrium.psi_axis = 0.5
        equilibrium.psi_boundary = 1.2
        equilibrium.psi_value.side_effect = [0.5, 1.2, 1.2]  # psi values
        # normalize_psi: O-point (twice for EFIT comparison), X1, X2
        equilibrium.normalize_psi.side_effect = [0.0, 0.0, 1.0024, 1.0024]

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=equilibrium)
        )

        text = handler.format_display_text()

        # Check structure: O-Points section followed by X-Points section
        assert 'O-Points:' in text
        assert 'X-Points:' in text
        assert text.index('O-Points:') < text.index('X-Points:')

    def test_format_display_text_shows_location_and_psi_n(self):
        """format_display_text should show R, Z coordinates, psi, and psi_N for each point."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.850000, 0.000000),
            'x_points': [(1.234000, -0.456000)]
        }

        equilibrium = Mock()
        equilibrium.axis_R = 1.849
        equilibrium.axis_Z = 0.001
        equilibrium.psi_axis = 0.5
        equilibrium.psi_boundary = 1.2
        equilibrium.psi_value.side_effect = [0.5, 1.2]  # raw psi values
        equilibrium.normalize_psi.side_effect = [0.0, 0.0, 1.0024]  # O-point (twice for EFIT comparison), X-point

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=equilibrium)
        )

        text = handler.format_display_text()

        # Check O-point info - now shows both Numerical and EFIT
        assert '1.850000' in text  # Numerical R
        assert '1.849000' in text  # EFIT R
        assert 'Numerical = 0.0' in text or 'Numerical = 0.000000' in text
        assert 'EFIT' in text

        # Check X-point info - shows location, psi, and psi_N (simplified format)
        assert '1.234000' in text  # X-point R
        assert '-0.456000' in text  # X-point Z
        assert 'psi:' in text
        assert 'psi_N:' in text
        assert '1.0024' in text or '1.002400' in text

    def test_format_display_text_handles_no_points(self):
        """format_display_text should handle case when no points are found."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        application_state = Mock()
        application_state.get_critical_points.return_value = None

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=Mock())
        )

        text = handler.format_display_text()

        assert 'No critical points found' in text

    def test_format_display_text_handles_single_o_point(self):
        """format_display_text should handle O-point without X-points."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.85, 0.0),
            'x_points': []
        }

        equilibrium = Mock()
        equilibrium.axis_R = 1.849
        equilibrium.axis_Z = 0.001
        equilibrium.psi_axis = 0.5
        equilibrium.psi_value.return_value = 0.5
        equilibrium.normalize_psi.return_value = 0.0

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=equilibrium)
        )

        text = handler.format_display_text()

        assert 'O-Points:' in text
        assert '1.850000' in text  # Numerical position
        # X-Points section should either not appear or say "None found"
        assert 'X-Points:' in text

    def test_format_display_text_handles_multiple_x_points(self):
        """format_display_text should handle multiple X-points (double-null)."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.85, 0.0),
            'x_points': [(1.2, -0.45), (1.2, 0.45), (1.8, -0.3)]
        }

        equilibrium = Mock()
        equilibrium.axis_R = 1.849
        equilibrium.axis_Z = 0.001
        equilibrium.psi_axis = 0.5
        equilibrium.psi_boundary = 1.2
        equilibrium.psi_value.side_effect = [0.5, 1.2, 1.2, 1.15]
        # normalize_psi called: O-point (twice for EFIT comparison), X1, X2, X3
        equilibrium.normalize_psi.side_effect = [0.0, 0.0, 1.0024, 1.0024, 0.95]

        handler = PsiCriticalPointsHandler(
            ax=Mock(),
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=equilibrium)
        )

        text = handler.format_display_text()

        # Should show all three X-points labeled as X1, X2, X3
        assert 'X1:' in text
        assert 'X2:' in text
        assert 'X3:' in text
        assert '1.200000' in text  # X-point R coordinates
        assert '-0.450000' in text or '0.450000' in text  # X-point Z coordinates


class TestMarkerVisualization:
    """Test marker drawing and removal functionality."""

    def test_show_markers_draws_green_circles_for_o_points(self):
        """show_markers should draw green 'o' markers for O-points."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        ax = Mock()
        # ax.plot() returns a list of artists
        ax.plot.return_value = [Mock()]

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.85, 0.0),
            'x_points': []
        }

        handler = PsiCriticalPointsHandler(
            ax=ax,
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=Mock())
        )

        handler.show_markers()

        # Should call ax.plot with green circle marker
        ax.plot.assert_called()
        call_args = ax.plot.call_args_list
        # Look for call with 'go' marker
        assert any('go' in str(call) for call in call_args)

    def test_show_markers_draws_green_x_for_x_points(self):
        """show_markers should draw green 'x' markers for X-points."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        ax = Mock()
        # ax.plot() returns a list of artists
        ax.plot.return_value = [Mock()]

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': None,
            'x_points': [(1.2, -0.45), (1.2, 0.45)]
        }

        handler = PsiCriticalPointsHandler(
            ax=ax,
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=Mock())
        )

        handler.show_markers()

        # Should call ax.plot with green x marker
        ax.plot.assert_called()
        call_args = ax.plot.call_args_list
        # Look for call with 'gx' marker
        assert any('gx' in str(call) for call in call_args)

    def test_hide_markers_removes_all_markers(self):
        """hide_markers should remove all marker artists."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        ax = Mock()
        canvas_controller = Mock()
        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.85, 0.0),
            'x_points': [(1.2, -0.45)]
        }

        handler = PsiCriticalPointsHandler(
            ax=ax,
            canvas_controller=canvas_controller,
            application_state=application_state,
            equilibrium_provider=Mock(return_value=Mock())
        )

        # First show markers
        mock_artist1 = Mock()
        mock_artist2 = Mock()
        ax.plot.side_effect = [[mock_artist1], [mock_artist2]]
        handler.show_markers()

        # Then hide them
        handler.hide_markers()

        # Artists should be removed
        mock_artist1.remove.assert_called_once()
        mock_artist2.remove.assert_called_once()

    def test_toggle_markers_independent_from_computation(self):
        """Markers can be toggled on/off without recomputing critical points."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        ax = Mock()
        # ax.plot() returns a list of artists
        ax.plot.return_value = [Mock()]

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.85, 0.0),
            'x_points': []
        }

        handler = PsiCriticalPointsHandler(
            ax=ax,
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=Mock())
        )

        # Show markers multiple times without finding again
        handler.show_markers()
        call_count_1 = ax.plot.call_count

        handler.hide_markers()
        handler.show_markers()
        call_count_2 = ax.plot.call_count

        # Should be able to show markers again from stored state
        assert call_count_2 > call_count_1

    def test_markers_use_correct_zorder(self):
        """Markers should use zorder=101 to appear above contours."""
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler

        ax = Mock()
        # ax.plot() returns a list of artists
        ax.plot.return_value = [Mock()]

        application_state = Mock()
        application_state.get_critical_points.return_value = {
            'o_point': (1.85, 0.0),
            'x_points': [(1.2, -0.45)]
        }

        handler = PsiCriticalPointsHandler(
            ax=ax,
            canvas_controller=Mock(),
            application_state=application_state,
            equilibrium_provider=Mock(return_value=Mock())
        )

        handler.show_markers()

        # Check that plot calls include zorder parameter
        call_args = ax.plot.call_args_list
        # At least one call should have zorder in kwargs
        assert any('zorder' in call.kwargs for call in call_args if call.kwargs)
