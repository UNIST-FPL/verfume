"""Test logging configuration."""
import logging
import os
from pathlib import Path


def test_logging_setup_module_exists():
    """Test that logging_setup module can be imported."""
    from mesh_gui_project.utils import logging_setup

    assert hasattr(logging_setup, 'setup_logging'), \
        "logging_setup module should have setup_logging function"


def test_setup_logging_creates_logger():
    """Test that setup_logging creates and configures a logger."""
    from mesh_gui_project.utils.logging_setup import setup_logging

    logger = setup_logging()

    assert logger is not None, "setup_logging should return a logger"
    assert isinstance(logger, logging.Logger), "should return a logging.Logger instance"


def test_setup_logging_respects_level_from_env(monkeypatch):
    """Test that logging level can be controlled via environment variable."""
    from mesh_gui_project.utils.logging_setup import setup_logging

    # Set environment variable for log level
    monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
    logger = setup_logging()

    assert logger.level == logging.DEBUG, "Logger level should be DEBUG when LOG_LEVEL=DEBUG"

    # Test with different level
    monkeypatch.setenv('LOG_LEVEL', 'WARNING')
    logger = setup_logging()

    assert logger.level == logging.WARNING, "Logger level should be WARNING when LOG_LEVEL=WARNING"


def test_setup_logging_default_level():
    """Test that setup_logging has a sensible default level."""
    from mesh_gui_project.utils.logging_setup import setup_logging

    # Clear environment variable if set
    if 'LOG_LEVEL' in os.environ:
        del os.environ['LOG_LEVEL']

    logger = setup_logging()

    assert logger.level in [logging.INFO, logging.DEBUG, logging.WARNING], \
        "Logger should have a reasonable default level"
