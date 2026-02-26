"""
Tests for DataInspectorPanel widget.
"""
import sys
import pytest
import numpy as np
from PyQt5.QtWidgets import QWidget, QScrollArea, QGroupBox, QApplication
from mesh_gui_project.ui.data_inspector_panel import DataInspectorPanel
from mesh_gui_project.core.equilibrium import EquilibriumData


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_data_inspector_panel_exists(qapp):
    """DataInspectorPanel should be a QWidget."""
    panel = DataInspectorPanel()
    assert isinstance(panel, QWidget)


def test_data_inspector_panel_has_update_data_method(qapp):
    """DataInspectorPanel should have update_data method."""
    panel = DataInspectorPanel()
    assert hasattr(panel, 'update_data')
    assert callable(panel.update_data)


def test_data_inspector_panel_has_scroll_area(qapp):
    """Panel should have a scroll area for smaller screens."""
    panel = DataInspectorPanel()
    # Find QScrollArea in children
    scroll_areas = panel.findChildren(QScrollArea)
    assert len(scroll_areas) > 0


def test_data_inspector_panel_has_grid_info_section(qapp):
    """Panel should have a section for grid information."""
    panel = DataInspectorPanel()
    # Find QGroupBox with title containing "Grid"
    group_boxes = panel.findChildren(QGroupBox)
    grid_boxes = [gb for gb in group_boxes if 'Grid' in gb.title()]
    assert len(grid_boxes) > 0


def test_data_inspector_panel_has_magnetic_axis_section(qapp):
    """Panel should have a section for magnetic axis information."""
    panel = DataInspectorPanel()
    group_boxes = panel.findChildren(QGroupBox)
    axis_boxes = [gb for gb in group_boxes if 'Axis' in gb.title() or 'O-point' in gb.title()]
    assert len(axis_boxes) > 0


def test_data_inspector_panel_has_boundary_section(qapp):
    """Panel should have a section for boundary information."""
    panel = DataInspectorPanel()
    group_boxes = panel.findChildren(QGroupBox)
    boundary_boxes = [gb for gb in group_boxes if 'Boundary' in gb.title()]
    assert len(boundary_boxes) > 0


def test_data_inspector_panel_has_data_quality_section(qapp):
    """Panel should have a section for data quality indicators."""
    panel = DataInspectorPanel()
    group_boxes = panel.findChildren(QGroupBox)
    quality_boxes = [gb for gb in group_boxes if 'Quality' in gb.title() or 'Data' in gb.title()]
    assert len(quality_boxes) > 0


def test_data_inspector_update_data_with_sample_equilibrium(qapp):
    """update_data should populate fields with EquilibriumData."""
    panel = DataInspectorPanel()

    # Create sample equilibrium data
    NR, NZ = 10, 10
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-1.0, 1.0, NZ)
    R_2d, Z_2d = np.meshgrid(R_grid, Z_grid, indexing='xy')
    psi_grid = (R_2d - 1.5)**2 + Z_2d**2

    data = {
        'NR': NR,
        'NZ': NZ,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 1.5,
        'Zmag': 0.0,
        'psi_axis': 0.5,
        'psi_boundary': 1.5,
        'boundary': np.array([[1.6, 0.0], [1.5, 0.1]]),
        'limiter': np.array([[1.0, -1.0], [2.0, -1.0], [2.0, 1.0]])
    }

    eq = EquilibriumData(data)

    # Should not raise exception
    panel.update_data(eq)


def test_data_inspector_handles_none_equilibrium(qapp):
    """update_data should handle None equilibrium gracefully."""
    panel = DataInspectorPanel()
    # Should not raise exception
    panel.update_data(None)


def test_data_inspector_handles_missing_boundary(qapp):
    """update_data should handle equilibrium without boundary curve."""
    panel = DataInspectorPanel()

    NR, NZ = 10, 10
    R_grid = np.linspace(1.0, 2.0, NR)
    Z_grid = np.linspace(-1.0, 1.0, NZ)
    psi_grid = np.zeros((NZ, NR))

    data = {
        'NR': NR,
        'NZ': NZ,
        'R_grid': R_grid,
        'Z_grid': Z_grid,
        'psi_grid': psi_grid,
        'Rmag': 1.5,
        'Zmag': 0.0,
        'psi_axis': 0.5,
        'psi_boundary': 1.5,
        'boundary': None,  # No boundary
        'limiter': None    # No limiter
    }

    eq = EquilibriumData(data)

    # Should not raise exception
    panel.update_data(eq)
