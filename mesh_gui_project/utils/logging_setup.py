"""Logging configuration for mesh_gui_project."""
import logging
import os


def setup_logging(name='mesh_gui_project', level=None):
    """
    Set up logging with configurable format and level.

    Args:
        name: Logger name (default: 'mesh_gui_project')
        level: Logging level. If None, reads from LOG_LEVEL env var or defaults to INFO.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Determine log level
    if level is None:
        level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, level_name, logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler with formatting
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
