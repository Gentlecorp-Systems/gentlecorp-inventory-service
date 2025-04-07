"""Neuladen der DB im Modus DEV."""

import sqlite3  # noqa: F401
from importlib.resources import files
from importlib.resources.abc import Traversable
from re import match
from string import Template
from typing import Final

from loguru import logger
from sqlalchemy import Connection, text

from inventory.config.config import resources_path
from inventory.config.db import db_url
from inventory.config.dev_modus import dev
from inventory.repository import engine, engine_admin

__all__ = ["db_populate"]


utf8: Final = "utf-8"
# https://docs.python.org/3/library/importlib.resources.htm
# https://docs.python.org/3/whatsnew/3.9.html#importlib
_db_traversable: Final[Traversable] = files(resources_path)


# DB-Migration ggf. durch Alembic https://alembic.sqlalchemy.org
def db_populate() -> None:
    """DB durch einzelne SQL-Anweisungen als Prepared Statement neu laden."""
    if not dev:
        return
    logger.warning(">>> Die DB wird neu geladen: {} <<<", db_url)

    connection: Connection
    with engine.connect() as connection:
        db_dialect: Final = connection.dialect.name
        dialect_path: Final = _db_traversable / db_dialect
        with open(file=str(dialect_path / "drop.sql"), encoding=utf8) as drop_sql:
            zeilen_drop: Final = _remove_comment(drop_sql.readlines())
            drop_statements: Final = _build_sql_statements(zeilen_drop)
            for stmt in drop_statements:
                connection.execute(text(stmt))
        with open(file=str(dialect_path / "create.sql"), encoding=utf8) as create_sql:
            zeilen_create: Final = _remove_comment(create_sql.readlines())
            create_statements: Final = _build_sql_statements(zeilen_create)
            for stmt in create_statements:
                connection.execute(text(stmt))
        connection.commit()
        # SQLite kann CSV-Dateien nur von der Kommandozeile laden
        # https://sqlite.org/cli.html#importing_files_as_csv_or_other_formats
        if db_dialect == "sqlite":
            _load_sqlite(dialect_path, connection)
            connection.commit()
    engine.dispose()

    if db_dialect != "sqlite":
        _load_csv_files(db_dialect=db_dialect)
    logger.warning(">>> Die DB wurde neu geladen <<<")


def _remove_comment(zeilen: list[str]) -> list[str]:
    """SQL-Kommentare und Leerzeilen entfernen."""
    # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
    return [zeile for zeile in zeilen if not match(r"^ *--", zeile) and zeile != "\n"]


def _build_sql_statements(zeilen: list[str]) -> list[str]:
    """Zeilen mit SQL-Anweisungen zu einer Zeile zusammenfassen."""
    statements: list[str] = []
    sql: str = ""
    anzahl: Final = len(zeilen)
    for i in range(anzahl):
        zeile = zeilen[i]
        sql += zeile.replace("\n", " ")
        if zeile.endswith(";\n"):
            statements.append(sql)
            sql = ""
    return statements


def _load_csv_files(db_dialect: str) -> None:
    logger.debug("begin")
    tabellen: Final = ["inventory", "reserved_item"]
    csv_path: Final = _get_csv_path(db_dialect)
    with engine_admin.connect() as connection:
        _set_schema(db_dialect, connection)
        for tabelle in tabellen:
            _load_csv_file(
                tabelle=tabelle,
                csv_path=csv_path,
                db_dialect=db_dialect,
                connection=connection,
            )
            connection.commit()
    engine_admin.dispose()


def _get_csv_path(db_dialect: str) -> str:
    match db_dialect:
        case "postgresql":
            return "/csv"

        case "mysql":
            return "/var/lib/mysql-files/inventory"
    return "/csv"


def _set_schema(db_dialect: str, connection: Connection) -> None:
    logger.debug("db_dialect={} url={}", db_dialect, connection.engine.url)
    if db_dialect == "postgresql":
        connection.execute(text("SET search_path TO inventory;"))
    elif db_dialect == "mysql":
        connection.execute(text("USE inventory;"))


def _load_csv_file(
    tabelle: str,
    csv_path: str,
    db_dialect: str,
    connection: Connection,
) -> None:
    match db_dialect:
        case "postgresql":
            _load_csv_postgres(
                tabelle=tabelle,
                csv_path=csv_path,
                connection=connection,
            )
        case "mysql":
            _load_csv_mysql(tabelle=tabelle, csv_path=csv_path, connection=connection)


# alternativ statt COPY: pandas.load_csv(), etwa 5-7 Mal langsamer
# https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
def _load_csv_postgres(tabelle: str, csv_path: str, connection: Connection) -> None:
    logger.debug("tabelle={}", tabelle)
    copy_cmd: Final = Template(
        "COPY ${TABELLE} FROM '"
        + csv_path
        + "/${TABELLE}.csv' (FORMAT csv, QUOTE '\"', DELIMITER ';', HEADER true);",
    ).substitute(TABELLE=tabelle)
    connection.execute(text(copy_cmd))


def _load_csv_mysql(tabelle: str, csv_path: str, connection: Connection) -> None:
    logger.debug("tabelle={}", tabelle)
    load_cmd: Final = (
        Template(
            "LOAD DATA INFILE '"
            + csv_path
            + "/${tabelle}.csv' INTO TABLE ${tabelle} FIELDS TERMINATED BY ';' ENCLOSED"
            " BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS;",
        )
        if tabelle != "inventory"
        else Template(
            "LOAD DATA INFILE '"
            + csv_path
            + "/${tabelle}.csv' INTO TABLE ${tabelle} FIELDS TERMINATED BY ';' ENCLOSED"
            " BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 ROWS "
            "(id, version, sku_code, quantity, unit_price, status, product_id, created, updated);"
        )
    ).substitute(tabelle=tabelle)
    connection.execute(text(load_cmd))


# ggf. https://sqlite-utils.datasette.io
def _load_sqlite(script_path: Traversable, connection: Connection) -> None:
    with open(file=str(script_path / "insert.sql"), encoding=utf8) as insert_sql:
        zeilen_insert: Final = _remove_comment(insert_sql.readlines())
        insert_statements: Final = _build_sql_statements(zeilen_insert)
        for stmt in insert_statements:
            connection.execute(text(stmt))


def db_populate_multiple() -> None:
    """DB durch mehrere SQL-Anweisungen als Batch neu laden."""
    logger.warning(">>> Die DB wird neu geladen: {} <<<", db_url)

    connection: Connection
    # durch "with" erhaelt man einen "Context Manager", der die Ressource/Connection
    # am Endes des Blocks schliesst
    with engine.connect() as connection:
        script_path: Final = _db_traversable / connection.dialect.name
        # "Context Manager" fuer die Ressource/Datei
        with open(file=str(script_path / "drop.sql"), encoding=utf8) as drop_sql:
            # text() fuer SQL-Anweisungen als String
            drop_statements: Final = text(drop_sql.read())
            connection.execute(drop_statements)
        with open(file=str(script_path / "create.sql"), encoding=utf8) as create_sql:
            create_statements: Final = text(create_sql.read())
            connection.execute(create_statements)
        with open(file=str(script_path / "insert.sql"), encoding=utf8) as insert_sql:
            insert_statements: Final = text(insert_sql.read())
            connection.execute(insert_statements)

        connection.commit()

    logger.warning(">>> Die DB wurde neu geladen <<<")
