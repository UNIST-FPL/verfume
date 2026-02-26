"""
PSI Edit Handler for managing PSI contour editing interactions.

Extracted from MainWindow as part of Phase 2 refactoring.
Handles preview contours, adding/deleting contours, and edit mode state.
"""
from typing import Optional, List, Callable
import numpy as np
from mesh_gui_project.core.application_state import ApplicationState
from mesh_gui_project.utils.contour_collection_manager import ContourCollectionManager
from mesh_gui_project.utils.psi_level_computer import PsiLevelComputer


class PsiEditHandler:
    """
    Handles PSI contour editing interactions.

    Responsibilities:
    - Manage PSI edit mode state
    - Create and update preview contours during mouse motion
    - Add permanent contours on left-click
    - Delete nearest contours on right-click
    - Track added and disabled PSI values
    """

    def __init__(
        self,
        equilibrium,
        psi_viz_controller,
        canvas_controller,
        on_redraw_callback: Callable[[], None],
        application_state: Optional[ApplicationState] = None,
        on_tooltip_restore_callback: Optional[Callable[[float, float], None]] = None
    ):
        """
        Initialize PSI edit handler.

        Args:
            equilibrium: EquilibriumData instance
            psi_viz_controller: PsiVisualizationController instance
            canvas_controller: CanvasController instance
            on_redraw_callback: Callback to trigger full redraw
            application_state: Optional ApplicationState for centralized state management
            on_tooltip_restore_callback: Optional callback to restore tooltip at (R, Z) position
        """
        self.equilibrium = equilibrium
        self.psi_viz_controller = psi_viz_controller
        self.canvas_controller = canvas_controller
        self._on_redraw_callback = on_redraw_callback
        self._on_tooltip_restore_callback = on_tooltip_restore_callback
        self._application_state = application_state

        # Contour collection manager
        self._contour_manager = ContourCollectionManager(canvas_controller.ax)

        # Edit mode state
        self._active = False

        # Preview contour state
        self._preview_contour = None
        self._last_preview_position = None

        # User modifications (legacy, deprecated when application_state is provided)
        self._added_psi_values: List[float] = []
        self._disabled_psi_levels: List[float] = []

    def is_active(self) -> bool:
        """
        Check if PSI edit mode is active.

        Returns:
            True if edit mode is active
        """
        return self._active

    def set_active(self, active: bool):
        """
        Enable or disable PSI edit mode.

        Args:
            active: True to enable edit mode, False to disable
        """
        self._active = active

        # Clear preview contour when deactivating
        if not active:
            self._clear_preview_contour()

    def handle_mouse_press(self, event, button: int) -> bool:
        """
        Handle mouse button press in PSI edit mode.

        Args:
            event: Matplotlib mouse event
            button: Button number (1=left, 3=right)

        Returns:
            True if event was handled, False otherwise
        """
        if not self._active:
            return False

        if event.xdata is None or event.ydata is None:
            return False

        if button == 1:
            # Left-click: add permanent contour
            self._add_permanent_contour(event.xdata, event.ydata)
            return True
        elif button == 3:
            # Right-click: delete nearest contour
            self._delete_nearest_contour(event.xdata, event.ydata)
            return True

        return False

    def handle_mouse_motion(self, event) -> bool:
        """
        Handle mouse motion in PSI edit mode.

        Creates/updates preview contour at mouse position.

        Args:
            event: Matplotlib mouse event

        Returns:
            True if event was handled, False otherwise
        """
        if not self._active:
            return False

        # Check if mouse is in axes and has valid coordinates
        if event.inaxes == self.canvas_controller.ax and event.xdata is not None and event.ydata is not None:
            self._update_preview_contour(event.xdata, event.ydata)
        else:
            self._clear_preview_contour()

        return True

    def get_added_values(self) -> List[float]:
        """
        Get list of user-added PSI values.

        Returns:
            List of PSI values added by user
        """
        if self._application_state is not None:
            return self._application_state.get_added_psi_values()
        return self._added_psi_values.copy()

    def get_disabled_levels(self) -> List[float]:
        """
        Get list of disabled PSI contour levels.

        Returns:
            List of disabled PSI levels
        """
        if self._application_state is not None:
            return self._application_state.get_disabled_psi_levels()
        return self._disabled_psi_levels.copy()

    def _update_preview_contour(self, R: float, Z: float):
        """
        Create or update the preview contour at given position.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Check if position is within psi grid bounds
        if not self.equilibrium.is_within_grid_bounds(R, Z):
            if self._preview_contour is not None:
                self._clear_preview_contour()
            self._last_preview_position = None
            return

        # Store position for potential restoration after redraw
        self._last_preview_position = (R, Z)

        # Clear existing preview
        if self._preview_contour is not None:
            self._clear_preview_contour()

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

        self._preview_contour = contour

        # Track the contour collections
        self._contour_manager.track_contour("preview", collections_before)

        # Redraw canvas efficiently
        self.canvas_controller.draw_idle()

    def _clear_preview_contour(self):
        """Clear the preview contour from the plot."""
        if self._preview_contour is not None:
            # Clear tracked contour collections
            self._contour_manager.clear_contour("preview")
            self._preview_contour = None
            # Redraw canvas to show the removal
            self.canvas_controller.draw_idle()
        # Clear saved position when explicitly clearing
        self._last_preview_position = None

    def _add_permanent_contour(self, R: float, Z: float):
        """
        Add a permanent PSI contour at the given position.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Check if position is within psi grid bounds
        if not self.equilibrium.is_within_grid_bounds(R, Z):
            return

        # Query psi value at click position
        try:
            psi_at_click = self.equilibrium.psi_value(R, Z)
        except Exception:
            # If query fails (e.g., outside grid), don't add
            return

        # Get current added values
        if self._application_state is not None:
            added_values = self._application_state.get_added_psi_values()
        else:
            added_values = self._added_psi_values

        # Check if this psi value is already added (avoid duplicates)
        for existing_psi in added_values:
            if abs(existing_psi - psi_at_click) < 1e-8:
                # Already have a contour at this psi level, skip
                return

        # Add to state
        if self._application_state is not None:
            self._application_state.add_psi_value(psi_at_click)
        else:
            self._added_psi_values.append(psi_at_click)

        # Also add to psi_viz_controller if available (for backward compatibility)
        if self.psi_viz_controller is not None:
            self.psi_viz_controller.add_psi_value(psi_at_click)

        # Save the current mouse position for preview restoration
        preview_position = self._last_preview_position

        # Trigger redraw to include the new contour level
        self._on_redraw_callback()

        # Restore preview contour if we're still in edit mode and had a preview
        if self._active and preview_position is not None:
            R_preview, Z_preview = preview_position
            self._update_preview_contour(R_preview, Z_preview)

            # Also restore tooltip if callback is available and Ctrl is pressed
            if self._on_tooltip_restore_callback is not None:
                self._on_tooltip_restore_callback(R_preview, Z_preview)

    def _delete_nearest_contour(self, R: float, Z: float):
        """
        Delete the nearest PSI contour (automatic or user-added) to the given position.

        Args:
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Check if position is within psi grid bounds
        if not self.equilibrium.is_within_grid_bounds(R, Z):
            return

        # Get psi value at click position
        try:
            psi_at_click = self.equilibrium.psi_value(R, Z)
        except Exception:
            # If query fails (e.g., outside grid), don't delete
            return

        # Get current state
        if self._application_state is not None:
            added_values = self._application_state.get_added_psi_values()
            disabled_levels = self._application_state.get_disabled_psi_levels()
        else:
            added_values = self._added_psi_values
            disabled_levels = self._disabled_psi_levels

        # Compute available contour levels
        psi_grid = self.equilibrium.psi_grid
        n_levels = 20
        available_levels = PsiLevelComputer.compute_levels(
            psi_grid, added_values, disabled_levels, n_levels
        )

        if len(available_levels) == 0:
            return  # No levels to delete

        # Find nearest level to click position
        distances = np.abs(np.array(available_levels) - psi_at_click)
        nearest_idx = np.argmin(distances)
        nearest_level = available_levels[nearest_idx]

        # Add to disabled levels
        if self._application_state is not None:
            self._application_state.disable_psi_level(nearest_level)
        else:
            self._disabled_psi_levels.append(nearest_level)

        # Save the current mouse position for restoration
        preview_position = self._last_preview_position

        # Trigger redraw
        self._on_redraw_callback()

        # Restore preview contour and tooltip after deletion
        if self._active and preview_position is not None:
            R_preview, Z_preview = preview_position
            self._update_preview_contour(R_preview, Z_preview)

            # Also restore tooltip if callback is available and Ctrl is pressed
            if self._on_tooltip_restore_callback is not None:
                self._on_tooltip_restore_callback(R_preview, Z_preview)
