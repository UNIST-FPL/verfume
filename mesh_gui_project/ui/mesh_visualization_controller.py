"""
Mesh visualization controller.

Manages mesh rendering including:
- Wireframe visualization
- Quality-based coloring (aspect ratio, min angle, area)
- Mesh quality colorbar management
- Statistics display
"""
import numpy as np
from typing import Optional, List, Dict
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.colorbar import Colorbar
import matplotlib.tri as tri
from PyQt5.QtWidgets import QComboBox, QLabel


class MeshVisualizationController:
    """
    Controller for mesh visualization on matplotlib canvas.

    This class encapsulates all mesh rendering logic,
    separating it from UI coordination in MainWindow.
    """

    def __init__(
        self,
        ax: Axes,
        figure: Figure,
        viz_mode_combo: QComboBox,
        vertex_count_label: QLabel,
        triangle_count_label: QLabel,
        avg_aspect_ratio_label: QLabel,
        min_angle_label: QLabel
    ):
        """
        Initialize mesh visualization controller.

        Args:
            ax: Matplotlib axes for plotting
            figure: Matplotlib figure (for colorbar management)
            viz_mode_combo: QComboBox for selecting visualization mode
            vertex_count_label: QLabel for displaying vertex count
            triangle_count_label: QLabel for displaying triangle count
            avg_aspect_ratio_label: QLabel for displaying average aspect ratio
            min_angle_label: QLabel for displaying minimum angle
        """
        self.ax = ax
        self.figure = figure
        self.viz_mode_combo = viz_mode_combo
        self.vertex_count_label = vertex_count_label
        self.triangle_count_label = triangle_count_label
        self.avg_aspect_ratio_label = avg_aspect_ratio_label
        self.min_angle_label = min_angle_label

        # Visualization state
        self._mesh_plot_artists: List = []
        self._mesh_quality_colorbar: Optional[Colorbar] = None

    def visualize_mesh(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        psi_colorbar_exists: bool = False
    ):
        """
        Visualize mesh on canvas based on selected visualization mode.

        Args:
            vertices: (N, 2) array of vertex coordinates (R, Z)
            elements: (E, 3) array of triangle connectivity
            psi_colorbar_exists: Whether PSI colorbar is currently displayed
        """
        if vertices is None or elements is None or len(vertices) == 0:
            return

        # Clear previous mesh visualization
        self._clear_mesh_artists()

        # Remove previous mesh quality colorbar if it exists
        self._remove_mesh_colorbar()

        # Get visualization mode
        viz_mode = self.viz_mode_combo.currentText()

        if viz_mode == "Wireframe":
            self._visualize_wireframe(vertices, elements)
        elif viz_mode.startswith("Quality:"):
            self._visualize_quality(vertices, elements, viz_mode, psi_colorbar_exists)

    def _visualize_wireframe(self, vertices: np.ndarray, elements: np.ndarray):
        """
        Visualize mesh as wireframe (triangle edges).

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
        """
        triangulation = tri.Triangulation(
            vertices[:, 0],
            vertices[:, 1],
            elements
        )
        triplot = self.ax.triplot(triangulation, 'k-', linewidth=0.5, alpha=0.7, zorder=10)
        # triplot returns a list of Line2D objects
        self._mesh_plot_artists.extend(triplot)

    def _visualize_quality(
        self,
        vertices: np.ndarray,
        elements: np.ndarray,
        viz_mode: str,
        psi_colorbar_exists: bool
    ):
        """
        Visualize mesh with quality-based coloring.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
            viz_mode: Visualization mode string
            psi_colorbar_exists: Whether PSI colorbar is displayed
        """
        from mesh_gui_project.core.new_mesher import ContourMesher

        mesher = ContourMesher()
        metrics = mesher.compute_quality_metrics(vertices, elements)

        # Determine which metric to display
        if "Aspect Ratio" in viz_mode:
            values = metrics['aspect_ratios']
            cmap = 'RdYlGn_r'  # Red (bad) to Green (good), reversed
            label = 'Aspect Ratio'
        elif "Min Angle" in viz_mode:
            values = metrics['min_angles']
            cmap = 'RdYlGn'  # Red (bad) to Green (good)
            label = 'Min Angle (°)'
        elif "Area" in viz_mode:
            values = metrics['areas']
            cmap = 'viridis'
            label = 'Triangle Area'
        else:
            values = metrics['aspect_ratios']
            cmap = 'RdYlGn_r'
            label = 'Aspect Ratio'

        # Create triangulation
        triangulation = tri.Triangulation(
            vertices[:, 0],
            vertices[:, 1],
            elements
        )

        # Plot filled triangles with quality coloring
        tripcolor = self.ax.tripcolor(
            triangulation,
            facecolors=values,
            cmap=cmap,
            alpha=0.7,
            edgecolors='k',
            linewidths=0.3,
            zorder=10
        )
        self._mesh_plot_artists.append(tripcolor)

        # Add colorbar for quality visualization
        if psi_colorbar_exists:
            # PSI colorbar exists - stack quality colorbar below it
            # PSI colorbar is at [0.82, 0.400, 0.03, 0.27] (top at 0.670)
            # Place quality colorbar below with gap
            cax = self.figure.add_axes([0.82, 0.110, 0.03, 0.27])
        else:
            # No PSI colorbar - center the quality colorbar vertically
            cax = self.figure.add_axes([0.82, 0.400, 0.03, 0.27])

        self._mesh_quality_colorbar = self.figure.colorbar(
            tripcolor, cax=cax, label=label
        )

    def _clear_mesh_artists(self):
        """Clear all mesh visualization artists from axes."""
        for artist in self._mesh_plot_artists:
            try:
                artist.remove()
            except (NotImplementedError, ValueError, AttributeError):
                # Some artists cannot be removed or are already gone
                pass
        self._mesh_plot_artists.clear()

    def _remove_mesh_colorbar(self):
        """Remove mesh quality colorbar if it exists."""
        if self._mesh_quality_colorbar is not None:
            try:
                # Remove the colorbar axes from the figure
                if self._mesh_quality_colorbar.ax in self.figure.axes:
                    self.figure.delaxes(self._mesh_quality_colorbar.ax)
            except (KeyError, ValueError, AttributeError):
                # Colorbar may already be removed or invalid, ignore
                pass
            self._mesh_quality_colorbar = None

    def update_statistics(self, vertices: np.ndarray, elements: np.ndarray):
        """
        Update mesh statistics labels.

        Args:
            vertices: (N, 2) vertex coordinates
            elements: (E, 3) triangle connectivity
        """
        from mesh_gui_project.core.new_mesher import ContourMesher

        # Update counts
        self.vertex_count_label.setText(str(len(vertices)))
        self.triangle_count_label.setText(str(len(elements)))

        # Compute quality metrics
        mesher = ContourMesher()
        metrics = mesher.compute_quality_metrics(vertices, elements)

        # Filter out inf values from aspect ratios (degenerate triangles)
        finite_aspect_ratios = metrics['aspect_ratios'][np.isfinite(metrics['aspect_ratios'])]
        if len(finite_aspect_ratios) > 0:
            self.avg_aspect_ratio_label.setText(f"{finite_aspect_ratios.mean():.2f}")
        else:
            self.avg_aspect_ratio_label.setText("N/A")

        # Filter out zero-area triangles from min angle (degenerate triangles)
        valid_angles = metrics['min_angles'][metrics['areas'] > 1e-10]
        if len(valid_angles) > 0:
            self.min_angle_label.setText(f"{valid_angles.min():.1f}°")
        else:
            self.min_angle_label.setText("N/A")

    def clear_statistics(self):
        """Clear mesh statistics labels."""
        self.vertex_count_label.setText("0")
        self.triangle_count_label.setText("0")
        self.avg_aspect_ratio_label.setText("N/A")
        self.min_angle_label.setText("N/A")

    def has_colorbar(self) -> bool:
        """
        Check if mesh quality colorbar currently exists.

        Returns:
            True if colorbar exists
        """
        return self._mesh_quality_colorbar is not None

    def remove_colorbar(self):
        """Remove mesh quality colorbar (called during plot clearing)."""
        self._remove_mesh_colorbar()
