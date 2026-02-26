"""Settings persistence for mesh_gui_project."""
import json
from pathlib import Path
from typing import Any, Optional


class Settings:
    """
    Manages application settings with file persistence.

    Stores settings like last used paths, window state, and preview quality.
    """

    def __init__(self, config_file: Path = None):
        """
        Initialize settings.

        Args:
            config_file: Path to the JSON config file. If None, uses default location.
        """
        if config_file is None:
            # Default to user's home directory
            config_dir = Path.home() / '.mesh_gui_project'
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / 'settings.json'

        self.config_file = Path(config_file)
        self._data = {}

        # Try to load existing settings
        if self.config_file.exists():
            self.load()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key
            default: Default value if key doesn't exist

        Returns:
            The setting value or default
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value (must be JSON-serializable)
        """
        self._data[key] = value

    def save(self) -> None:
        """Save settings to disk."""
        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Write settings as JSON
        with open(self.config_file, 'w') as f:
            json.dump(self._data, f, indent=2)

    def load(self) -> None:
        """Load settings from disk."""
        if not self.config_file.exists():
            # No config file yet, start with empty settings
            self._data = {}
            return

        try:
            with open(self.config_file, 'r') as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # If file is corrupted, start fresh
            self._data = {}
