"""Event Handler Coordinator for MainWindow.

This module coordinates event handling for MainWindow, reducing MainWindow's
size and improving separation of concerns. It handles:
- Menu action events
- Button click events
- Checkbox state changes
- List selection changes
- Tab change events
"""


class EventHandlerCoordinator:
    """Coordinates event handling for MainWindow UI interactions."""

    def __init__(self, parent_window):
        """
        Initialize the event handler coordinator.

        Args:
            parent_window: Reference to the MainWindow instance
        """
        self.parent_window = parent_window

    # PSI-related event handlers
    def handle_psi_edit_mode_toggled(self, checked):
        """
        Handle PSI edit mode button toggle.

        Args:
            checked: True if button is checked (edit mode active), False otherwise
        """
        # Delegate to PSI edit handler
        if self.parent_window.psi_edit_handler is not None:
            self.parent_window.psi_edit_handler.set_active(checked)

        # Keep legacy state for compatibility (will be removed later)
        self.parent_window._psi_edit_mode_active = checked

    def handle_psi_display_mode_changed(self):
        """Handle PSI field display mode change from checkboxes."""
        # Only redraw if equilibrium is loaded
        if self.parent_window.equilibrium is None:
            return

        # Completely redraw the entire plot from scratch
        self.parent_window._redraw_rz_plot()

    def handle_psi_contour_selection_changed(self):
        """Handle selection change in PSI contour list."""
        # Get selected items
        selected_items = self.parent_window.psi_contour_list.selectedItems()

        if len(selected_items) == 0:
            # No selection - reset all to default
            self.parent_window._reset_all_contour_highlighting()
            self.parent_window.canvas_controller.draw_idle()
            return

        # Get selected psi level
        selected_item = selected_items[0]
        from PyQt5.QtCore import Qt
        psi_level = selected_item.data(Qt.UserRole)

        # Highlight the selected contour
        self.parent_window._highlight_contour_level(psi_level)
        self.parent_window.canvas_controller.draw_idle()

        # Update workflow breadcrumb
        self.parent_window.workflow_breadcrumb.set_step("generate")

        # Update tab indicators
        self.parent_window._update_tab_indicators()

    def handle_save_psi_contours(self):
        """Save PSI contour levels to a text file."""
        self.parent_window._save_psi_contours()

    # Mesh-related event handlers
    def handle_generate_mesh_clicked(self):
        """Handle Generate Mesh button click."""
        self.parent_window._on_generate_mesh_clicked()

    def handle_mesh_edit_mode_toggled(self, checked):
        """Handle Enter Edit Mode button toggle."""
        self.parent_window._on_mesh_edit_mode_toggled(checked)

    def handle_remesh_optimize_clicked(self):
        """Handle Remesh & Optimize button click."""
        self.parent_window._on_remesh_optimize_clicked()

    def handle_export_mesh_clicked(self):
        """Handle Export Mesh button click."""
        self.parent_window._on_export_mesh_clicked()

    def handle_mesh_viz_mode_changed(self):
        """Handle mesh visualization mode change from dropdown."""
        self.parent_window._on_mesh_viz_mode_changed()

    # Tab and menu event handlers
    def handle_tab_changed(self, index):
        """Handle tab change event."""
        self.parent_window._on_tab_changed(index)

    def handle_open_geqdsk_dialog(self):
        """Show file dialog to open a gEQDSK file."""
        self.parent_window.open_geqdsk_dialog()

    def handle_close(self):
        """Close the application."""
        self.parent_window.close()

    # View options event handlers
    def handle_view_option_changed(self):
        """Handle view option checkbox changes (O/X Points, Limiter, LCFS)."""
        # Only redraw if equilibrium is loaded
        if self.parent_window.equilibrium is None:
            return

        # Redraw the plot to reflect the new view option states
        self.parent_window._redraw_rz_plot()
