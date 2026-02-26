"""Test settings persistence."""
import json
import tempfile
from pathlib import Path


def test_settings_module_exists():
    """Test that settings module can be imported."""
    from mesh_gui_project.utils import settings

    assert hasattr(settings, 'Settings'), \
        "settings module should have Settings class"


def test_settings_initialization():
    """Test that Settings can be initialized."""
    from mesh_gui_project.utils.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / 'test_config.json'
        s = Settings(config_file)

        assert s is not None, "Settings should be initialized"
        assert s.config_file == config_file, "Settings should store config file path"


def test_settings_get_default_value():
    """Test that Settings.get returns default value when key doesn't exist."""
    from mesh_gui_project.utils.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / 'test_config.json'
        s = Settings(config_file)

        value = s.get('nonexistent_key', default='default_value')
        assert value == 'default_value', "Should return default value for nonexistent key"


def test_settings_set_and_get():
    """Test that Settings can store and retrieve values."""
    from mesh_gui_project.utils.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / 'test_config.json'
        s = Settings(config_file)

        # Set a value
        s.set('last_path', '/home/user/test.geqdsk')
        s.set('preview_quality', 'high')
        s.set('window_width', 800)

        # Get the values back
        assert s.get('last_path') == '/home/user/test.geqdsk'
        assert s.get('preview_quality') == 'high'
        assert s.get('window_width') == 800


def test_settings_persistence():
    """Test that Settings persists data to disk and can be reloaded."""
    from mesh_gui_project.utils.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / 'test_config.json'

        # Create settings and save some values
        s1 = Settings(config_file)
        s1.set('last_path', '/home/user/test.geqdsk')
        s1.set('window_state', {'width': 1024, 'height': 768})
        s1.save()

        # Create new settings instance and verify values persist
        s2 = Settings(config_file)
        s2.load()

        assert s2.get('last_path') == '/home/user/test.geqdsk'
        assert s2.get('window_state') == {'width': 1024, 'height': 768}


def test_settings_handles_missing_file():
    """Test that Settings gracefully handles missing config file."""
    from mesh_gui_project.utils.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / 'nonexistent_config.json'
        s = Settings(config_file)

        # Should not raise error when loading from nonexistent file
        s.load()

        # Should return defaults
        assert s.get('some_key', 'default') == 'default'
