"""
Mouse Interaction Coordinator for routing mouse events to appropriate handlers.

Extracted from MainWindow as part of Phase 2 refactoring.
Implements priority-based event routing: mesh edit > psi edit > pan > tooltip
"""
from typing import Callable
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor


class MouseInteractionCoordinator:
    """
    Coordinates mouse interactions between different handlers.

    Responsibilities:
    - Route mouse events to appropriate handlers based on priority
    - Implement priority system: mesh edit (dragging) > panning > psi edit (preview) > tooltip
    - Ensure clean separation between different interaction modes
    """

    def __init__(
        self,
        psi_edit_handler,
        mesh_edit_handler,
        canvas_controller,
        on_tooltip_update_callback: Callable
    ):
        """
        Initialize mouse interaction coordinator.

        Args:
            psi_edit_handler: PsiEditHandler instance
            mesh_edit_handler: MeshEditHandler instance
            canvas_controller: CanvasController instance
            on_tooltip_update_callback: Callback for tooltip updates
        """
        self.psi_edit_handler = psi_edit_handler
        self.mesh_edit_handler = mesh_edit_handler
        self.canvas_controller = canvas_controller
        self._on_tooltip_update_callback = on_tooltip_update_callback

    def handle_mouse_press(self, event):
        """
        Handle mouse button press events.

        Routes to handlers with priority: mesh edit > psi edit > pan

        Args:
            event: Matplotlib mouse event
        """
        # Check if not in axes
        if event.inaxes != self.canvas_controller.ax:
            return

        # Priority 1: Mesh edit mode (if active)
        if self.mesh_edit_handler.is_active():
            handled = self.mesh_edit_handler.handle_mouse_press(event)
            if handled:
                return

        # Priority 2: PSI edit mode (if active)
        if self.psi_edit_handler.is_active():
            handled = self.psi_edit_handler.handle_mouse_press(event, button=event.button)
            if handled:
                return

        # Priority 3: Pan mode (default for left-click)
        if event.button == 1 and event.xdata is not None and event.ydata is not None:
            self.canvas_controller.start_pan(event.xdata, event.ydata)

    def handle_mouse_release(self, event):
        """
        Handle mouse button release events.

        Args:
            event: Matplotlib mouse event
        """
        # Check mesh edit handler first
        handled = self.mesh_edit_handler.handle_mouse_release(event)
        if handled:
            return

        # End panning if left button
        if event.button == 1:
            self.canvas_controller.end_pan()

    def handle_mouse_motion(self, event):
        """
        Handle mouse motion events.

        Routes with priority: mesh dragging > panning > psi preview > tooltip

        Args:
            event: Matplotlib mouse event
        """
        # Priority 1: Mesh vertex dragging (highest priority)
        if self.mesh_edit_handler.is_dragging():
            self.mesh_edit_handler.handle_mouse_motion(event)
            # Cursor set to closed hand during drag
            self._set_cursor(Qt.ClosedHandCursor)
            return

        # Priority 2: Panning mode
        if self.canvas_controller.is_panning():
            # Check if cursor is still in axes
            if event.inaxes != self.canvas_controller.ax:
                return

            # Get current position
            if event.xdata is None or event.ydata is None:
                return

            self.canvas_controller.update_pan(event.xdata, event.ydata)
            # Cursor set to closed hand during pan
            self._set_cursor(Qt.ClosedHandCursor)
            return

        # Priority 3: PSI edit mode preview
        if self.psi_edit_handler.is_active():
            # Always show the preview contour when in edit mode
            self.psi_edit_handler.handle_mouse_motion(event)

            # Set crosshair cursor in PSI edit mode
            self._set_cursor(Qt.CrossCursor)

            # Additionally show tooltip if Ctrl key is pressed
            modifiers = QApplication.keyboardModifiers()
            ctrl_pressed = modifiers & Qt.ControlModifier

            if ctrl_pressed:
                # Show tooltip in addition to preview when Ctrl is pressed
                self._on_tooltip_update_callback(event)
            else:
                # Hide tooltip when Ctrl is not pressed (but keep preview contour)
                self._on_tooltip_update_callback(None)

            return

        # Check if mesh edit mode is active and mouse is over a vertex
        if self.mesh_edit_handler.is_active():
            # Check if mouse is near a vertex for selection
            if event.inaxes == self.canvas_controller.ax and event.xdata is not None:
                near_vertex = self.mesh_edit_handler.is_near_vertex(event.xdata, event.ydata)
                if near_vertex:
                    # Set open hand cursor when near a vertex
                    self._set_cursor(Qt.OpenHandCursor)
                else:
                    # Set arrow cursor when not near a vertex
                    self._set_cursor(Qt.ArrowCursor)
            return

        # Priority 4: Tooltip display (lowest priority, default behavior)
        self._set_cursor(Qt.ArrowCursor)
        self._on_tooltip_update_callback(event)

    def _set_cursor(self, cursor_shape):
        """
        Set the cursor shape for the canvas.

        Args:
            cursor_shape: Qt cursor shape constant
        """
        if hasattr(self.canvas_controller, 'canvas') and self.canvas_controller.canvas is not None:
            self.canvas_controller.canvas.setCursor(QCursor(cursor_shape))

    def handle_scroll(self, event):
        """
        Handle mouse scroll events (zoom).

        Args:
            event: Matplotlib scroll event
        """
        self.canvas_controller.on_scroll_zoom(event)
