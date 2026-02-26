"""
Tests for FileOperationsHandler class.

Following TDD approach: write tests first, then implement.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path


class TestFileOperationsHandlerConstruction:
    """Test FileOperationsHandler construction and initialization."""

    def test_handler_can_be_instantiated(self):
        """FileOperationsHandler should be instantiable with required dependencies."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        assert handler is not None
        assert handler.parent_window == parent_window
        assert handler.settings_manager == settings_manager


class TestOpenGeqdskDialog:
    """Test opening gEQDSK file dialog."""

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    def test_open_dialog_returns_selected_file(self, mock_dialog):
        """File dialog should return selected file path."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        # Setup mocks
        mock_dialog.return_value = ('/path/to/file.geqdsk', 'gEQDSK Files (*.geqdsk)')
        parent_window = Mock()
        settings_manager = Mock()
        settings_manager.get.return_value = '/default/path'

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Call method
        file_path = handler.open_geqdsk_dialog()

        # Verify
        assert file_path == '/path/to/file.geqdsk'
        mock_dialog.assert_called_once()

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    def test_open_dialog_returns_none_when_cancelled(self, mock_dialog):
        """File dialog should return None when user cancels."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        # Setup mocks - empty string means cancelled
        mock_dialog.return_value = ('', '')
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Call method
        file_path = handler.open_geqdsk_dialog()

        # Verify
        assert file_path is None


class TestLoadGeqdsk:
    """Test loading gEQDSK file."""

    @patch('mesh_gui_project.data.geqdsk_parser.parse_geqdsk')
    def test_load_geqdsk_parses_file(self, mock_parse):
        """load_geqdsk should parse file and return equilibrium."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        import numpy as np

        # Setup mocks - provide realistic equilibrium data
        mock_eq_data = {
            'NR': 65, 'NZ': 65,
            'R_grid': np.linspace(1.0, 2.0, 65),
            'Z_grid': np.linspace(-1.0, 1.0, 65),
            'psi_grid': np.zeros((65, 65)),
            'Rmag': 1.5, 'Zmag': 0.0,
            'psi_axis': 0.0, 'psi_boundary': 1.0
        }
        mock_parse.return_value = mock_eq_data
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Call method
        result = handler.load_geqdsk('/path/to/file.geqdsk')

        # Verify
        assert result is not None
        assert hasattr(result, 'NR')
        assert result.NR == 65
        mock_parse.assert_called_once_with('/path/to/file.geqdsk')

    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    @patch('mesh_gui_project.data.geqdsk_parser.parse_geqdsk')
    def test_load_geqdsk_shows_error_on_failure(self, mock_parse, mock_critical):
        """load_geqdsk should show error dialog if parsing fails."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        # Setup mocks
        mock_parse.side_effect = Exception("Parse error")
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Call method
        result = handler.load_geqdsk('/path/to/file.geqdsk')

        # Verify
        assert result is None
        mock_critical.assert_called_once()
        # Verify error message contains the exception text
        call_args = mock_critical.call_args[0]
        assert "Parse error" in call_args[2]


class TestSaveMesh:
    """Test saving mesh to file."""

    @patch('meshio.write')
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_mesh_writes_to_file(self, mock_dialog, mock_meshio_write):
        """save_mesh should write vertices and elements to file."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        import numpy as np

        # Setup mocks
        mock_dialog.return_value = ('/path/to/mesh.msh', 'Gmsh Files (*.msh)')
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method
        result = handler.save_mesh(vertices, elements)

        # Verify
        assert result is True
        mock_dialog.assert_called_once()
        mock_meshio_write.assert_called_once()

    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_mesh_returns_false_when_cancelled(self, mock_dialog):
        """save_mesh should return False when user cancels."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        import numpy as np

        # Setup mocks - empty string means cancelled
        mock_dialog.return_value = ('', '')
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0]])
        elements = np.array([[0]])

        # Call method
        result = handler.save_mesh(vertices, elements)

        # Verify
        assert result is False


class TestSavePsiContours:
    """Test saving PSI contour data."""

    @patch('builtins.open', new_callable=mock_open)
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    @patch('json.dump')
    def test_save_psi_contours_writes_json(self, mock_json, mock_dialog, mock_file):
        """save_psi_contours should write contour data to JSON file."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        # Setup mocks
        mock_dialog.return_value = ('/path/to/contours.json', 'JSON Files (*.json)')
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        contour_data = [
            {'psi_n': 0.5, 'psi': 0.05, 'source': 'AUTO'},
            {'psi_n': 0.7, 'psi': 0.07, 'source': 'USER'}
        ]

        # Call method
        result = handler.save_psi_contours(contour_data)

        # Verify
        assert result is True
        mock_dialog.assert_called_once()
        mock_json.assert_called_once()


class TestSaveMeshSCOREC:
    """Test saving mesh to SCOREC formats (.smb and .dmg)."""

    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch('mesh_gui_project.core.exporter.export_mesh_to_scorec')
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_mesh_detects_smb_format(self, mock_dialog, mock_export, mock_question, mock_critical):
        """save_mesh should detect .smb extension and call SCOREC exporter."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        from PyQt5.QtWidgets import QMessageBox
        import numpy as np

        # Setup mocks
        mock_dialog.return_value = ('/path/to/mesh.smb', 'SCOREC SMB Files (*.smb)')
        mock_question.return_value = QMessageBox.Yes  # User clicks Yes to add partition number
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method
        result = handler.save_mesh(vertices, elements)

        # Verify
        assert result is True
        mock_dialog.assert_called_once()
        mock_export.assert_called_once()
        # Verify partition number prompt was shown
        assert mock_question.called, "Should prompt for partition number"

    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch('mesh_gui_project.core.exporter.export_mesh_to_scorec')
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_mesh_prompts_for_partition_when_user_omits_extension(
        self, mock_dialog, mock_export, mock_question, mock_critical
    ):
        """
        When user types just filename without extension and selects SMB filter,
        should still prompt for partition number (not auto-add 0).

        This is the typical user workflow - relying on the filter to add extension.
        """
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        from PyQt5.QtWidgets import QMessageBox
        import numpy as np

        # Setup mocks - user types 'mesh' without any extension
        mock_dialog.return_value = ('/path/to/mesh', 'SCOREC SMB Files (*.smb)')
        mock_question.return_value = QMessageBox.Yes  # User clicks Yes to add partition number
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method
        result = handler.save_mesh(vertices, elements)

        # Verify
        assert result is True
        mock_dialog.assert_called_once()

        # CRITICAL: Verify partition number prompt was shown
        # This is the bug - currently it auto-adds '0.smb' without prompting
        assert mock_question.called, (
            "Should prompt for partition number even when user omits extension. "
            "User typed 'mesh', filter is '*.smb' - should add '.smb' then prompt for partition number."
        )

        # Verify exported with partition number
        mock_export.assert_called_once()
        # The call should be with 'mesh0.smb' (after user confirms)
        call_args = mock_export.call_args[0]
        smb_path = call_args[3]  # Fourth argument is the SMB path (vertices, elements, dmg, smb)
        assert '0.smb' in smb_path, "Should export with partition number after user confirms"

    @patch('mesh_gui_project.core.exporter.export_mesh_to_dmg')
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_mesh_detects_dmg_format(self, mock_dialog, mock_export):
        """save_mesh should detect .dmg extension and call DMG exporter."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        import numpy as np

        # Setup mocks
        mock_dialog.return_value = ('/path/to/mesh.dmg', 'SCOREC DMG Files (*.dmg)')
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method
        result = handler.save_mesh(vertices, elements)

        # Verify
        assert result is True
        mock_dialog.assert_called_once()
        mock_export.assert_called_once()

    @patch('mesh_gui_project.core.exporter.export_mesh_to_dmg')
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_mesh_auto_adds_dmg_extension(self, mock_dialog, mock_export):
        """save_mesh should auto-add .dmg extension if user doesn't provide it."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        import numpy as np

        # Setup mocks - user types "myfile" without extension
        mock_dialog.return_value = ('myfile', 'SCOREC DMG Files (*.dmg)')
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method
        result = handler.save_mesh(vertices, elements)

        # Verify
        assert result is True
        mock_dialog.assert_called_once()
        mock_export.assert_called_once()

        # Verify the path passed to export had .dmg extension added
        call_args = mock_export.call_args[0]
        file_path = call_args[2]  # Third argument is file_path
        assert file_path == 'myfile.dmg', f"Expected 'myfile.dmg', got '{file_path}'"

    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch('mesh_gui_project.core.exporter.export_mesh_to_scorec')
    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_mesh_auto_adds_smb_extension(self, mock_dialog, mock_export, mock_question, mock_critical):
        """
        When user types filename without extension and selects SMB filter,
        should add .smb extension then prompt for partition number.
        """
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        from PyQt5.QtWidgets import QMessageBox
        import numpy as np

        # Setup mocks - user types "myfile" without extension
        mock_dialog.return_value = ('myfile', 'SCOREC SMB Files (*.smb)')
        mock_question.return_value = QMessageBox.Yes  # User accepts adding partition number
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method
        result = handler.save_mesh(vertices, elements)

        # Verify
        assert result is True
        mock_dialog.assert_called_once()
        mock_question.assert_called_once()  # Should prompt for partition number
        mock_export.assert_called_once()

        # Verify the path passed to export had 0.smb extension added (with partition number)
        call_args = mock_export.call_args[0]
        smb_path = call_args[3]  # Fourth argument is smb_path
        assert smb_path == 'myfile0.smb', f"Expected 'myfile0.smb', got '{smb_path}'"

    @patch('PyQt5.QtWidgets.QMessageBox.critical')
    @patch('mesh_gui_project.core.exporter.export_mesh_to_scorec')
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_save_mesh_prompts_for_partition_number(self, mock_question, mock_export, mock_critical):
        """save_mesh should prompt user to add partition number if missing."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        from PyQt5.QtWidgets import QMessageBox
        import numpy as np

        # Setup - user provides filename with .smb but no partition number
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Mock user clicking "Yes" to add partition number
        mock_question.return_value = QMessageBox.Yes

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method with file_path (bypass dialog)
        result = handler.save_mesh(vertices, elements, 'mesh.smb')

        # Verify message box was shown
        assert mock_question.called, "Message box should be shown"

        # Verify
        assert result is True
        mock_export.assert_called_once()

        # Verify the path was corrected to mesh0.smb
        call_args = mock_export.call_args[0]
        smb_path = call_args[3]  # Fourth argument is smb_path
        assert smb_path == 'mesh0.smb', f"Expected 'mesh0.smb', got '{smb_path}'"

    @patch('mesh_gui_project.core.exporter.export_mesh_to_scorec')
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_save_mesh_accepts_existing_partition_number(self, mock_question, mock_export):
        """save_mesh should not prompt if partition number already exists."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
        import numpy as np

        # Setup
        parent_window = Mock()
        settings_manager = Mock()

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Test data
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        # Call method with file_path that already has partition number
        result = handler.save_mesh(vertices, elements, 'mesh0.smb')

        # Verify message box was NOT shown
        assert not mock_question.called, "Message box should not be shown when partition number exists"

        # Verify
        assert result is True
        mock_export.assert_called_once()

        # Verify the path was not modified
        call_args = mock_export.call_args[0]
        smb_path = call_args[3]  # Fourth argument is smb_path
        assert smb_path == 'mesh0.smb', f"Expected 'mesh0.smb', got '{smb_path}'"


class TestRecentFiles:
    """Test recent files management."""

    def test_add_to_recent_files_adds_file(self):
        """add_to_recent_files should add file to recent list."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        parent_window = Mock()
        settings_manager = Mock()
        settings_manager.get.return_value = []

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Call method
        handler.add_to_recent_files('/path/to/file.geqdsk')

        # Verify
        settings_manager.set.assert_called_once()
        call_args = settings_manager.set.call_args[0]
        assert call_args[0] == 'recent_files'
        assert '/path/to/file.geqdsk' in call_args[1]

    def test_add_to_recent_files_limits_to_max(self):
        """add_to_recent_files should limit list to maximum size."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        parent_window = Mock()
        settings_manager = Mock()
        # Start with 10 files
        settings_manager.get.return_value = [f'/file{i}.geqdsk' for i in range(10)]

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Add new file
        handler.add_to_recent_files('/new/file.geqdsk')

        # Verify list is still max 10
        call_args = settings_manager.set.call_args[0]
        assert len(call_args[1]) == 10
        assert call_args[1][0] == '/new/file.geqdsk'  # New file at top

    def test_get_recent_files_returns_list(self):
        """get_recent_files should return list of recent files."""
        from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler

        parent_window = Mock()
        settings_manager = Mock()
        recent_files = ['/file1.geqdsk', '/file2.geqdsk']
        settings_manager.get.return_value = recent_files

        handler = FileOperationsHandler(parent_window, settings_manager)

        # Call method
        result = handler.get_recent_files()

        # Verify
        assert result == recent_files
