"""
UIFactory for creating UI components.

Responsible for creating menus, tabs, and UI widgets.
Separates UI construction from business logic.
"""
from PyQt5.QtWidgets import (QMenuBar, QAction, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QCheckBox, QLabel, QFormLayout, QLineEdit,
                             QPushButton, QListWidget, QTabWidget, QComboBox, QSpinBox,
                             QDoubleSpinBox, QTextEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from mesh_gui_project.ui.data_inspector_panel import DataInspectorPanel


class UIFactory:
    """Factory for creating UI components."""

    @staticmethod
    def create_menu_bar(parent):
        """
        Create complete menu bar with File and Help menus.

        Args:
            parent: Parent window

        Returns:
            QMenuBar: Complete menu bar with all menus and actions

        Note:
            Actions are created but not connected to handlers.
            Parent window is responsible for connecting signals.
        """
        menu_bar = QMenuBar(parent)

        # File menu
        file_menu = menu_bar.addMenu('&File')

        open_action = QAction('&Open gEQDSK...', parent)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        parent.open_action = open_action  # Store reference for connection

        recent_menu = file_menu.addMenu('Open &Recent')
        parent.recent_menu = recent_menu  # Store reference for updates
        file_menu.addSeparator()

        quit_action = QAction('&Quit', parent)
        quit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(quit_action)
        parent.quit_action = quit_action

        # Help menu
        help_menu = menu_bar.addMenu('&Help')

        about_action = QAction('&About', parent)
        help_menu.addAction(about_action)
        parent.about_action = about_action

        return menu_bar

    @staticmethod
    def create_left_panel(parent):
        """
        Create left panel with tabs for Meta, Psi, and Meshing.

        Args:
            parent: Parent window

        Returns:
            QTabWidget: Tab widget with all tabs configured

        Note:
            Widgets are created with object names for easy reference.
            Parent window is responsible for connecting signals.
        """
        # Create tab widget
        left_tabs = QTabWidget()
        left_tabs.setMaximumWidth(300)

        # Tab 0: Meta (Data Inspector)
        data_inspector = DataInspectorPanel()
        left_tabs.addTab(data_inspector, "Meta")
        parent.data_inspector = data_inspector

        # Tab 1: Psi (Visualization)
        psi_tab = UIFactory._create_psi_tab(parent)
        left_tabs.addTab(psi_tab, "Psi")

        # Tab 2: Meshing (Mesh Editing)
        mesh_tab = UIFactory._create_mesh_tab(parent)
        left_tabs.addTab(mesh_tab, "Meshing")

        # Store reference
        parent.left_tabs = left_tabs

        return left_tabs

    @staticmethod
    def _create_psi_tab(parent):
        """
        Create Psi visualization tab.

        Args:
            parent: Parent window

        Returns:
            QWidget: Psi tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Psi Field Display group
        psi_field_group = QGroupBox("Psi Field Display")
        psi_field_layout = QVBoxLayout()
        psi_field_group.setLayout(psi_field_layout)

        # Create checkboxes for display modes
        psi_display_contour_checkbox = QCheckBox("Contour Lines")
        psi_display_contour_checkbox.setObjectName('psi_display_contour_checkbox')
        psi_display_contourf_checkbox = QCheckBox("Filled Contours")
        psi_display_contourf_checkbox.setObjectName('psi_display_contourf_checkbox')

        # Add checkboxes to layout
        psi_field_layout.addWidget(psi_display_contour_checkbox)
        psi_field_layout.addWidget(psi_display_contourf_checkbox)

        # Store references in parent
        parent.psi_display_contour_checkbox = psi_display_contour_checkbox
        parent.psi_display_contourf_checkbox = psi_display_contourf_checkbox

        # Add min/max psi display
        psi_stats_layout = QFormLayout()
        psi_min_display = QLineEdit()
        psi_min_display.setReadOnly(True)
        psi_max_display = QLineEdit()
        psi_max_display.setReadOnly(True)
        psi_stats_layout.addRow("Min ψ_N:", psi_min_display)
        psi_stats_layout.addRow("Max ψ_N:", psi_max_display)
        psi_field_layout.addLayout(psi_stats_layout)

        parent.psi_min_display = psi_min_display
        parent.psi_max_display = psi_max_display

        layout.addWidget(psi_field_group)

        # Psi Edit Mode group
        psi_edit_group = QGroupBox("Psi Contour Editing")
        psi_edit_layout = QVBoxLayout()
        psi_edit_group.setLayout(psi_edit_layout)

        # Create PSI Edit Mode toggle button
        psi_edit_mode_button = QPushButton("Edit Psi Contours")
        psi_edit_mode_button.setObjectName('psi_edit_mode_button')
        psi_edit_mode_button.setCheckable(True)
        psi_edit_mode_button.setChecked(False)
        psi_edit_layout.addWidget(psi_edit_mode_button)

        parent.psi_edit_mode_button = psi_edit_mode_button

        # Add help text
        help_label = QLabel("When edit mode is active:\n• Move mouse to preview contour\n• Left-click to add contour\n• Right-click to delete nearest")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        psi_edit_layout.addWidget(help_label)

        # PSI Contour List
        psi_list_label = QLabel("Contour Levels:")
        psi_edit_layout.addWidget(psi_list_label)

        psi_contour_list = QListWidget()
        psi_contour_list.setObjectName('psi_contour_list')
        psi_contour_list.setSelectionMode(QListWidget.SingleSelection)
        psi_edit_layout.addWidget(psi_contour_list)

        parent.psi_contour_list = psi_contour_list

        # Save PSI Contours button
        save_psi_contours_button = QPushButton("Save Contour Levels...")
        psi_edit_layout.addWidget(save_psi_contours_button)

        parent.save_psi_contours_button = save_psi_contours_button

        layout.addWidget(psi_edit_group)

        # Critical Points Finder group
        crit_points_group = QGroupBox("Critical Points Finder")
        crit_points_layout = QVBoxLayout()
        crit_points_group.setLayout(crit_points_layout)

        # Find Critical Points button
        find_crit_points_button = QPushButton("Find Critical Points")
        find_crit_points_button.setObjectName('find_crit_points_button')
        crit_points_layout.addWidget(find_crit_points_button)

        parent.find_crit_points_button = find_crit_points_button

        # Results display (table widget for compact summary)
        crit_points_table = QTableWidget()
        crit_points_table.setObjectName('crit_points_table')
        crit_points_table.setColumnCount(5)
        crit_points_table.setHorizontalHeaderLabels(["Type", "R (m)", "Z (m)", "ψ_N", "ψ (Wb/rad)"])
        crit_points_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        crit_points_table.setSelectionBehavior(QTableWidget.SelectRows)
        crit_points_table.setSelectionMode(QTableWidget.SingleSelection)
        crit_points_table.setMaximumHeight(150)  # Compact height for 3-4 rows
        crit_points_table.verticalHeader().setVisible(False)  # Hide row numbers

        # Auto-resize columns to content
        header = crit_points_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        crit_points_layout.addWidget(crit_points_table)

        parent.crit_points_table = crit_points_table

        # Keep old display for backward compatibility (will be removed later)
        crit_points_display = QTextEdit()
        crit_points_display.setObjectName('crit_points_display')
        crit_points_display.setReadOnly(True)
        crit_points_display.setVisible(False)  # Hidden, replaced by table
        parent.crit_points_display = crit_points_display

        # View Details button
        crit_points_detail_button = QPushButton("View Details...")
        crit_points_detail_button.setObjectName('crit_points_detail_button')
        crit_points_detail_button.setEnabled(False)  # Disabled until points found
        crit_points_layout.addWidget(crit_points_detail_button)

        parent.crit_points_detail_button = crit_points_detail_button

        # Show Markers checkbox
        show_crit_markers_checkbox = QCheckBox("Show Markers")
        show_crit_markers_checkbox.setObjectName('show_crit_markers_checkbox')
        show_crit_markers_checkbox.setChecked(False)  # Default off
        crit_points_layout.addWidget(show_crit_markers_checkbox)

        parent.show_crit_markers_checkbox = show_crit_markers_checkbox

        layout.addWidget(crit_points_group)

        # Add stretch
        layout.addStretch()

        return tab

    @staticmethod
    def _create_mesh_tab(parent):
        """
        Create Meshing tab.

        Args:
            parent: Parent window

        Returns:
            QWidget: Mesh tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Visualization Mode group
        viz_group = QGroupBox("Mesh Visualization")
        viz_layout = QVBoxLayout()
        viz_group.setLayout(viz_layout)

        # Visualization mode dropdown
        viz_form = QFormLayout()
        mesh_viz_mode_combo = QComboBox()
        mesh_viz_mode_combo.setObjectName('mesh_viz_mode_combo')
        mesh_viz_mode_combo.addItems([
            "Wireframe",
            "Quality: Aspect Ratio",
            "Quality: Min Angle",
            "Quality: Area"
        ])
        viz_form.addRow("Display Mode:", mesh_viz_mode_combo)
        viz_layout.addLayout(viz_form)

        parent.mesh_viz_mode_combo = mesh_viz_mode_combo

        layout.addWidget(viz_group)

        # Mesh Generation Parameters group
        params_group = QGroupBox("Generation Parameters")
        params_layout = QVBoxLayout()
        params_group.setLayout(params_layout)

        # Toroidal steps input
        params_form = QFormLayout()
        mesh_toroidal_steps_spinbox = QSpinBox()
        mesh_toroidal_steps_spinbox.setObjectName('mesh_toroidal_steps_spinbox')
        mesh_toroidal_steps_spinbox.setMinimum(4)
        mesh_toroidal_steps_spinbox.setMaximum(512)
        mesh_toroidal_steps_spinbox.setValue(64)
        params_form.addRow("Toroidal Steps (N):", mesh_toroidal_steps_spinbox)

        parent.mesh_toroidal_steps_spinbox = mesh_toroidal_steps_spinbox

        # Mesh size input
        mesh_size_spinbox = QDoubleSpinBox()
        mesh_size_spinbox.setObjectName('mesh_size_spinbox')
        mesh_size_spinbox.setDecimals(6)  # Allow high precision input (e.g., 0.001234)
        mesh_size_spinbox.setMinimum(0.000001)  # Support very fine meshes
        mesh_size_spinbox.setMaximum(1.0)
        mesh_size_spinbox.setSingleStep(0.001)  # Increment by 0.001 for user convenience
        mesh_size_spinbox.setValue(0.05)
        params_form.addRow("Mesh Size:", mesh_size_spinbox)

        parent.mesh_size_spinbox = mesh_size_spinbox

        params_layout.addLayout(params_form)

        layout.addWidget(params_group)

        # Control Buttons group
        controls_group = QGroupBox("Mesh Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)

        # Generate Mesh button
        generate_mesh_button = QPushButton("Generate Mesh")
        generate_mesh_button.setObjectName('generate_mesh_button')
        controls_layout.addWidget(generate_mesh_button)

        parent.generate_mesh_button = generate_mesh_button

        # Enter Edit Mode button
        enter_edit_mode_button = QPushButton("Enter Edit Mode")
        enter_edit_mode_button.setObjectName('enter_edit_mode_button')
        enter_edit_mode_button.setCheckable(True)
        controls_layout.addWidget(enter_edit_mode_button)

        parent.enter_edit_mode_button = enter_edit_mode_button

        # Remesh & Optimize button
        remesh_optimize_button = QPushButton("Remesh && Optimize")
        controls_layout.addWidget(remesh_optimize_button)

        parent.remesh_optimize_button = remesh_optimize_button

        # Export Mesh button
        export_mesh_button = QPushButton("Export Mesh...")
        controls_layout.addWidget(export_mesh_button)

        parent.export_mesh_button = export_mesh_button

        layout.addWidget(controls_group)

        # Mesh Statistics group
        stats_group = QGroupBox("Mesh Statistics")
        stats_layout = QFormLayout()
        stats_group.setLayout(stats_layout)

        # Vertex count label
        mesh_vertex_count_label = QLabel("0")
        stats_layout.addRow("Vertices:", mesh_vertex_count_label)

        parent.mesh_vertex_count_label = mesh_vertex_count_label

        # Triangle count label
        mesh_triangle_count_label = QLabel("0")
        stats_layout.addRow("Triangles:", mesh_triangle_count_label)

        parent.mesh_triangle_count_label = mesh_triangle_count_label

        # Quality metrics labels
        mesh_avg_aspect_ratio_label = QLabel("N/A")
        stats_layout.addRow("Avg Aspect Ratio:", mesh_avg_aspect_ratio_label)

        parent.mesh_avg_aspect_ratio_label = mesh_avg_aspect_ratio_label

        mesh_min_angle_label = QLabel("N/A")
        stats_layout.addRow("Min Angle:", mesh_min_angle_label)

        parent.mesh_min_angle_label = mesh_min_angle_label

        layout.addWidget(stats_group)

        # Add stretch
        layout.addStretch()

        return tab
