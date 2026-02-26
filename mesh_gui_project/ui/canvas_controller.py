"""
Canvas controller for matplotlib figure and axes management.

Manages:
- Canvas creation and configuration
- Zoom and pan operations
- Tooltip display
- Axis limits and aspect ratio
"""
from typing import Optional, Tuple
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.text import Annotation
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


class CanvasController:
    """
    Controller for matplotlib canvas operations.

    This class manages the matplotlib figure, axes, and canvas,
    providing zoom, pan, and tooltip functionality.
    """

    def __init__(self):
        """Initialize canvas controller."""
        # Canvas components
        self.figure: Optional[Figure] = None
        self.ax: Optional[Axes] = None
        self.canvas: Optional[FigureCanvas] = None

        # Pan state
        self._is_panning = False
        self._pan_start_x: Optional[float] = None
        self._pan_start_y: Optional[float] = None

        # Tooltip state
        self._psi_tooltip_annotation: Optional[Annotation] = None

    def create_canvas(self, figsize=(8, 6)) -> FigureCanvas:
        """
        Create matplotlib canvas for R-Z plane visualization.

        Args:
            figsize: Figure size in inches (width, height)

        Returns:
            FigureCanvas widget
        """
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=figsize)
        self.canvas = FigureCanvas(self.figure)

        # Create axes for R-Z plane
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('R (m)')
        self.ax.set_ylabel('Z (m)')
        self.ax.grid(True, alpha=0.3)

        # Use 'equal' aspect to get same unit length for all axes
        # Use 'box' adjustable to preserve zoom - adjusts the box size instead of data limits
        self.ax.set_aspect('equal', adjustable='box')

        # Maximize plotting area by minimizing margins
        # right=0.80 leaves space for colorbars at left=0.82
        self.figure.subplots_adjust(left=0.08, bottom=0.08, right=0.80, top=0.98)

        return self.canvas

    def on_scroll_zoom(self, event):
        """
        Handle mouse scroll for zooming.

        Args:
            event: Matplotlib scroll event
        """
        # Only zoom if cursor is in axes
        if event.inaxes != self.ax:
            return

        # Get current axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Get mouse position in data coordinates
        xdata = event.xdata
        ydata = event.ydata

        if xdata is None or ydata is None:
            return

        # Zoom factor
        zoom_factor = 1.1

        # Determine zoom direction
        if event.button == 'up':
            # Zoom in - decrease range
            scale_factor = 1.0 / zoom_factor
        elif event.button == 'down':
            # Zoom out - increase range
            scale_factor = zoom_factor
        else:
            return

        # Calculate new limits centered on mouse position
        # For x-axis
        x_range = xlim[1] - xlim[0]
        new_x_range = x_range * scale_factor
        x_center_ratio = (xdata - xlim[0]) / x_range
        new_xlim = [
            xdata - new_x_range * x_center_ratio,
            xdata + new_x_range * (1 - x_center_ratio)
        ]

        # For y-axis
        y_range = ylim[1] - ylim[0]
        new_y_range = y_range * scale_factor
        y_center_ratio = (ydata - ylim[0]) / y_range
        new_ylim = [
            ydata - new_y_range * y_center_ratio,
            ydata + new_y_range * (1 - y_center_ratio)
        ]

        # Apply new limits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Redraw canvas
        self.canvas.draw()

    def start_pan(self, xdata: float, ydata: float):
        """
        Start panning operation.

        Args:
            xdata: X data coordinate where pan started
            ydata: Y data coordinate where pan started
        """
        self._is_panning = True
        self._pan_start_x = xdata
        self._pan_start_y = ydata

    def update_pan(self, xdata: float, ydata: float):
        """
        Update pan position.

        Args:
            xdata: Current X data coordinate
            ydata: Current Y data coordinate
        """
        if not self._is_panning:
            return

        if self._pan_start_x is None or self._pan_start_y is None:
            return

        # Calculate delta
        dx = self._pan_start_x - xdata
        dy = self._pan_start_y - ydata

        # Get current limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Apply pan (shift limits by delta)
        self.ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
        self.ax.set_ylim(ylim[0] + dy, ylim[1] + dy)

        # Redraw canvas
        self.canvas.draw()

    def end_pan(self):
        """End panning operation."""
        self._is_panning = False
        self._pan_start_x = None
        self._pan_start_y = None

    def is_panning(self) -> bool:
        """
        Check if currently panning.

        Returns:
            True if panning
        """
        return self._is_panning

    def should_show_psi_tooltip(
        self,
        event,
        equilibrium,
        contour_enabled: bool,
        contourf_enabled: bool
    ) -> bool:
        """
        Determine if psi tooltip should be shown.

        Args:
            event: Matplotlib mouse event
            equilibrium: EquilibriumData instance (or None)
            contour_enabled: Whether contour display is enabled
            contourf_enabled: Whether contourf display is enabled

        Returns:
            True if tooltip should be shown
        """
        # Check if equilibrium is loaded
        if equilibrium is None:
            return False

        # Check if cursor is in axes
        if event.inaxes != self.ax:
            return False

        # Check if coordinates are valid
        if event.xdata is None or event.ydata is None:
            return False

        # Check if at least one contour display is enabled
        if not (contour_enabled or contourf_enabled):
            return False

        # Check if Ctrl key is pressed
        modifiers = QApplication.keyboardModifiers()
        ctrl_pressed = modifiers & Qt.ControlModifier

        if not ctrl_pressed:
            return False

        # Check if mouse position is within psi domain bounds
        if not equilibrium.is_within_psi_domain(event.xdata, event.ydata):
            return False

        return True

    def update_psi_tooltip(self, equilibrium, R: float, Z: float):
        """
        Update or create psi tooltip at given position.

        Args:
            equilibrium: EquilibriumData instance
            R: R coordinate (meters)
            Z: Z coordinate (meters)
        """
        # Query psi value at cursor position
        try:
            psi = equilibrium.psi_value(R, Z)
            psi_n = equilibrium.normalize_psi(psi)
        except Exception:
            # If query fails, hide tooltip
            self.hide_psi_tooltip()
            return

        # Format enhanced tooltip text with multiple lines
        # Calculate percentage for easier interpretation
        psi_n_percent = psi_n * 100

        text = f'ψ_N: {psi_n:.4f} ({psi_n_percent:.1f}%)\nψ: {psi:.6e} Wb/rad\nR: {R:.4f} m, Z: {Z:.4f} m'

        # Create or update annotation
        if self._psi_tooltip_annotation is None:
            # Create new annotation with enhanced styling
            self._psi_tooltip_annotation = self.ax.annotate(
                text,
                xy=(R, Z),
                xytext=(10, 10),  # Offset from cursor
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.9, edgecolor='black', linewidth=1),
                fontsize=9,
                family='monospace',  # Monospace for better alignment
                zorder=1000  # Ensure it's on top
            )
        else:
            # Update existing annotation
            self._psi_tooltip_annotation.set_text(text)
            self._psi_tooltip_annotation.xy = (R, Z)
            # Make sure annotation is visible when updating
            self._psi_tooltip_annotation.set_visible(True)

        # Redraw canvas efficiently
        self.canvas.draw_idle()

    def hide_psi_tooltip(self):
        """Hide the psi tooltip annotation."""
        if self._psi_tooltip_annotation is not None:
            self._psi_tooltip_annotation.set_visible(False)
            self.canvas.draw_idle()

    def clear_axes(self):
        """Clear all artists from axes (for complete redraw)."""
        self.ax.clear()

        # Re-setup axes properties
        self.ax.set_xlabel('R (m)')
        self.ax.set_ylabel('Z (m)')
        self.ax.grid(True, alpha=0.3)
        # Use 'box' adjustable to preserve zoom - adjusts the box size instead of data limits
        self.ax.set_aspect('equal', adjustable='box')

    def get_axis_limits(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get current axis limits.

        Returns:
            Tuple of ((xmin, xmax), (ymin, ymax))
        """
        return self.ax.get_xlim(), self.ax.get_ylim()

    def set_axis_limits(self, xlim: Tuple[float, float], ylim: Tuple[float, float]):
        """
        Set axis limits.

        Args:
            xlim: (xmin, xmax) tuple
            ylim: (ymin, ymax) tuple
        """
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

    def draw(self):
        """Redraw canvas."""
        self.canvas.draw()

    def draw_idle(self):
        """Redraw canvas (idle/deferred)."""
        self.canvas.draw_idle()
