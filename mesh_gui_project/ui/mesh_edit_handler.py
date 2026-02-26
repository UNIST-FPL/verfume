"""
Mesh Edit Handler for managing mesh vertex editing interactions.

Extracted from MainWindow as part of Phase 2 refactoring.
Handles vertex selection, dragging, boundary constraints, and edit mode state.
"""
from typing import Optional, Set, Tuple, Callable
import numpy as np


class MeshEditHandler:
    """
    Handles mesh vertex editing interactions.

    Responsibilities:
    - Manage mesh edit mode state
    - Handle vertex selection on mouse click
    - Handle vertex dragging during mouse motion
    - Apply boundary constraints to vertices
    - Track manually moved vertices
    - Provide visual feedback (highlighting)
    """

    def __init__(
        self,
        canvas_controller,
        on_mesh_update_callback: Callable[[], None]
    ):
        """
        Initialize mesh edit handler.

        Args:
            canvas_controller: CanvasController instance
            on_mesh_update_callback: Callback to trigger mesh visualization update
        """
        self.canvas_controller = canvas_controller
        self._on_mesh_update_callback = on_mesh_update_callback

        # Edit mode state
        self._active = False

        # Mesh editor instance
        self._mesh_editor = None

        # Dragging state
        self._dragging_vertex_idx: Optional[int] = None

        # Visual feedback
        self._vertex_highlight = None

    def is_active(self) -> bool:
        """
        Check if mesh edit mode is active.

        Returns:
            True if edit mode is active
        """
        return self._active

    def set_active(
        self,
        active: bool,
        vertices: Optional[np.ndarray] = None,
        elements: Optional[np.ndarray] = None
    ) -> bool:
        """
        Enable or disable mesh edit mode.

        Args:
            active: True to enable edit mode, False to disable
            vertices: Mesh vertices (required when activating)
            elements: Mesh elements (required when activating)

        Returns:
            True if mode change successful, False otherwise
        """
        if active:
            # Activating - need mesh data
            if vertices is None or elements is None:
                return False

            # Create mesh editor
            from mesh_gui_project.ui.mesh_editor import MeshEditor
            self._mesh_editor = MeshEditor(vertices, elements)

            self._active = True
            return True
        else:
            # Deactivating
            self._active = False

            # Clear highlight
            self._clear_highlight()

            # Keep mesh_editor for retrieving final state
            # (caller should call get_mesh() to retrieve)

            return True

    def set_boundary_constraints(
        self,
        boundary_vertex_indices: list,
        boundary_contour: np.ndarray
    ):
        """
        Set boundary constraints on specified vertices.

        Args:
            boundary_vertex_indices: List of vertex indices on boundary
            boundary_contour: Contour path for boundary constraint
        """
        if self._mesh_editor is None:
            return

        for vertex_idx in boundary_vertex_indices:
            self._mesh_editor.set_contour_constraint(vertex_idx, boundary_contour)

    def handle_mouse_press(self, event) -> bool:
        """
        Handle mouse button press in mesh edit mode.

        Args:
            event: Matplotlib mouse event

        Returns:
            True if event was handled, False otherwise
        """
        if not self._active or self._mesh_editor is None:
            return False

        if event.xdata is None or event.ydata is None:
            return False

        # Try to select a vertex near the click position
        vertex_idx = self._mesh_editor.select_vertex(event.xdata, event.ydata, threshold=0.05)

        if vertex_idx is not None:
            # Start dragging this vertex
            self._dragging_vertex_idx = vertex_idx
            self._highlight_vertex(vertex_idx)
            return True

        return False

    def handle_mouse_motion(self, event) -> bool:
        """
        Handle mouse motion in mesh edit mode.

        Moves dragged vertex to new position.

        Args:
            event: Matplotlib mouse event

        Returns:
            True if event was handled, False otherwise
        """
        if not self._active or self._dragging_vertex_idx is None or self._mesh_editor is None:
            return False

        if event.xdata is None or event.ydata is None:
            return False

        # Move the vertex
        self._mesh_editor.move_vertex(self._dragging_vertex_idx, event.xdata, event.ydata)

        # Update highlight position
        self._highlight_vertex(self._dragging_vertex_idx)

        # Trigger mesh update callback
        self._on_mesh_update_callback()

        return True

    def handle_mouse_release(self, event) -> bool:
        """
        Handle mouse button release in mesh edit mode.

        Ends vertex dragging.

        Args:
            event: Matplotlib mouse event

        Returns:
            True if event was handled, False otherwise
        """
        if not self._active:
            return False

        if self._dragging_vertex_idx is not None:
            # End dragging
            self._dragging_vertex_idx = None
            return True

        return False

    def is_dragging(self) -> bool:
        """
        Check if currently dragging a vertex.

        Returns:
            True if dragging
        """
        return self._dragging_vertex_idx is not None

    def is_near_vertex(self, x: float, y: float, threshold: float = 0.05) -> bool:
        """
        Check if mouse position is near any vertex.

        Args:
            x: X coordinate in data space
            y: Y coordinate in data space
            threshold: Distance threshold for "near" detection

        Returns:
            True if near a vertex, False otherwise
        """
        if not self._active or self._mesh_editor is None:
            return False

        # Try to find a vertex near the position
        vertex_idx = self._mesh_editor.select_vertex(x, y, threshold=threshold)
        return vertex_idx is not None

    def get_mesh(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Get current mesh vertices and elements.

        Returns:
            Tuple of (vertices, elements), or (None, None) if no mesh editor
        """
        if self._mesh_editor is None:
            return None, None

        return self._mesh_editor.get_mesh()

    def get_manually_moved_vertices(self) -> Set[int]:
        """
        Get set of vertex indices that were manually moved.

        Returns:
            Set of vertex indices
        """
        if self._mesh_editor is None:
            return set()

        if hasattr(self._mesh_editor, 'manually_moved_vertices'):
            return self._mesh_editor.manually_moved_vertices.copy()

        return set()

    def _highlight_vertex(self, vertex_idx: int):
        """
        Highlight the selected vertex with a visual marker.

        Args:
            vertex_idx: Index of vertex to highlight
        """
        if self._mesh_editor is None:
            return

        # Remove previous highlight if exists
        self._clear_highlight()

        # Get vertex position
        vertex = self._mesh_editor.vertices[vertex_idx]

        # Draw highlight marker (yellow circle with larger size)
        self._vertex_highlight = self.canvas_controller.ax.plot(
            vertex[0], vertex[1],
            'o',  # Circle marker
            color='yellow',
            markersize=12,
            markeredgecolor='black',
            markeredgewidth=2,
            zorder=1000  # Draw on top of everything
        )[0]

        self.canvas_controller.draw_idle()

    def _clear_highlight(self):
        """Clear vertex highlight from the plot."""
        if self._vertex_highlight is not None:
            self._vertex_highlight.remove()
            self._vertex_highlight = None
