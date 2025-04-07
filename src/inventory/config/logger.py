
"""Konfiguration für Logging."""

from pathlib import Path
from typing import Final

from loguru import logger

__all__ = ["config_logger"]

LOG_FILE: Final = Path("log") / "app.log"


# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html
def config_logger() -> None:
    """Konfiguration für Logging."""
    logger.add(LOG_FILE, rotation="1 MB")
