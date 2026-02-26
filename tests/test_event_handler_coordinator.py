"""Tests for EventHandlerCoordinator."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from mesh_gui_project.ui.event_handler_coordinator import EventHandlerCoordinator


class TestEventHandlerCoordinator:
    """Test suite for EventHandlerCoordinator class."""

    def test_initialization(self):
        """Test that EventHandlerCoordinator initializes correctly."""
        # Create mock dependencies
        mock_main_window = Mock()

        # Create coordinator
        coordinator = EventHandlerCoordinator(parent_window=mock_main_window)

        # Verify initialization
        assert coordinator is not None
        assert coordinator.parent_window == mock_main_window

    def test_handle_psi_edit_mode_toggled(self):
        """Test PSI edit mode toggle handler."""
        # Create mock main window with required dependencies
        mock_main_window = Mock()
        mock_main_window.psi_edit_handler = Mock()
        mock_main_window._psi_edit_mode_active = False

        # Create coordinator
        coordinator = EventHandlerCoordinator(parent_window=mock_main_window)

        # Test enabling edit mode
        coordinator.handle_psi_edit_mode_toggled(True)

        # Verify handler was called
        mock_main_window.psi_edit_handler.set_active.assert_called_once_with(True)
        assert mock_main_window._psi_edit_mode_active is True

        # Test disabling edit mode
        coordinator.handle_psi_edit_mode_toggled(False)

        # Verify handler was called
        assert mock_main_window.psi_edit_handler.set_active.call_count == 2
        assert mock_main_window._psi_edit_mode_active is False

    def test_handle_psi_display_mode_changed(self):
        """Test PSI display mode change handler."""
        # Create mock main window
        mock_main_window = Mock()
        mock_main_window.equilibrium = Mock()
        mock_main_window._redraw_rz_plot = Mock()

        # Create coordinator
        coordinator = EventHandlerCoordinator(parent_window=mock_main_window)

        # Test display mode change with equilibrium loaded
        coordinator.handle_psi_display_mode_changed()
        mock_main_window._redraw_rz_plot.assert_called_once()

        # Test with no equilibrium
        mock_main_window.equilibrium = None
        coordinator.handle_psi_display_mode_changed()
        # Should still be called only once (not called again)
        mock_main_window._redraw_rz_plot.assert_called_once()

    def test_handle_generate_mesh_clicked(self):
        """Test generate mesh button handler."""
        # Create mock main window
        mock_main_window = Mock()
        mock_main_window._on_generate_mesh_clicked = Mock()

        # Create coordinator
        coordinator = EventHandlerCoordinator(parent_window=mock_main_window)

        # Test mesh generation
        coordinator.handle_generate_mesh_clicked()
        mock_main_window._on_generate_mesh_clicked.assert_called_once()

    def test_handle_mesh_edit_mode_toggled(self):
        """Test mesh edit mode toggle handler."""
        # Create mock main window
        mock_main_window = Mock()
        mock_main_window._on_mesh_edit_mode_toggled = Mock()

        # Create coordinator
        coordinator = EventHandlerCoordinator(parent_window=mock_main_window)

        # Test enabling mesh edit mode
        coordinator.handle_mesh_edit_mode_toggled(True)
        mock_main_window._on_mesh_edit_mode_toggled.assert_called_once_with(True)

        # Test disabling mesh edit mode
        coordinator.handle_mesh_edit_mode_toggled(False)
        assert mock_main_window._on_mesh_edit_mode_toggled.call_count == 2
