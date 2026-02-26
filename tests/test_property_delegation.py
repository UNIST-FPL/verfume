"""Test property delegation optimization in MainWindow."""
import sys
import pytest
import numpy as np
from PyQt5.QtWidgets import QApplication
from mesh_gui_project.ui.main_window import MainWindow
from mesh_gui_project.core.equilibrium import EquilibriumData


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_canvas_property_delegation(qapp):
    """Test that ax property delegates to canvas_controller."""
    window = MainWindow()

    # The ax property should delegate to canvas_controller.ax
    assert window.ax is not None
    assert window.ax is window.canvas_controller.ax


def test_canvas_canvas_property_delegation(qapp):
    """Test that canvas property delegates to canvas_controller."""
    window = MainWindow()

    # The canvas property should delegate to canvas_controller.canvas
    assert window.canvas is not None
    assert window.canvas is window.canvas_controller.canvas


def test_equilibrium_property_delegation(qapp):
    """Test that equilibrium property delegates to app_state."""
    window = MainWindow()

    # Create test equilibrium
    test_data = {
        'NR': 10,
        'NZ': 10,
        'R_grid': np.linspace(1.0, 2.0, 10),
        'Z_grid': np.linspace(-1.0, 1.0, 10),
        'psi_grid': np.random.rand(10, 10),
        'Rmag': 1.5,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 1.0
    }
    eq = EquilibriumData(test_data)

    # Set via property
    window.equilibrium = eq

    # Verify delegation
    assert window.equilibrium is eq
    assert window.app_state.get_equilibrium() is eq


def test_mesh_vertices_property_delegation(qapp):
    """Test that _mesh_vertices delegates to app_state."""
    window = MainWindow()

    vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
    elements = np.array([[0, 1, 2]])

    # Set via property
    window._mesh_vertices = vertices
    window._mesh_elements = elements

    # Verify delegation
    assert np.array_equal(window._mesh_vertices, vertices)
    retrieved_vertices, _ = window.app_state.get_mesh()
    assert np.array_equal(retrieved_vertices, vertices)


def test_mesh_elements_property_delegation(qapp):
    """Test that _mesh_elements delegates to app_state."""
    window = MainWindow()

    vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
    elements = np.array([[0, 1, 2]])

    # Set via property
    window._mesh_vertices = vertices
    window._mesh_elements = elements

    # Verify delegation
    assert np.array_equal(window._mesh_elements, elements)
    _, retrieved_elements = window.app_state.get_mesh()
    assert np.array_equal(retrieved_elements, elements)


def test_psi_contour_plot_property_delegation(qapp):
    """Test that _psi_contour_plot delegates to psi_viz_controller."""
    window = MainWindow()

    # Initially None
    assert window._psi_contour_plot is None

    # Set via property
    test_value = "test_plot_object"
    window._psi_contour_plot = test_value

    # Verify delegation
    assert window._psi_contour_plot == test_value
    assert window.psi_viz_controller._psi_contour_plot == test_value


def test_added_psi_values_property_delegation(qapp):
    """Test that _added_psi_values delegates to app_state."""
    window = MainWindow()

    test_values = [0.2, 0.5, 0.8]

    # Set via property
    window._added_psi_values = test_values

    # Verify delegation
    assert window._added_psi_values == test_values
    assert window.app_state.get_added_psi_values() == test_values


def test_mesh_boundary_property_delegation(qapp):
    """Test that _mesh_boundary delegates to app_state."""
    window = MainWindow()

    boundary = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])

    # Set via property
    window._mesh_boundary = boundary

    # Verify delegation
    assert np.array_equal(window._mesh_boundary, boundary)
    assert np.array_equal(window.app_state.get_mesh_boundary(), boundary)


def test_property_delegation_maintains_backward_compatibility(qapp):
    """Test that all delegation properties maintain backward compatibility."""
    window = MainWindow()

    # This test ensures that code using the old property interface still works

    # Test equilibrium
    test_data = {
        'NR': 5,
        'NZ': 5,
        'R_grid': np.linspace(1.0, 2.0, 5),
        'Z_grid': np.linspace(-1.0, 1.0, 5),
        'psi_grid': np.random.rand(5, 5),
        'Rmag': 1.5,
        'Zmag': 0.0,
        'psi_axis': 0.0,
        'psi_boundary': 1.0
    }
    eq = EquilibriumData(test_data)
    window.equilibrium = eq
    assert window.equilibrium is eq

    # Test mesh data
    vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
    elements = np.array([[0, 1, 2]])
    window._mesh_vertices = vertices
    window._mesh_elements = elements
    assert np.array_equal(window._mesh_vertices, vertices)
    assert np.array_equal(window._mesh_elements, elements)

    # Test PSI values
    psi_values = [0.3, 0.6, 0.9]
    window._added_psi_values = psi_values
    assert window._added_psi_values == psi_values

    # Test canvas access
    assert window.ax is not None
    assert window.canvas is not None
