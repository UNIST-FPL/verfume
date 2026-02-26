"""
PSI field visualization controller.

Manages PSI contour and filled contour visualization, including:
- Contour line and filled contour plotting
- Colorbar lifecycle management
- Preview contour rendering
- Contour list management
"""
import numpy as np
import warnings
from typing import Optional, List, Tuple
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.colorbar import Colorbar
from matplotlib.contour import ContourSet
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from mesh_gui_project.core.application_state import ApplicationState
from mesh_gui_project.utils.contour_collection_manager import ContourCollectionManager
from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer


class PsiVisualizationController:
    """
    Controller for PSI field visualization on matplotlib canvas.

    This class encapsulates all PSI contour visualization logic,
    separating it from UI coordination in MainWindow.
    """

    def __init__(
        self,
        ax: Axes,
        figure: Figure,
        psi_contour_list_widget: QListWidget,
        application_state: Optional[ApplicationState] = None
    ):
        """
        Initialize PSI visualization controller.

        Args:
            ax: Matplotlib axes for plotting
            figure: Matplotlib figure (for colorbar management)
            psi_contour_list_widget: QListWidget for displaying contour levels
            application_state: Optional ApplicationState for centralized state management
        """
        self.ax = ax
        self.figure = figure
        self.psi_contour_list_widget = psi_contour_list_widget
        self._application_state = application_state

        # Contour collection manager
        self._contour_manager = ContourCollectionManager(ax)

        # Visualization state
        self._psi_contour_plot: Optional[ContourSet] = None
        self._psi_contourf_plot: Optional[ContourSet] = None
        self._psi_colorbar: Optional[Colorbar] = None

        # Preview state
        self._psi_preview_contour: Optional[ContourSet] = None
        self._last_preview_position: Optional[Tuple[float, float]] = None

        # User-managed contour data (legacy, deprecated when application_state is provided)
        self._added_psi_values: List[float] = []
        self._disabled_psi_levels: List[float] = []

    def plot_psi_field(
        self,
        equilibrium,
        show_contour: bool,
        show_contourf: bool,
        n_levels: int = 20
    ):
        """
        Plot PSI field visualization based on display settings.

        Creates contour lines and/or filled contours depending on
        which modes are enabled. Both can be displayed simultaneously.

        Args:
            equilibrium: EquilibriumData instance with psi grid
            show_contour: Whether to show contour lines
            show_contourf: Whether to show filled contours
            n_levels: Number of automatic contour levels
        """
        if equilibrium is None:
            return

        # Get psi grid data
        R_grid = equilibrium.R_grid
        Z_grid = equilibrium.Z_grid
        psi_grid = equilibrium.psi_grid

        # Create meshgrid for plotting
        R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)

        # Determine contour levels
        levels_to_use = self._compute_contour_levels(psi_grid, n_levels)

        # Track which plot to use for colorbar
        colorbar_mappable = None

        # Plot filled contours first (if enabled) so line contours appear on top
        if show_contourf:
            contourf = self.ax.contourf(
                R_mesh, Z_mesh, psi_grid,
                levels=levels_to_use,
                cmap='viridis',
                alpha=0.6,
                zorder=1  # Behind boundaries and points
            )
            self._psi_contourf_plot = contourf
            colorbar_mappable = contourf
        else:
            # Clear filled contour plot reference when disabled
            self._psi_contourf_plot = None

        # Plot line contours (if enabled)
        if show_contour:
            contour = self.ax.contour(
                R_mesh, Z_mesh, psi_grid,
                levels=levels_to_use,
                cmap='viridis',
                linewidths=1.0,
                alpha=0.6,
                zorder=2  # On top of filled contours but behind boundaries
            )
            self._psi_contour_plot = contour
            # Only use contour for colorbar if contourf is not enabled
            if colorbar_mappable is None:
                colorbar_mappable = contour
        else:
            # Clear contour plot reference when disabled
            self._psi_contour_plot = None

        # Add colorbar if any visualization is shown
        if colorbar_mappable is not None and self._psi_colorbar is None:
            # Create colorbar in optimized position
            # Position: left=0.82, bottom=0.400 for better text visibility
            cax = self.figure.add_axes([0.82, 0.400, 0.03, 0.27])
            self._psi_colorbar = self.figure.colorbar(
                colorbar_mappable, cax=cax, label='ψ_N'
            )

        # Update the PSI contour list widget
        self._update_psi_contour_list(equilibrium)

    def _compute_contour_levels(self, psi_grid: np.ndarray, n_levels: int) -> np.ndarray:
        """
        Compute contour levels including automatic and user-added values.

        Args:
            psi_grid: 2D PSI grid data
            n_levels: Number of automatic levels

        Returns:
            Array of contour levels to use
        """
        # Get PSI values from application state or local state
        if self._application_state is not None:
            added_values = self._application_state.get_added_psi_values()
            disabled_levels = self._application_state.get_disabled_psi_levels()
        else:
            added_values = self._added_psi_values
            disabled_levels = self._disabled_psi_levels

        # Compute filtered contour levels
        levels_to_use = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # If all levels were disabled, need at least one level for contour plot
        if len(levels_to_use) == 0:
            return n_levels

        return levels_to_use

    def clear_psi_field(self):
        """
        Clear PSI field visualization from the plot.

        Removes contour/contourf plots and colorbar if present.
        """
        # Remove contour line plot if it exists
        if self._psi_contour_plot is not None:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                if hasattr(self._psi_contour_plot, 'collections'):
                    collections = self._psi_contour_plot.collections
                    for collection in collections:
                        collection.remove()
            self._psi_contour_plot = None

        # Remove filled contour plot if it exists
        if self._psi_contourf_plot is not None:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                if hasattr(self._psi_contourf_plot, 'collections'):
                    collections = self._psi_contourf_plot.collections
                    for collection in collections:
                        collection.remove()
            self._psi_contourf_plot = None

        # Remove colorbar if it exists
        if self._psi_colorbar is not None:
            try:
                self._psi_colorbar.remove()
            except (KeyError, ValueError):
                pass
            self._psi_colorbar = None

    def remove_colorbar(self):
        """
        Remove PSI colorbar (called during plot clearing).

        This is separate from clear_psi_field to allow selective removal.
        """
        if self._psi_colorbar is not None:
            try:
                self._psi_colorbar.remove()
            except (KeyError, ValueError):
                pass
            self._psi_colorbar = None

    def update_psi_preview_contour(self, equilibrium, R: float, Z: float):
        """
        Update preview contour for psi value at mouse position.

        Args:
            equilibrium: EquilibriumData instance
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Check if position is within psi grid bounds
        if not equilibrium.is_within_grid_bounds(R, Z):
            if self._psi_preview_contour is not None:
                self.clear_psi_preview_contour()
            self._last_preview_position = None
            return

        # Get grid data for plotting
        R_grid = equilibrium.R_grid
        Z_grid = equilibrium.Z_grid

        # Store position for potential restoration after redraw
        self._last_preview_position = (R, Z)

        # Clear existing preview
        if self._psi_preview_contour is not None:
            self.clear_psi_preview_contour()

        # Query psi value at cursor position
        try:
            psi_at_mouse = equilibrium.psi_value(R, Z)
        except Exception:
            self._last_preview_position = None
            return

        # Get psi grid data for contour plotting
        psi_grid = equilibrium.psi_grid

        # Create meshgrid for plotting
        R_mesh, Z_mesh = np.meshgrid(R_grid, Z_grid)

        # Count collections before creating contour
        collections_before = len(self.ax.collections)

        # Plot a single contour line at the psi value under the mouse
        contour = self.ax.contour(
            R_mesh, Z_mesh, psi_grid,
            levels=[psi_at_mouse],
            colors='red',
            linestyles='dashed',
            linewidths=2.0,
            alpha=0.7,
            zorder=100  # High z-order to appear on top
        )

        self._psi_preview_contour = contour

        # Track the contour collections
        self._contour_manager.track_contour("psi_preview", collections_before)

    def clear_psi_preview_contour(self):
        """Clear the psi preview contour from the plot."""
        if self._psi_preview_contour is not None:
            # Clear tracked contour collections
            self._contour_manager.clear_contour("psi_preview")
            self._psi_preview_contour = None
        self._last_preview_position = None

    def add_psi_value(self, psi_value: float):
        """
        Add a user-specified PSI value to the contour list.

        Args:
            psi_value: Raw PSI value to add
        """
        # Check if this psi value is already added (avoid duplicates)
        for existing_psi in self._added_psi_values:
            if abs(existing_psi - psi_value) < 1e-8:
                return  # Already have this contour

        self._added_psi_values.append(psi_value)

    def disable_psi_level(self, psi_value: float):
        """
        Disable a PSI level (mark it for exclusion from display).

        Args:
            psi_value: Raw PSI value to disable
        """
        if psi_value not in self._disabled_psi_levels:
            self._disabled_psi_levels.append(psi_value)

        # If this level was in added values, remove it
        if psi_value in self._added_psi_values:
            self._added_psi_values.remove(psi_value)

    def _update_psi_contour_list(self, equilibrium):
        """
        Update the PSI contour list widget with currently displayed levels.

        Args:
            equilibrium: EquilibriumData instance for normalization
        """
        # Clear list
        self.psi_contour_list_widget.clear()

        if equilibrium is None:
            return

        # Get PSI values from application state or local state
        if self._application_state is not None:
            added_values = self._application_state.get_added_psi_values()
            disabled_levels = self._application_state.get_disabled_psi_levels()
        else:
            added_values = self._added_psi_values
            disabled_levels = self._disabled_psi_levels

        # Get all active levels
        psi_grid = equilibrium.psi_grid
        n_levels = 20

        # Compute active levels
        active_levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        # Convert to psi_N and add to list
        for psi_level in sorted(active_levels):
            psi_n = equilibrium.normalize_psi(psi_level)

            # Determine if this is a user-added or automatic level
            source = "USER" if psi_level in added_values else "AUTO"

            # Create list item
            item = QListWidgetItem(f"ψ_N = {psi_n:.4f} ({source})")
            item.setData(Qt.UserRole, psi_level)  # Store raw psi value
            self.psi_contour_list_widget.addItem(item)

    def highlight_contour_level(self, psi_level: float):
        """
        Highlight a specific contour level by making it brighter/thicker.

        Args:
            psi_level: Raw PSI value to highlight
        """
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
        num_levels = len(levels)
        linewidths = np.ones(num_levels) * 1.0  # Default linewidth
        alphas = np.ones(num_levels) * 0.6      # Default alpha

        # Highlight the selected level
        linewidths[level_index] = 3.0  # Thicker
        alphas[level_index] = 1.0      # Fully opaque

        # Apply to the contour plot
        self._psi_contour_plot.set_linewidth(linewidths)
        self._psi_contour_plot.set_alpha(alphas)

    def reset_all_contour_highlighting(self):
        """Reset all contours to default appearance."""
        if self._psi_contour_plot is None:
            return

        # Get number of levels
        levels = self._psi_contour_plot.levels
        num_levels = len(levels)

        # Reset all to default values
        linewidths = np.ones(num_levels) * 1.0
        alphas = np.ones(num_levels) * 0.6

        # Apply to the contour plot
        self._psi_contour_plot.set_linewidth(linewidths)
        self._psi_contour_plot.set_alpha(alphas)

    def get_last_preview_position(self) -> Optional[Tuple[float, float]]:
        """
        Get the last preview position for restoration after redraw.

        Returns:
            Tuple of (R, Z) or None
        """
        return self._last_preview_position

    def has_colorbar(self) -> bool:
        """
        Check if PSI colorbar currently exists.

        Returns:
            True if colorbar exists
        """
        return self._psi_colorbar is not None

    def set_added_psi_values(self, values: List[float]):
        """
        Set the list of user-added PSI values.

        Args:
            values: List of PSI values to set
        """
        self._added_psi_values = values

    def set_disabled_psi_levels(self, levels: List[float]):
        """
        Set the list of disabled PSI levels.

        Args:
            levels: List of PSI levels to disable
        """
        self._disabled_psi_levels = levels
