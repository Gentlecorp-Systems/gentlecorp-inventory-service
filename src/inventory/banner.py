"""Banner beim Start des Servers."""

import sys
from collections import namedtuple
from getpass import getuser
from importlib.metadata import version
from locale import getlocale
from socket import gethostbyname, gethostname
from sysconfig import get_platform
from typing import Final

from loguru import logger
from pyfiglet import Figlet
from starlette.routing import BaseRoute, Route
from tabulate import tabulate

from inventory.config import db_url
from inventory.repository import engine

# tabulate() hat ein Argument vom Typ "Tuple" und nicht dataclass
TableEntry = namedtuple("TableEntry", "pfad http_methoden funktion")


def _route_to_table_entry(route: Route) -> TableEntry:
    """Route als Tupel mit Pfad, HTTP-Methode, implementierende Funktion."""
    endpoint: Final = route.endpoint
    # Liste als String ohne [] und ohne '
    methods_str = str(route.methods)[2:-2] if route.methods is not None else "-"
    methods_str = methods_str.replace("', '", ", ")
    return TableEntry(
        pfad=route.path,
        http_methoden=methods_str,
        funktion=f"{endpoint.__module__}.{endpoint.__qualname__}",
    )


def _routes_to_str(routes: list[BaseRoute]) -> str:
    routes_str: Final = [
        _route_to_table_entry(route) for route in routes if isinstance(route, Route)
    ]
    return tabulate(
        sorted(routes_str),
        headers=["Pfad", "HTTP-Methoden", "Implementierung"],
    )


def banner(routes: list[BaseRoute]) -> None:
    """Banner für den Start des Servers."""
    figlet: Final = Figlet()
    print()
    print(figlet.renderText("inventory"))

    rechnername: Final = gethostname()
    # Default Isolation Level "read committed": Schreibsperren und keine Lesesperren
    # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#transaction-isolation-level
    # https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DEFAULT-TRANSACTION-ISOLATION

    db_dialect: Final = engine.dialect
    logger.info("Python           {}", sys.version_info)
    logger.info("Plattform        {}", get_platform())
    logger.info("uvicorn          {}", version("uvicorn"))
    logger.info("FastAPI          {}", version("fastapi"))
    logger.info("Starlette        {}", version("starlette"))
    logger.info("AnyIO            {}", version("anyio"))
    logger.info("Pydantic         {}", version("pydantic"))
    logger.info("Strawberry       {}", version("strawberry-graphql"))
    logger.info("SQLAlchemy       {}", version("sqlalchemy"))
    # logger.info("psycopg          {}", version("psycopg"))
    logger.info("PyMySQL          {}", version("pymysql"))
    logger.info("DB URL           {}", db_url)
    logger.info("Identity Columns {}", db_dialect.supports_identity_columns)
    logger.info("Sequence         {}", db_dialect.supports_sequences)
    logger.info("Boolean          {}", db_dialect.supports_native_boolean)
    logger.info("Decimal          {}", db_dialect.supports_native_decimal)
    logger.info("Enum             {}", db_dialect.supports_native_enum)
    logger.info("UPDATE RETURNING {}", db_dialect.update_returning)
    logger.info("UUID             {}", db_dialect.supports_native_uuid)
    # logger.info("PyJWT            {}", version("pyjwt"))
    # logger.info("cryptography     {}", version("cryptography"))
    # logger.info("Argon2           {}", argon2.__version__)
    logger.info("Environment      {}", sys.prefix)
    logger.info("User             {}", getuser())
    logger.info("Locale           {}", getlocale())
    logger.info("Rechnername      {}", rechnername)
    logger.info("IP               {}", gethostbyname(rechnername))
    logger.info("{} Routes:", len(routes))

    print()
    print(_routes_to_str(routes))
    print()
