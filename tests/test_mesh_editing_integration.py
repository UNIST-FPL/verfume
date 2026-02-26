"""
Integration tests for mesh editing workflow (Phase 7).
"""
import sys
import pytest
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import Qt
from mesh_gui_project.ui.main_window import MainWindow
from mesh_gui_project.core.equilibrium import EquilibriumData


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def window_with_equilibrium(qapp):
    """Create MainWindow with loaded equilibrium data."""
    window = MainWindow()

    # Load a test gEQDSK file
    geqdsk_file = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    window.load_geqdsk(geqdsk_file)

    return window


def test_workflow_select_and_generate(window_with_equilibrium):
    """
    Test 7.1: Test workflow: Select contour → Generate mesh → Display

    Workflow:
    1. Load equilibrium data (done in fixture)
    2. Switch to Mesh Editing tab
    3. Enable PSI contour display
    4. Click Generate Mesh button
    5. Verify mesh is generated
    6. Verify mesh is displayed on canvas
    7. Verify statistics are updated
    """
    window = window_with_equilibrium

    # Switch to Mesh Editing tab
    window.left_tabs.setCurrentIndex(2)  # 0=Visualization, 1=Data Inspector, 2=Mesh Editing

    # Verify equilibrium is loaded
    assert window.equilibrium is not None
    assert window.equilibrium._interpolator is not None

    # Enable PSI contour display (required for mesh generation)
    window.psi_display_contour_checkbox.setChecked(True)

    # Initial state: no mesh generated yet
    assert window._mesh_vertices is None
    assert window._mesh_elements is None
    assert window.mesh_vertex_count_label.text() == "0"
    assert window.mesh_triangle_count_label.text() == "0"

    # Click Generate Mesh button
    window.generate_mesh_button.click()

    # Verify mesh is generated
    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None
    assert len(window._mesh_vertices) > 0
    assert len(window._mesh_elements) > 0

    # Verify statistics are updated
    vertex_count = int(window.mesh_vertex_count_label.text())
    triangle_count = int(window.mesh_triangle_count_label.text())
    assert vertex_count > 0
    assert triangle_count > 0
    assert window.mesh_avg_aspect_ratio_label.text() != "N/A"
    assert window.mesh_min_angle_label.text() != "N/A"

    # Verify mesh is visualized (check that artists were added)
    assert len(window._mesh_plot_artists) > 0


def test_workflow_edit_remesh_export(window_with_equilibrium, tmp_path):
    """
    Test 7.2: Test workflow: Edit vertices → Remesh → Export

    Workflow:
    1. Load equilibrium and generate mesh (reuse test 7.1 setup)
    2. Enter edit mode
    3. Click Remesh & Optimize
    4. Export mesh to file
    5. Verify file was created
    """
    window = window_with_equilibrium

    # Setup: Generate a mesh first (same as test_workflow_select_and_generate)
    window.left_tabs.setCurrentIndex(2)
    window.psi_display_contour_checkbox.setChecked(True)
    window.generate_mesh_button.click()

    # Verify mesh was generated
    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None

    # Enter edit mode
    window.enter_edit_mode_button.setChecked(True)
    assert window._mesh_edit_mode_active == True
    assert window._mesh_editor is not None

    # Exit edit mode
    window.enter_edit_mode_button.setChecked(False)
    assert window._mesh_edit_mode_active == False

    # Click Remesh & Optimize
    initial_vertex_count = len(window._mesh_vertices)
    window.remesh_optimize_button.click()

    # Verify mesh still exists after optimization
    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None

    # Export mesh (programmatically set file path)
    import tempfile
    test_file = tmp_path / "test_mesh.msh"

    # Temporarily replace the file dialog with a mock that returns our test path
    original_getSaveFileName = QFileDialog.getSaveFileName

    def mock_getSaveFileName(*args, **kwargs):
        return (str(test_file), "Gmsh Mesh (*.msh)")

    QFileDialog.getSaveFileName = mock_getSaveFileName

    try:
        window.export_mesh_button.click()

        # Verify file was created
        assert test_file.exists()
        assert test_file.stat().st_size > 0
    finally:
        # Restore original method
        QFileDialog.getSaveFileName = original_getSaveFileName


def test_psi_contour_integration(window_with_equilibrium):
    """
    Test 7.3: Test integration with existing PSI contour edit mode

    Workflow:
    1. Load equilibrium
    2. Enable PSI edit mode
    3. Add a PSI contour
    4. Switch to Mesh Editing tab
    5. Generate mesh from the added contour
    6. Verify mesh matches the selected PSI value
    """
    window = window_with_equilibrium

    # Enable PSI contours display
    window.psi_display_contour_checkbox.setChecked(True)

    # Enable PSI edit mode
    window.psi_edit_mode_button.setChecked(True)
    assert window.psi_edit_handler.is_active() == True

    # Simulate adding a PSI contour by clicking at a location
    from unittest.mock import Mock
    R_test = window.equilibrium.axis_R + 0.2
    Z_test = window.equilibrium.axis_Z

    event = Mock()
    event.inaxes = window.canvas_controller.ax
    event.xdata = R_test
    event.ydata = Z_test
    event.button = 1
    window.psi_edit_handler.handle_mouse_press(event, button=1)

    # Verify contour was added
    added_values = window.psi_edit_handler.get_added_values()
    assert len(added_values) > 0
    psi_added = added_values[0]

    # Exit PSI edit mode
    window.psi_edit_mode_button.setChecked(False)

    # Switch to Mesh Editing tab
    window.left_tabs.setCurrentIndex(2)

    # Select the added PSI contour in the list
    for i in range(window.psi_contour_list.count()):
        item = window.psi_contour_list.item(i)
        if item.data(Qt.UserRole) == psi_added:
            window.psi_contour_list.setCurrentItem(item)
            break

    # Generate mesh from the selected contour
    window.generate_mesh_button.click()

    # Verify mesh was generated
    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None

    # Verify the mesh was generated from the correct PSI value
    assert window._selected_psi_for_mesh == psi_added


def test_limiter_mesh_generation_without_psi_contours(window_with_equilibrium):
    """
    Test 7.4: Test mesh generation using limiter geometry without PSI contours

    Workflow:
    1. Load equilibrium (done in fixture)
    2. Switch to Mesh Editing tab
    3. Generate mesh WITHOUT selecting any PSI contour
    4. Verify mesh is generated using limiter geometry
    5. Verify mesh size parameter is used
    """
    window = window_with_equilibrium

    # Switch to Mesh Editing tab
    window.left_tabs.setCurrentIndex(2)

    # Verify equilibrium is loaded
    assert window.equilibrium is not None

    # Do NOT enable PSI contours (keep them off)
    # Do NOT select any PSI contour in the list

    # Set a specific mesh size
    test_mesh_size = 0.01
    window.mesh_size_spinbox.setValue(test_mesh_size)

    # Initial state: no mesh generated yet
    assert window._mesh_vertices is None
    assert window._mesh_elements is None

    # Click Generate Mesh button (should use limiter geometry)
    window.generate_mesh_button.click()

    # Verify mesh is generated
    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None
    assert len(window._mesh_vertices) > 0
    assert len(window._mesh_elements) > 0

    # Verify no PSI value was selected (limiter-based generation)
    assert window._selected_psi_for_mesh is None

    # Verify statistics are updated
    vertex_count = int(window.mesh_vertex_count_label.text())
    triangle_count = int(window.mesh_triangle_count_label.text())
    assert vertex_count > 0
    assert triangle_count > 0


def test_vertex_drag_and_drop_in_edit_mode(window_with_equilibrium):
    """
    Test 7.5: Test vertex selection and drag-and-drop in edit mode

    Workflow:
    1. Generate a mesh
    2. Enter edit mode
    3. Simulate mouse press near a vertex (select it)
    4. Simulate mouse motion (drag vertex)
    5. Simulate mouse release (drop vertex)
    6. Verify vertex position changed
    7. Click Remesh & Optimize to use adjusted vertices
    8. Verify remesh uses adjusted vertex positions
    """
    window = window_with_equilibrium

    # Setup: Generate a mesh first
    window.left_tabs.setCurrentIndex(2)  # Mesh Editing tab
    window.psi_display_contour_checkbox.setChecked(True)
    window.generate_mesh_button.click()

    # Verify mesh is generated
    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None
    initial_vertices = window._mesh_vertices.copy()
    initial_vertex_count = len(initial_vertices)

    # Enter edit mode
    window.enter_edit_mode_button.setChecked(True)
    assert window.mesh_edit_handler.is_active() is True

    # Find an interior vertex (not on boundary) to drag
    # Skip boundary vertices by finding one farther from the boundary
    # Find centroid of all vertices as a good interior point
    centroid = initial_vertices.mean(axis=0)

    # Find vertex closest to centroid (should be interior)
    distances_to_centroid = np.linalg.norm(initial_vertices - centroid, axis=1)
    vertex_idx = np.argmin(distances_to_centroid)
    original_R, original_Z = initial_vertices[vertex_idx]

    # Simulate mouse press near the vertex (to select it)
    from matplotlib.backend_bases import MouseEvent

    # Create press event near the vertex
    press_event = MouseEvent(
        'button_press_event',
        window.canvas,
        original_R, original_Z,
        button=1,  # Left click
        key=None
    )
    press_event.inaxes = window.ax
    press_event.xdata = original_R
    press_event.ydata = original_Z

    # Call the mouse press handler
    window.on_mouse_press(press_event)

    # Verify vertex is selected (dragging state is now in handler)
    assert window.mesh_edit_handler.is_dragging() is True

    # Simulate mouse motion to drag the vertex
    new_R = original_R + 0.05  # Move 5 cm in R
    new_Z = original_Z + 0.05  # Move 5 cm in Z

    motion_event = MouseEvent(
        'motion_notify_event',
        window.canvas,
        new_R, new_Z,
        button=1,
        key=None
    )
    motion_event.inaxes = window.ax
    motion_event.xdata = new_R
    motion_event.ydata = new_Z

    # Call the mouse motion handler
    window.on_mouse_motion(motion_event)

    # Verify vertex position changed in mesh editor (get from handler)
    handler_vertices, _ = window.mesh_edit_handler.get_mesh()
    updated_vertex = handler_vertices[vertex_idx]
    assert not np.allclose(updated_vertex, [original_R, original_Z], atol=1e-6)
    assert np.allclose(updated_vertex, [new_R, new_Z], atol=1e-3)

    # Simulate mouse release to drop the vertex
    release_event = MouseEvent(
        'button_release_event',
        window.canvas,
        new_R, new_Z,
        button=1,
        key=None
    )
    release_event.inaxes = window.ax
    release_event.xdata = new_R
    release_event.ydata = new_Z

    # Call the mouse release handler
    window.on_mouse_release(release_event)

    # Verify dragging stopped
    assert window.mesh_edit_handler.is_dragging() is False

    # Exit edit mode
    window.enter_edit_mode_button.setChecked(False)
    assert window.mesh_edit_handler.is_active() is False

    # Get updated vertices from editor
    assert window._mesh_vertices is not None
    updated_vertices = window._mesh_vertices

    # Verify the vertex position persisted after exiting edit mode
    assert not np.allclose(updated_vertices[vertex_idx], [original_R, original_Z], atol=1e-6)
    assert np.allclose(updated_vertices[vertex_idx], [new_R, new_Z], atol=1e-3)

    # Click Remesh & Optimize to retriangulate with adjusted vertices
    window.remesh_optimize_button.click()

    # Verify remesh succeeded (mesh still exists with same or similar vertex count)
    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None
    # Vertex count should be similar (optimizer may add/remove a few)
    assert abs(len(window._mesh_vertices) - initial_vertex_count) < initial_vertex_count * 0.2


def test_manually_moved_vertex_stays_fixed_during_optimization(window_with_equilibrium):
    """
    Test that manually moved vertices stay fixed during 'Remesh & Optimize'.

    User story: If a user moves a vertex in edit mode, that vertex position
    must be preserved even after multiple 'Remesh & Optimize' operations.

    Test scenario:
    1. Generate mesh
    2. Enter edit mode
    3. Move an interior vertex
    4. Exit edit mode
    5. Click 'Remesh & Optimize'
    6. Verify moved vertex stayed at its new position
    7. Enter edit mode again
    8. Move a different vertex
    9. Exit edit mode
    10. Click 'Remesh & Optimize' again
    11. Verify BOTH vertices stayed at their moved positions
    """
    window = window_with_equilibrium

    # Setup: Generate a mesh first
    window.left_tabs.setCurrentIndex(2)
    window.psi_display_contour_checkbox.setChecked(True)
    window.generate_mesh_button.click()

    assert window._mesh_vertices is not None
    assert window._mesh_elements is not None

    initial_vertices = window._mesh_vertices.copy()

    # Find two interior vertices (not on boundary) to move
    centroid = initial_vertices.mean(axis=0)
    distances_to_centroid = np.linalg.norm(initial_vertices - centroid, axis=1)
    sorted_indices = np.argsort(distances_to_centroid)

    # Get first two interior vertices (closest to centroid, definitely not on boundary)
    vertex1_idx = sorted_indices[0]
    vertex2_idx = sorted_indices[1]

    # === FIRST EDIT CYCLE: Move vertex 1 ===
    window.enter_edit_mode_button.setChecked(True)
    assert window.mesh_edit_handler.is_active()

    # Move vertex 1 significantly (use handler's internal mesh_editor)
    old_pos1 = initial_vertices[vertex1_idx].copy()
    new_pos1 = old_pos1 + np.array([0.05, 0.05])  # Move 5cm in R and Z

    # Access the handler's internal mesh_editor to move the vertex
    handler_vertices, _ = window.mesh_edit_handler.get_mesh()
    from mesh_gui_project.ui.mesh_editor import MeshEditor
    # Get reference to handler's mesh editor
    handler_mesh_editor = window.mesh_edit_handler._mesh_editor
    handler_mesh_editor.move_vertex(vertex1_idx, new_pos1[0], new_pos1[1])

    # Exit edit mode (should save manually moved vertices)
    window.enter_edit_mode_button.setChecked(False)
    assert not window.mesh_edit_handler.is_active()

    # Verify vertex1 is tracked as manually moved
    assert vertex1_idx in window._manually_moved_vertex_indices

    # Get position after exiting edit mode
    position_after_edit1 = window._mesh_vertices[vertex1_idx].copy()

    # Verify vertex1 moved to new position
    assert np.linalg.norm(position_after_edit1 - new_pos1) < 0.001  # Within 1mm

    # === OPTIMIZE: Vertex 1 should stay fixed ===
    window.remesh_optimize_button.click()

    # Verify vertex1 stayed at its moved position (within 1mm tolerance)
    position_after_optimize1 = window._mesh_vertices[vertex1_idx].copy()
    distance_moved = np.linalg.norm(position_after_optimize1 - position_after_edit1)
    assert distance_moved < 0.001, f"Manually moved vertex1 moved {distance_moved:.6f}m during optimization (should be fixed)"

    # === SECOND EDIT CYCLE: Move vertex 2 ===
    window.enter_edit_mode_button.setChecked(True)

    # Move vertex 2 (use handler's internal mesh_editor)
    old_pos2 = initial_vertices[vertex2_idx].copy()
    new_pos2 = old_pos2 + np.array([0.06, -0.04])  # Move 6cm in R, -4cm in Z
    handler_mesh_editor = window.mesh_edit_handler._mesh_editor
    handler_mesh_editor.move_vertex(vertex2_idx, new_pos2[0], new_pos2[1])

    # Exit edit mode
    window.enter_edit_mode_button.setChecked(False)

    # Verify both vertices are tracked
    assert vertex1_idx in window._manually_moved_vertex_indices
    assert vertex2_idx in window._manually_moved_vertex_indices

    position_after_edit2_v1 = window._mesh_vertices[vertex1_idx].copy()
    position_after_edit2_v2 = window._mesh_vertices[vertex2_idx].copy()

    # Verify vertex2 moved to new position
    assert np.linalg.norm(position_after_edit2_v2 - new_pos2) < 0.001

    # === OPTIMIZE AGAIN: Both vertices should stay fixed ===
    window.remesh_optimize_button.click()

    # Verify both vertices stayed at their moved positions
    position_after_optimize2_v1 = window._mesh_vertices[vertex1_idx].copy()
    position_after_optimize2_v2 = window._mesh_vertices[vertex2_idx].copy()

    distance_moved_v1 = np.linalg.norm(position_after_optimize2_v1 - position_after_edit2_v1)
    distance_moved_v2 = np.linalg.norm(position_after_optimize2_v2 - position_after_edit2_v2)

    assert distance_moved_v1 < 0.001, f"Manually moved vertex1 moved {distance_moved_v1:.6f}m during second optimization"
    assert distance_moved_v2 < 0.001, f"Manually moved vertex2 moved {distance_moved_v2:.6f}m during second optimization"

    # Verify vertex1 is still at its position from first edit cycle
    total_distance_v1 = np.linalg.norm(position_after_optimize2_v1 - position_after_edit1)
    assert total_distance_v1 < 0.001, "Vertex1 drifted from its original moved position across multiple optimizations"
