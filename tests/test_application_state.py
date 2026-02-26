"""
Tests for ApplicationState - Centralized state management.

Following TDD: Write tests first (RED phase).
"""
import pytest
import numpy as np
from mesh_gui_project.core.application_state import ApplicationState
from mesh_gui_project.core.equilibrium import EquilibriumData


class TestApplicationStateEquilibrium:
    """Test equilibrium state management."""

    def test_application_state_can_be_created(self):
        """ApplicationState should be instantiable."""
        state = ApplicationState()
        assert state is not None

    def test_initial_equilibrium_is_none(self):
        """Initial equilibrium should be None."""
        state = ApplicationState()
        assert state.get_equilibrium() is None

    def test_can_set_and_get_equilibrium(self):
        """Should be able to set and retrieve equilibrium data."""
        state = ApplicationState()
        eq_data = EquilibriumData({
            'NR': 2,
            'NZ': 2,
            'R_grid': np.array([1.0, 2.0]),
            'Z_grid': np.array([0.0, 1.0]),
            'psi_grid': np.array([[1.0, 2.0], [3.0, 4.0]]),
            'psi_axis': 1.0,
            'psi_boundary': 4.0
        })

        state.set_equilibrium(eq_data)
        retrieved = state.get_equilibrium()

        assert retrieved is not None
        assert np.array_equal(retrieved.R_grid, eq_data.R_grid)
        assert np.array_equal(retrieved.Z_grid, eq_data.Z_grid)
        assert np.array_equal(retrieved.psi_grid, eq_data.psi_grid)

    def test_can_clear_equilibrium(self):
        """Should be able to clear equilibrium data."""
        state = ApplicationState()
        eq_data = EquilibriumData({
            'NR': 1,
            'NZ': 1,
            'R_grid': np.array([1.0]),
            'Z_grid': np.array([0.0]),
            'psi_grid': np.array([[1.0]]),
            'psi_axis': 1.0,
            'psi_boundary': 2.0
        })

        state.set_equilibrium(eq_data)
        state.set_equilibrium(None)

        assert state.get_equilibrium() is None


class TestApplicationStatePsi:
    """Test PSI values state management."""

    def test_initial_psi_values_empty(self):
        """Initial added PSI values should be empty list."""
        state = ApplicationState()
        assert state.get_added_psi_values() == []

    def test_can_add_psi_value(self):
        """Should be able to add a PSI value."""
        state = ApplicationState()
        state.add_psi_value(0.5)

        assert 0.5 in state.get_added_psi_values()

    def test_can_add_multiple_psi_values(self):
        """Should be able to add multiple PSI values."""
        state = ApplicationState()
        state.add_psi_value(0.5)
        state.add_psi_value(0.7)
        state.add_psi_value(0.9)

        values = state.get_added_psi_values()
        assert len(values) == 3
        assert 0.5 in values
        assert 0.7 in values
        assert 0.9 in values

    def test_can_remove_psi_value(self):
        """Should be able to remove a PSI value."""
        state = ApplicationState()
        state.add_psi_value(0.5)
        state.add_psi_value(0.7)

        state.remove_psi_value(0.5)

        values = state.get_added_psi_values()
        assert 0.5 not in values
        assert 0.7 in values

    def test_initial_disabled_psi_levels_empty(self):
        """Initial disabled PSI levels should be empty list."""
        state = ApplicationState()
        assert state.get_disabled_psi_levels() == []

    def test_can_disable_psi_level(self):
        """Should be able to disable a PSI level."""
        state = ApplicationState()
        state.disable_psi_level(0.5)

        assert 0.5 in state.get_disabled_psi_levels()

    def test_can_enable_psi_level(self):
        """Should be able to re-enable a disabled PSI level."""
        state = ApplicationState()
        state.disable_psi_level(0.5)
        state.enable_psi_level(0.5)

        assert 0.5 not in state.get_disabled_psi_levels()

    def test_clear_all_psi_values(self):
        """Should be able to clear all PSI values."""
        state = ApplicationState()
        state.add_psi_value(0.5)
        state.add_psi_value(0.7)
        state.disable_psi_level(0.3)

        state.clear_psi_values()

        assert state.get_added_psi_values() == []
        assert state.get_disabled_psi_levels() == []


class TestApplicationStateMesh:
    """Test mesh state management."""

    def test_initial_mesh_is_none(self):
        """Initial mesh should be None."""
        state = ApplicationState()
        vertices, elements = state.get_mesh()
        assert vertices is None
        assert elements is None

    def test_can_set_and_get_mesh(self):
        """Should be able to set and retrieve mesh data."""
        state = ApplicationState()
        vertices = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
        elements = np.array([[0, 1, 2]])

        state.set_mesh(vertices, elements)
        ret_vertices, ret_elements = state.get_mesh()

        assert np.array_equal(ret_vertices, vertices)
        assert np.array_equal(ret_elements, elements)

    def test_can_clear_mesh(self):
        """Should be able to clear mesh data."""
        state = ApplicationState()
        vertices = np.array([[0.0, 0.0], [1.0, 0.0]])
        elements = np.array([[0, 1, 2]])

        state.set_mesh(vertices, elements)
        state.set_mesh(None, None)

        ret_vertices, ret_elements = state.get_mesh()
        assert ret_vertices is None
        assert ret_elements is None

    def test_initial_boundary_is_none(self):
        """Initial mesh boundary should be None."""
        state = ApplicationState()
        assert state.get_mesh_boundary() is None

    def test_can_set_and_get_mesh_boundary(self):
        """Should be able to set and retrieve mesh boundary."""
        state = ApplicationState()
        boundary = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])

        state.set_mesh_boundary(boundary)

        assert np.array_equal(state.get_mesh_boundary(), boundary)


class TestApplicationStateObserver:
    """Test observer pattern for state changes."""

    def test_can_add_observer(self):
        """Should be able to add an observer."""
        state = ApplicationState()
        observer_called = []

        def observer(event_type, **kwargs):
            observer_called.append((event_type, kwargs))

        state.add_observer(observer)
        state.set_equilibrium(None)

        # Observer should have been called
        assert len(observer_called) > 0

    def test_equilibrium_change_notifies_observers(self):
        """Setting equilibrium should notify observers."""
        state = ApplicationState()
        events = []

        def observer(event_type, **kwargs):
            events.append(event_type)

        state.add_observer(observer)

        eq_data = EquilibriumData({
            'NR': 1,
            'NZ': 1,
            'R_grid': np.array([1.0]),
            'Z_grid': np.array([0.0]),
            'psi_grid': np.array([[1.0]]),
            'psi_axis': 1.0,
            'psi_boundary': 2.0
        })
        state.set_equilibrium(eq_data)

        assert "equilibrium_changed" in events

    def test_psi_change_notifies_observers(self):
        """Adding/removing PSI values should notify observers."""
        state = ApplicationState()
        events = []

        def observer(event_type, **kwargs):
            events.append(event_type)

        state.add_observer(observer)
        state.add_psi_value(0.5)

        assert "psi_values_changed" in events

    def test_mesh_change_notifies_observers(self):
        """Setting mesh should notify observers."""
        state = ApplicationState()
        events = []

        def observer(event_type, **kwargs):
            events.append(event_type)

        state.add_observer(observer)

        vertices = np.array([[0.0, 0.0]])
        elements = np.array([[0, 1, 2]])
        state.set_mesh(vertices, elements)

        assert "mesh_changed" in events

    def test_multiple_observers_all_notified(self):
        """Multiple observers should all be notified."""
        state = ApplicationState()
        observer1_events = []
        observer2_events = []

        def observer1(event_type, **kwargs):
            observer1_events.append(event_type)

        def observer2(event_type, **kwargs):
            observer2_events.append(event_type)

        state.add_observer(observer1)
        state.add_observer(observer2)

        state.add_psi_value(0.5)

        assert "psi_values_changed" in observer1_events
        assert "psi_values_changed" in observer2_events


class TestApplicationStateCriticalPoints:
    """Test critical points state management."""

    def test_initial_critical_points_is_none(self):
        """Initial critical points should be None."""
        state = ApplicationState()
        assert state.get_critical_points() is None

    def test_can_set_and_get_critical_points(self):
        """Should be able to set and retrieve critical points data."""
        state = ApplicationState()
        o_point = (1.85, 0.0)
        x_points = [(1.2, -0.45), (1.2, 0.45)]

        state.set_critical_points(o_point, x_points)
        data = state.get_critical_points()

        assert data is not None
        assert data['o_point'] == o_point
        assert data['x_points'] == x_points

    def test_can_set_critical_points_with_none_o_point(self):
        """Should handle None O-point (when not found)."""
        state = ApplicationState()
        x_points = [(1.2, -0.45)]

        state.set_critical_points(None, x_points)
        data = state.get_critical_points()

        assert data is not None
        assert data['o_point'] is None
        assert data['x_points'] == x_points

    def test_can_set_critical_points_with_empty_x_points(self):
        """Should handle empty X-points list (when not found)."""
        state = ApplicationState()
        o_point = (1.85, 0.0)

        state.set_critical_points(o_point, [])
        data = state.get_critical_points()

        assert data is not None
        assert data['o_point'] == o_point
        assert data['x_points'] == []

    def test_can_clear_critical_points(self):
        """Should be able to clear critical points data."""
        state = ApplicationState()
        state.set_critical_points((1.85, 0.0), [(1.2, -0.45)])

        state.clear_critical_points()

        assert state.get_critical_points() is None

    def test_setting_critical_points_notifies_observers(self):
        """Setting critical points should notify observers."""
        state = ApplicationState()
        events = []

        def observer(event_type, **kwargs):
            events.append((event_type, kwargs))

        state.add_observer(observer)

        o_point = (1.85, 0.0)
        x_points = [(1.2, -0.45)]
        state.set_critical_points(o_point, x_points)

        assert len(events) == 1
        event_type, kwargs = events[0]
        assert event_type == "critical_points_changed"
        assert kwargs['o_point'] == o_point
        assert kwargs['x_points'] == x_points

    def test_clearing_critical_points_notifies_observers(self):
        """Clearing critical points should notify observers."""
        state = ApplicationState()
        events = []

        def observer(event_type, **kwargs):
            events.append((event_type, kwargs))

        state.add_observer(observer)
        state.set_critical_points((1.85, 0.0), [(1.2, -0.45)])
        events.clear()  # Clear the set event

        state.clear_critical_points()

        assert len(events) == 1
        event_type, kwargs = events[0]
        assert event_type == "critical_points_changed"
        assert kwargs['o_point'] is None
        assert kwargs['x_points'] == []
