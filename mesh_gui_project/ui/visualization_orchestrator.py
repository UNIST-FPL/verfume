"""Visualization orchestrator for coordinating multiple visualization controllers."""


class VisualizationOrchestrator:
    """Coordinates visualization updates across all controllers."""

    def __init__(self, canvas_ctrl, psi_viz_ctrl, mesh_viz_ctrl, eq_viz_ctrl):
        """
        Initialize the visualization orchestrator.

        Args:
            canvas_ctrl: CanvasController instance
            psi_viz_ctrl: PsiVisualizationController instance
            mesh_viz_ctrl: MeshVisualizationController instance
            eq_viz_ctrl: EquilibriumVisualizationController instance
        """
        self.canvas = canvas_ctrl
        self.psi_viz = psi_viz_ctrl
        self.mesh_viz = mesh_viz_ctrl
        self.eq_viz = eq_viz_ctrl

    def update_psi_range_display(self, psi_min_display, psi_max_display, psi_min, psi_max):
        """
        Update PSI min/max display widgets.

        Args:
            psi_min_display: QLabel widget for displaying minimum PSI value
            psi_max_display: QLabel widget for displaying maximum PSI value
            psi_min: Minimum PSI value (normalized), or None
            psi_max: Maximum PSI value (normalized), or None
        """
        if psi_min is None or psi_max is None:
            psi_min_display.setText("")
            psi_max_display.setText("")
            return

        # Ensure min is less than max (normalization can invert order)
        actual_min = min(psi_min, psi_max)
        actual_max = max(psi_min, psi_max)

        psi_min_display.setText(f"{actual_min:.4f}")
        psi_max_display.setText(f"{actual_max:.4f}")

    def update_psi_visualization(self, equilibrium, show_contour, show_contourf,
                                  added_psi_values=None, disabled_psi_levels=None):
        """
        Update PSI field visualization (contour/contourf).

        Args:
            equilibrium: Equilibrium data object
            show_contour: Whether to show contour lines
            show_contourf: Whether to show filled contours
            added_psi_values: List of user-added PSI values (optional)
            disabled_psi_levels: List of disabled PSI levels (optional)
        """
        if self.psi_viz:
            # Sync PSI values to controller if provided
            if added_psi_values is not None:
                self.psi_viz.set_added_psi_values(added_psi_values)
            if disabled_psi_levels is not None:
                self.psi_viz.set_disabled_psi_levels(disabled_psi_levels)

            # Plot PSI field
            self.psi_viz.plot_psi_field(equilibrium, show_contour, show_contourf)

    def clear_psi_visualization(self):
        """Clear PSI field visualization."""
        if self.psi_viz:
            self.psi_viz.clear_psi_field()

    def update_mesh_visualization(self, vertices, elements, psi_colorbar_exists):
        """
        Update mesh visualization with specified mode.

        Args:
            vertices: Mesh vertices array
            elements: Mesh elements array
            psi_colorbar_exists: Whether a PSI colorbar is currently displayed
        """
        if self.mesh_viz:
            self.mesh_viz.visualize_mesh(vertices, elements, psi_colorbar_exists)

        # Redraw canvas
        if self.canvas:
            self.canvas.draw()
