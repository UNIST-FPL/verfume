"""
Tests for Meshing Tab GUI (renamed from Mesh Editing Tab in Phase 6).
"""
import sys
import pytest
from PyQt5.QtWidgets import QApplication, QTabWidget, QComboBox, QSpinBox, QPushButton, QLabel
from mesh_gui_project.ui.main_window import MainWindow


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_mesh_editing_tab_exists(qapp):
    """Test that Meshing tab exists in left panel TabWidget."""
    window = MainWindow()

    # Get left tabs
    left_tabs = window.left_tabs

    assert left_tabs is not None
    assert isinstance(left_tabs, QTabWidget)

    # Check that "Meshing" tab exists (renamed from "Mesh Editing")
    tab_names = [left_tabs.tabText(i) for i in range(left_tabs.count())]
    assert "Meshing" in tab_names


def test_visualization_mode_dropdown_exists(qapp):
    """Test that tab contains visualization mode dropdown."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    assert tab_index >= 0, "Meshing tab not found"

    # Get the tab widget
    mesh_tab = left_tabs.widget(tab_index)

    # Find visualization mode dropdown
    # Should have a QComboBox with items: "Wireframe", "Quality: Aspect Ratio", "Quality: Min Angle", "Quality: Area"
    visualization_combo = None
    for child in mesh_tab.findChildren(QComboBox):
        # Check if this is the visualization mode combo by checking its items
        items = [child.itemText(i) for i in range(child.count())]
        if "Wireframe" in items:
            visualization_combo = child
            break

    assert visualization_combo is not None, "Visualization mode dropdown not found"
    assert isinstance(visualization_combo, QComboBox)

    # Check that it has all required items
    items = [visualization_combo.itemText(i) for i in range(visualization_combo.count())]
    assert "Wireframe" in items
    assert "Quality: Aspect Ratio" in items
    assert "Quality: Min Angle" in items
    assert "Quality: Area" in items


def test_toroidal_steps_input_exists(qapp):
    """Test that tab contains toroidal steps input field."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    mesh_tab = left_tabs.widget(tab_index)

    # Find toroidal steps spin box
    toroidal_spinbox = None
    for child in mesh_tab.findChildren(QSpinBox):
        # Check if this is the toroidal steps spinbox
        # It should have a default value of 64
        if child.value() == 64:
            toroidal_spinbox = child
            break

    assert toroidal_spinbox is not None, "Toroidal steps input not found"
    assert isinstance(toroidal_spinbox, QSpinBox)
    assert toroidal_spinbox.value() == 64  # Default value


def test_generate_mesh_button_exists(qapp):
    """Test that tab contains Generate Mesh button."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    mesh_tab = left_tabs.widget(tab_index)

    # Find Generate Mesh button
    generate_button = None
    for child in mesh_tab.findChildren(QPushButton):
        if "Generate Mesh" in child.text():
            generate_button = child
            break

    assert generate_button is not None, "Generate Mesh button not found"
    assert isinstance(generate_button, QPushButton)


def test_enter_edit_mode_button_exists(qapp):
    """Test that tab contains Enter Edit Mode button."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    mesh_tab = left_tabs.widget(tab_index)

    # Find Enter Edit Mode button
    edit_button = None
    for child in mesh_tab.findChildren(QPushButton):
        if "Edit Mode" in child.text():
            edit_button = child
            break

    assert edit_button is not None, "Enter Edit Mode button not found"
    assert isinstance(edit_button, QPushButton)
    assert edit_button.isCheckable(), "Enter Edit Mode button should be checkable"


def test_remesh_optimize_button_exists(qapp):
    """Test that tab contains Remesh & Optimize button."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    mesh_tab = left_tabs.widget(tab_index)

    # Find Remesh & Optimize button
    remesh_button = None
    for child in mesh_tab.findChildren(QPushButton):
        if "Remesh" in child.text() and "Optimize" in child.text():
            remesh_button = child
            break

    assert remesh_button is not None, "Remesh & Optimize button not found"
    assert isinstance(remesh_button, QPushButton)


def test_export_mesh_button_exists(qapp):
    """Test that tab contains Export Mesh button."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    mesh_tab = left_tabs.widget(tab_index)

    # Find Export Mesh button
    export_button = None
    for child in mesh_tab.findChildren(QPushButton):
        if "Export" in child.text() and "Mesh" in child.text():
            export_button = child
            break

    assert export_button is not None, "Export Mesh button not found"
    assert isinstance(export_button, QPushButton)


def test_mesh_statistics_display_exists(qapp):
    """Test that tab displays mesh statistics."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    mesh_tab = left_tabs.widget(tab_index)

    # Find statistics labels
    # Should have labels for: vertex count, triangle count, quality metrics
    labels = mesh_tab.findChildren(QLabel)
    label_texts = [label.text().lower() for label in labels]

    # Check for statistics-related labels
    has_vertex_label = any("vertex" in text or "vertices" in text or "nodes" in text for text in label_texts)
    has_triangle_label = any("triangle" in text or "element" in text for text in label_texts)

    assert has_vertex_label or has_triangle_label, "Mesh statistics labels not found"


def test_mesh_size_input_exists(qapp):
    """Test that tab contains mesh size input field with default value 0.05."""
    window = MainWindow()

    # Find the Meshing tab
    left_tabs = window.left_tabs
    tab_index = -1
    for i in range(left_tabs.count()):
        if left_tabs.tabText(i) == "Meshing":
            tab_index = i
            break

    mesh_tab = left_tabs.widget(tab_index)

    # Find mesh size spinbox (should be QDoubleSpinBox)
    from PyQt5.QtWidgets import QDoubleSpinBox
    mesh_size_spinbox = None
    for child in mesh_tab.findChildren(QDoubleSpinBox):
        # Check if this is the mesh size spinbox (default value 0.05)
        if abs(child.value() - 0.05) < 1e-6:
            mesh_size_spinbox = child
            break

    assert mesh_size_spinbox is not None, "Mesh size input not found"
    assert isinstance(mesh_size_spinbox, QDoubleSpinBox)
    assert abs(mesh_size_spinbox.value() - 0.05) < 1e-6  # Default value
