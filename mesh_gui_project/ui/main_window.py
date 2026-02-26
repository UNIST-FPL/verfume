"""Main window for mesh_gui_project."""
import os
import numpy as np

from PyQt5.QtWidgets import (QMainWindow, QAction, QWidget, QHBoxLayout,
                              QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel,
                              QLineEdit, QGroupBox, QFileDialog, QMessageBox,
                              QTabWidget, QRadioButton, QButtonGroup, QCheckBox,
                              QApplication, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mesh_gui_project.core.application_state import ApplicationState
from mesh_gui_project.ui.data_inspector_panel import DataInspectorPanel
from mesh_gui_project.ui.canvas_controller import CanvasController
from mesh_gui_project.ui.psi_edit_handler import PsiEditHandler
from mesh_gui_project.ui.mesh_edit_handler import MeshEditHandler
from mesh_gui_project.ui.mouse_interaction_coordinator import MouseInteractionCoordinator
from mesh_gui_project.ui.file_operations_handler import FileOperationsHandler
from mesh_gui_project.ui.error_handler import ErrorHandler
from mesh_gui_project.ui.status_bar_controller import StatusBarController
from mesh_gui_project.ui.ui_factory import UIFactory
from mesh_gui_project.ui.event_handler_coordinator import EventHandlerCoordinator
from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Verfume")
        self.setMinimumSize(1024, 768)

        # Set window icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'resources',
            'FPLUNIST_LOGO.png'
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Initialize centralized application state
        self.app_state = ApplicationState()

        # Initialize data attributes
        # Note: equilibrium now delegates to app_state for centralized management
        self.mesher = None
        self.geqdsk_filename = None

        # Initialize application state (single source of truth)
        self.application_state = ApplicationState()

        # Initialize psi edit mode state
        self._psi_edit_mode_active = False
        # Note: _psi_contour_plot, _psi_contourf_plot, _psi_colorbar are now properties
        # that delegate to psi_viz_controller
        self._psi_preview_contour = None
        self._psi_preview_collections_count = 0
        # Note: _added_psi_values and _disabled_psi_levels now delegate to app_state
        self._last_preview_position = None

        # Initialize mesh editing state
        # Note: _mesh_vertices, _mesh_elements, _mesh_boundary now delegate to app_state
        self._mesh_editor = None  # MeshEditor instance for interactive editing
        self._mesh_edit_mode_active = False  # Mesh edit mode toggle
        self._selected_psi_for_mesh = None  # PSI value selected for mesh generation
        self._boundary_vertex_indices = None  # Indices of vertices on the boundary
        self._manually_moved_vertex_indices = set()  # Track vertices manually moved by user

        # Initialize vertex dragging state
        self._dragging_vertex_idx = None  # Index of vertex being dragged
        self._vertex_highlight_artist = None  # Artist for highlighting selected vertex

        # Initialize settings
        from mesh_gui_project.utils.settings import Settings
        self.settings = Settings()

        # Initialize file operations handler (needs settings)
        self.file_ops_handler = FileOperationsHandler(
            parent_window=self,
            settings_manager=self.settings
        )

        # Initialize error handler
        self.error_handler = ErrorHandler(parent_window=self)

        # Initialize mesh generation workflow
        from mesh_gui_project.core.mesh_generation_workflow import MeshGenerationWorkflow
        self.mesh_workflow = MeshGenerationWorkflow()

        # Initialize preview debounce timer
        self.preview_debounce_timer = QTimer(self)
        self.preview_debounce_timer.setSingleShot(True)
        self.preview_debounce_timer.setInterval(150)  # 150ms debounce

        # Controllers will be initialized after widgets are created
        self.canvas_controller = None
        self.psi_viz_controller = None
        self.mesh_viz_controller = None

        # Interaction handlers will be initialized after controllers
        self.psi_edit_handler = None
        self.psi_crit_points_handler = None
        self.mesh_edit_handler = None
        self.mouse_coordinator = None

        # Event handler coordinator (initialized before connecting signals)
        self.event_coordinator = None

        self._create_menus()
        self._create_central_widget()
        self._create_status_bar()

        # Initialize event handler coordinator after all widgets are created
        self.event_coordinator = EventHandlerCoordinator(parent_window=self)

        # Connect UI signals to event coordinator
        self._connect_signals()

    def _connect_signals(self):
        """Connect UI widget signals to event coordinator handlers."""
        # Menu actions
        self.open_action.triggered.connect(self.event_coordinator.handle_open_geqdsk_dialog)
        self.quit_action.triggered.connect(self.event_coordinator.handle_close)
        self.about_action.triggered.connect(self.show_about_dialog)

        # PSI visualization controls
        self.psi_display_contour_checkbox.stateChanged.connect(
            self.event_coordinator.handle_psi_display_mode_changed
        )
        self.psi_display_contourf_checkbox.stateChanged.connect(
            self.event_coordinator.handle_psi_display_mode_changed
        )
        self.psi_edit_mode_button.toggled.connect(
            self.event_coordinator.handle_psi_edit_mode_toggled
        )
        self.psi_contour_list.itemSelectionChanged.connect(
            self.event_coordinator.handle_psi_contour_selection_changed
        )
        self.save_psi_contours_button.clicked.connect(
            self.event_coordinator.handle_save_psi_contours
        )

        # Critical points controls
        self.find_crit_points_button.clicked.connect(self._on_find_critical_points)
        self.crit_points_detail_button.clicked.connect(self._on_show_critical_points_detail)
        self.show_crit_markers_checkbox.toggled.connect(self._on_toggle_crit_markers)

        # Mesh controls
        self.mesh_viz_mode_combo.currentIndexChanged.connect(
            self.event_coordinator.handle_mesh_viz_mode_changed
        )
        self.generate_mesh_button.clicked.connect(
            self.event_coordinator.handle_generate_mesh_clicked
        )
        self.enter_edit_mode_button.toggled.connect(
            self.event_coordinator.handle_mesh_edit_mode_toggled
        )
        self.remesh_optimize_button.clicked.connect(
            self.event_coordinator.handle_remesh_optimize_clicked
        )
        self.export_mesh_button.clicked.connect(
            self.event_coordinator.handle_export_mesh_clicked
        )

        # Tab changes
        self.left_tabs.currentChanged.connect(
            self.event_coordinator.handle_tab_changed
        )

        # View options in Meta tab (DataInspectorPanel)
        self.data_inspector.show_o_x_checkbox.stateChanged.connect(
            self.event_coordinator.handle_view_option_changed
        )
        self.data_inspector.show_limiter_checkbox.stateChanged.connect(
            self.event_coordinator.handle_view_option_changed
        )
        self.data_inspector.show_lcfs_checkbox.stateChanged.connect(
            self.event_coordinator.handle_view_option_changed
        )

    # Compatibility properties for tests (delegate to controllers)
    @property
    def ax(self):
        """Compatibility property: delegate to canvas_controller.ax."""
        return self.canvas_controller.ax if self.canvas_controller else None

    @property
    def canvas(self):
        """Compatibility property: delegate to canvas_controller.canvas."""
        return self.canvas_controller.canvas if self.canvas_controller else None

    @canvas.setter
    def canvas(self, value):
        """Compatibility setter: ignore assignment (canvas is managed by controller)."""
        pass  # Canvas is managed by canvas_controller

    # PSI visualization state delegation (explicit properties)
    @property
    def _psi_contour_plot(self):
        """Delegate to PSI visualization controller."""
        return self.psi_viz_controller._psi_contour_plot if self.psi_viz_controller else None

    @_psi_contour_plot.setter
    def _psi_contour_plot(self, value):
        """Delegate setter to controller."""
        if self.psi_viz_controller:
            self.psi_viz_controller._psi_contour_plot = value

    @property
    def _psi_contourf_plot(self):
        """Delegate to PSI visualization controller."""
        return self.psi_viz_controller._psi_contourf_plot if self.psi_viz_controller else None

    @_psi_contourf_plot.setter
    def _psi_contourf_plot(self, value):
        """Delegate setter to controller."""
        if self.psi_viz_controller:
            self.psi_viz_controller._psi_contourf_plot = value

    @property
    def _psi_colorbar(self):
        """Delegate to PSI visualization controller."""
        return self.psi_viz_controller._psi_colorbar if self.psi_viz_controller else None

    @_psi_colorbar.setter
    def _psi_colorbar(self, value):
        """Delegate setter to controller."""
        if self.psi_viz_controller:
            self.psi_viz_controller._psi_colorbar = value

    # Application state delegation
    @property
    def equilibrium(self):
        """Delegate to ApplicationState for centralized management."""
        return self.app_state.get_equilibrium()

    @equilibrium.setter
    def equilibrium(self, value):
        """Delegate setter to ApplicationState."""
        self.app_state.set_equilibrium(value)

    @property
    def _added_psi_values(self):
        """Delegate to ApplicationState."""
        return self.app_state.get_added_psi_values()

    @_added_psi_values.setter
    def _added_psi_values(self, value):
        self.app_state.clear_psi_values()
        for psi_val in value:
            self.app_state.add_psi_value(psi_val)

    @property
    def _disabled_psi_levels(self):
        """Delegate to ApplicationState."""
        return self.app_state.get_disabled_psi_levels()

    @_disabled_psi_levels.setter
    def _disabled_psi_levels(self, value):
        current_added = self.app_state.get_added_psi_values()
        self.app_state.clear_psi_values()
        for psi_val in current_added:
            self.app_state.add_psi_value(psi_val)
        for level in value:
            self.app_state.disable_psi_level(level)

    @property
    def _mesh_vertices(self):
        """Delegate to ApplicationState."""
        return self.app_state.get_mesh()[0]

    @_mesh_vertices.setter
    def _mesh_vertices(self, value):
        self.app_state.set_mesh(value, self.app_state.get_mesh()[1])

    @property
    def _mesh_elements(self):
        """Delegate to ApplicationState."""
        return self.app_state.get_mesh()[1]

    @_mesh_elements.setter
    def _mesh_elements(self, value):
        self.app_state.set_mesh(self.app_state.get_mesh()[0], value)

    @property
    def _mesh_boundary(self):
        """Delegate to ApplicationState."""
        return self.app_state.get_mesh_boundary()

    @_mesh_boundary.setter
    def _mesh_boundary(self, value):
        self.app_state.set_mesh_boundary(value)

    # Mesh visualization state delegation (explicit properties)
    @property
    def _mesh_plot_artists(self):
        """Delegate to mesh visualization controller."""
        return self.mesh_viz_controller._mesh_plot_artists if self.mesh_viz_controller else []

    @_mesh_plot_artists.setter
    def _mesh_plot_artists(self, value):
        """Delegate setter to controller."""
        if self.mesh_viz_controller:
            self.mesh_viz_controller._mesh_plot_artists = value

    @property
    def _mesh_quality_colorbar(self):
        """Delegate to mesh visualization controller."""
        return self.mesh_viz_controller._mesh_quality_colorbar if self.mesh_viz_controller else None

    @_mesh_quality_colorbar.setter
    def _mesh_quality_colorbar(self, value):
        """Delegate setter to controller."""
        if self.mesh_viz_controller:
            self.mesh_viz_controller._mesh_quality_colorbar = value

    def _create_menus(self):
        """Create menu bar with File, View, Tools, and Help menus."""
        # Delegate to UIFactory
        menu_bar = UIFactory.create_menu_bar(self)
        self.setMenuBar(menu_bar)

        # Note: Menu action connections will be done in _connect_signals()
        # after event_coordinator is initialized

        # Update recent menu after creation
        self._update_recent_menu()

    def _create_central_widget(self):
        """Create central widget with left panel and center canvas."""
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main vertical layout to hold breadcrumb + horizontal layout
        from mesh_gui_project.ui.workflow_breadcrumb import WorkflowBreadcrumb

        main_vertical_layout = QVBoxLayout()
        central_widget.setLayout(main_vertical_layout)

        # Add workflow breadcrumb at top
        self.workflow_breadcrumb = WorkflowBreadcrumb()
        main_vertical_layout.addWidget(self.workflow_breadcrumb)

        # Create horizontal layout for left panel + canvas
        main_layout = QHBoxLayout()

        # Left panel for psi_N input
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)

        # Center: matplotlib canvas
        canvas_widget = self._create_matplotlib_canvas()
        main_layout.addWidget(canvas_widget, stretch=1)

        # Add horizontal layout to vertical layout
        main_vertical_layout.addLayout(main_layout)

    def _create_left_panel(self):
        """Create left panel with tabs for Visualization, Data Inspector, and Mesh Editing."""
        # Delegate to UIFactory
        left_panel = UIFactory.create_left_panel(self)

        # Add context-sensitive help tooltips to buttons
        self._setup_button_tooltips()

        # Note: Signal connections will be set up after event_coordinator is initialized
        # This is deferred to avoid circular dependencies during initialization

        return left_panel

    def _setup_button_tooltips(self):
        """Setup context-sensitive help tooltips for buttons."""
        # PSI tab buttons
        self._add_button_tooltip_to_statusbar(
            self.psi_edit_mode_button,
            "Edit PSI Contours → Left-click to add, Right-click to delete, Ctrl+hover to show values"
        )
        self._add_button_tooltip_to_statusbar(
            self.save_psi_contours_button,
            "Save current contour levels to a text file"
        )
        self._add_button_tooltip_to_statusbar(
            self.find_crit_points_button,
            "Find O-points and X-points in the equilibrium"
        )

        # Mesh tab buttons
        self._add_button_tooltip_to_statusbar(
            self.generate_mesh_button,
            "Generate mesh from selected PSI contour or limiter boundary"
        )
        self._add_button_tooltip_to_statusbar(
            self.enter_edit_mode_button,
            "Edit Mesh → Click to select vertex, drag to move (boundary vertices stay on contour)"
        )
        self._add_button_tooltip_to_statusbar(
            self.remesh_optimize_button,
            "Retriangulate and optimize mesh quality (preserves moved vertices)"
        )
        self._add_button_tooltip_to_statusbar(
            self.export_mesh_button,
            "Export mesh to .msh (Gmsh), .vtk, .smb (SCOREC), or .dmg (SCOREC) format"
        )

    def _update_tab_indicators(self):
        """Update tab labels to show current state (file loaded, contour selected, mesh generated)."""
        # Tab 0: Meta
        if self.equilibrium is not None:
            self.left_tabs.setTabText(0, "Meta ✓")
        else:
            self.left_tabs.setTabText(0, "Meta")

        # Tab 1: Psi
        selected_items = self.psi_contour_list.selectedItems()
        if len(selected_items) > 0:
            psi_value = selected_items[0].data(Qt.UserRole)
            psi_n = self.equilibrium.normalize_psi(psi_value) if self.equilibrium else 0
            self.left_tabs.setTabText(1, f"Psi (ψ_N={psi_n:.2f})")
        else:
            self.left_tabs.setTabText(1, "Psi")

        # Tab 2: Meshing
        if self._mesh_vertices is not None and self._mesh_elements is not None:
            num_vertices = len(self._mesh_vertices)
            self.left_tabs.setTabText(2, f"Meshing ({num_vertices}v)")
        else:
            self.left_tabs.setTabText(2, "Meshing")


    def _create_matplotlib_canvas(self):
        """Create embedded matplotlib canvas for R-Z plane visualization."""
        from PyQt5.QtWidgets import QWidget, QVBoxLayout
        from mesh_gui_project.ui.mode_indicator_banner import ModeIndicatorBanner

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create mode indicator banner (kept as object for API compatibility, not shown in layout)
        self.mode_indicator_banner = ModeIndicatorBanner()

        # Create canvas controller
        self.canvas_controller = CanvasController()
        canvas = self.canvas_controller.create_canvas(figsize=(8, 6))
        layout.addWidget(canvas)

        container.setLayout(layout)

        # Initialize interaction handlers (after canvas_controller is created)
        self._initialize_interaction_handlers()

        # Connect mouse events for zoom and pan
        canvas.mpl_connect('scroll_event', self.on_scroll_zoom)
        canvas.mpl_connect('button_press_event', self.on_mouse_press)
        canvas.mpl_connect('button_release_event', self.on_mouse_release)
        canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)

        # Create PSI visualization controller (after psi_contour_list is created)
        # Will be done in _create_visualization_tab

        # Create mesh visualization controller (after mesh widgets are created)
        # Will be done in _create_mesh_editing_tab

        return container

    def _initialize_interaction_handlers(self):
        """Initialize interaction handlers for mouse events."""
        # Create equilibrium visualization controller
        from mesh_gui_project.ui.equilibrium_visualization_controller import EquilibriumVisualizationController
        self.equilibrium_viz_controller = EquilibriumVisualizationController(
            ax=self.canvas_controller.ax,
            canvas_controller=self.canvas_controller
        )

        # Create PSI visualization controller (now that canvas and psi_contour_list exist)
        from mesh_gui_project.ui.psi_visualization_controller import PsiVisualizationController
        self.psi_viz_controller = PsiVisualizationController(
            ax=self.canvas_controller.ax,
            figure=self.canvas_controller.figure,
            psi_contour_list_widget=self.psi_contour_list,
            application_state=self.application_state
        )

        # Create mesh visualization controller (now that canvas and widgets exist)
        from mesh_gui_project.ui.mesh_visualization_controller import MeshVisualizationController
        self.mesh_viz_controller = MeshVisualizationController(
            ax=self.canvas_controller.ax,
            figure=self.canvas_controller.figure,
            viz_mode_combo=self.mesh_viz_mode_combo,
            vertex_count_label=self.mesh_vertex_count_label,
            triangle_count_label=self.mesh_triangle_count_label,
            avg_aspect_ratio_label=self.mesh_avg_aspect_ratio_label,
            min_angle_label=self.mesh_min_angle_label
        )

        # Create PSI edit handler
        self.psi_edit_handler = PsiEditHandler(
            equilibrium=None,  # Will be set when equilibrium is loaded
            psi_viz_controller=self.psi_viz_controller,
            canvas_controller=self.canvas_controller,
            on_redraw_callback=lambda: self._redraw_rz_plot(),
            application_state=self.application_state,
            on_tooltip_restore_callback=lambda R, Z: self._restore_tooltip_if_ctrl_pressed(R, Z)
        )

        # Create critical points handler
        from mesh_gui_project.ui.psi_critical_points_handler import PsiCriticalPointsHandler
        self.psi_crit_points_handler = PsiCriticalPointsHandler(
            ax=self.ax,
            canvas_controller=self.canvas_controller,
            application_state=self.application_state,
            equilibrium_provider=lambda: self.equilibrium
        )

        # Create mesh edit handler
        self.mesh_edit_handler = MeshEditHandler(
            canvas_controller=self.canvas_controller,
            on_mesh_update_callback=self._on_mesh_handler_update
        )

        # Create mouse interaction coordinator
        self.mouse_coordinator = MouseInteractionCoordinator(
            psi_edit_handler=self.psi_edit_handler,
            mesh_edit_handler=self.mesh_edit_handler,
            canvas_controller=self.canvas_controller,
            on_tooltip_update_callback=self._handle_tooltip_update
        )

        # Create visualization orchestrator
        from mesh_gui_project.ui.visualization_orchestrator import VisualizationOrchestrator
        self.viz_orchestrator = VisualizationOrchestrator(
            canvas_ctrl=self.canvas_controller,
            psi_viz_ctrl=self.psi_viz_controller,
            mesh_viz_ctrl=self.mesh_viz_controller,
            eq_viz_ctrl=self.equilibrium_viz_controller
        )

    def _handle_tooltip_update(self, event):
        """
        Handle tooltip updates for mouse motion events.

        Args:
            event: Matplotlib mouse event or None to hide tooltip
        """
        # If event is None, hide tooltip (used when Ctrl is released in edit mode)
        if event is None:
            self._hide_psi_tooltip()
            return

        # Handle tooltip display when not panning and not in edit mode
        if self._should_show_psi_tooltip(event):
            self._update_psi_tooltip(event.xdata, event.ydata)
        else:
            self._hide_psi_tooltip()

    def _on_mesh_handler_update(self):
        """
        Callback when mesh edit handler updates mesh.

        Updates internal mesh state and triggers visualization.
        """
        # Get updated mesh from handler
        if self.mesh_edit_handler is not None:
            vertices, elements = self.mesh_edit_handler.get_mesh()
            if vertices is not None and elements is not None:
                self._mesh_vertices = vertices
                self._mesh_elements = elements

        # Update visualization
        self._visualize_mesh()

    def _create_status_bar(self):
        """Create status bar for displaying mouse position and mesh stats."""
        self.statusBar().showMessage('Ready')

    def update_status_bar(self, r=None, z=None, psi=None, nodes=None, triangles=None):
        """
        Update status bar with mouse position and mesh statistics.

        Args:
            r: R coordinate (optional)
            z: Z coordinate (optional)
            psi: Psi value at cursor (optional)
            nodes: Number of mesh nodes (optional)
            triangles: Number of mesh triangles (optional)
        """
        parts = []

        if r is not None and z is not None:
            parts.append(f"R={r:.4f} m, Z={z:.4f} m")

        if psi is not None:
            parts.append(f"psi={psi:.6f}")

        if nodes is not None or triangles is not None:
            mesh_info = []
            if nodes is not None:
                mesh_info.append(f"{nodes} nodes")
            if triangles is not None:
                mesh_info.append(f"{triangles} triangles")
            parts.append("Mesh: " + ", ".join(mesh_info))

        if parts:
            self.statusBar().showMessage(" | ".join(parts))
        else:
            self.statusBar().showMessage("Ready")

    def _add_button_tooltip_to_statusbar(self, button, help_text: str):
        """
        Add hover event to button to show help text in status bar.

        Args:
            button: QPushButton widget
            help_text: Help text to display in status bar on hover
        """
        def on_enter(event):
            self.statusBar().showMessage(f"💡 {help_text}")

        def on_leave(event):
            self.statusBar().showMessage("Ready")

        button.enterEvent = on_enter
        button.leaveEvent = on_leave


    def on_canvas_click(self, event):
        """
        Handle mouse clicks on the matplotlib canvas.

        Args:
            event: Matplotlib mouse event
        """
        # Only process if we have data button presses in axes
        if event.inaxes != self.canvas_controller.ax or event.button != 1:
            return

        # Get click coordinates
        R_click = event.xdata
        Z_click = event.ydata

        if R_click is None or Z_click is None:
            return

        # Update status bar with clicked position
        self.update_status_bar(r=R_click, z=Z_click)

        # Store clicked point for later use
        # (This will be used when flux surface mode is active)
        self.last_click_r = R_click
        self.last_click_z = Z_click

    def on_scroll_zoom(self, event):
        """
        Handle mouse scroll for zooming.

        Args:
            event: Matplotlib scroll event
        """
        # Delegate to mouse interaction coordinator
        if self.mouse_coordinator is not None:
            self.mouse_coordinator.handle_scroll(event)

    def on_mouse_press(self, event):
        """
        Handle mouse button press for panning, psi edit mode, and mesh vertex dragging.

        Args:
            event: Matplotlib mouse event
        """
        # Delegate to mouse interaction coordinator
        if self.mouse_coordinator is not None:
            self.mouse_coordinator.handle_mouse_press(event)

    def on_mouse_release(self, event):
        """
        Handle mouse button release to end panning or vertex dragging.

        Args:
            event: Matplotlib mouse event
        """
        # Delegate to mouse interaction coordinator
        if self.mouse_coordinator is not None:
            self.mouse_coordinator.handle_mouse_release(event)

    def on_mouse_motion(self, event):
        """
        Handle mouse motion for panning, vertex dragging, and psi tooltip display.

        Args:
            event: Matplotlib mouse event
        """
        # Delegate to mouse interaction coordinator
        if self.mouse_coordinator is not None:
            self.mouse_coordinator.handle_mouse_motion(event)

    def _should_show_psi_tooltip(self, event):
        """
        Determine if psi tooltip should be shown.

        Args:
            event: Matplotlib mouse event

        Returns:
            bool: True if tooltip should be shown
        """
        contour_enabled = self.psi_display_contour_checkbox.isChecked()
        contourf_enabled = self.psi_display_contourf_checkbox.isChecked()

        return self.canvas_controller.should_show_psi_tooltip(
            event,
            self.equilibrium,
            contour_enabled,
            contourf_enabled
        )

    def _update_psi_tooltip(self, R, Z):
        """
        Update or create psi tooltip at given position.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        self.canvas_controller.update_psi_tooltip(self.equilibrium, R, Z)

    def _hide_psi_tooltip(self):
        """Hide the psi tooltip annotation."""
        self.canvas_controller.hide_psi_tooltip()

    def _restore_tooltip_if_ctrl_pressed(self, R: float, Z: float):
        """
        Restore tooltip at given position if Ctrl key is currently pressed.

        This is called after a redraw operation (e.g., adding/deleting contours)
        to restore the tooltip if the user is still holding Ctrl.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt

        # Check if Ctrl key is currently pressed
        modifiers = QApplication.keyboardModifiers()
        ctrl_pressed = bool(modifiers & Qt.ControlModifier)

        if ctrl_pressed and self.equilibrium is not None:
            # Restore tooltip at the given position
            self._update_psi_tooltip(R, Z)

    def _save_psi_contours(self):
        """
        Save PSI contour levels to a text file.

        Shows file dialog with default filename 'psi4contour.txt' and saves
        current contour levels including both raw psi and normalized psi_N values.
        """
        # Check if equilibrium is loaded
        if self.equilibrium is None:
            self.error_handler.show_warning("No Data",
                                           "No equilibrium data loaded. Load a gEQDSK file first.")
            return

        # Check if there are any contours to save
        if self.psi_contour_list.count() == 0:
            self.error_handler.show_warning("No Contours",
                                           "No contour levels to save. Enable PSI contours first.")
            return

        # Show save file dialog with default filename
        filters = "Text Files (*.txt);;All Files (*)"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save PSI Contour Levels",
            "psi4contour.txt",
            filters
        )

        # User cancelled
        if not file_path:
            return

        try:
            # Get user-added values from handler (refactored to handler)
            added_psi_values = self.psi_edit_handler.get_added_values() if self.psi_edit_handler else []

            # Collect contour levels from the list
            contour_data = []
            for i in range(self.psi_contour_list.count()):
                item = self.psi_contour_list.item(i)
                psi_value = item.data(Qt.UserRole)  # Raw psi value
                psi_n = self.equilibrium.normalize_psi(psi_value)
                source = "USER" if psi_value in added_psi_values else "AUTO"
                contour_data.append((psi_n, psi_value, source))

            # Write to file
            with open(file_path, 'w') as f:
                # Write header
                f.write("# PSI Contour Levels\n")
                f.write(f"# gEQDSK File: {self.geqdsk_filename if self.geqdsk_filename else 'N/A'}\n")
                f.write(f"# Number of contours: {len(contour_data)}\n")
                f.write("#\n")
                f.write("# Format: psi_N, psi (raw), source\n")
                f.write("#\n")

                # Write data
                for psi_n, psi_value, source in contour_data:
                    f.write(f"{psi_n:.6f}, {psi_value:.6e}, {source}\n")

            self.statusBar().showMessage(
                f"Saved {len(contour_data)} contour levels to {file_path}",
                5000
            )

        except Exception as e:
            self.error_handler.show_error("Save Failed",
                                         f"Failed to save contour levels: {str(e)}")
            self.statusBar().showMessage(f"Save failed: {str(e)}", 5000)

    def open_geqdsk_dialog(self):
        """
        Show file dialog to open a gEQDSK file.

        Displays file picker and loads the selected gEQDSK file.
        """
        # Delegate to file operations handler
        file_path = self.file_ops_handler.open_geqdsk_dialog()

        if file_path:
            self.load_geqdsk(file_path)

    def load_geqdsk(self, file_path: str):
        """
        Load and render a gEQDSK equilibrium file.

        Args:
            file_path: Path to the gEQDSK file

        Loads the equilibrium data, sets up interpolation, and renders
        the boundary/limiter curves if present.
        """
        # Delegate parsing to file operations handler
        self.equilibrium = self.file_ops_handler.load_geqdsk(file_path)

        # If loading failed, handler already showed error dialog
        if self.equilibrium is None:
            return

        try:
            # Import required modules
            from mesh_gui_project.utils.interpolation import make_bicubic_interpolator

            # Store the filename for later reference
            self.geqdsk_filename = file_path

            # Attach interpolator
            interp = make_bicubic_interpolator(
                self.equilibrium.R_grid,
                self.equilibrium.Z_grid,
                self.equilibrium.psi_grid
            )
            self.equilibrium.attach_interpolator(interp)

            # Update PSI edit handler with equilibrium
            if self.psi_edit_handler is not None:
                self.psi_edit_handler.equilibrium = self.equilibrium

            # Clear the current plot
            self.canvas_controller.ax.clear()

            # Set axis labels
            self.canvas_controller.ax.set_xlabel('R (m)')
            self.canvas_controller.ax.set_ylabel('Z (m)')
            self.canvas_controller.ax.grid(True, alpha=0.3)

            # Use 'equal' aspect to get same unit length for all axes
            self.canvas_controller.ax.set_aspect('equal', adjustable='datalim')

            # Set position and use tight layout
            # right=0.80 leaves space for colorbars at left=0.82
            self.canvas_controller.figure.subplots_adjust(left=0.08, bottom=0.08, right=0.80, top=0.98)

            # Plot boundary (LCFS) if present and enabled
            if self.equilibrium.boundary_curve is not None and self.data_inspector.show_lcfs_checkbox.isChecked():
                self.equilibrium.plot_boundary(self.canvas_controller.ax)

            # Plot limiter if present and enabled
            if self.equilibrium.limiter_curve is not None and self.data_inspector.show_limiter_checkbox.isChecked():
                self.equilibrium.plot_limiter(self.canvas_controller.ax)

            # Plot critical points if enabled
            if self.data_inspector.show_o_x_checkbox.isChecked():
                self.equilibrium_viz_controller.plot_critical_points(self.equilibrium)

            # Update data inspector panel
            self.data_inspector.update_data(self.equilibrium)

            # Update psi min/max display
            self._update_psi_minmax_display()

            # Update status bar
            self.statusBar().showMessage(
                f"Loaded {file_path} (NR={len(self.equilibrium.R_grid)}, NZ={len(self.equilibrium.Z_grid)})",
                5000
            )

            # Add to recent files on successful load
            self.file_ops_handler.add_to_recent_files(file_path)
            self._update_recent_menu()

            # Update workflow breadcrumb
            self.workflow_breadcrumb.set_step("select")

            # Update tab indicators
            self._update_tab_indicators()

        except Exception as e:
            self.error_handler.show_error("Setup Failed",
                                         f"Failed to set up equilibrium: {str(e)}")
            self.statusBar().showMessage(f"Setup failed: {str(e)}", 5000)
            return

    def _add_to_recent_files(self, file_path: str):
        """
        Add a file path to the recent files list.

        Args:
            file_path: Path to add to recent files

        Updates the settings and refreshes the recent menu.
        """
        # Delegate to file operations handler
        self.file_ops_handler.add_to_recent_files(file_path)
        self.settings.save()

        # Update the menu
        self._update_recent_menu()

    def _update_recent_menu(self):
        """
        Update the recent files menu with current recent files.

        Clears existing actions and populates with current list.
        """
        # Clear existing actions
        self.recent_menu.clear()

        # Get recent files from handler
        recent_files = self.file_ops_handler.get_recent_files()

        if not recent_files:
            # Show a disabled "No recent files" action
            no_files_action = QAction('No recent files', self)
            no_files_action.setEnabled(False)
            self.recent_menu.addAction(no_files_action)
            return

        # Add action for each recent file
        import os
        for file_path in recent_files:
            # Show just the filename in the menu
            display_name = os.path.basename(file_path)
            action = QAction(display_name, self)
            action.setToolTip(file_path)  # Full path as tooltip

            # Connect to load the file when clicked
            # Use lambda with default argument to capture file_path correctly
            action.triggered.connect(lambda checked=False, path=file_path: self.load_geqdsk(path))

            self.recent_menu.addAction(action)

    def _update_psi_minmax_display(self):
        """Update min/max psi_N values in visualization tab (delegates to orchestrator)."""
        if self.equilibrium is None:
            self.viz_orchestrator.update_psi_range_display(
                self.psi_min_display,
                self.psi_max_display,
                None,
                None
            )
            return

        psi_grid = self.equilibrium.psi_grid
        psi_min = psi_grid.min()
        psi_max = psi_grid.max()

        # Convert to normalized psi_N
        psi_min_n = self.equilibrium.normalize_psi(psi_min)
        psi_max_n = self.equilibrium.normalize_psi(psi_max)

        self.viz_orchestrator.update_psi_range_display(
            self.psi_min_display,
            self.psi_max_display,
            psi_min_n,
            psi_max_n
        )

    def add_psi_n_value(self):
        """
        Add psi_N value from input field to the list.

        Validates the input and adds it to the sorted list.
        """
        # Get text from input
        text = self.psi_n_input.text().strip()

        if not text:
            return

        # Parse value
        try:
            value = float(text)
        except ValueError:
            self.error_handler.show_warning("Invalid Input",
                                           f"'{text}' is not a valid number")
            return

        # Validate range (0.0 to 1.0)
        if value < 0.0 or value > 1.0:
            self.error_handler.show_warning("Invalid Range",
                                           f"psi_N must be between 0.0 and 1.0, got {value}")
            return

        # Check if value already exists
        for i in range(self.psi_n_list.count()):
            item_text = self.psi_n_list.item(i).text()
            existing_value = float(item_text.split()[0])
            if abs(existing_value - value) < 1e-6:
                self.error_handler.show_info("Duplicate",
                                            f"psi_N = {value} already in list")
                return

        # Add to list
        self.psi_n_list.addItem(f"{value:.4f}")

        # Sort the list
        self._sort_psi_n_list()

        # Clear input field
        self.psi_n_input.clear()

    def remove_psi_n_value(self):
        """Remove selected psi_N value from the list."""
        current_row = self.psi_n_list.currentRow()

        if current_row >= 0:
            self.psi_n_list.takeItem(current_row)

    def _sort_psi_n_list(self):
        """Sort psi_N list in ascending order."""
        # Get all values
        values = []
        for i in range(self.psi_n_list.count()):
            text = self.psi_n_list.item(i).text()
            value = float(text.split()[0])
            values.append(value)

        # Sort
        values.sort()

        # Clear list
        self.psi_n_list.clear()

        # Re-add sorted values
        for value in values:
            self.psi_n_list.addItem(f"{value:.4f}")

    def _on_psi_edit_mode_toggled(self, checked):
        """
        Handle psi edit mode button toggle.

        Args:
            checked: True if button is checked (edit mode active), False otherwise
        """
        # Delegate to PSI edit handler
        if self.psi_edit_handler is not None:
            self.psi_edit_handler.set_active(checked)

        # Update status bar with edit mode info
        if checked:
            self.statusBar().showMessage(
                "EDIT MODE: PSI Contours  |  Left-Click: Add  |  Right-Click: Delete  |  Ctrl+Hover: Show Values"
            )
        else:
            self.statusBar().showMessage("Ready")

        # Keep legacy state for compatibility (will be removed later)
        self._psi_edit_mode_active = checked

    def _on_psi_display_mode_changed(self):
        """Handle psi field display mode change from checkboxes."""
        # Only redraw if equilibrium is loaded
        if self.equilibrium is None:
            return

        # Completely redraw the entire plot from scratch
        self._redraw_rz_plot()

    def _redraw_rz_plot(self):
        """
        Redraw the entire R-Z plot from scratch.

        This method clears the axes and redraws all elements including:
        - Psi field visualization (based on checkbox states)
        - Boundary curves
        - Limiter curves
        - Critical points (O-points and X-points)

        This ensures that matplotlib properly removes old artists and
        displays only the currently selected visualizations.
        """
        if self.equilibrium is None:
            return

        # Save current axis limits before clearing (to preserve zoom)
        saved_xlim = self.canvas_controller.ax.get_xlim()
        saved_ylim = self.canvas_controller.ax.get_ylim()

        # Check if limits are reasonable (not default matplotlib limits)
        # Default limits are often (0, 1) when axes are first created
        # Only reset limits if they look like uninitialized defaults (around 0-1)
        xlim_range = saved_xlim[1] - saved_xlim[0]
        ylim_range = saved_ylim[1] - saved_ylim[0]
        has_psi_display = (self.psi_display_contour_checkbox.isChecked() or
                          self.psi_display_contourf_checkbox.isChecked())

        # Only reset if limits look like matplotlib defaults (0-1 range) AND centered near origin
        # This avoids resetting intentional user zoom
        looks_like_default = (
            abs(saved_xlim[0]) < 0.1 and abs(saved_xlim[1] - 1.0) < 0.1 and
            abs(saved_ylim[0]) < 0.1 and abs(saved_ylim[1] - 1.0) < 0.1
        )

        if has_psi_display and looks_like_default:
            # Limits look like uninitialized defaults, use PSI grid extent instead
            R_min, R_max = self.equilibrium.R_grid.min(), self.equilibrium.R_grid.max()
            Z_min, Z_max = self.equilibrium.Z_grid.min(), self.equilibrium.Z_grid.max()
            # Add small margin (5%)
            R_margin = (R_max - R_min) * 0.05
            Z_margin = (Z_max - Z_min) * 0.05
            saved_xlim = (R_min - R_margin, R_max + R_margin)
            saved_ylim = (Z_min - Z_margin, Z_max + Z_margin)

        # Remove colorbars via controllers
        if self.psi_viz_controller is not None:
            self.psi_viz_controller.remove_colorbar()

        if self.mesh_viz_controller is not None:
            self.mesh_viz_controller.remove_colorbar()

        # Remove legacy colorbar if it exists
        if self._psi_colorbar is not None:
            try:
                self._psi_colorbar.remove()
            except:
                pass  # Ignore errors if already removed
            self._psi_colorbar = None

        # Clear all previous artists from axes
        self.canvas_controller.ax.clear()

        # IMPORTANT: Reset preview contour state after clearing axes
        # The old preview contour object is now invalid after ax.clear()
        self._psi_preview_contour = None
        self._psi_preview_collections_count = 0

        # ALSO reset PSI edit handler preview state (if handler exists)
        # This prevents stale preview contour references from interfering
        if self.psi_edit_handler is not None:
            self.psi_edit_handler._preview_contour = None
            self.psi_edit_handler._preview_collections_count = 0

        # IMPORTANT: Reset tooltip annotation after ax.clear()
        # The annotation object is now invalid after clearing axes
        self.canvas_controller._psi_tooltip_annotation = None

        # Re-setup axes properties
        self.canvas_controller.ax.set_xlabel('R (m)')
        self.canvas_controller.ax.set_ylabel('Z (m)')
        self.canvas_controller.ax.grid(True, alpha=0.3)

        # Use 'equal' aspect to get same unit length for all axes
        # Use 'box' adjustable to preserve zoom - adjusts the box size instead of data limits
        self.canvas_controller.ax.set_aspect('equal', adjustable='box')

        # CRITICAL: Disable autoscaling BEFORE setting limits and plotting
        # This prevents matplotlib from automatically adjusting limits during plot operations
        self.canvas_controller.ax.set_autoscale_on(False)

        # Restore saved axis limits BEFORE plotting to prevent any autoscaling
        # This ensures all subsequent plot operations respect the user's zoom/view
        self.canvas_controller.ax.set_xlim(saved_xlim)
        self.canvas_controller.ax.set_ylim(saved_ylim)

        # Set position and use tight layout
        # right=0.80 leaves space for colorbars at left=0.82
        self.canvas_controller.figure.subplots_adjust(left=0.08, bottom=0.08, right=0.80, top=0.98)

        # Plot psi field first (background layer) based on checkbox states
        self._plot_psi_field()

        # Plot boundary (LCFS) if present and enabled
        if self.equilibrium.boundary_curve is not None and self.data_inspector.show_lcfs_checkbox.isChecked():
            self.equilibrium.plot_boundary(self.canvas_controller.ax)

        # Plot limiter if present and enabled
        if self.equilibrium.limiter_curve is not None and self.data_inspector.show_limiter_checkbox.isChecked():
            self.equilibrium.plot_limiter(self.canvas_controller.ax)

        # Plot critical points if enabled
        if self.data_inspector.show_o_x_checkbox.isChecked():
            self.equilibrium_viz_controller.plot_critical_points(self.equilibrium)

        # Restore critical points markers if checkbox is enabled
        if hasattr(self, 'show_crit_markers_checkbox') and \
           self.show_crit_markers_checkbox.isChecked():
            self.psi_crit_points_handler.show_markers()

        # Force canvas to redraw
        self.canvas_controller.canvas.draw()

    def _plot_psi_field(self):
        """
        Plot psi field visualization (delegates to orchestrator).

        Wrapper for backwards compatibility that delegates to VisualizationOrchestrator.
        """
        if self.equilibrium:
            # Get PSI values from handler
            added_psi_values = self.psi_edit_handler.get_added_values() if self.psi_edit_handler else []
            disabled_psi_levels = self.psi_edit_handler.get_disabled_levels() if self.psi_edit_handler else []

            show_contour = self.psi_display_contour_checkbox.isChecked()
            show_contourf = self.psi_display_contourf_checkbox.isChecked()

            self.viz_orchestrator.update_psi_visualization(
                self.equilibrium,
                show_contour,
                show_contourf,
                added_psi_values,
                disabled_psi_levels
            )

    def _clear_psi_field(self):
        """
        Clear psi field visualization (delegates to orchestrator).

        Wrapper for backwards compatibility that delegates to VisualizationOrchestrator.
        """
        self.viz_orchestrator.clear_psi_visualization()

    def _on_psi_contour_selection_changed(self):
        """Handle selection change in PSI contour list."""
        import warnings

        # Get selected items
        selected_items = self.psi_contour_list.selectedItems()

        if len(selected_items) == 0:
            # No selection - reset all to default
            self._reset_all_contour_highlighting()
            self.canvas_controller.draw_idle()
            return

        # Get selected psi level
        selected_item = selected_items[0]
        psi_level = selected_item.data(Qt.UserRole)

        # Highlight the selected contour
        self._highlight_contour_level(psi_level)
        self.canvas_controller.draw_idle()

        # Update workflow breadcrumb
        self.workflow_breadcrumb.set_step("generate")

        # Update tab indicators
        self._update_tab_indicators()

    def _highlight_contour_level(self, psi_level):
        """Highlight a specific contour level by making it brighter/thicker."""
        if self._psi_contour_plot is None:
            return

        # Get contour levels
        levels = self._psi_contour_plot.levels

        # Find the index of the selected level
        level_index = None
        for i, level in enumerate(levels):
            if abs(level - psi_level) < 1e-8:
                level_index = i
                break

        if level_index is None:
            return

        # Create arrays for linewidths and alphas
        # In modern matplotlib (3.8+), we set properties per level using numpy arrays
        num_levels = len(levels)
        linewidths = np.ones(num_levels) * 1.0  # Default linewidth
        alphas = np.ones(num_levels) * 0.6      # Default alpha

        # Highlight the selected level
        linewidths[level_index] = 3.0  # Thicker
        alphas[level_index] = 1.0      # Fully opaque

        # Apply to the contour plot
        self._psi_contour_plot.set_linewidth(linewidths)
        self._psi_contour_plot.set_alpha(alphas)

    def _reset_all_contour_highlighting(self):
        """Reset all contours to default appearance."""
        if self._psi_contour_plot is None:
            return

        # Get number of levels
        levels = self._psi_contour_plot.levels
        num_levels = len(levels)

        # Reset all to default values using numpy arrays
        linewidths = np.ones(num_levels) * 1.0
        alphas = np.ones(num_levels) * 0.6

        # Apply to the contour plot
        self._psi_contour_plot.set_linewidth(linewidths)
        self._psi_contour_plot.set_alpha(alphas)

    def _on_find_critical_points(self):
        """Handle Find Critical Points button click."""
        if self.equilibrium is None:
            self.error_handler.show_error("No Equilibrium",
                                        "Load a gEQDSK file first.")
            return

        # Compute critical points
        success = self.psi_crit_points_handler.find_critical_points()

        if success:
            # Update table display
            self.psi_crit_points_handler.populate_table(self.crit_points_table)

            # Enable detail button
            self.crit_points_detail_button.setEnabled(True)

            # Update text display (for backward compatibility, hidden)
            text = self.psi_crit_points_handler.format_display_text()
            self.crit_points_display.setText(text)

            # If checkbox is enabled, show markers
            if self.show_crit_markers_checkbox.isChecked():
                self._on_toggle_crit_markers(True)
        else:
            self.error_handler.show_error("Computation Failed",
                                        "Could not find critical points.")

    def _on_show_critical_points_detail(self):
        """Show detailed critical points information in a dialog."""
        from mesh_gui_project.ui.critical_points_detail_dialog import CriticalPointsDetailDialog

        dialog = CriticalPointsDetailDialog(self.psi_crit_points_handler, parent=self)
        dialog.exec_()

    def _on_toggle_crit_markers(self, checked: bool):
        """Handle Show Markers checkbox toggle."""
        if checked:
            self.psi_crit_points_handler.show_markers()
        else:
            self.psi_crit_points_handler.hide_markers()

        self.canvas_controller.draw()

    def _update_psi_preview_contour(self, R, Z):
        """
        Update preview contour for psi value at mouse position.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Check if position is within psi grid bounds
        # This prevents extrapolation warnings
        R_grid = self.equilibrium.R_grid
        Z_grid = self.equilibrium.Z_grid
        R_min, R_max = R_grid.min(), R_grid.max()
        Z_min, Z_max = Z_grid.min(), Z_grid.max()

        # If mouse is outside grid bounds, clear preview and return
        if R < R_min or R > R_max or Z < Z_min or Z > Z_max:
            # Clear preview if it exists
            if self._psi_preview_contour is not None:
                self._clear_psi_preview_contour()
            self._last_preview_position = None
            return

        # Store position for potential restoration after redraw
        self._last_preview_position = (R, Z)

        # Clear existing preview only if it exists
        # This prevents clearing collections that belong to the main psi field
        if self._psi_preview_contour is not None:
            self._clear_psi_preview_contour()

        # Query psi value at cursor position
        try:
            psi_at_mouse = self.equilibrium.psi_value(R, Z)
        except Exception:
            # If query fails (e.g., outside grid), don't show preview
            self._last_preview_position = None
            return

        # Get psi grid data for contour plotting
        R_grid = self.equilibrium.R_grid
        Z_grid = self.equilibrium.Z_grid
        psi_grid = self.equilibrium.psi_grid

        # Create meshgrid for plotting
        R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)

        # Count collections before creating contour
        collections_before = len(self.canvas_controller.ax.collections)

        # Plot a single contour line at the psi value under the mouse
        # Use dashed style to indicate it's a preview
        contour = self.canvas_controller.ax.contour(
            R_mesh, Z_mesh, psi_grid,
            levels=[psi_at_mouse],  # Single level at mouse position
            colors='red',  # Red color to indicate preview
            linestyles='dashed',  # Dashed to indicate preview
            linewidths=2.0,
            alpha=0.7,
            zorder=100  # High z-order to appear on top
        )

        self._psi_preview_contour = contour

        # Count collections after creating contour to track how many were added
        collections_after = len(self.canvas_controller.ax.collections)
        self._psi_preview_collections_count = collections_after - collections_before

        # Redraw canvas efficiently
        self.canvas_controller.draw_idle()

    def _clear_psi_preview_contour(self):
        """Clear the psi preview contour from the plot."""
        if self._psi_preview_contour is not None:
            # Remove the last N collections that were added by the preview contour
            # We remove from the end because the preview was added most recently
            for _ in range(self._psi_preview_collections_count):
                if len(self.canvas_controller.ax.collections) > 0:
                    # Remove the last collection (most recently added)
                    coll = self.canvas_controller.ax.collections[-1]
                    coll.remove()
            self._psi_preview_contour = None
            self._psi_preview_collections_count = 0
        # Clear saved position when explicitly clearing
        self._last_preview_position = None

    def _add_permanent_psi_contour(self, R, Z):
        """
        Add a permanent psi contour at the given position.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Check if position is within psi grid bounds
        # This prevents extrapolation warnings
        R_grid = self.equilibrium.R_grid
        Z_grid = self.equilibrium.Z_grid
        R_min, R_max = R_grid.min(), R_grid.max()
        Z_min, Z_max = Z_grid.min(), Z_grid.max()

        # If click is outside grid bounds, don't add contour
        if R < R_min or R > R_max or Z < Z_min or Z > Z_max:
            return

        # Query psi value at click position
        try:
            psi_at_click = self.equilibrium.psi_value(R, Z)
        except Exception:
            # If query fails (e.g., outside grid), don't add
            return

        # Check if this psi value is already added (avoid duplicates)
        for existing_psi in self._added_psi_values:
            if abs(existing_psi - psi_at_click) < 1e-8:
                # Already have a contour at this psi level, skip
                return

        # Add to list of psi values (both MainWindow and controller)
        self._added_psi_values.append(psi_at_click)
        if self.psi_viz_controller is not None:
            self.psi_viz_controller.add_psi_value(psi_at_click)

        # Save the current mouse position for preview restoration
        preview_position = self._last_preview_position

        # Redraw the entire R-Z plot to include the new contour level
        # This ensures the added contour uses the same colormap and style
        # as the existing psi field visualization
        self._redraw_rz_plot()

        # Restore preview contour if we're still in edit mode and had a preview
        if self._psi_edit_mode_active and preview_position is not None:
            R_preview, Z_preview = preview_position
            self._update_psi_preview_contour(R_preview, Z_preview)

    def _delete_nearest_psi_contour(self, R, Z):
        """
        Delete the nearest psi contour (automatic or user-added) to the given position.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Get psi value at click position
        try:
            psi_at_click = self.equilibrium.psi_value(R, Z)
        except Exception:
            # If query fails (e.g., outside grid), don't delete
            return

        # Compute active contour levels
        psi_grid = self.equilibrium.psi_grid
        n_levels = 20
        active_levels = PsiLevelComputer.compute_levels(
            psi_grid, self._added_psi_values, self._disabled_psi_levels, n_levels
        )

        # If no active levels, nothing to delete
        if len(active_levels) == 0:
            return

        # Find the nearest active level to the click position
        nearest_level = active_levels[0]
        min_distance = abs(active_levels[0] - psi_at_click)

        for level in active_levels:
            distance = abs(level - psi_at_click)
            if distance < min_distance:
                min_distance = distance
                nearest_level = level

        # Add to disabled levels list
        self._disabled_psi_levels.append(nearest_level)

        # If this level was in _added_psi_values, also remove it from there
        if nearest_level in self._added_psi_values:
            self._added_psi_values.remove(nearest_level)

        # Save the current mouse position for preview restoration
        preview_position = (R, Z)

        # Redraw the entire R-Z plot without the deleted contour level
        self._redraw_rz_plot()

        # Restore preview contour if we're still in edit mode
        if self._psi_edit_mode_active:
            self._update_psi_preview_contour(R, Z)

    def _on_generate_mesh_clicked(self):
        """
        Handle Generate Mesh button click.

        Generates mesh from currently selected PSI contour or limiter geometry.
        If no PSI contour is selected, uses the entire limiter geometry.
        """
        # Check if equilibrium is loaded
        if self.equilibrium is None:
            self.error_handler.show_warning("No Equilibrium",
                                           "Load a gEQDSK file first before generating mesh.")
            return

        # Get selected PSI contour from list
        selected_items = self.psi_contour_list.selectedItems()
        use_limiter = (len(selected_items) == 0)

        # Get mesh size from spinbox
        mesh_size = self.mesh_size_spinbox.value()

        try:
            if use_limiter:
                # No PSI contour selected, use limiter geometry
                self._selected_psi_for_mesh = None
                boundary = self.equilibrium.limiter_curve

                # Validate mesh size
                validation = self.mesh_workflow.validate_mesh_size(boundary, mesh_size)
                if validation['warning']:
                    should_continue = self.error_handler.ask_confirmation(
                        "Large Mesh Warning",
                        f"The current mesh size ({mesh_size}) will create approximately "
                        f"{int(validation['estimated_triangles']):,} triangles.\n\n"
                        f"This may take a long time and freeze the GUI.\n\n"
                        f"Recommended mesh size for this boundary: {validation['recommended_size']:.4f}\n\n"
                        f"Continue anyway?"
                    )
                    if not should_continue:
                        return

                # Generate mesh from limiter
                result = self.mesh_workflow.generate_mesh_from_limiter(
                    equilibrium=self.equilibrium,
                    target_element_size=mesh_size
                )
            else:
                # Use selected PSI value
                psi_value = selected_items[0].data(Qt.UserRole)
                self._selected_psi_for_mesh = psi_value

                # Extract boundary to validate mesh size
                from mesh_gui_project.core.mesh_boundary_selector import MeshBoundarySelector
                boundary_selector = MeshBoundarySelector(self.equilibrium)
                boundary = boundary_selector.get_boundary_from_psi(psi_value)

                # Validate mesh size
                validation = self.mesh_workflow.validate_mesh_size(boundary, mesh_size)
                if validation['warning']:
                    should_continue = self.error_handler.ask_confirmation(
                        "Large Mesh Warning",
                        f"The current mesh size ({mesh_size}) will create approximately "
                        f"{int(validation['estimated_triangles']):,} triangles.\n\n"
                        f"This may take a long time and freeze the GUI.\n\n"
                        f"Recommended mesh size for this boundary: {validation['recommended_size']:.4f}\n\n"
                        f"Continue anyway?"
                    )
                    if not should_continue:
                        return

                # Generate mesh from PSI contour
                result = self.mesh_workflow.generate_mesh_from_psi(
                    equilibrium=self.equilibrium,
                    psi_value=psi_value,
                    target_element_size=mesh_size
                )

            # Store mesh data
            self._mesh_vertices = result['vertices']
            self._mesh_elements = result['elements']
            self._mesh_boundary = result['boundary'].copy()
            self._boundary_vertex_indices = result['boundary_vertex_indices']

            # Clear manually moved vertices (new mesh = new vertex indices)
            self._manually_moved_vertex_indices = set()

            # Update statistics labels
            metrics = result['metrics']
            self.mesh_vertex_count_label.setText(str(len(result['vertices'])))
            self.mesh_triangle_count_label.setText(str(len(result['elements'])))
            self._update_mesh_quality_labels(metrics)

            # Visualize mesh on canvas
            self._visualize_mesh()

            # Update status bar
            self.statusBar().showMessage(
                f"Mesh generated: {len(result['vertices'])} vertices, {len(result['elements'])} triangles",
                5000
            )

            # Update workflow breadcrumb - skip "select" step if using limiter
            selected_items = self.psi_contour_list.selectedItems()
            if len(selected_items) == 0:
                # Generated from limiter - mark "select" as completed even though skipped
                self.workflow_breadcrumb.set_step("optimize", skip_steps=["select"])
            else:
                # Generated from selected contour - normal progression
                self.workflow_breadcrumb.set_step("optimize")

            # Update tab indicators
            self._update_tab_indicators()

        except Exception as e:
            self.error_handler.show_error("Mesh Generation Failed",
                                         f"Failed to generate mesh: {str(e)}")
            import traceback
            traceback.print_exc()

    def _update_mesh_quality_labels(self, metrics):
        """
        Update mesh quality metric labels from computed metrics.

        Filters out invalid values (inf, NaN) from aspect ratios and angles
        before displaying them in the UI labels.

        Args:
            metrics: Dictionary containing quality metrics with keys:
                - 'aspect_ratios': array of triangle aspect ratios
                - 'min_angles': array of minimum angles per triangle
                - 'areas': array of triangle areas
        """
        # Filter out inf values from aspect ratios (degenerate triangles)
        finite_aspect_ratios = metrics['aspect_ratios'][np.isfinite(metrics['aspect_ratios'])]
        if len(finite_aspect_ratios) > 0:
            self.mesh_avg_aspect_ratio_label.setText(f"{finite_aspect_ratios.mean():.2f}")
        else:
            self.mesh_avg_aspect_ratio_label.setText("N/A")

        # Filter out zero-area triangles from min angle (degenerate triangles)
        valid_angles = metrics['min_angles'][metrics['areas'] > 1e-10]
        if len(valid_angles) > 0:
            self.mesh_min_angle_label.setText(f"{valid_angles.min():.1f}°")
        else:
            self.mesh_min_angle_label.setText("N/A")

    def _on_mesh_edit_mode_toggled(self, checked):
        """
        Handle Enter Edit Mode button toggle.

        Args:
            checked: True if edit mode is active, False otherwise
        """
        if checked:
            # Entering edit mode
            if self._mesh_vertices is None or self._mesh_elements is None:
                self.error_handler.show_warning("No Mesh",
                                               "Generate a mesh first before entering edit mode.")
                self.enter_edit_mode_button.setChecked(False)
                return

            # Delegate to mesh edit handler
            if self.mesh_edit_handler is not None:
                success = self.mesh_edit_handler.set_active(
                    True,
                    vertices=self._mesh_vertices,
                    elements=self._mesh_elements
                )
                if not success:
                    self.enter_edit_mode_button.setChecked(False)
                    return

                # Set contour constraints for boundary vertices
                if self._boundary_vertex_indices is not None and self._mesh_boundary is not None:
                    self.mesh_edit_handler.set_boundary_constraints(
                        self._boundary_vertex_indices,
                        self._mesh_boundary
                    )

            # Show edit mode info in status bar (persists until mode is exited)
            self.statusBar().showMessage(
                "EDIT MODE: Mesh Vertices  |  Click: Select Vertex  |  Drag: Move Vertex  |  Boundary vertices constrained to contour"
            )

            # Keep legacy state for compatibility (will be removed later)
            self._mesh_edit_mode_active = True
            # Keep legacy mesh_editor for now
            from mesh_gui_project.ui.mesh_editor import MeshEditor
            self._mesh_editor = MeshEditor(self._mesh_vertices, self._mesh_elements)
            if self._boundary_vertex_indices is not None and self._mesh_boundary is not None:
                for vertex_idx in self._boundary_vertex_indices:
                    self._mesh_editor.set_contour_constraint(vertex_idx, self._mesh_boundary)

        else:
            # Exiting edit mode
            if self.mesh_edit_handler is not None:
                self.mesh_edit_handler.set_active(False)
                # Get current mesh state from handler
                vertices, elements = self.mesh_edit_handler.get_mesh()
                if vertices is not None and elements is not None:
                    self._mesh_vertices = vertices
                    self._mesh_elements = elements
                # Copy manually moved vertices
                manually_moved = self.mesh_edit_handler.get_manually_moved_vertices()
                self._manually_moved_vertex_indices.update(manually_moved)

            # Legacy cleanup (don't overwrite handler's mesh changes!)
            if self._mesh_editor is not None:
                # Only update from legacy editor if handler isn't available
                if self.mesh_edit_handler is None:
                    self._mesh_vertices, self._mesh_elements = self._mesh_editor.get_mesh()
                if hasattr(self._mesh_editor, 'manually_moved_vertices') and self.mesh_edit_handler is None:
                    self._manually_moved_vertex_indices.update(self._mesh_editor.manually_moved_vertices)
                self._mesh_editor = None

            self._mesh_edit_mode_active = False
            self.statusBar().showMessage("Ready")

    def _highlight_selected_vertex(self, vertex_idx):
        """
        Highlight the selected vertex with a visual marker.

        Args:
            vertex_idx: Index of vertex to highlight
        """
        if self._mesh_editor is None:
            return

        # Remove previous highlight if exists
        if self._vertex_highlight_artist is not None:
            self._vertex_highlight_artist.remove()
            self._vertex_highlight_artist = None

        # Get vertex position
        vertex = self._mesh_editor.vertices[vertex_idx]

        # Draw highlight marker (yellow circle with larger size)
        self._vertex_highlight_artist = self.canvas_controller.ax.plot(
            vertex[0], vertex[1],
            'o',  # Circle marker
            color='yellow',
            markersize=12,
            markeredgecolor='black',
            markeredgewidth=2,
            zorder=1000  # Draw on top of everything
        )[0]

        self.canvas_controller.draw_idle()

    def _on_remesh_optimize_clicked(self):
        """
        Handle Remesh & Optimize button click.

        Retriangulates mesh and applies quality optimization.
        """
        if self._mesh_vertices is None or self._mesh_elements is None:
            self.error_handler.show_warning("No Mesh",
                                           "Generate a mesh first before optimizing.")
            return

        # If Edit Mode is still active, automatically exit it first
        # This ensures manually moved vertices are saved
        if self._mesh_edit_mode_active:
            self.enter_edit_mode_button.setChecked(False)
            # The toggle will trigger _on_mesh_edit_mode_toggled which saves manually moved vertices

        try:
            # Combine constrained vertices (boundary + manually moved vertices should not move)
            constrained_vertices = set()
            if self._boundary_vertex_indices is not None:
                constrained_vertices.update(self._boundary_vertex_indices)

            # Also constrain manually moved vertices from edit mode
            if self._manually_moved_vertex_indices:
                constrained_vertices.update(self._manually_moved_vertex_indices)

            # Use workflow to optimize mesh
            result = self.mesh_workflow.remesh_and_optimize(
                vertices=self._mesh_vertices,
                elements=self._mesh_elements,
                constrained_vertices=constrained_vertices,
                n_iterations=5
            )

            # Update mesh
            self._mesh_vertices = result['vertices']
            self._mesh_elements = result['elements']

            # Update visualization
            self._visualize_mesh()

            # Update statistics
            metrics = result['metrics']
            self.mesh_vertex_count_label.setText(str(len(result['vertices'])))
            self.mesh_triangle_count_label.setText(str(len(result['elements'])))
            self._update_mesh_quality_labels(metrics)

            self.statusBar().showMessage("Mesh optimized", 3000)

            # Update workflow breadcrumb
            self.workflow_breadcrumb.set_step("export")

        except Exception as e:
            self.error_handler.show_error("Optimization Failed",
                                         f"Failed to optimize mesh: {str(e)}")

    def _on_export_mesh_clicked(self):
        """
        Handle Export Mesh button click.

        Exports current mesh to .msh, .vtk, .smb, or .dmg format.
        """
        if self._mesh_vertices is None or self._mesh_elements is None:
            self.error_handler.show_warning("No Mesh",
                                           "Generate a mesh first before exporting.")
            return

        # Delegate to file operations handler which supports all formats
        success = self.file_ops_handler.save_mesh(
            self._mesh_vertices,
            self._mesh_elements
        )

        if success:
            self.statusBar().showMessage(
                "Mesh exported successfully",
                5000
            )

            # Update workflow breadcrumb
            self.workflow_breadcrumb.set_step("export")

    def _on_tab_changed(self, index):
        """
        Handle tab change event.

        Args:
            index: Index of the newly selected tab (0=Meta, 1=Psi, 2=Meshing)
        """
        # When switching to Meshing tab, re-visualize mesh if it exists
        if index == 2:  # Meshing tab
            if self._mesh_vertices is not None and self._mesh_elements is not None:
                self._visualize_mesh()

    def _on_mesh_viz_mode_changed(self):
        """Handle mesh visualization mode change from dropdown."""
        # Only redraw if mesh is loaded
        if self._mesh_vertices is None or self._mesh_elements is None:
            return

        # Re-visualize mesh with new mode
        self._visualize_mesh()

    def _visualize_mesh(self):
        """
        Visualize current mesh on R-Z canvas (delegates to orchestrator).

        Uses the selected visualization mode (wireframe or quality coloring).
        """
        if self._mesh_vertices is None or self._mesh_elements is None:
            return

        # Keep PSI colorbar if PSI visualization is active, otherwise remove it
        # Check if any PSI visualization is enabled
        psi_viz_active = (
            self.psi_display_contour_checkbox.isChecked() or
            self.psi_display_contourf_checkbox.isChecked()
        )

        if not psi_viz_active and self._psi_colorbar is not None:
            # PSI visualization is OFF - remove PSI colorbar
            try:
                self._psi_colorbar.remove()
            except (KeyError, ValueError):
                # Colorbar may already be removed or invalid, ignore
                pass
            self._psi_colorbar = None

        # Delegate to visualization orchestrator
        psi_colorbar_exists = self._psi_colorbar is not None
        self.viz_orchestrator.update_mesh_visualization(
            self._mesh_vertices,
            self._mesh_elements,
            psi_colorbar_exists
        )

    def show_about_dialog(self):
        """
        Show About dialog.

        Displays application information including version, license,
        contact details, and links.
        """
        from mesh_gui_project.ui.about_dialog import AboutDialog

        dialog = AboutDialog(self)
        dialog.exec_()
