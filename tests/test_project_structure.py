"""Test project structure and initialization."""
import os
from pathlib import Path


def test_project_directories_exist():
    """Test that all required project directories exist."""
    project_root = Path(__file__).parent.parent

    required_dirs = [
        'mesh_gui_project',
        'mesh_gui_project/ui',
        'mesh_gui_project/data',
        'mesh_gui_project/core',
        'mesh_gui_project/utils',
        'mesh_gui_project/resources',
        'tests',
    ]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
        assert full_path.is_dir(), f"{dir_path} exists but is not a directory"


def test_package_init_exists():
    """Test that mesh_gui_project has __init__.py."""
    project_root = Path(__file__).parent.parent
    init_file = project_root / 'mesh_gui_project' / '__init__.py'

    assert init_file.exists(), "mesh_gui_project/__init__.py does not exist"
    assert init_file.is_file(), "mesh_gui_project/__init__.py exists but is not a file"


def test_requirements_file_exists():
    """Test that requirements.txt exists and contains required packages."""
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / 'requirements.txt'

    assert requirements_file.exists(), "requirements.txt does not exist"
    assert requirements_file.is_file(), "requirements.txt exists but is not a file"

    # Verify essential packages are listed
    content = requirements_file.read_text()
    required_packages = ['PyQt5', 'numpy', 'scipy', 'matplotlib', 'meshio', 'gmsh']

    for package in required_packages:
        assert package in content, f"Required package {package} not found in requirements.txt"
