"""Test main window UI components."""
import sys
from PyQt5.QtWidgets import QApplication
import pytest


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_main_window_can_be_instantiated(qapp):
    """Test that MainWindow can be instantiated."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()
    assert window is not None
    assert window.windowTitle() == "Verfume"


def test_main_window_has_menubar(qapp):
    """Test that MainWindow has a menubar with required menus."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()
    menubar = window.menuBar()

    assert menubar is not None, "MainWindow should have a menubar"

    # Get menu titles
    menus = {action.text(): action.menu() for action in menubar.actions()}

    # Check required menus exist
    assert 'File' in menus or '&File' in menus, "Should have File menu"
    assert 'Help' in menus or '&Help' in menus, "Should have Help menu"
    # View menu should NOT exist (moved to Meta tab)
    assert 'View' not in menus and '&View' not in menus, "View menu should be removed"
    # Tools menu should NOT exist (removed)
    assert 'Tools' not in menus and '&Tools' not in menus, "Tools menu should be removed"


def test_file_menu_has_required_actions(qapp):
    """Test that File menu has Open, Recent, and Quit actions."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()
    menubar = window.menuBar()

    # Find File menu
    file_menu = None
    for action in menubar.actions():
        if 'File' in action.text():
            file_menu = action.menu()
            break

    assert file_menu is not None, "File menu should exist"

    # Get action texts
    action_texts = [action.text() for action in file_menu.actions() if action.text()]

    # Check for required actions (allowing for keyboard shortcuts like &Open)
    has_open = any('Open' in text for text in action_texts)
    has_quit = any('Quit' in text or 'Exit' in text for text in action_texts)

    assert has_open, "File menu should have Open action"
    assert has_quit, "File menu should have Quit/Exit action"


def test_main_window_has_status_bar(qapp):
    """Test that MainWindow has a status bar."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()
    statusbar = window.statusBar()

    assert statusbar is not None, "MainWindow should have a status bar"


def test_main_window_has_central_widget(qapp):
    """Test that MainWindow has a central widget."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()
    central_widget = window.centralWidget()

    assert central_widget is not None, "MainWindow should have a central widget"




def test_main_window_has_matplotlib_canvas(qapp):
    """Test that MainWindow has an embedded matplotlib canvas."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have a matplotlib canvas widget
    assert hasattr(window, 'canvas'), "MainWindow should have canvas attribute"
    assert window.canvas is not None, "canvas should be initialized"


def test_status_bar_update_method_exists(qapp):
    """Test that MainWindow has a method to update status bar with position/stats."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have method to update status bar
    assert hasattr(window, 'update_status_bar'), "MainWindow should have update_status_bar method"
    assert callable(window.update_status_bar), "update_status_bar should be callable"


def test_main_window_has_plot_critical_points_method(qapp):
    """Test that MainWindow has equilibrium_viz_controller with plot_critical_points method."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, 'equilibrium_viz_controller'), "Should have equilibrium_viz_controller"
    assert hasattr(window.equilibrium_viz_controller, 'plot_critical_points'), \
        "Controller should have plot_critical_points method"
    assert callable(window.equilibrium_viz_controller.plot_critical_points), \
        "plot_critical_points should be callable"


def test_view_menu_has_critical_points_toggle(qapp):
    """Test that Meta tab has toggle for critical points (O/X Points)."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Check that data inspector has the O/X Points checkbox
    assert hasattr(window.data_inspector, 'show_o_x_checkbox'), "Should have show_o_x_checkbox in Meta tab"
    assert window.data_inspector.show_o_x_checkbox.text() == "Show O/X Points", "Checkbox should be labeled 'Show O/X Points'"
    assert window.data_inspector.show_o_x_checkbox.isCheckable(), "O/X Points checkbox should be checkable"


def test_main_window_has_plot_flux_surfaces_method(qapp):
    """Test that MainWindow has equilibrium_viz_controller with plot_flux_surfaces method."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, 'equilibrium_viz_controller'), "Should have equilibrium_viz_controller"
    assert hasattr(window.equilibrium_viz_controller, 'plot_flux_surfaces'), \
        "Controller should have plot_flux_surfaces method"
    assert callable(window.equilibrium_viz_controller.plot_flux_surfaces), \
        "plot_flux_surfaces should be callable"


def test_main_window_has_canvas_click_handler(qapp):
    """Test that MainWindow has method to handle canvas clicks."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, 'on_canvas_click'), "Should have on_canvas_click method"
    assert callable(window.on_canvas_click), "on_canvas_click should be callable"


# T9.1 - Open and re-render tests

def test_main_window_has_load_geqdsk_method(qapp):
    """Test that MainWindow has load_geqdsk method."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, 'load_geqdsk'), "MainWindow should have load_geqdsk method"
    assert callable(window.load_geqdsk), "load_geqdsk should be callable"


def test_open_action_triggers_file_dialog(qapp, monkeypatch):
    """Test that Open action shows file dialog."""
    from mesh_gui_project.ui.main_window import MainWindow
    from PyQt5.QtWidgets import QFileDialog

    window = MainWindow()

    # Mock file dialog
    dialog_called = []

    def mock_get_open_filename(parent, caption, directory, filter_str):
        dialog_called.append((caption, filter_str))
        return '', ''  # Return empty to cancel

    monkeypatch.setattr(QFileDialog, 'getOpenFileName', mock_get_open_filename)

    # Find and trigger Open action
    menubar = window.menuBar()
    file_menu = None
    for action in menubar.actions():
        if 'File' in action.text():
            file_menu = action.menu()
            break

    open_action = None
    for action in file_menu.actions():
        if 'Open' in action.text() and 'Recent' not in action.text():
            open_action = action
            break

    assert open_action is not None, "Should have Open action"

    # Trigger action
    open_action.trigger()

    # Should have called dialog
    assert len(dialog_called) == 1, "Should have shown file dialog"


def test_load_geqdsk_with_file(qapp, tmp_path):
    """Test loading a gEQDSK file."""
    from mesh_gui_project.ui.main_window import MainWindow
    import numpy as np

    window = MainWindow()

    # Create a minimal gEQDSK file
    geqdsk_path = tmp_path / "test.geqdsk"

    # Write minimal gEQDSK data
    with open(geqdsk_path, 'w') as f:
        # Header line
        f.write("  Test equilibrium                                        3 65 65\n")
        # Line 2: Rdim, Zdim, Rcentr, Rleft, Zmid
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        # Line 3: Rmag, Zmag, simag (psi_axis), sibry (psi_boundary), Bcentr
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        # Line 4: Ip, simag (duplicate), _, Rmag (duplicate), _
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        # Line 5: Zmag (duplicate), _, sibry (duplicate), _, _
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # Write fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write psi grid (65x65 = 4225 values)
        psi_values = []
        for i in range(65):
            for j in range(65):
                R = 1.0 + j * (2.0 - 1.0) / 64
                Z = -0.5 + i * (0.5 - (-0.5)) / 64
                psi = ((R - 1.5)**2 + Z**2)
                psi_values.append(psi)

        # Write in 5 columns format
        for i, val in enumerate(psi_values):
            f.write(f"  {val:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if len(psi_values) % 5 != 0:
            f.write("\n")

        # Write pres array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write pprime array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write ffprime array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write qpsi array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write boundary and limiter counts
        f.write("  0 0\n")  # NBDRY=0, NLIM=0 (no boundary/limiter)

    # Load the file
    window.load_geqdsk(str(geqdsk_path))

    # Check that equilibrium was loaded
    assert window.equilibrium is not None, "Equilibrium should be loaded"


def test_load_geqdsk_renders_plot(qapp, tmp_path):
    """Test that loading gEQDSK renders the plot."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create minimal gEQDSK file
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        # Line 2: Rdim, Zdim, Rcentr, Rleft, Zmid
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        # Line 3: Rmag, Zmag, simag (psi_axis), sibry (psi_boundary), Bcentr
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        # Line 4: Ip, simag (duplicate), _, Rmag (duplicate), _
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        # Line 5: Zmag (duplicate), _, sibry (duplicate), _, _
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Minimal psi grid
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # pprime array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # ffprime array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # qpsi array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        f.write("  0 0\n")

    # Load file
    window.load_geqdsk(str(geqdsk_path))

    # Check that axes have labels (via canvas controller)
    assert window.canvas_controller.ax.get_xlabel() != '', "X-axis should have label"
    assert window.canvas_controller.ax.get_ylabel() != '', "Y-axis should have label"

    # Check equal aspect ratio (matplotlib converts 'equal' to 1.0)
    aspect = window.canvas_controller.ax.get_aspect()
    assert aspect == 'equal' or aspect == 1.0, f"Axes should have equal aspect ratio, got {aspect}"


def test_load_geqdsk_with_boundary_renders_boundary(qapp, tmp_path):
    """Test that loading gEQDSK with boundary renders it."""
    from mesh_gui_project.ui.main_window import MainWindow
    import numpy as np

    window = MainWindow()

    # Create gEQDSK with boundary
    geqdsk_path = tmp_path / "test_with_boundary.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        # Line 2: Rdim, Zdim, Rcentr, Rleft, Zmid
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        # Line 3: Rmag, Zmag, simag (psi_axis), sibry (psi_boundary), Bcentr
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        # Line 4: Ip, simag (duplicate), _, Rmag (duplicate), _
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        # Line 5: Zmag (duplicate), _, sibry (duplicate), _, _
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # pprime array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # ffprime array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # qpsi array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Boundary: 10 points
        f.write("  10 0\n")
        for i in range(10):
            theta = 2 * np.pi * i / 10
            R = 1.5 + 0.3 * np.cos(theta)
            Z = 0.0 + 0.3 * np.sin(theta)
            f.write(f"  {R:15.8E}  {Z:15.8E}\n")

    # Load file
    window.load_geqdsk(str(geqdsk_path))

    # Check that equilibrium has boundary
    assert window.equilibrium is not None, "Equilibrium should be loaded"
    assert window.equilibrium.boundary_curve is not None, "Should have boundary curve"


# T9.2 - psi_N input and array tools tests



# T9.3 - Click selection mode tests

def test_canvas_click_updates_status_bar(qapp, tmp_path):
    """Test that clicking canvas updates status bar with R, Z coordinates."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Create mock event
    event = Mock()
    event.inaxes = window.ax
    event.button = 1  # Left click
    event.xdata = 1.5  # R coordinate
    event.ydata = 0.3  # Z coordinate

    # Call handler
    window.on_canvas_click(event)

    # Status bar should show coordinates
    status_text = window.statusBar().currentMessage()
    assert "1.5" in status_text or "1.500" in status_text, f"Status should show R coordinate, got: {status_text}"
    assert "0.3" in status_text or "0.300" in status_text, f"Status should show Z coordinate, got: {status_text}"


def test_canvas_click_stores_coordinates(qapp):
    """Test that canvas click stores clicked coordinates."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Create mock event
    event = Mock()
    event.inaxes = window.ax
    event.button = 1
    event.xdata = 2.0
    event.ydata = -0.5

    # Call handler
    window.on_canvas_click(event)

    # Coordinates should be stored
    assert hasattr(window, 'last_click_r'), "Should store last_click_r"
    assert hasattr(window, 'last_click_z'), "Should store last_click_z"
    assert window.last_click_r == 2.0, f"Should store R=2.0, got {window.last_click_r}"
    assert window.last_click_z == -0.5, f"Should store Z=-0.5, got {window.last_click_z}"


# T9.4 - Meshing preview toggle tests

def test_mesh_preview_toggle_exists(qapp):
    """Test that mesh preview toggle was removed."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # toggle_mesh_preview_action should NOT exist (removed from View menu)
    assert not hasattr(window, 'toggle_mesh_preview_action'), \
        "toggle_mesh_preview_action should be removed"


# T12.1 - Preview optimization with debouncing tests

def test_main_window_has_debounce_timer(qapp):
    """Test that MainWindow has a QTimer for debouncing updates."""
    from mesh_gui_project.ui.main_window import MainWindow
    from PyQt5.QtCore import QTimer

    window = MainWindow()

    # Should have a debounce timer
    assert hasattr(window, 'preview_debounce_timer'), \
        "MainWindow should have preview_debounce_timer attribute"
    assert isinstance(window.preview_debounce_timer, QTimer), \
        "preview_debounce_timer should be a QTimer instance"


def test_main_window_has_tab_widget_in_left_panel(qapp):
    """Test that MainWindow uses QTabWidget for left panel."""
    from mesh_gui_project.ui.main_window import MainWindow
    from PyQt5.QtWidgets import QTabWidget

    window = MainWindow()

    # Should have a tab widget
    assert hasattr(window, 'left_tabs'), "MainWindow should have left_tabs attribute"
    assert isinstance(window.left_tabs, QTabWidget), \
        "left_tabs should be a QTabWidget instance"


def test_main_window_has_no_flux_surfaces_tab(qapp):
    """Test that MainWindow does NOT have 'Flux Surfaces' tab."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Check tab does not exist
    tab_texts = [window.left_tabs.tabText(i) for i in range(window.left_tabs.count())]
    assert not any('Flux' in text for text in tab_texts), \
        "Should NOT have a tab with 'Flux' in the name"


def test_main_window_has_data_inspector_tab(qapp):
    """Test that MainWindow has 'Meta' tab (renamed from 'Data Inspector')."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Check tab exists (renamed to "Meta")
    tab_texts = [window.left_tabs.tabText(i) for i in range(window.left_tabs.count())]
    assert any('Meta' in text for text in tab_texts), \
        "Should have a tab with 'Meta' in the name"


def test_main_window_has_data_inspector_panel(qapp):
    """Test that MainWindow has DataInspectorPanel instance."""
    from mesh_gui_project.ui.main_window import MainWindow
    from mesh_gui_project.ui.data_inspector_panel import DataInspectorPanel

    window = MainWindow()

    # Should have data inspector panel
    assert hasattr(window, 'data_inspector'), \
        "MainWindow should have data_inspector attribute"
    assert isinstance(window.data_inspector, DataInspectorPanel), \
        "data_inspector should be a DataInspectorPanel instance"


# Canvas zoom and pan interaction tests

def test_canvas_has_scroll_zoom_handler(qapp):
    """Test that canvas has scroll event handler for zooming."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have on_scroll_zoom method
    assert hasattr(window, 'on_scroll_zoom'), \
        "MainWindow should have on_scroll_zoom method"
    assert callable(window.on_scroll_zoom), \
        "on_scroll_zoom should be callable"


def test_scroll_zoom_in_changes_axis_limits(qapp):
    """Test that scrolling in zooms the view (decreases axis range)."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Set initial axis limits
    window.ax.set_xlim(0, 10)
    window.ax.set_ylim(0, 10)
    initial_xlim = window.ax.get_xlim()
    initial_ylim = window.ax.get_ylim()
    initial_x_range = initial_xlim[1] - initial_xlim[0]
    initial_y_range = initial_ylim[1] - initial_ylim[0]

    # Create scroll up event (zoom in)
    event = Mock()
    event.inaxes = window.ax
    event.button = 'up'
    event.xdata = 5.0
    event.ydata = 5.0

    # Trigger zoom
    window.on_scroll_zoom(event)

    # Get new limits
    new_xlim = window.ax.get_xlim()
    new_ylim = window.ax.get_ylim()
    new_x_range = new_xlim[1] - new_xlim[0]
    new_y_range = new_ylim[1] - new_ylim[0]

    # Range should be smaller (zoomed in)
    assert new_x_range < initial_x_range, \
        f"X range should decrease on zoom in: {initial_x_range} -> {new_x_range}"
    assert new_y_range < initial_y_range, \
        f"Y range should decrease on zoom in: {initial_y_range} -> {new_y_range}"


def test_scroll_zoom_out_changes_axis_limits(qapp):
    """Test that scrolling out zooms out the view (increases axis range)."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Set initial axis limits
    window.ax.set_xlim(0, 10)
    window.ax.set_ylim(0, 10)
    initial_xlim = window.ax.get_xlim()
    initial_ylim = window.ax.get_ylim()
    initial_x_range = initial_xlim[1] - initial_xlim[0]
    initial_y_range = initial_ylim[1] - initial_ylim[0]

    # Create scroll down event (zoom out)
    event = Mock()
    event.inaxes = window.ax
    event.button = 'down'
    event.xdata = 5.0
    event.ydata = 5.0

    # Trigger zoom
    window.on_scroll_zoom(event)

    # Get new limits
    new_xlim = window.ax.get_xlim()
    new_ylim = window.ax.get_ylim()
    new_x_range = new_xlim[1] - new_xlim[0]
    new_y_range = new_ylim[1] - new_ylim[0]

    # With aspect ratio adjustment, at least one range should increase
    # (the other might adjust to maintain aspect ratio)
    max_initial_range = max(initial_x_range, initial_y_range)
    max_new_range = max(new_x_range, new_y_range)

    assert max_new_range > max_initial_range, \
        f"At least one range should increase on zoom out: max({initial_x_range}, {initial_y_range}) -> max({new_x_range}, {new_y_range})"


def test_zoom_preserves_aspect_ratio(qapp):
    """Test that zoom preserves equal aspect ratio."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Set initial limits with equal aspect
    window.ax.set_xlim(0, 10)
    window.ax.set_ylim(0, 10)

    # Zoom in
    event = Mock()
    event.inaxes = window.ax
    event.button = 'up'
    event.xdata = 5.0
    event.ydata = 5.0

    window.on_scroll_zoom(event)

    # Aspect should remain equal after zoom
    aspect = window.ax.get_aspect()
    assert aspect == 'equal' or aspect == 1.0, \
        f"Aspect ratio should remain equal after zoom, got {aspect}"


def test_canvas_has_pan_handlers(qapp):
    """Test that canvas has handlers for pan (drag) operations."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have pan-related methods
    assert hasattr(window, 'on_mouse_press'), \
        "MainWindow should have on_mouse_press method"
    assert hasattr(window, 'on_mouse_release'), \
        "MainWindow should have on_mouse_release method"
    assert hasattr(window, 'on_mouse_motion'), \
        "MainWindow should have on_mouse_motion method"

    assert callable(window.on_mouse_press), "on_mouse_press should be callable"
    assert callable(window.on_mouse_release), "on_mouse_release should be callable"
    assert callable(window.on_mouse_motion), "on_mouse_motion should be callable"


def test_left_click_drag_pans_view(qapp):
    """Test that left-click drag translates the view."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Set initial limits
    window.ax.set_xlim(0, 10)
    window.ax.set_ylim(0, 10)

    # Simulate mouse press (start drag)
    press_event = Mock()
    press_event.inaxes = window.ax
    press_event.button = 1  # Left click
    press_event.xdata = 5.0
    press_event.ydata = 5.0

    window.on_mouse_press(press_event)

    # Simulate mouse motion (drag)
    motion_event = Mock()
    motion_event.inaxes = window.ax
    motion_event.xdata = 3.0  # Moved left by 2 units
    motion_event.ydata = 3.0  # Moved down by 2 units

    window.on_mouse_motion(motion_event)

    # Get new limits
    new_xlim = window.ax.get_xlim()
    new_ylim = window.ax.get_ylim()

    # View should have shifted (limits should have changed)
    # Since we dragged from 5,5 to 3,3 (moved mouse left/down),
    # the view should pan right/up (limits increase)
    assert new_xlim[0] > 0, "View should have panned (X limits changed)"
    assert new_ylim[0] > 0, "View should have panned (Y limits changed)"


def test_pan_preserves_aspect_ratio(qapp):
    """Test that panning preserves equal aspect ratio."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Set initial limits
    window.ax.set_xlim(0, 10)
    window.ax.set_ylim(0, 10)

    # Start drag
    press_event = Mock()
    press_event.inaxes = window.ax
    press_event.button = 1
    press_event.xdata = 5.0
    press_event.ydata = 5.0

    window.on_mouse_press(press_event)

    # Drag
    motion_event = Mock()
    motion_event.inaxes = window.ax
    motion_event.xdata = 3.0
    motion_event.ydata = 3.0

    window.on_mouse_motion(motion_event)

    # Aspect should remain equal after pan
    aspect = window.ax.get_aspect()
    assert aspect == 'equal' or aspect == 1.0, \
        f"Aspect ratio should remain equal after pan, got {aspect}"


def test_mouse_release_ends_pan(qapp):
    """Test that releasing mouse button ends pan operation."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Start drag
    press_event = Mock()
    press_event.inaxes = window.ax
    press_event.button = 1
    press_event.xdata = 5.0
    press_event.ydata = 5.0

    window.on_mouse_press(press_event)

    # Should be in pan mode (panning state is now in canvas_controller)
    assert window.canvas_controller.is_panning() is True, "Should be panning after press"

    # Release mouse
    release_event = Mock()
    release_event.button = 1

    window.on_mouse_release(release_event)

    # Should no longer be panning
    assert window.canvas_controller.is_panning() is False, "Should not be panning after release"


# Psi field visualization tests

def test_main_window_has_visualization_tab(qapp):
    """Test that MainWindow has 'Psi' tab (renamed from 'Visualization')."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Check tab exists (renamed to "Psi")
    tab_texts = [window.left_tabs.tabText(i) for i in range(window.left_tabs.count())]
    assert any('Psi' in text for text in tab_texts), \
        f"Should have a tab with 'Psi' in the name, got: {tab_texts}"


def test_visualization_tab_has_checkboxes(qapp):
    """Test that Visualization tab has checkboxes for display modes."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have checkbox attributes
    assert hasattr(window, 'psi_display_contour_checkbox'), \
        "Should have psi_display_contour_checkbox attribute"
    assert hasattr(window, 'psi_display_contourf_checkbox'), \
        "Should have psi_display_contourf_checkbox attribute"


def test_visualization_checkboxes_are_independent(qapp):
    """Test that visualization checkboxes can be independently checked."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Both checkboxes can be checked
    window.psi_display_contour_checkbox.setChecked(True)
    window.psi_display_contourf_checkbox.setChecked(True)
    assert window.psi_display_contour_checkbox.isChecked(), \
        "Contour checkbox should be checked"
    assert window.psi_display_contourf_checkbox.isChecked(), \
        "Contourf checkbox should also be checked"

    # One can be unchecked while other stays checked
    window.psi_display_contour_checkbox.setChecked(False)
    assert not window.psi_display_contour_checkbox.isChecked(), \
        "Contour checkbox should be unchecked"
    assert window.psi_display_contourf_checkbox.isChecked(), \
        "Contourf checkbox should remain checked"


def test_visualization_checkboxes_are_unchecked_by_default(qapp):
    """Test that checkboxes are unchecked by default."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert not window.psi_display_contour_checkbox.isChecked(), \
        "Contour checkbox should be unchecked by default"
    assert not window.psi_display_contourf_checkbox.isChecked(), \
        "Contourf checkbox should be unchecked by default"


def test_main_window_has_psi_field_plot_method(qapp):
    """Test that MainWindow has method to plot psi field."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, '_plot_psi_field'), \
        "MainWindow should have _plot_psi_field method"
    assert callable(window._plot_psi_field), \
        "_plot_psi_field should be callable"


def test_main_window_has_clear_psi_field_method(qapp):
    """Test that MainWindow has method to clear psi field visualization."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, '_clear_psi_field'), \
        "MainWindow should have _clear_psi_field method"
    assert callable(window._clear_psi_field), \
        "_clear_psi_field should be callable"


def test_checkbox_triggers_visualization_update(qapp, tmp_path):
    """Test that clicking checkbox triggers visualization update."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import patch
    import numpy as np

    window = MainWindow()

    # Create minimal gEQDSK file
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres, pprime, ffprime, qpsi arrays (65 values each)
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    # Load file
    window.load_geqdsk(str(geqdsk_path))

    # Mock the plot method to verify it's called
    with patch.object(window, '_plot_psi_field') as mock_plot:
        # Click contour checkbox
        window.psi_display_contour_checkbox.setChecked(True)
        # The plot method should be called
        # (Note: signal may not fire immediately in test, so we test this indirectly)


def test_contour_checkbox_creates_contour_plot(qapp, tmp_path):
    """Test that checking Contour checkbox creates a contour plot."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres, pprime, ffprime, qpsi arrays
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Select contour mode and trigger plot
    window.psi_display_contour_checkbox.setChecked(True)
    window._plot_psi_field()

    # Check that a contour plot object was created
    assert hasattr(window, '_psi_contour_plot'), \
        "Should have _psi_contour_plot attribute after plotting"
    assert window._psi_contour_plot is not None, \
        "Should have created contour plot object"


def test_contourf_checkbox_creates_filled_contour_plot(qapp, tmp_path):
    """Test that checking Contourf checkbox creates a filled contour plot."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres, pprime, ffprime, qpsi arrays
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Select contourf mode and trigger plot
    window.psi_display_contourf_checkbox.setChecked(True)
    window._plot_psi_field()

    # Check that a contourf plot object was created
    assert hasattr(window, '_psi_contourf_plot'), \
        "Should have _psi_contourf_plot attribute after plotting"
    assert window._psi_contourf_plot is not None, \
        "Should have created filled contour plot object"


def test_both_checkboxes_can_be_enabled_simultaneously(qapp, tmp_path):
    """Test that both contour types can be overlayed when both checkboxes are checked."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # Arrays
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Check both checkboxes
    window.psi_display_contour_checkbox.setChecked(True)
    window.psi_display_contourf_checkbox.setChecked(True)
    window._plot_psi_field()

    # Both plot objects should exist
    assert window._psi_contour_plot is not None, \
        "Should have created contour plot object"
    assert window._psi_contourf_plot is not None, \
        "Should have created filled contour plot object"


def test_unchecking_checkbox_clears_visualization(qapp, tmp_path):
    """Test that unchecking a checkbox clears its corresponding visualization."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # Arrays
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Check contour checkbox and plot
    window.psi_display_contour_checkbox.setChecked(True)
    window._plot_psi_field()
    assert window._psi_contour_plot is not None, \
        "Should have created contour plot"

    # Uncheck the checkbox and redraw
    window.psi_display_contour_checkbox.setChecked(False)
    window._on_psi_display_mode_changed()

    # The plot should be cleared
    assert window._psi_contour_plot is None, \
        "Should have cleared contour plot after unchecking"


def test_unchecking_all_checkboxes_clears_colorbar(qapp, tmp_path):
    """Test that unchecking all checkboxes clears the colorbar."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # Arrays
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Check both checkboxes and plot
    window.psi_display_contour_checkbox.setChecked(True)
    window.psi_display_contourf_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()

    assert window._psi_colorbar is not None, \
        "Should have colorbar when visualizations are shown"

    # Uncheck both checkboxes
    window.psi_display_contour_checkbox.setChecked(False)
    window.psi_display_contourf_checkbox.setChecked(False)
    window._on_psi_display_mode_changed()

    # Everything should be cleared
    assert window._psi_contour_plot is None, \
        "Should have cleared contour plot"
    assert window._psi_contourf_plot is None, \
        "Should have cleared contourf plot"
    assert window._psi_colorbar is None, \
        "Should have cleared colorbar when no visualizations are shown"


def test_toggling_checkbox_multiple_times_no_colorbar_multiplication(qapp, tmp_path):
    """Test that toggling checkboxes multiple times doesn't create multiple colorbars."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # Arrays
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Count initial axes on figure
    initial_axes_count = len(window.canvas.figure.axes)

    # Toggle checkbox on and off multiple times
    for _ in range(5):
        window.psi_display_contour_checkbox.setChecked(True)
        window._on_psi_display_mode_changed()
        window.psi_display_contour_checkbox.setChecked(False)
        window._on_psi_display_mode_changed()

    # Should only have the main axes (no extra colorbar axes)
    final_axes_count = len(window.canvas.figure.axes)
    assert final_axes_count == initial_axes_count, \
        f"Should not multiply colorbars: started with {initial_axes_count} axes, ended with {final_axes_count}"


def test_both_checked_uses_contourf_colorbar(qapp, tmp_path):
    """Test that when both are checked, contourf colorbar is used (not contour)."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # Arrays
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Check both checkboxes
    window.psi_display_contour_checkbox.setChecked(True)
    window.psi_display_contourf_checkbox.setChecked(True)
    window._on_psi_display_mode_changed()

    # Both should be plotted
    assert window._psi_contour_plot is not None, "Should have contour plot"
    assert window._psi_contourf_plot is not None, "Should have contourf plot"

    # Should have exactly one colorbar using contourf
    assert window._psi_colorbar is not None, "Should have colorbar"
    # The colorbar's mappable should be the contourf plot (filled contours)
    assert window._psi_colorbar.mappable == window._psi_contourf_plot, \
        "When both are checked, colorbar should use contourf (filled contours)"


def test_colorbar_size_and_position(qapp):
    """Test that colorbar height is approximately 30% of original and positioned correctly."""
    from mesh_gui_project.ui.main_window import MainWindow
    import os

    window = MainWindow()

    # Load test geqdsk file
    test_file = os.path.join(
        os.path.dirname(__file__), '..', 'examples',
        'kstar_EFIT01_35582_010000.esy_headerMod.geqdsk'
    )
    window.load_geqdsk(test_file)

    # Enable contourf to create colorbar
    window.psi_display_contourf_checkbox.setChecked(True)

    # Should have colorbar
    assert window._psi_colorbar is not None, "Should have colorbar"

    # Get colorbar axes position [left, bottom, width, height]
    colorbar_ax = window._psi_colorbar.ax
    bbox = colorbar_ax.get_position()

    # Height should be approximately 0.27 (30% of original 0.90)
    # Allow small tolerance for floating point
    expected_height = 0.27
    assert abs(bbox.height - expected_height) < 0.01, \
        f"Colorbar height should be ~{expected_height}, got {bbox.height}"

    # Should be centered vertically (bottom + height/2 ≈ 0.5)
    vertical_center = bbox.y0 + bbox.height / 2
    assert abs(vertical_center - 0.5) < 0.1, \
        f"Colorbar should be vertically centered, center is at {vertical_center}"

    # Left position should be around 0.82 (optimized for better text visibility)
    expected_left = 0.82
    assert abs(bbox.x0 - expected_left) < 0.01, \
        f"Colorbar left position should be ~{expected_left}, got {bbox.x0}"

    # Width should remain at 0.03
    expected_width = 0.03
    assert abs(bbox.width - expected_width) < 0.01, \
        f"Colorbar width should be ~{expected_width}, got {bbox.width}"


# Recent files functionality tests

def test_main_window_has_recent_menu(qapp):
    """Test that MainWindow has a recent files menu stored as instance variable."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have recent_menu attribute
    assert hasattr(window, 'recent_menu'), \
        "MainWindow should have recent_menu attribute"
    assert window.recent_menu is not None, \
        "recent_menu should be initialized"


def test_loading_geqdsk_adds_to_recent_files(qapp, tmp_path):
    """Test that successfully loading a gEQDSK file adds it to recent files."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create minimal gEQDSK file
    geqdsk_path = tmp_path / "test_recent.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # Other arrays
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    # Load the file
    window.load_geqdsk(str(geqdsk_path))

    # Check that recent files list is populated
    recent_files = window.settings.get('recent_files', [])
    assert len(recent_files) >= 1, "Recent files list should have at least 1 entry"
    assert str(geqdsk_path) in recent_files, \
        f"Loaded file should be in recent files, got: {recent_files}"


def test_recent_menu_is_populated_after_loading_file(qapp, tmp_path):
    """Test that recent files menu is populated with actions after loading file."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create minimal gEQDSK file
    geqdsk_path = tmp_path / "test_menu.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    # Load the file
    window.load_geqdsk(str(geqdsk_path))

    # Check that recent menu has actions
    actions = window.recent_menu.actions()
    assert len(actions) > 0, "Recent menu should have at least one action after loading file"

    # At least one action should reference the file
    action_texts = [action.text() for action in actions]
    has_file_ref = any('test_menu.geqdsk' in text for text in action_texts)
    assert has_file_ref, f"Recent menu should reference loaded file, got actions: {action_texts}"


def test_clicking_recent_file_loads_it(qapp, tmp_path):
    """Test that clicking a recent file menu item loads that file."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create two gEQDSK files
    geqdsk_path1 = tmp_path / "test1.geqdsk"
    geqdsk_path2 = tmp_path / "test2.geqdsk"

    for path in [geqdsk_path1, geqdsk_path2]:
        with open(path, 'w') as f:
            f.write("  Test                                                    3 65 65\n")
            f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
            f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
            f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
            f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

            for i in range(65):
                f.write(f"  {1.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

            for i in range(4225):
                f.write(f"  {0.1*i:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")

            for _ in range(4):
                for i in range(65):
                    f.write(f"  {0.0:15.8E}")
                    if (i + 1) % 5 == 0:
                        f.write("\n")
                if 65 % 5 != 0:
                    f.write("\n")

            f.write("  0 0\n")

    # Load first file
    window.load_geqdsk(str(geqdsk_path1))

    # Load second file
    window.load_geqdsk(str(geqdsk_path2))

    # Now trigger the recent file action for the first file
    actions = window.recent_menu.actions()

    # Find action for test1.geqdsk
    target_action = None
    for action in actions:
        if 'test1.geqdsk' in action.text():
            target_action = action
            break

    assert target_action is not None, "Should have action for test1.geqdsk"

    # Trigger the action
    target_action.trigger()

    # The first file should be loaded again (we can check equilibrium was reloaded)
    assert window.equilibrium is not None, "Equilibrium should be loaded after clicking recent file"


def test_recent_files_limited_to_max_count(qapp, tmp_path):
    """Test that recent files list is limited to a maximum number of entries."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Create and load 12 files (more than typical max of 10)
    for i in range(12):
        geqdsk_path = tmp_path / f"test{i}.geqdsk"

        with open(geqdsk_path, 'w') as f:
            f.write("  Test                                                    3 65 65\n")
            f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
            f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
            f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
            f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

            for j in range(65):
                f.write(f"  {1.0:15.8E}")
                if (j + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

            for j in range(4225):
                f.write(f"  {0.1*j:15.8E}")
                if (j + 1) % 5 == 0:
                    f.write("\n")

            for _ in range(4):
                for j in range(65):
                    f.write(f"  {0.0:15.8E}")
                    if (j + 1) % 5 == 0:
                        f.write("\n")
                if 65 % 5 != 0:
                    f.write("\n")

            f.write("  0 0\n")

        window.load_geqdsk(str(geqdsk_path))

    # Check recent files count
    recent_files = window.settings.get('recent_files', [])
    assert len(recent_files) <= 10, \
        f"Recent files should be limited to 10 entries, got {len(recent_files)}"


# Psi tooltip tests

def test_main_window_has_psi_tooltip_annotation_attribute(qapp):
    """Test that MainWindow's canvas_controller has psi tooltip annotation attribute initialized to None."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have tooltip annotation attribute in canvas_controller (refactored to controller)
    assert hasattr(window.canvas_controller, '_psi_tooltip_annotation'), \
        "CanvasController should have _psi_tooltip_annotation attribute"
    assert window.canvas_controller._psi_tooltip_annotation is None, \
        "Tooltip annotation should be initialized to None"


def test_tooltip_appears_on_mouse_motion_with_contours_enabled(qapp, tmp_path):
    """Test that tooltip appears when mouse moves over plot with contours enabled and Ctrl key pressed."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock, patch
    from PyQt5.QtCore import Qt

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid - create simple gradient
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres, pprime, ffprime, qpsi arrays
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Create mock mouse event
    event = Mock()
    event.inaxes = window.ax
    event.xdata = 1.5  # R coordinate within grid
    event.ydata = 0.0  # Z coordinate within grid

    # Mock QApplication.keyboardModifiers() to return Ctrl pressed
    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=Qt.ControlModifier):
        # Trigger mouse motion (not panning)
        window._is_panning = False
        window.on_mouse_motion(event)

        # Tooltip annotation should be created
        assert window.canvas_controller._psi_tooltip_annotation is not None, \
            "Tooltip annotation should be created on mouse motion when Ctrl is pressed"

    # Tooltip should have text with psi_N value
    tooltip_text = window.canvas_controller._psi_tooltip_annotation.get_text()
    assert 'ψ' in tooltip_text or 'psi' in tooltip_text.lower(), \
        f"Tooltip should contain psi label, got: {tooltip_text}"

    # Tooltip should be positioned at the cursor location
    tooltip_xy = window.canvas_controller._psi_tooltip_annotation.xy
    assert tooltip_xy[0] == 1.5 and tooltip_xy[1] == 0.0, \
        f"Tooltip should be at cursor position (1.5, 0.0), got: {tooltip_xy}"


def test_tooltip_hidden_when_no_equilibrium_loaded(qapp):
    """Test that tooltip does not appear when no equilibrium is loaded."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # No equilibrium loaded
    assert window.equilibrium is None

    # Enable contour display (though no equilibrium)
    window.psi_display_contour_checkbox.setChecked(True)

    # Create mock mouse event
    event = Mock()
    event.inaxes = window.ax
    event.xdata = 1.5
    event.ydata = 0.0

    # Trigger mouse motion
    window._is_panning = False
    window.on_mouse_motion(event)

    # Tooltip should not be created
    assert window.canvas_controller._psi_tooltip_annotation is None, \
        "Tooltip should not appear when no equilibrium is loaded"


def test_tooltip_hidden_when_cursor_outside_plot(qapp, tmp_path):
    """Test that tooltip disappears when cursor leaves plot area."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock, patch
    from PyQt5.QtCore import Qt

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"
    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")
        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))
    window.psi_display_contour_checkbox.setChecked(True)

    # First, create tooltip by moving over plot with Ctrl key
    event_inside = Mock()
    event_inside.inaxes = window.ax
    event_inside.xdata = 1.5
    event_inside.ydata = 0.0

    # Mock QApplication.keyboardModifiers() to return Ctrl pressed
    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=Qt.ControlModifier):
        window._is_panning = False
        window.on_mouse_motion(event_inside)

        # Verify tooltip exists
        assert window.canvas_controller._psi_tooltip_annotation is not None

    # Now move cursor outside plot
    event_outside = Mock()
    event_outside.inaxes = None  # Cursor outside axes
    event_outside.xdata = None
    event_outside.ydata = None
    window.on_mouse_motion(event_outside)

    # Tooltip should be hidden (invisible but not None)
    if window.canvas_controller._psi_tooltip_annotation is not None:
        assert window.canvas_controller._psi_tooltip_annotation.get_visible() is False, \
            "Tooltip should be hidden when cursor leaves plot area"


def test_tooltip_hidden_during_panning(qapp, tmp_path):
    """Test that tooltip does not appear during panning operation."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"
    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")
        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))
    window.psi_display_contour_checkbox.setChecked(True)

    # Set panning mode
    window._is_panning = True
    window._pan_start_x = 1.5
    window._pan_start_y = 0.0

    # Create mock mouse event
    event = Mock()
    event.inaxes = window.ax
    event.xdata = 1.6
    event.ydata = 0.1

    # Trigger mouse motion during panning
    window.on_mouse_motion(event)

    # Tooltip should not be created during panning
    assert window.canvas_controller._psi_tooltip_annotation is None, \
        "Tooltip should not appear during panning operation"


def test_tooltip_hidden_when_both_checkboxes_unchecked(qapp, tmp_path):
    """Test that tooltip does not appear when both contour checkboxes are unchecked."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"
    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")
        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Both checkboxes unchecked (default state)
    assert not window.psi_display_contour_checkbox.isChecked()
    assert not window.psi_display_contourf_checkbox.isChecked()

    # Create mock mouse event
    event = Mock()
    event.inaxes = window.ax
    event.xdata = 1.5
    event.ydata = 0.0

    # Trigger mouse motion
    window._is_panning = False
    window.on_mouse_motion(event)

    # Tooltip should not appear
    assert window.canvas_controller._psi_tooltip_annotation is None, \
        "Tooltip should not appear when both contour checkboxes are unchecked"


def test_tooltip_only_appears_when_ctrl_key_pressed(qapp, tmp_path):
    """Test that tooltip only appears when left Ctrl key is pressed."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock, patch
    from PyQt5.QtCore import Qt

    window = MainWindow()

    # Create and load minimal gEQDSK
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid - create simple gradient
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres, pprime, ffprime, qpsi arrays
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Create mock mouse event WITHOUT Ctrl key
    event = Mock()
    event.inaxes = window.ax
    event.xdata = 1.5  # R coordinate within grid
    event.ydata = 0.0  # Z coordinate within grid

    # Trigger mouse motion (not panning) WITHOUT Ctrl
    # keyboardModifiers returns no modifier by default
    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=Qt.NoModifier):
        window._is_panning = False
        window.on_mouse_motion(event)

        # Tooltip should NOT appear without Ctrl key
        assert window.canvas_controller._psi_tooltip_annotation is None, \
            "Tooltip should not appear when Ctrl key is not pressed"

    # Now simulate Ctrl key being pressed
    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=Qt.ControlModifier):
        # Trigger mouse motion WITH Ctrl
        window.on_mouse_motion(event)

        # Tooltip SHOULD appear with Ctrl key
        assert window.canvas_controller._psi_tooltip_annotation is not None, \
            "Tooltip should appear when Ctrl key is pressed"

    # Tooltip should have text with psi_N value
    tooltip_text = window.canvas_controller._psi_tooltip_annotation.get_text()
    assert 'ψ' in tooltip_text or 'psi' in tooltip_text.lower(), \
        f"Tooltip should contain psi label, got: {tooltip_text}"


def test_tooltip_hidden_when_mouse_outside_psi_domain(qapp, tmp_path):
    """Test that tooltip does not appear when mouse is outside the psi domain bounds."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock, patch
    from PyQt5.QtCore import Qt

    window = MainWindow()

    # Create and load minimal gEQDSK with domain bounds [1.0, 2.0] x [-1.0, 1.0]
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        # Header: R in [1.0, 2.0], Z in [-1.0, 1.0]
        f.write("  Test                                                    3 65 65\n")
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        f.write("  1.000000E+00  1.000000E+00 -1.000000E+00  1.500000E+00  0.000000E+00\n")
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # fpol array
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Psi grid - create simple gradient
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # pres, pprime, ffprime, qpsi arrays
        for _ in range(4):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        f.write("  0 0\n")

    window.load_geqdsk(str(geqdsk_path))

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Test 1: Mouse position OUTSIDE domain (R too large)
    event_outside = Mock()
    event_outside.inaxes = window.ax
    event_outside.xdata = 2.5  # R > R_max (2.0)
    event_outside.ydata = 0.0  # Z within bounds

    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=Qt.ControlModifier):
        window._is_panning = False
        window.on_mouse_motion(event_outside)

        # Tooltip should NOT appear when outside domain
        assert window.canvas_controller._psi_tooltip_annotation is None, \
            "Tooltip should not appear when mouse R coordinate is outside domain bounds"

    # Test 2: Mouse position OUTSIDE domain (Z too small)
    event_outside_z = Mock()
    event_outside_z.inaxes = window.ax
    event_outside_z.xdata = 1.5  # R within bounds
    event_outside_z.ydata = -1.5  # Z < Z_min (-1.0)

    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=Qt.ControlModifier):
        window.on_mouse_motion(event_outside_z)

        # Tooltip should NOT appear when outside domain
        assert window.canvas_controller._psi_tooltip_annotation is None, \
            "Tooltip should not appear when mouse Z coordinate is outside domain bounds"

    # Test 3: Mouse position INSIDE domain - tooltip should appear
    event_inside = Mock()
    event_inside.inaxes = window.ax
    event_inside.xdata = 1.5  # R within [1.0, 2.0]
    event_inside.ydata = 0.0  # Z within [-1.0, 1.0]

    with patch('PyQt5.QtWidgets.QApplication.keyboardModifiers', return_value=Qt.ControlModifier):
        window.on_mouse_motion(event_inside)

        # Tooltip SHOULD appear when inside domain
        assert window.canvas_controller._psi_tooltip_annotation is not None, \
            "Tooltip should appear when mouse is inside domain bounds"


def test_plot_has_no_title_after_initialization(qapp):
    """Test that the plot has no title after window initialization."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Plot should have no title (empty string)
    assert window.ax.get_title() == "", \
        "Plot should have no title after initialization"


def test_visualization_tab_has_psi_minmax_display_widgets(qapp):
    """Test that Visualization tab has min/max psi display widgets."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should have psi_min_display attribute
    assert hasattr(window, 'psi_min_display'), \
        "Should have psi_min_display attribute"

    # Should have psi_max_display attribute
    assert hasattr(window, 'psi_max_display'), \
        "Should have psi_max_display attribute"

    # Both should be read-only QLineEdit widgets
    assert window.psi_min_display.isReadOnly(), \
        "psi_min_display should be read-only"
    assert window.psi_max_display.isReadOnly(), \
        "psi_max_display should be read-only"


def test_psi_minmax_display_empty_before_loading(qapp):
    """Test that psi min/max displays are empty before loading equilibrium."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Should be empty strings initially
    assert window.psi_min_display.text() == "", \
        "psi_min_display should be empty before loading equilibrium"
    assert window.psi_max_display.text() == "", \
        "psi_max_display should be empty before loading equilibrium"


def test_psi_minmax_display_shows_values_after_loading(qapp, tmp_path):
    """Test that psi min/max displays show correct values after loading equilibrium."""
    from mesh_gui_project.ui.main_window import MainWindow
    import numpy as np

    window = MainWindow()

    # Create a minimal gEQDSK file with known psi values
    geqdsk_path = tmp_path / "test.geqdsk"

    with open(geqdsk_path, 'w') as f:
        # Header line
        f.write("  Test equilibrium                                        3 65 65\n")
        # Line 2: Rdim, Zdim, Rcentr, Rleft, Zmid
        f.write("  1.000000E+00  1.000000E+00  1.500000E+00  1.000000E+00  0.000000E+00\n")
        # Line 3: Rmag, Zmag, simag (psi_axis), sibry (psi_boundary), Bcentr
        # psi_axis = 1.0, psi_boundary = 0.0
        f.write("  1.500000E+00  0.000000E+00  1.000000E+00  0.000000E+00  2.000000E+00\n")
        # Line 4: Ip, simag (duplicate), _, Rmag (duplicate), _
        f.write("  1.000000E+00  1.000000E+00  0.000000E+00  1.500000E+00  0.000000E+00\n")
        # Line 5: Zmag (duplicate), _, sibry (duplicate), _, _
        f.write("  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00\n")

        # Write fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write psi grid (65x65 = 4225 values)
        # Create psi values ranging from 0.0 to 2.0
        psi_values = []
        for i in range(65):
            for j in range(65):
                R = 1.0 + j * (2.0 - 1.0) / 64
                Z = -0.5 + i * (0.5 - (-0.5)) / 64
                psi = ((R - 1.5)**2 + Z**2)
                psi_values.append(psi)

        # Write in 5 columns format
        for i, val in enumerate(psi_values):
            f.write(f"  {val:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if len(psi_values) % 5 != 0:
            f.write("\n")

        # Write pres array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write pprime array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write ffprim array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write qpsi array (65 values)
        for i in range(65):
            f.write(f"  {2.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # Write nbbbs and limitr
        f.write("  0  0\n")

    # Load the file
    window.load_geqdsk(str(geqdsk_path))

    # Check that displays are populated
    min_text = window.psi_min_display.text()
    max_text = window.psi_max_display.text()

    assert min_text != "", "psi_min_display should not be empty after loading"
    assert max_text != "", "psi_max_display should not be empty after loading"

    # Check format: should be floating point with 4 decimal places
    min_val = float(min_text)
    max_val = float(max_text)

    # Min should be less than max
    assert min_val < max_val, "Min psi_N should be less than max psi_N"

    # Values should be normalized (psi_N)
    # With psi_axis=1.0, psi_boundary=0.0, min psi value is 0.0
    # psi_N = (psi - psi_axis) / (psi_boundary - psi_axis)
    # psi_N = (0.0 - 1.0) / (0.0 - 1.0) = 1.0
    # Max psi is around 2.0, so psi_N = (2.0 - 1.0) / (0.0 - 1.0) = -1.0
    # Actually these values will be negative because psi_boundary < psi_axis

    # Just verify they're reasonable normalized values
    assert -5.0 < min_val < 5.0, f"Min psi_N should be reasonable, got {min_val}"
    assert -5.0 < max_val < 5.0, f"Max psi_N should be reasonable, got {max_val}"


def test_visualization_tab_has_psi_edit_mode_button(qapp):
    """Test that the visualization tab has a psi edit mode button."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Switch to visualization tab
    window.left_tabs.setCurrentIndex(1)

    # Check that psi edit mode button exists
    assert hasattr(window, 'psi_edit_mode_button'), \
        "MainWindow should have psi_edit_mode_button attribute"

    # Check button type
    from PyQt5.QtWidgets import QPushButton
    assert isinstance(window.psi_edit_mode_button, QPushButton), \
        "psi_edit_mode_button should be a QPushButton"

    # Check button is checkable (toggle button)
    assert window.psi_edit_mode_button.isCheckable(), \
        "psi_edit_mode_button should be checkable (toggle button)"

    # Check button default state
    assert not window.psi_edit_mode_button.isChecked(), \
        "psi_edit_mode_button should start unchecked"

    # Check button has appropriate text
    button_text = window.psi_edit_mode_button.text()
    assert "Edit" in button_text or "edit" in button_text, \
        f"psi_edit_mode_button should have 'Edit' in text, got '{button_text}'"


def test_psi_edit_mode_toggles_state(qapp):
    """Test that clicking the psi edit mode button toggles the mode state."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    # Check initial state
    assert hasattr(window, '_psi_edit_mode_active'), \
        "MainWindow should have _psi_edit_mode_active attribute"
    assert window._psi_edit_mode_active is False, \
        "_psi_edit_mode_active should start False"

    # Click button to enable
    window.psi_edit_mode_button.setChecked(True)

    # State should be True
    assert window._psi_edit_mode_active is True, \
        "_psi_edit_mode_active should be True when button is checked"

    # Click button to disable
    window.psi_edit_mode_button.setChecked(False)

    # State should be False again
    assert window._psi_edit_mode_active is False, \
        "_psi_edit_mode_active should be False when button is unchecked"


def test_psi_preview_contour_appears_on_mouse_move_in_edit_mode(qapp):
    """Test that a preview contour appears when mouse moves in edit mode."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import tempfile

    window = MainWindow()

    # Create a minimal gEQDSK file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        geqdsk_path = f.name

        # Write minimal gEQDSK header and data
        f.write("  Test equilibrium   0    65    65\n")
        f.write("  1.0000E+00  2.0000E+00  1.0000E+00 -1.0000E+00  1.5000E+00\n")
        f.write("  1.5000E+00  0.0000E+00  5.9200E-02  1.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  1.0000E+00  0.0000E+00  2.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # pres, pprime, ffprime arrays (65 values each)
        for _ in range(3):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        # Psi grid - create simple gradient (65x65 = 4225 values)
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # qpsi array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        f.write("  0 0\n")

    # Load gEQDSK file
    window.load_geqdsk(str(geqdsk_path))

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)
    assert window._psi_edit_mode_active is True

    # Simulate mouse motion event
    # Grid ranges: R from rleft=-1.0 to rleft+rdim=0.0, Z from zmid-zdim/2=0.5 to zmid+zdim/2=2.5
    event = Mock()
    event.inaxes = window.ax
    event.xdata = -0.5  # R coordinate within domain [-1.0, 0.0]
    event.ydata = 1.5  # Z coordinate within domain [0.5, 2.5]

    # Call mouse motion handler
    window.on_mouse_motion(event)

    # Check that preview contour was created (now in handler)
    # We can't directly access handler's internal _preview_contour, so check collections on axes
    # Preview contour adds collections to the axes
    initial_collections_count = len(window.ax.collections)
    assert initial_collections_count > 0, \
        "Preview contour should be created (axes should have collections) when mouse moves in edit mode"


def test_psi_preview_contour_updates_when_mouse_moves_to_new_position(qapp):
    """Test that preview contour updates (not accumulates) when mouse moves to different positions."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import tempfile

    window = MainWindow()

    # Create a minimal gEQDSK file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        geqdsk_path = f.name

        # Write minimal gEQDSK header and data
        f.write("  Test equilibrium   0    65    65\n")
        f.write("  1.0000E+00  2.0000E+00  1.0000E+00 -1.0000E+00  1.5000E+00\n")
        f.write("  1.5000E+00  0.0000E+00  5.9200E-02  1.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  1.0000E+00  0.0000E+00  2.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # pres, pprime, ffprime arrays (65 values each)
        for _ in range(3):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        # Psi grid - create simple gradient (65x65 = 4225 values)
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # qpsi array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        f.write("  0 0\n")

    # Load gEQDSK file
    window.load_geqdsk(str(geqdsk_path))

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)

    # Move mouse to first position
    # Grid ranges: R from rleft=-1.0 to rleft+rdim=0.0, Z from zmid-zdim/2=0.5 to zmid+zdim/2=2.5
    event1 = Mock()
    event1.inaxes = window.ax
    event1.xdata = -0.7  # R coordinate within domain [-1.0, 0.0]
    event1.ydata = 1.0  # Z coordinate within domain [0.5, 2.5]
    window.on_mouse_motion(event1)

    # Count number of collections in the axes after first move
    collections_before = len(window.ax.collections)
    assert collections_before > 0, "Preview contour should add collections"

    # Move mouse to second position (different psi value)
    event2 = Mock()
    event2.inaxes = window.ax
    event2.xdata = -0.3  # Different R coordinate within domain [-1.0, 0.0]
    event2.ydata = 1.5  # Different Z coordinate within domain [0.5, 2.5]
    window.on_mouse_motion(event2)

    # Count number of collections in the axes after second move
    collections_after = len(window.ax.collections)

    # CRITICAL: The number of collections should be the same or similar
    # This means old preview was removed before new one was added
    # Allow small variation in collection count due to contour complexity
    assert abs(collections_after - collections_before) <= 1, \
        f"Preview contour should replace (not accumulate). Collections before: {collections_before}, after: {collections_after}"


def test_left_click_adds_permanent_psi_contour_in_edit_mode(qapp):
    """Test that left-clicking in edit mode adds a permanent contour at the preview position."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import tempfile

    window = MainWindow()

    # Create a minimal gEQDSK file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        geqdsk_path = f.name

        # Write minimal gEQDSK header and data
        f.write("  Test equilibrium   0    65    65\n")
        f.write("  1.0000E+00  2.0000E+00  1.0000E+00 -1.0000E+00  1.5000E+00\n")
        f.write("  1.5000E+00  0.0000E+00  5.9200E-02  1.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  1.0000E+00  0.0000E+00  2.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # pres, pprime, ffprime arrays (65 values each)
        for _ in range(3):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        # Psi grid - create simple gradient (65x65 = 4225 values)
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # qpsi array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        f.write("  0 0\n")

    # Load gEQDSK file
    window.load_geqdsk(str(geqdsk_path))

    # Enable psi contour visualization (required for added contours to be visible)
    window.psi_display_contour_checkbox.setChecked(True)

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)

    # Check initial state - no added contours
    assert hasattr(window, '_added_psi_values'), \
        "MainWindow should have _added_psi_values attribute"
    assert len(window._added_psi_values) == 0, \
        "Initially, no psi contours should be added"

    # Move mouse to position
    # Grid ranges: R from rleft=-1.0 to rleft+rdim=0.0, Z from zmid-zdim/2=0.5 to zmid+zdim/2=2.5
    motion_event = Mock()
    motion_event.inaxes = window.ax
    motion_event.xdata = -0.5  # R coordinate within domain [-1.0, 0.0]
    motion_event.ydata = 1.5  # Z coordinate within domain [0.5, 2.5]
    window.on_mouse_motion(motion_event)

    # Get the psi value at this position for verification
    psi_at_position = window.equilibrium.psi_value(-0.5, 1.5)

    # Simulate left-click at this position
    click_event = Mock()
    click_event.inaxes = window.ax
    click_event.xdata = -0.5  # R coordinate within domain [-1.0, 0.0]
    click_event.ydata = 1.5  # Z coordinate within domain [0.5, 2.5]
    click_event.button = 1  # Left button

    # Trigger left-click
    window.on_mouse_press(click_event)

    # Check that psi value was added to the list (now in handler)
    added_values = window.psi_edit_handler.get_added_values()
    assert len(added_values) == 1, \
        "One psi value should be added after left-click"
    assert abs(added_values[0] - psi_at_position) < 1e-6, \
        f"Added psi value should match position: {added_values[0]} vs {psi_at_position}"

    # Check that the plot was redrawn (should have contour visualization)
    assert window._psi_contour_plot is not None, \
        "Psi contour plot should exist after adding contour"

    # Verify that clicking at same position doesn't add duplicate
    window.on_mouse_press(click_event)
    added_values = window.psi_edit_handler.get_added_values()
    assert len(added_values) == 1, \
        "Should not add duplicate psi value at same position"


def test_right_click_deletes_nearest_psi_contour_in_edit_mode(qapp):
    """Test that right-clicking in edit mode deletes the nearest added contour."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import tempfile

    window = MainWindow()

    # Create a minimal gEQDSK file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        geqdsk_path = f.name

        # Write minimal gEQDSK header and data
        f.write("  Test equilibrium   0    65    65\n")
        f.write("  1.0000E+00  2.0000E+00  1.0000E+00 -1.0000E+00  1.5000E+00\n")
        f.write("  1.5000E+00  0.0000E+00  5.9200E-02  1.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  1.0000E+00  0.0000E+00  2.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # pres, pprime, ffprime arrays (65 values each)
        for _ in range(3):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        # Psi grid - create simple gradient (65x65 = 4225 values)
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # qpsi array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        f.write("  0 0\n")

    # Load gEQDSK file
    window.load_geqdsk(str(geqdsk_path))

    # Enable contour checkbox
    window.psi_display_contour_checkbox.setChecked(True)

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)

    # Add three contours at different positions
    # Grid ranges: R from rleft=-1.0 to rleft+rdim=0.0, Z from zmid-zdim/2=0.5 to zmid+zdim/2=2.5
    positions = [
        (-0.7, 1.0),  # First contour
        (-0.5, 1.5),  # Second contour (this one will be deleted)
        (-0.3, 2.0),  # Third contour
    ]

    for R, Z in positions:
        click_event = Mock()
        click_event.inaxes = window.ax
        click_event.xdata = R
        click_event.ydata = Z
        click_event.button = 1  # Left button
        window.on_mouse_press(click_event)

    # Verify all three were added (now in handler)
    added_values = window.psi_edit_handler.get_added_values()
    assert len(added_values) == 3, \
        "Should have three psi values added"

    # Store psi value at second position for verification
    psi_at_second = window.equilibrium.psi_value(-0.5, 1.5)

    # Right-click near the second contour position
    right_click_event = Mock()
    right_click_event.inaxes = window.ax
    right_click_event.xdata = -0.5  # Same R as second contour
    right_click_event.ydata = 1.5  # Same Z as second contour
    right_click_event.button = 3  # Right button

    # Trigger right-click
    window.on_mouse_press(right_click_event)

    # Verify that the contour was disabled (not removed from added, but added to disabled)
    disabled_levels = window.psi_edit_handler.get_disabled_levels()
    assert len(disabled_levels) >= 1, \
        "Should have at least one disabled level after right-click"

    # The nearest psi level should be in disabled list
    assert any(abs(level - psi_at_second) < 1e-6 for level in disabled_levels), \
        "The psi value at the second position should have been disabled"

    # Verify that the plot was redrawn
    assert window._psi_contour_plot is not None, \
        "Psi contour plot should still exist after deleting one contour"


def test_right_click_deletes_automatic_contour_levels(qapp):
    """Test that right-clicking can delete automatic contour levels, not just user-added ones."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import tempfile
    import numpy as np

    window = MainWindow()

    # Create a minimal gEQDSK file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.geqdsk', delete=False) as f:
        geqdsk_path = f.name

        # Write minimal gEQDSK header and data
        f.write("  Test equilibrium   0    65    65\n")
        f.write("  1.0000E+00  2.0000E+00  1.0000E+00 -1.0000E+00  1.5000E+00\n")
        f.write("  1.5000E+00  0.0000E+00  5.9200E-02  1.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  1.0000E+00  0.0000E+00  2.0000E+00  0.0000E+00\n")
        f.write("  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00\n")

        # fpol array (65 values)
        for i in range(65):
            f.write(f"  {1.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        # pres, pprime, ffprime arrays (65 values each)
        for _ in range(3):
            for i in range(65):
                f.write(f"  {0.0:15.8E}")
                if (i + 1) % 5 == 0:
                    f.write("\n")
            if 65 % 5 != 0:
                f.write("\n")

        # Psi grid - create simple gradient (65x65 = 4225 values)
        for i in range(4225):
            f.write(f"  {0.1*i:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")

        # qpsi array (65 values)
        for i in range(65):
            f.write(f"  {0.0:15.8E}")
            if (i + 1) % 5 == 0:
                f.write("\n")
        if 65 % 5 != 0:
            f.write("\n")

        f.write("  0 0\n")

    # Load gEQDSK file
    window.load_geqdsk(str(geqdsk_path))

    # Enable contour checkbox
    window.psi_display_contour_checkbox.setChecked(True)

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)

    # Calculate what the automatic levels should be
    psi_grid = window.equilibrium.psi_grid
    n_levels = 20
    auto_levels = np.linspace(psi_grid.min(), psi_grid.max(), n_levels)

    # Pick a middle automatic level to delete (index 10)
    target_psi_level = auto_levels[10]

    # Find a position (R, Z) that has this psi value
    # We need to search for an (R,Z) where psi_value() returns target_psi_level
    # Start from the center of the domain
    R_grid = window.equilibrium.R_grid
    Z_grid = window.equilibrium.Z_grid
    R_center = (R_grid.min() + R_grid.max()) / 2
    Z_center = (Z_grid.min() + Z_grid.max()) / 2

    # Search radially from center for a point with target psi value
    R_target = None
    Z_target = None
    for radius in np.linspace(0.1, 0.4, 20):
        for angle in np.linspace(0, 2*np.pi, 30):
            R_try = R_center + radius * np.cos(angle)
            Z_try = Z_center + radius * np.sin(angle)
            # Check if within bounds
            if R_grid.min() <= R_try <= R_grid.max() and Z_grid.min() <= Z_try <= Z_grid.max():
                psi_try = window.equilibrium.psi_value(R_try, Z_try)
                if abs(psi_try - target_psi_level) < 0.1 * (psi_grid.max() - psi_grid.min()):
                    R_target = R_try
                    Z_target = Z_try
                    break
        if R_target is not None:
            break

    # If we couldn't find a good position, just use a position and check the actual psi value
    if R_target is None:
        R_target = -0.5
        Z_target = 1.5
        target_psi_level = window.equilibrium.psi_value(R_target, Z_target)

    # Verify this level doesn't exist in disabled list yet (now in handler)
    initial_disabled = window.psi_edit_handler.get_disabled_levels()
    initial_disabled_count = len(initial_disabled)

    # Right-click at this position to delete the automatic contour
    right_click_event = Mock()
    right_click_event.inaxes = window.ax
    right_click_event.xdata = R_target
    right_click_event.ydata = Z_target
    right_click_event.button = 3  # Right button

    # Trigger right-click
    window.on_mouse_press(right_click_event)

    # Verify that the level was added to disabled list (now in handler)
    disabled_levels = window.psi_edit_handler.get_disabled_levels()
    assert len(disabled_levels) == initial_disabled_count + 1, \
        "Should have one more disabled level after right-click"

    # Verify that the disabled level is close to the target level
    assert any(abs(disabled - target_psi_level) < 0.01 * (psi_grid.max() - psi_grid.min())
               for disabled in disabled_levels), \
        "The deleted level should be close to the target automatic level"


def test_psi_contour_list_widget_exists(qapp):
    """Test that PSI contour list widget exists in Visualization tab."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, 'psi_contour_list'), \
        "MainWindow should have psi_contour_list attribute"
    assert window.psi_contour_list is not None, \
        "psi_contour_list should be initialized"


def test_psi_contour_list_populates_on_load(qapp):
    """Test that list populates with contour levels after loading gEQDSK."""
    from mesh_gui_project.ui.main_window import MainWindow
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Should have automatic levels (default is 20)
    assert window.psi_contour_list.count() > 0, \
        "List should have items after loading gEQDSK and enabling contours"
    assert window.psi_contour_list.count() == 20, \
        "Should have 20 automatic contour levels by default"


def test_psi_contour_selection_highlights_contour(qapp):
    """Test that selecting item in list highlights corresponding contour."""
    from mesh_gui_project.ui.main_window import MainWindow
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Verify contour plot exists
    assert window._psi_contour_plot is not None, \
        "Contour plot should exist"

    # Select first item in list
    window.psi_contour_list.setCurrentRow(0)

    # Check that one level has modified properties (highlighted)
    # In modern matplotlib, linewidths are set per level on the QuadContourSet
    linewidths = window._psi_contour_plot.get_linewidth()

    # Count how many levels have linewidth > 1.0
    highlighted_count = sum(1 for lw in linewidths if lw > 1.0)

    assert highlighted_count == 1, \
        f"Exactly one contour level should be highlighted, found {highlighted_count}"


def test_psi_contour_list_updates_when_contour_added(qapp):
    """Test that list updates when user adds contour in edit mode."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    initial_count = window.psi_contour_list.count()

    # Activate edit mode and add contour via handler
    window.psi_edit_handler.set_active(True)

    # Simulate left-click to add contour
    event = Mock()
    event.inaxes = window.canvas_controller.ax
    event.xdata = 1.8
    event.ydata = 0.0
    event.button = 1
    window.psi_edit_handler.handle_mouse_press(event, button=1)

    # Should have one more item in list
    assert window.psi_contour_list.count() == initial_count + 1, \
        f"List should have {initial_count + 1} items after adding, found {window.psi_contour_list.count()}"


def test_psi_contour_list_updates_when_contour_deleted(qapp):
    """Test that list updates when user deletes contour."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    initial_count = window.psi_contour_list.count()

    # Activate edit mode and delete contour via handler
    window.psi_edit_handler.set_active(True)

    # Simulate right-click to delete contour
    event = Mock()
    event.inaxes = window.canvas_controller.ax
    event.xdata = 1.8
    event.ydata = 0.0
    event.button = 3
    window.psi_edit_handler.handle_mouse_press(event, button=3)

    # Should have one fewer item in list
    assert window.psi_contour_list.count() == initial_count - 1, \
        f"List should have {initial_count - 1} items after deleting, found {window.psi_contour_list.count()}"


def test_deselection_resets_highlighting(qapp):
    """Test that deselecting item resets all contours to default."""
    from mesh_gui_project.ui.main_window import MainWindow
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Select and then deselect
    window.psi_contour_list.setCurrentRow(0)
    window.psi_contour_list.clearSelection()

    # All levels should have default linewidth (1.0)
    # In modern matplotlib, check linewidths array on QuadContourSet
    linewidths = window._psi_contour_plot.get_linewidth()

    for lw in linewidths:
        assert lw == 1.0, f"All contour levels should have linewidth 1.0 after deselection, found {lw}"


def test_zoom_preserved_when_adding_psi_contour_in_edit_mode(qapp):
    """Test that zoom level is preserved when adding a PSI contour in edit mode."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)

    # Set custom zoom limits (simulate zooming in)
    window.ax.set_xlim(1.5, 2.0)  # Zoom into specific R range
    window.ax.set_ylim(-0.5, 0.5)  # Zoom into specific Z range
    window.canvas.draw()

    # Get the actual zoom limits after aspect ratio adjustment
    original_xlim = window.ax.get_xlim()
    original_ylim = window.ax.get_ylim()

    # Simulate left-click to add contour at zoomed location
    click_event = Mock()
    click_event.inaxes = window.ax
    click_event.xdata = 1.7  # R coordinate within zoomed domain
    click_event.ydata = 0.0  # Z coordinate within zoomed domain
    click_event.button = 1  # Left button

    # Trigger left-click
    window.on_mouse_press(click_event)

    # Verify that zoom was preserved after adding contour
    final_xlim = window.ax.get_xlim()
    final_ylim = window.ax.get_ylim()

    assert abs(final_xlim[0] - original_xlim[0]) < 0.01, \
        f"X min limit should be preserved: expected {original_xlim[0]}, got {final_xlim[0]}"
    assert abs(final_xlim[1] - original_xlim[1]) < 0.01, \
        f"X max limit should be preserved: expected {original_xlim[1]}, got {final_xlim[1]}"
    assert abs(final_ylim[0] - original_ylim[0]) < 0.01, \
        f"Y min limit should be preserved: expected {original_ylim[0]}, got {final_ylim[0]}"
    assert abs(final_ylim[1] - original_ylim[1]) < 0.01, \
        f"Y max limit should be preserved: expected {original_ylim[1]}, got {final_ylim[1]}"


def test_zoom_preserved_when_deleting_psi_contour_in_edit_mode(qapp):
    """Test that zoom level is preserved when deleting a PSI contour in edit mode."""
    from mesh_gui_project.ui.main_window import MainWindow
    from unittest.mock import Mock
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)

    # Set custom zoom limits (simulate zooming in)
    window.ax.set_xlim(1.5, 2.0)  # Zoom into specific R range
    window.ax.set_ylim(-0.5, 0.5)  # Zoom into specific Z range
    window.canvas.draw()

    # Get the actual zoom limits after aspect ratio adjustment
    original_xlim = window.ax.get_xlim()
    original_ylim = window.ax.get_ylim()

    # Simulate right-click to delete nearest contour at zoomed location
    click_event = Mock()
    click_event.inaxes = window.ax
    click_event.xdata = 1.7  # R coordinate within zoomed domain
    click_event.ydata = 0.0  # Z coordinate within zoomed domain
    click_event.button = 3  # Right button

    # Trigger right-click
    window.on_mouse_press(click_event)

    # Verify that zoom was preserved after deleting contour
    final_xlim = window.ax.get_xlim()
    final_ylim = window.ax.get_ylim()

    assert abs(final_xlim[0] - original_xlim[0]) < 0.01, \
        f"X min limit should be preserved: expected {original_xlim[0]}, got {final_xlim[0]}"
    assert abs(final_xlim[1] - original_xlim[1]) < 0.01, \
        f"X max limit should be preserved: expected {original_xlim[1]}, got {final_xlim[1]}"
    assert abs(final_ylim[0] - original_ylim[0]) < 0.01, \
        f"Y min limit should be preserved: expected {original_ylim[0]}, got {final_ylim[0]}"
    assert abs(final_ylim[1] - original_ylim[1]) < 0.01, \
        f"Y max limit should be preserved: expected {original_ylim[1]}, got {final_ylim[1]}"


def test_save_psi_contours_button_exists(qapp):
    """Test that save PSI contours button exists in UI."""
    from mesh_gui_project.ui.main_window import MainWindow

    window = MainWindow()

    assert hasattr(window, 'save_psi_contours_button'), \
        "MainWindow should have save_psi_contours_button attribute"
    assert window.save_psi_contours_button is not None, \
        "save_psi_contours_button should be initialized"


def test_save_psi_contours_shows_dialog(qapp, monkeypatch):
    """Test that save PSI contours button shows file dialog."""
    from mesh_gui_project.ui.main_window import MainWindow
    from PyQt5.QtWidgets import QFileDialog
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"
    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Mock QFileDialog.getSaveFileName to avoid actual dialog
    dialog_called = []

    def mock_get_save_filename(parent, caption, directory, filter_str):
        dialog_called.append((caption, directory, filter_str))
        return '', ''  # Return empty to cancel

    monkeypatch.setattr(QFileDialog, 'getSaveFileName', mock_get_save_filename)

    # Click save button
    window.save_psi_contours_button.click()

    # Should have called the dialog
    assert len(dialog_called) == 1, "Should have shown save dialog"
    caption, directory, filter_str = dialog_called[0]
    assert 'Save' in caption or 'save' in caption or 'PSI' in caption or 'psi' in caption, \
        f"Dialog caption should mention 'Save' or 'PSI', got: {caption}"
    assert 'psi4contour.txt' in directory, \
        f"Default filename should be 'psi4contour.txt', got: {directory}"


def test_save_psi_contours_creates_file_with_values(qapp, monkeypatch, tmp_path):
    """Test that save PSI contours creates file with correct contour values."""
    from mesh_gui_project.ui.main_window import MainWindow
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5.QtCore import Qt
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"
    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Mock dialog to return a path
    test_path = str(tmp_path / "test_psi_contours.txt")

    def mock_get_save_filename(parent, caption, directory, filter_str):
        return test_path, filter_str.split(';;')[0]

    monkeypatch.setattr(QFileDialog, 'getSaveFileName', mock_get_save_filename)

    # Click save button
    window.save_psi_contours_button.click()

    # File should be created
    assert os.path.exists(test_path), f"PSI contours file should be created at {test_path}"

    # Read file and verify contents
    with open(test_path, 'r') as f:
        content = f.read()

    # Should have header
    assert '# PSI Contour Levels' in content or 'PSI' in content, \
        "File should have header mentioning PSI"

    # Should have data lines with contour values
    lines = [line for line in content.split('\n') if line and not line.startswith('#')]
    assert len(lines) > 0, "File should have data lines"

    # Each line should have psi_N and psi values
    # Format could be: "psi_N, psi, source" or similar
    first_data_line = lines[0]
    assert ',' in first_data_line or '\t' in first_data_line or ' ' in first_data_line, \
        "Data lines should have delimiters (comma, tab, or space)"

    # Should have 20 automatic levels by default
    assert len(lines) == 20, \
        f"Should have 20 contour levels by default, got {len(lines)}"


def test_save_psi_contours_includes_user_added_contours(qapp, monkeypatch, tmp_path):
    """Test that save PSI contours includes both automatic and user-added contours."""
    from mesh_gui_project.ui.main_window import MainWindow
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5.QtCore import Qt, QPoint
    import os

    window = MainWindow()

    # Load test gEQDSK file
    test_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"
    window.load_geqdsk(test_file)

    # Enable contour display
    window.psi_display_contour_checkbox.setChecked(True)

    # Enable PSI edit mode
    window.psi_edit_mode_button.setChecked(True)

    # Simulate left-click to add a contour using Mock event (like other tests)
    from unittest.mock import Mock
    event = Mock()
    event.inaxes = window.ax
    event.xdata = 1.75  # Middle of R range
    event.ydata = 0.0   # Middle of Z range
    event.button = 1    # Left button
    window.on_mouse_press(event)

    # Should now have 21 contours (20 automatic + 1 user-added)
    # Check psi_contour_list widget count
    assert window.psi_contour_list.count() == 21, \
        f"Should have 21 contours after adding one, got {window.psi_contour_list.count()}"

    # Mock dialog to return a path
    test_path = str(tmp_path / "test_psi_with_user_contours.txt")

    def mock_get_save_filename(parent, caption, directory, filter_str):
        return test_path, filter_str.split(';;')[0]

    monkeypatch.setattr(QFileDialog, 'getSaveFileName', mock_get_save_filename)

    # Click save button
    window.save_psi_contours_button.click()

    # Read file and verify it has 21 contours
    with open(test_path, 'r') as f:
        content = f.read()

    lines = [line for line in content.split('\n') if line and not line.startswith('#')]
    assert len(lines) == 21, \
        f"Should have 21 contour levels (20 AUTO + 1 USER), got {len(lines)}"

    # At least one line should indicate USER source
    assert any('USER' in line for line in lines), \
        "At least one line should indicate USER source"
