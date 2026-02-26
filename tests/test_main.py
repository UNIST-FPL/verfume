"""Test main entry point."""
import sys
from pathlib import Path


def test_main_file_exists():
    """Test that main.py exists in the project root."""
    project_root = Path(__file__).parent.parent
    main_file = project_root / 'main.py'

    assert main_file.exists(), "main.py does not exist"
    assert main_file.is_file(), "main.py exists but is not a file"


def test_main_has_main_function():
    """Test that main.py has a main() function."""
    # Import the main module
    import main

    assert hasattr(main, 'main'), "main.py should have a main() function"
    assert callable(main.main), "main.main should be callable"


def test_main_module_can_be_imported():
    """Test that main module can be imported without errors."""
    try:
        import main
        assert True, "main module imported successfully"
    except ImportError as e:
        assert False, f"Failed to import main module: {e}"


def test_main_imports_qapplication():
    """Test that main.py imports QApplication."""
    import main

    # Check that the module uses QApplication
    source = Path(__file__).parent.parent / 'main.py'
    content = source.read_text()

    assert 'QApplication' in content, "main.py should import QApplication"
    assert 'QMessageBox' in content, "main.py should import QMessageBox for error dialogs"


def test_main_imports_mainwindow():
    """Test that main.py imports MainWindow."""
    import main

    source = Path(__file__).parent.parent / 'main.py'
    content = source.read_text()

    assert 'MainWindow' in content, "main.py should import MainWindow"


def test_main_has_error_handling():
    """Test that main() function has exception handling."""
    source = Path(__file__).parent.parent / 'main.py'
    content = source.read_text()

    assert 'try:' in content, "main() should have try-except block"
    assert 'except' in content, "main() should have exception handling"
    assert 'QMessageBox' in content, "main() should use QMessageBox for error dialogs"
