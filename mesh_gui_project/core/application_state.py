"""
ApplicationState - Centralized state management for the mesh GUI application.

This module provides a single source of truth for application state,
eliminating duplicate state across components and improving maintainability.

Following the Observer pattern for state change notifications.
"""
from typing import Optional, List, Tuple, Callable
import numpy as np
from mesh_gui_project.core.equilibrium import EquilibriumData


class ApplicationState:
    """
    Centralized application state management.

    Manages all application state including:
    - Equilibrium data
    - PSI values and levels
    - Mesh data
    - UI state

    Uses Observer pattern to notify components of state changes.
    """

    def __init__(self):
        """Initialize application state with default values."""
        # Equilibrium state
        self._equilibrium: Optional[EquilibriumData] = None
        self._equilibrium_file_path: Optional[str] = None

        # PSI state
        self._added_psi_values: List[float] = []
        self._disabled_psi_levels: List[float] = []

        # Mesh state
        self._mesh_vertices: Optional[np.ndarray] = None
        self._mesh_elements: Optional[np.ndarray] = None
        self._mesh_boundary: Optional[np.ndarray] = None

        # Critical points state
        self._critical_points_data: Optional[dict] = None

        # Observer pattern
        self._observers: List[Callable] = []

    # ===== Equilibrium Methods =====

    def set_equilibrium(self, equilibrium: Optional[EquilibriumData]) -> None:
        """
        Set the equilibrium data.

        Args:
            equilibrium: EquilibriumData instance or None to clear
        """
        self._equilibrium = equilibrium
        self._notify_observers("equilibrium_changed", equilibrium=equilibrium)

    def get_equilibrium(self) -> Optional[EquilibriumData]:
        """
        Get the current equilibrium data.

        Returns:
            EquilibriumData instance or None if not set
        """
        return self._equilibrium

    def set_equilibrium_file_path(self, file_path: Optional[str]) -> None:
        """Set the path to the equilibrium file."""
        self._equilibrium_file_path = file_path

    def get_equilibrium_file_path(self) -> Optional[str]:
        """Get the path to the equilibrium file."""
        return self._equilibrium_file_path

    # ===== PSI Methods =====

    def add_psi_value(self, value: float) -> None:
        """
        Add a PSI value to the added values list.

        Args:
            value: PSI value to add
        """
        if value not in self._added_psi_values:
            self._added_psi_values.append(value)
            self._notify_observers("psi_values_changed", added_psi_values=self._added_psi_values)

    def remove_psi_value(self, value: float) -> None:
        """
        Remove a PSI value from the added values list.

        Args:
            value: PSI value to remove
        """
        if value in self._added_psi_values:
            self._added_psi_values.remove(value)
            self._notify_observers("psi_values_changed", added_psi_values=self._added_psi_values)

    def get_added_psi_values(self) -> List[float]:
        """
        Get the list of manually added PSI values.

        Returns:
            List of PSI values
        """
        return self._added_psi_values.copy()

    def disable_psi_level(self, level: float) -> None:
        """
        Disable a PSI level from display.

        Args:
            level: PSI level to disable
        """
        if level not in self._disabled_psi_levels:
            self._disabled_psi_levels.append(level)
            self._notify_observers("psi_values_changed", disabled_psi_levels=self._disabled_psi_levels)

    def enable_psi_level(self, level: float) -> None:
        """
        Re-enable a previously disabled PSI level.

        Args:
            level: PSI level to enable
        """
        if level in self._disabled_psi_levels:
            self._disabled_psi_levels.remove(level)
            self._notify_observers("psi_values_changed", disabled_psi_levels=self._disabled_psi_levels)

    def get_disabled_psi_levels(self) -> List[float]:
        """
        Get the list of disabled PSI levels.

        Returns:
            List of disabled PSI levels
        """
        return self._disabled_psi_levels.copy()

    def clear_psi_values(self) -> None:
        """Clear all PSI values and disabled levels."""
        self._added_psi_values.clear()
        self._disabled_psi_levels.clear()
        self._notify_observers("psi_values_changed",
                              added_psi_values=self._added_psi_values,
                              disabled_psi_levels=self._disabled_psi_levels)

    # ===== Mesh Methods =====

    def set_mesh(self, vertices: Optional[np.ndarray], elements: Optional[np.ndarray]) -> None:
        """
        Set the mesh data.

        Args:
            vertices: Vertex coordinates array (N, 2) or None to clear
            elements: Element connectivity array (E, 3) or None to clear
        """
        self._mesh_vertices = vertices
        self._mesh_elements = elements
        self._notify_observers("mesh_changed", vertices=vertices, elements=elements)

    def get_mesh(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Get the current mesh data.

        Returns:
            Tuple of (vertices, elements) or (None, None) if not set
        """
        return self._mesh_vertices, self._mesh_elements

    def set_mesh_boundary(self, boundary: Optional[np.ndarray]) -> None:
        """
        Set the mesh boundary.

        Args:
            boundary: Boundary coordinates array (N, 2) or None to clear
        """
        self._mesh_boundary = boundary
        self._notify_observers("mesh_boundary_changed", boundary=boundary)

    def get_mesh_boundary(self) -> Optional[np.ndarray]:
        """
        Get the mesh boundary.

        Returns:
            Boundary coordinates array or None if not set
        """
        return self._mesh_boundary

    # ===== Critical Points Methods =====

    def set_critical_points(self, o_point: Optional[Tuple[float, float]],
                           x_points: List[Tuple[float, float]]) -> None:
        """
        Set critical points data.

        Args:
            o_point: O-point location (R, Z) or None if not found
            x_points: List of X-point locations [(R, Z), ...]
        """
        self._critical_points_data = {
            'o_point': o_point,
            'x_points': x_points
        }
        self._notify_observers("critical_points_changed",
                              o_point=o_point, x_points=x_points)

    def get_critical_points(self) -> Optional[dict]:
        """
        Get critical points data.

        Returns:
            Dictionary with 'o_point' and 'x_points' keys, or None if not set
        """
        return self._critical_points_data

    def clear_critical_points(self) -> None:
        """Clear critical points data."""
        self._critical_points_data = None
        self._notify_observers("critical_points_changed",
                              o_point=None, x_points=[])

    # ===== Observer Pattern =====

    def add_observer(self, observer: Callable) -> None:
        """
        Add an observer to be notified of state changes.

        Args:
            observer: Callable that takes (event_type: str, **kwargs)
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Callable) -> None:
        """
        Remove an observer.

        Args:
            observer: Observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, event_type: str, **kwargs) -> None:
        """
        Notify all observers of a state change.

        Args:
            event_type: Type of event (e.g., "equilibrium_changed")
            **kwargs: Additional event data
        """
        for observer in self._observers:
            try:
                observer(event_type, **kwargs)
            except Exception as e:
                # Don't let observer errors break state updates
                print(f"Observer error: {e}")
