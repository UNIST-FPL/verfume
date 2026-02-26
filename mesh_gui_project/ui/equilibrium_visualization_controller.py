"""
Equilibrium Visualization Controller for plotting critical points and flux surfaces.
"""
from mesh_gui_project.core.critical_points import find_o_point, find_x_points


class EquilibriumVisualizationController:
    """Controller for equilibrium visualization (O-points, X-points, flux surfaces)."""

    def __init__(self, ax, canvas_controller):
        """
        Initialize equilibrium visualization controller.

        Args:
            ax: Matplotlib axes instance
            canvas_controller: CanvasController instance for drawing
        """
        self.ax = ax
        self.canvas_controller = canvas_controller

    def plot_critical_points(self, eq):
        """
        Plot O-point and X-points on the current axes.

        Adds circle marker with "O" label for O-point and "X" markers with
        labels for X-points.

        Args:
            eq: EquilibriumData instance with attached interpolator
        """
        # Find and plot O-point
        try:
            R_o, Z_o = find_o_point(eq)

            # Plot O-point as circle with "O" label
            self.ax.plot(R_o, Z_o, 'ro', markersize=10, label='O-point')
            self.ax.annotate('O', xy=(R_o, Z_o), xytext=(5, 5),
                           textcoords='offset points', fontsize=12,
                           fontweight='bold', color='red')
        except Exception as e:
            # O-point finding failed, skip plotting
            print(f"Could not find O-point: {e}")

        # Find and plot X-points
        try:
            x_points = find_x_points(eq)

            for i, (R_x, Z_x) in enumerate(x_points):
                # Plot X-point as X marker
                self.ax.plot(R_x, Z_x, 'bx', markersize=12, markeredgewidth=3,
                           label='X-point' if i == 0 else '')
                self.ax.annotate(f'X{i+1}', xy=(R_x, Z_x), xytext=(5, -10),
                               textcoords='offset points', fontsize=12,
                               fontweight='bold', color='blue')
        except Exception as e:
            # X-point finding failed, skip plotting
            print(f"Could not find X-points: {e}")

        # Refresh canvas
        self.canvas_controller.draw()

    def plot_flux_surfaces(self, eq, psi_n_list):
        """
        Plot flux surfaces for given psi_N values.

        Extracts and plots flux surfaces as green lines on the current axes.

        Args:
            eq: EquilibriumData instance with attached interpolator
            psi_n_list: List of normalized psi values to plot
        """
        from mesh_gui_project.core.flux_surface import FluxSurfaceExtractor

        # Create extractor
        extractor = FluxSurfaceExtractor(eq, n_rays=360)

        # Extract and plot surfaces
        try:
            surfaces = extractor.extract_by_psiN(psi_n_list)

            for i, (surface, psi_n) in enumerate(zip(surfaces, psi_n_list)):
                if len(surface) > 0:
                    # Plot flux surface
                    self.ax.plot(surface[:, 0], surface[:, 1],
                               'g-', linewidth=1.5, alpha=0.6,
                               label=f'psi_N={psi_n:.2f}' if i < 5 else '')
        except Exception as e:
            print(f"Could not plot flux surfaces: {e}")

        # Refresh canvas
        self.canvas_controller.draw()
