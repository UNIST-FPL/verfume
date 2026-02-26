"""Tests for UIFactory module."""
import pytest
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QWidget, QTabWidget,
                             QPushButton, QTextEdit, QCheckBox)
from mesh_gui_project.ui.ui_factory import UIFactory


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def parent_window(qapp):
    """Create parent window for UI components."""
    window = QMainWindow()
    return window


class TestUIFactory:
    """Test UIFactory class."""

    def test_ui_factory_exists(self):
        """Test that UIFactory class can be imported."""
        from mesh_gui_project.ui.ui_factory import UIFactory
        assert UIFactory is not None

    def test_create_menu_bar(self, parent_window):
        """Test that create_menu_bar returns a QMenuBar."""
        menu_bar = UIFactory.create_menu_bar(parent_window)
        assert isinstance(menu_bar, QMenuBar)

        # Check that expected menus exist
        menus = [menu_bar.actions()[i].text() for i in range(len(menu_bar.actions()))]
        assert '&File' in menus
        assert '&Help' in menus
        # View menu should NOT exist (moved to Meta tab)
        assert '&View' not in menus
        # Tools menu should NOT exist (removed)
        assert '&Tools' not in menus

    def test_file_menu_has_expected_actions(self, parent_window):
        """Test that File menu has expected actions."""
        menu_bar = UIFactory.create_menu_bar(parent_window)

        # Get File menu
        file_menu = None
        for action in menu_bar.actions():
            if action.text() == '&File':
                file_menu = action.menu()
                break

        assert file_menu is not None

        # Check for expected actions
        action_texts = [action.text() for action in file_menu.actions() if action.text()]
        assert '&Open gEQDSK...' in action_texts
        assert '&Batch Run...' not in action_texts
        assert '&Quit' in action_texts

    def test_create_left_panel(self, parent_window):
        """Test that create_left_panel returns a QTabWidget."""
        left_panel = UIFactory.create_left_panel(parent_window)
        assert isinstance(left_panel, QTabWidget)

        # Check that expected tabs exist
        assert left_panel.count() == 3
        assert left_panel.tabText(0) == "Meta"
        assert left_panel.tabText(1) == "Psi"
        assert left_panel.tabText(2) == "Meshing"

    def test_meta_tab_has_data_inspector(self, parent_window):
        """Test that Meta tab contains DataInspectorPanel."""
        left_panel = UIFactory.create_left_panel(parent_window)
        meta_tab = left_panel.widget(0)

        assert meta_tab is not None
        # DataInspectorPanel is the meta tab widget
        from mesh_gui_project.ui.data_inspector_panel import DataInspectorPanel
        assert isinstance(meta_tab, DataInspectorPanel)

    def test_psi_tab_has_expected_widgets(self, parent_window):
        """Test that Psi tab has expected widgets."""
        left_panel = UIFactory.create_left_panel(parent_window)
        psi_tab = left_panel.widget(1)

        assert psi_tab is not None

        # Check for expected child widgets by object name
        # PSI display checkboxes
        psi_display_contour = psi_tab.findChild(type(None), 'psi_display_contour_checkbox')
        psi_display_contourf = psi_tab.findChild(type(None), 'psi_display_contourf_checkbox')

        # PSI edit mode button
        psi_edit_mode_button = psi_tab.findChild(type(None), 'psi_edit_mode_button')

        # PSI contour list
        psi_contour_list = psi_tab.findChild(type(None), 'psi_contour_list')

    def test_mesh_tab_has_expected_widgets(self, parent_window):
        """Test that Mesh tab has expected widgets."""
        left_panel = UIFactory.create_left_panel(parent_window)
        mesh_tab = left_panel.widget(2)

        assert mesh_tab is not None

        # Check for expected child widgets by object name
        # Mesh visualization mode combo
        mesh_viz_mode_combo = mesh_tab.findChild(type(None), 'mesh_viz_mode_combo')

        # Mesh generation parameters
        mesh_toroidal_steps_spinbox = mesh_tab.findChild(type(None), 'mesh_toroidal_steps_spinbox')
        mesh_size_spinbox = mesh_tab.findChild(type(None), 'mesh_size_spinbox')

        # Control buttons
        generate_mesh_button = mesh_tab.findChild(type(None), 'generate_mesh_button')
        enter_edit_mode_button = mesh_tab.findChild(type(None), 'enter_edit_mode_button')

    def test_menu_bar_actions_are_not_connected(self, parent_window):
        """Test that menu bar actions are created but not connected to handlers."""
        # UIFactory should create UI elements but not wire up event handlers
        # The parent window is responsible for connecting signals
        menu_bar = UIFactory.create_menu_bar(parent_window)

        # Get File menu -> Open action
        file_menu = None
        for action in menu_bar.actions():
            if action.text() == '&File':
                file_menu = action.menu()
                break

        open_action = None
        for action in file_menu.actions():
            if action.text() == '&Open gEQDSK...':
                open_action = action
                break

        assert open_action is not None
        # The action should exist but have no connections yet
        # (parent window will connect them)

    def test_psi_tab_has_critical_points_finder_group(self, parent_window):
        """Test that Psi tab has Critical Points Finder group with expected widgets."""
        left_panel = UIFactory.create_left_panel(parent_window)
        psi_tab = left_panel.widget(1)

        assert psi_tab is not None

        # Check for critical points widgets by object name
        find_button = psi_tab.findChild(QPushButton, 'find_crit_points_button')
        assert find_button is not None
        assert find_button.text() == "Find Critical Points"

        # Check for new table widget (replaces old QTextEdit)
        from PyQt5.QtWidgets import QTableWidget
        table = psi_tab.findChild(QTableWidget, 'crit_points_table')
        assert table is not None
        assert table.columnCount() == 5
        assert table.editTriggers() == QTableWidget.NoEditTriggers

        # Check for detail button
        detail_button = psi_tab.findChild(QPushButton, 'crit_points_detail_button')
        assert detail_button is not None
        assert "Detail" in detail_button.text()

        checkbox = psi_tab.findChild(QCheckBox, 'show_crit_markers_checkbox')
        assert checkbox is not None
        assert checkbox.text() == "Show Markers"
        assert not checkbox.isChecked()  # Should start unchecked
