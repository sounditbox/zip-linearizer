"""Logging for Zip Linearizer."""

import logging
import sys
from typing import Optional


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Setup logging for application.

    Args:
        verbose: Enable verbose logging.
        quiet: Disable all messages except errors.
    """
    level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with specified name.

    Args:
        name: Logger name.

    Returns:
        Configured logger.
    """
    return logging.getLogger(name)

