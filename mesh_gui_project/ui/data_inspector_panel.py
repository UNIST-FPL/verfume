"""
Data Inspector Panel for displaying parsed gEQDSK data.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QScrollArea, QLabel, QCheckBox
)
from PyQt5.QtCore import Qt


class DataInspectorPanel(QWidget):
    """Widget for displaying parsed gEQDSK equilibrium data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        main_layout = QVBoxLayout(self)

        # Create scroll area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)

        # Grid Dimensions section
        self.grid_group = QGroupBox("Grid Dimensions")
        grid_layout = QFormLayout()
        self.grid_size = QLineEdit()
        self.grid_size.setReadOnly(True)
        self.r_range = QLineEdit()
        self.r_range.setReadOnly(True)
        self.z_range = QLineEdit()
        self.z_range.setReadOnly(True)
        grid_layout.addRow("Grid Size:", self.grid_size)
        grid_layout.addRow("R Range:", self.r_range)
        grid_layout.addRow("Z Range:", self.z_range)
        self.grid_group.setLayout(grid_layout)
        container_layout.addWidget(self.grid_group)

        # Magnetic Axis section
        self.axis_group = QGroupBox("Magnetic Axis (O-point)")
        axis_layout = QFormLayout()
        self.axis_position = QLineEdit()
        self.axis_position.setReadOnly(True)
        self.axis_psi = QLineEdit()
        self.axis_psi.setReadOnly(True)
        axis_layout.addRow("Position:", self.axis_position)
        axis_layout.addRow("Psi at axis:", self.axis_psi)
        self.axis_group.setLayout(axis_layout)
        container_layout.addWidget(self.axis_group)

        # Plasma Boundary section
        self.boundary_group = QGroupBox("Plasma Boundary")
        boundary_layout = QFormLayout()
        self.boundary_psi = QLineEdit()
        self.boundary_psi.setReadOnly(True)
        self.boundary_points = QLineEdit()
        self.boundary_points.setReadOnly(True)
        self.limiter_points = QLineEdit()
        self.limiter_points.setReadOnly(True)
        boundary_layout.addRow("Psi at boundary:", self.boundary_psi)
        boundary_layout.addRow("Boundary points:", self.boundary_points)
        boundary_layout.addRow("Limiter points:", self.limiter_points)
        self.boundary_group.setLayout(boundary_layout)
        container_layout.addWidget(self.boundary_group)

        # Data Quality section
        self.quality_group = QGroupBox("Data Quality")
        quality_layout = QFormLayout()
        self.psi_range = QLineEdit()
        self.psi_range.setReadOnly(True)
        self.has_nan = QLineEdit()
        self.has_nan.setReadOnly(True)
        self.has_interpolator = QLineEdit()
        self.has_interpolator.setReadOnly(True)
        quality_layout.addRow("Psi min/max:", self.psi_range)
        quality_layout.addRow("Contains NaN:", self.has_nan)
        quality_layout.addRow("Valid interpolator:", self.has_interpolator)
        self.quality_group.setLayout(quality_layout)
        container_layout.addWidget(self.quality_group)

        # View Options section (at the bottom)
        self.view_options_group = QGroupBox("View Options")
        view_options_layout = QVBoxLayout()

        # Create checkboxes for visualization options
        self.show_o_x_checkbox = QCheckBox("Show O/X Points")
        self.show_o_x_checkbox.setChecked(True)
        view_options_layout.addWidget(self.show_o_x_checkbox)

        self.show_limiter_checkbox = QCheckBox("Show Limiter")
        self.show_limiter_checkbox.setChecked(True)
        view_options_layout.addWidget(self.show_limiter_checkbox)

        self.show_lcfs_checkbox = QCheckBox("Show LCFS")
        self.show_lcfs_checkbox.setChecked(True)
        view_options_layout.addWidget(self.show_lcfs_checkbox)

        self.view_options_group.setLayout(view_options_layout)
        container_layout.addWidget(self.view_options_group)

        # Add stretch to push everything to top
        container_layout.addStretch()

        # Set container in scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def update_data(self, equilibrium):
        """
        Update displayed data with EquilibriumData.

        Args:
            equilibrium: EquilibriumData instance or None
        """
        if equilibrium is None:
            self._clear_fields()
            return

        # Grid dimensions
        NR = len(equilibrium.R_grid) if equilibrium.R_grid is not None else 0
        NZ = len(equilibrium.Z_grid) if equilibrium.Z_grid is not None else 0
        self.grid_size.setText(f"{NR} × {NZ}")

        # R range
        if equilibrium.R_grid is not None and len(equilibrium.R_grid) > 0:
            R_min = equilibrium.R_grid[0]
            R_max = equilibrium.R_grid[-1]
            self.r_range.setText(f"{R_min:.4f} → {R_max:.4f} m")
        else:
            self.r_range.setText("N/A")

        # Z range
        if equilibrium.Z_grid is not None and len(equilibrium.Z_grid) > 0:
            Z_min = equilibrium.Z_grid[0]
            Z_max = equilibrium.Z_grid[-1]
            self.z_range.setText(f"{Z_min:.4f} → {Z_max:.4f} m")
        else:
            self.z_range.setText("N/A")

        # Magnetic axis
        self.axis_position.setText(f"R={equilibrium.axis_R:.4f} m, Z={equilibrium.axis_Z:.4f} m")
        self.axis_psi.setText(f"{equilibrium.psi_axis:.6e}")

        # Plasma boundary
        self.boundary_psi.setText(f"{equilibrium.psi_boundary:.6e}")

        # Boundary points
        if equilibrium.boundary_curve is not None:
            n_boundary = len(equilibrium.boundary_curve)
            self.boundary_points.setText(f"{n_boundary} points")
        else:
            self.boundary_points.setText("None")

        # Limiter points
        if equilibrium.limiter_curve is not None:
            n_limiter = len(equilibrium.limiter_curve)
            self.limiter_points.setText(f"{n_limiter} points")
        else:
            self.limiter_points.setText("None")

        # Psi range
        if equilibrium.psi_grid is not None:
            psi_min = equilibrium.psi_grid.min()
            psi_max = equilibrium.psi_grid.max()
            self.psi_range.setText(f"{psi_min:.6e} to {psi_max:.6e}")
        else:
            self.psi_range.setText("N/A")

        # NaN check
        has_nan = hasattr(equilibrium, 'has_nan') and equilibrium.has_nan
        self.has_nan.setText("Yes" if has_nan else "No")

        # Interpolator check
        has_interp = hasattr(equilibrium, '_interpolator') and equilibrium._interpolator is not None
        self.has_interpolator.setText("Yes" if has_interp else "No")

    def _clear_fields(self):
        """Clear all displayed fields."""
        self.grid_size.setText("")
        self.r_range.setText("")
        self.z_range.setText("")
        self.axis_position.setText("")
        self.axis_psi.setText("")
        self.boundary_psi.setText("")
        self.boundary_points.setText("")
        self.limiter_points.setText("")
        self.psi_range.setText("")
        self.has_nan.setText("")
        self.has_interpolator.setText("")
