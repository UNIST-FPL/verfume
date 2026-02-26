"""
Handler for critical points finder feature in Psi tab.

Manages computation, display, and visualization of critical points (O-points and X-points).
"""
from typing import Optional, List, Tuple, Callable
from PyQt5.QtWidgets import QTableWidgetItem
from mesh_gui_project.core.critical_points import find_o_point, find_x_points


class PsiCriticalPointsHandler:
    """
    Handler for finding and displaying critical points in the Psi tab.

    Responsibilities:
    - Compute critical points (O-points and X-points) on demand
    - Format display text in grouped format
    - Manage green marker artists on canvas
    - Handle show/hide marker logic
    """

    def __init__(self, ax, canvas_controller, application_state, equilibrium_provider: Callable):
        """
        Initialize the critical points handler.

        Args:
            ax: Matplotlib Axes object for plotting
            canvas_controller: CanvasController instance for canvas operations
            application_state: ApplicationState instance for state management
            equilibrium_provider: Callable that returns current equilibrium data
        """
        self.ax = ax
        self.canvas_controller = canvas_controller
        self.application_state = application_state
        self.equilibrium_provider = equilibrium_provider

        # Store marker artists for removal
        self._marker_artists = []

    def find_critical_points(self) -> bool:
        """
        Find critical points (O-point and X-points) for current equilibrium.

        Returns:
            True if computation succeeded, False otherwise
        """
        equilibrium = self.equilibrium_provider()

        if equilibrium is None:
            return False

        # Find O-point (magnetic axis)
        o_point = find_o_point(equilibrium)

        # Find X-points (separatrix points)
        x_points = find_x_points(equilibrium)

        # Store results in ApplicationState
        self.application_state.set_critical_points(o_point, x_points)

        return True

    def format_display_text(self) -> str:
        """
        Format critical points data as grouped text display.

        Shows both psi and psi_N values, and differences from gEQDSK header positions.

        Returns:
            Formatted text string with O-points and X-points sections
        """
        import numpy as np

        data = self.application_state.get_critical_points()

        if data is None:
            return "No critical points found.\nClick 'Find Critical Points' to analyze the current equilibrium."

        equilibrium = self.equilibrium_provider()
        lines = []

        # O-Points section
        lines.append("O-Points:")
        o_point = data.get('o_point')
        if o_point is not None:
            R, Z = o_point
            psi = equilibrium.psi_value(R, Z)
            psi_N = equilibrium.normalize_psi(psi)

            # Get gEQDSK header values for comparison
            R_efit = equilibrium.axis_R
            Z_efit = equilibrium.axis_Z
            psi_efit = equilibrium.psi_axis
            psi_N_efit = equilibrium.normalize_psi(psi_efit)

            # Calculate differences
            dR = R - R_efit
            dZ = Z - Z_efit
            distance = np.sqrt(dR**2 + dZ**2)
            dpsi = psi - psi_efit
            dpsi_N = psi_N - psi_N_efit

            lines.append(f"  Numerical:  (R, Z) = ({R:.6f}, {Z:.6f}) m")
            lines.append(f"  EFIT:       (R, Z) = ({R_efit:.6f}, {Z_efit:.6f}) m")
            lines.append(f"  Difference: ΔR = {dR*1e3:.3f} mm, ΔZ = {dZ*1e3:.3f} mm, |Δ| = {distance*1e3:.3f} mm")
            lines.append(f"  psi:        Numerical = {psi:.6f}, EFIT = {psi_efit:.6f}, Δpsi = {dpsi:.6e}")
            lines.append(f"  psi_N:      Numerical = {psi_N:.6f}, EFIT = {psi_N_efit:.6f}, Δpsi_N = {dpsi_N:.6e}")
        else:
            lines.append("  None found")

        lines.append("")  # Empty line separator

        # X-Points section
        lines.append("X-Points:")
        x_points = data.get('x_points', [])
        if x_points:
            for i, (R, Z) in enumerate(x_points, 1):
                psi = equilibrium.psi_value(R, Z)
                psi_N = equilibrium.normalize_psi(psi)

                lines.append(f"  X{i}:")
                lines.append(f"    Location: (R, Z) = ({R:.6f}, {Z:.6f}) m")
                lines.append(f"    psi:      {psi:.6f}")
                lines.append(f"    psi_N:    {psi_N:.6f}")
        else:
            lines.append("  None found")

        return "\n".join(lines)

    def populate_table(self, table_widget) -> None:
        """
        Populate QTableWidget with critical points summary data.

        Args:
            table_widget: QTableWidget to populate with critical points

        Table columns: Type | R (m) | Z (m) | ψ_N | ψ (Wb/rad)
        """
        data = self.application_state.get_critical_points()

        if data is None:
            table_widget.setRowCount(0)
            return

        equilibrium = self.equilibrium_provider()
        if equilibrium is None:
            table_widget.setRowCount(0)
            return

        # Collect all points for table
        points_data = []

        # O-Point
        o_point = data.get('o_point')
        if o_point is not None:
            R, Z = o_point
            psi = equilibrium.psi_value(R, Z)
            psi_N = equilibrium.normalize_psi(psi)
            points_data.append(("O-Point", R, Z, psi_N, psi))

        # X-Points
        x_points = data.get('x_points', [])
        for i, (R, Z) in enumerate(x_points, 1):
            psi = equilibrium.psi_value(R, Z)
            psi_N = equilibrium.normalize_psi(psi)
            type_name = f"X{i}" if i == 1 else f"X{i}"
            points_data.append((type_name, R, Z, psi_N, psi))

        # Set table row count
        table_widget.setRowCount(len(points_data))

        # Populate table
        for row, (point_type, R, Z, psi_N, psi) in enumerate(points_data):
            # Column 0: Type
            table_widget.setItem(row, 0, QTableWidgetItem(point_type))

            # Column 1: R (m) - 4 decimal places for compact display
            table_widget.setItem(row, 1, QTableWidgetItem(f"{R:.4f}"))

            # Column 2: Z (m) - 4 decimal places
            table_widget.setItem(row, 2, QTableWidgetItem(f"{Z:.4f}"))

            # Column 3: ψ_N - 6 decimal places
            table_widget.setItem(row, 3, QTableWidgetItem(f"{psi_N:.6f}"))

            # Column 4: ψ (Wb/rad) - scientific notation
            table_widget.setItem(row, 4, QTableWidgetItem(f"{psi:.6e}"))

    def show_markers(self) -> None:
        """
        Show critical points markers on the canvas.

        Draws green 'o' markers for O-points and green 'x' markers for X-points.
        """
        # Clear any existing markers first
        self.hide_markers()

        data = self.application_state.get_critical_points()
        if data is None:
            return

        # Draw O-point marker (green circle)
        o_point = data.get('o_point')
        if o_point is not None:
            R, Z = o_point
            artist = self.ax.plot(R, Z, 'go', markersize=10, zorder=101, label='O-point')[0]
            self._marker_artists.append(artist)

        # Draw X-point markers (green x)
        x_points = data.get('x_points', [])
        for R, Z in x_points:
            artist = self.ax.plot(R, Z, 'gx', markersize=10, markeredgewidth=2, zorder=101)[0]
            self._marker_artists.append(artist)

    def hide_markers(self) -> None:
        """
        Hide (remove) all critical points markers from the canvas.
        """
        for artist in self._marker_artists:
            artist.remove()
        self._marker_artists.clear()
