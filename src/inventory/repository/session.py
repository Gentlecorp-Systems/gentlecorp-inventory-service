
"""Asynchrone Engine und die Factory für asynchrone Sessions konfigurieren."""

import logging
from typing import Final

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventory.config.db import (
    db_connect_args,
    db_dialect,
    db_log_statements,
    db_url,
    db_url_admin,
)

__all__ = ["Session", "dispose_connection_pool", "engine"]

engine: Final = (
    create_engine(
        db_url,
        connect_args=db_connect_args,
        echo=db_log_statements,
    )
    if db_dialect in {"postgresql", "mysql"}
    else create_engine(db_url, echo=db_log_statements)
)
"""
"Engine" für SQLAlchemy, um DB-Verbindungen und Sessions zu erstellen.
"""


def dispose_connection_pool() -> None:
    """SQLAlchemy-Engine vom Connection-Pool trennen."""
    logger.info("Connection-Pool fuer die DB wird getrennt.")
    engine.dispose()


engine_admin: Final = (
    create_engine(
        db_url_admin,
        connect_args=db_connect_args,
        echo=db_log_statements,
    )
    if db_dialect in {"postgresql", "mysql"}
    else create_engine(db_url_admin, echo=db_log_statements)
)
"""
"Engine" für SQLAlchemy mit Admin-Rechten zum Laden von CSV-Dateien.
"""

Session = sessionmaker(engine, autoflush=False)
"""
Factory für Sessions, um durch SQLAlchemy generierte SQL-Anweisungen in Transaktionen
abzusetzen.
"""

if db_dialect == "sqlite":
    # Default-Loglevel ist DEBUG
    logging.getLogger("aiosqlite").setLevel(level=logging.INFO)
