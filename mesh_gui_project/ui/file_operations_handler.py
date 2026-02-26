"""
File Operations Handler for managing file I/O operations.

Extracted from MainWindow as part of Phase 3 refactoring.
Handles gEQDSK loading, mesh saving, PSI contour saving, and recent files management.
"""
from typing import Optional, List, Tuple
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import json
import meshio
import numpy as np


class FileOperationsHandler:
    """
    Handles file operations for the application.

    Responsibilities:
    - Show file dialogs for opening/saving
    - Load gEQDSK files (parsing only)
    - Save mesh files to various formats
    - Save PSI contour data
    - Manage recent files list
    """

    def __init__(self, parent_window, settings_manager):
        """
        Initialize file operations handler.

        Args:
            parent_window: Parent QWidget for dialogs
            settings_manager: Settings manager for recent files
        """
        self.parent_window = parent_window
        self.settings_manager = settings_manager
        self.MAX_RECENT_FILES = 10

    def open_geqdsk_dialog(self) -> Optional[str]:
        """
        Show file dialog to open a gEQDSK file.

        Returns:
            Selected file path, or None if cancelled
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent_window,
            "Open gEQDSK File",
            self.settings_manager.get('last_directory', '') if self.settings_manager else '',
            "gEQDSK Files (*.geqdsk *.eqdsk *.g);;All Files (*)"
        )

        if file_path:
            # Save directory for next time
            if self.settings_manager:
                import os
                self.settings_manager.set('last_directory', os.path.dirname(file_path))
            return file_path

        return None

    def load_geqdsk(self, file_path: str):
        """
        Load and parse a gEQDSK equilibrium file.

        Args:
            file_path: Path to the gEQDSK file

        Returns:
            EquilibriumData object, or None if loading failed

        Note: This method only handles parsing. The caller is responsible
        for UI updates, interpolator attachment, and visualization.
        """
        try:
            from mesh_gui_project.data.geqdsk_parser import parse_geqdsk
            from mesh_gui_project.core.equilibrium import EquilibriumData

            # Parse the gEQDSK file
            eq_data = parse_geqdsk(file_path)

            # Create equilibrium object
            equilibrium = EquilibriumData(eq_data)

            return equilibrium

        except Exception as e:
            # Show error dialog
            QMessageBox.critical(
                self.parent_window,
                "Load Failed",
                f"Failed to load gEQDSK file: {str(e)}"
            )
            return None

    def save_mesh(self, vertices: np.ndarray, elements: np.ndarray,
                  file_path: Optional[str] = None) -> bool:
        """
        Save mesh to file.

        Args:
            vertices: Mesh vertices array (N, 2)
            elements: Mesh elements array (E, 3)
            file_path: Optional file path. If None, show save dialog.

        Returns:
            True if save successful, False otherwise
        """
        # Show save dialog if no path provided
        if file_path is None:
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self.parent_window,
                "Save Mesh",
                self.settings_manager.get('last_directory', '') if self.settings_manager else '',
                "Gmsh Files (*.msh);;VTK Files (*.vtk);;SCOREC SMB Files (*.smb);;SCOREC DMG Files (*.dmg);;All Files (*)"
            )

            if not file_path:
                return False  # User cancelled

            # Add appropriate extension if user didn't provide one
            # Determine extension from selected filter
            import re
            has_extension = (
                file_path.endswith('.msh') or
                file_path.endswith('.vtk') or
                file_path.endswith('.dmg') or
                file_path.endswith('.smb') or  # Recognize .smb even without partition number
                re.search(r'\d+\.smb$', file_path)  # Also recognize partition-numbered .smb
            )

            if not has_extension:
                # Extract extension from filter
                if '*.smb' in selected_filter:
                    # Add .smb extension - partition number validation will prompt user
                    file_path += '.smb'
                elif '*.dmg' in selected_filter:
                    file_path += '.dmg'
                elif '*.msh' in selected_filter:
                    file_path += '.msh'
                elif '*.vtk' in selected_filter:
                    file_path += '.vtk'
                else:
                    # Default to .vtk if no filter matched
                    file_path += '.vtk'

        try:
            # Determine format from extension
            import re

            if file_path.endswith('.vtk'):
                self._save_mesh_vtk(vertices, elements, file_path)
            elif file_path.endswith('.msh'):
                self._save_mesh_gmsh(vertices, elements, file_path)
            elif file_path.endswith('.smb') or re.search(r'\d+\.smb$', file_path):
                # Match SMB files (with or without partition number)
                # _save_mesh_smb will handle adding partition number if needed
                self._save_mesh_smb(vertices, elements, file_path)
            elif file_path.endswith('.dmg'):
                self._save_mesh_dmg(vertices, elements, file_path)
            else:
                # Should not reach here after adding extension above
                # but handle it gracefully with a better error message
                raise ValueError(
                    f"Unsupported file format. File must end with .msh, .vtk, .smb, or .dmg\n"
                    f"Got: {file_path}"
                )

            return True

        except Exception as e:
            QMessageBox.critical(
                self.parent_window,
                "Save Failed",
                f"Failed to save mesh: {str(e)}"
            )
            return False

    def _save_mesh_vtk(self, vertices: np.ndarray, elements: np.ndarray, file_path: str):
        """Save mesh in VTK format using meshio."""
        # Convert 2D vertices to 3D (Z coordinate = 0)
        vertices_3d = np.column_stack([vertices, np.zeros(len(vertices))])

        # Create meshio mesh
        cells = [("triangle", elements)]
        mesh = meshio.Mesh(vertices_3d, cells)

        # Write to file
        meshio.write(file_path, mesh)

    def _save_mesh_gmsh(self, vertices: np.ndarray, elements: np.ndarray, file_path: str):
        """Save mesh in Gmsh format using meshio."""
        # Convert 2D vertices to 3D
        vertices_3d = np.column_stack([vertices, np.zeros(len(vertices))])

        # Create meshio mesh
        cells = [("triangle", elements)]
        mesh = meshio.Mesh(vertices_3d, cells)

        # Write to file
        meshio.write(file_path, mesh, file_format="gmsh")

    def _save_mesh_smb(self, vertices: np.ndarray, elements: np.ndarray, file_path: str):
        """Save mesh in SCOREC .smb format (exports both .smb and .dmg)."""
        from mesh_gui_project.core.exporter import export_mesh_to_scorec
        import os
        import re

        # Check if filename has partition number before .smb extension
        # Valid: mesh0.smb, mesh1.smb, etc.
        # Invalid: mesh.smb
        if not re.search(r'\d+\.smb$', file_path):
            # No partition number found - ask user if they want to add it
            response = QMessageBox.question(
                self.parent_window,
                "SCOREC SMB Partition Number",
                "SCOREC .smb files require a partition number before the extension.\n\n"
                "Example: 'mesh0.smb' instead of 'mesh.smb'\n\n"
                "The partition number (usually 0 for single-partition meshes) is required by PUMI.\n\n"
                f"Current filename: {os.path.basename(file_path)}\n"
                f"Suggested filename: {os.path.basename(file_path.replace('.smb', '0.smb'))}\n\n"
                "Do you want to add '0' before '.smb'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes  # Default to Yes
            )

            if response == QMessageBox.Yes:
                # Add partition number 0
                file_path = file_path.replace('.smb', '0.smb')
            else:
                # User chose not to add partition number - save as is
                # (This may cause PUMI to fail loading, but respect user choice)
                pass

        # Generate .dmg path from .smb path
        dmg_path = file_path.replace('.smb', '.dmg')
        export_mesh_to_scorec(vertices, elements, dmg_path, file_path)

    def _save_mesh_dmg(self, vertices: np.ndarray, elements: np.ndarray, file_path: str):
        """Save geometric model in SCOREC .dmg format only."""
        from mesh_gui_project.core.exporter import export_mesh_to_dmg
        export_mesh_to_dmg(vertices, elements, file_path)

    def save_psi_contours(self, contour_data: List[dict],
                         file_path: Optional[str] = None) -> bool:
        """
        Save PSI contour data to JSON file.

        Args:
            contour_data: List of contour dictionaries with psi_n, psi, source
            file_path: Optional file path. If None, show save dialog.

        Returns:
            True if save successful, False otherwise
        """
        # Show save dialog if no path provided
        if file_path is None:
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent_window,
                "Save PSI Contours",
                self.settings_manager.get('last_directory', '') if self.settings_manager else '',
                "JSON Files (*.json);;All Files (*)"
            )

            if not file_path:
                return False  # User cancelled

        try:
            with open(file_path, 'w') as f:
                json.dump(contour_data, f, indent=2)

            return True

        except Exception as e:
            QMessageBox.critical(
                self.parent_window,
                "Save Failed",
                f"Failed to save PSI contours: {str(e)}"
            )
            return False

    def add_to_recent_files(self, file_path: str):
        """
        Add a file path to the recent files list.

        Args:
            file_path: Path to add to recent files

        Updates settings with the new recent files list.
        """
        if not self.settings_manager:
            return

        # Get current recent files list
        recent_files = self.settings_manager.get('recent_files', [])

        # Remove the path if it already exists (to move it to the top)
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to the beginning of the list
        recent_files.insert(0, file_path)

        # Limit to max recent files
        if len(recent_files) > self.MAX_RECENT_FILES:
            recent_files = recent_files[:self.MAX_RECENT_FILES]

        # Save back to settings
        self.settings_manager.set('recent_files', recent_files)

    def get_recent_files(self) -> List[str]:
        """
        Get list of recent files.

        Returns:
            List of recent file paths
        """
        if not self.settings_manager:
            return []

        return self.settings_manager.get('recent_files', [])

    def clear_recent_files(self):
        """Clear the recent files list."""
        if self.settings_manager:
            self.settings_manager.set('recent_files', [])
