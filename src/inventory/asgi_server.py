
"""Funktion `run`, um die FastAPI-Applikation mit einem ASGI-Server zu starten.

Dazu stehen _uvicorn_ (default) und _hypercorn_ zur Verfügung.
"""

import asyncio
from ssl import PROTOCOL_TLS_SERVER
from typing import Final

import uvicorn
from hypercorn.asyncio import serve
from hypercorn.config import Config

from .config import (
    asgi,
    host_binding,
    port,
    tls_certfile,
    tls_keyfile,
)
from .fastapi_app import app

__all__ = ["run"]


def _run_unicorn() -> None:
    """Start der Anwendung mit uvicorn."""
    # https://www.uvicorn.org/settings mit folgenden Defaultwerten
    # host="127.0.0.1"
    # port=8000
    # loop="auto" (default), "asyncio" , "uvloop" (nur fuer Linux und MacOS)
    # http="auto" (def), "h11", "httptools" Python Binding fuer den HTTP Parser von Node
    # interface="auto" (default), "asgi2", "asgi3", "wsgi"
    # loop: Final[Literal["uvloop", "asyncio"]] = (
    #     "uvloop" if platform.system() != "Windows" else "asyncio"
    # )
    uvicorn.run(
        "inventory:app",
        loop="asyncio",
        http="h11",
        interface="asgi3",
        host=host_binding,
        port=port,
        ssl_keyfile=tls_keyfile,
        ssl_certfile=tls_certfile,
        ssl_version=PROTOCOL_TLS_SERVER,  # DevSkim: ignore DS440070
    )


def _run_hypercorn() -> None:
    """Start der Anwendung mit hypercorn."""
    config: Final = Config()
    config.bind = [f"{host_binding}:{port}"]
    config.keyfile = tls_keyfile
    config.certfile = tls_certfile
    asyncio.run(serve(app=app, config=config, mode="asgi"))  # pyright: ignore[reportArgumentType]


def run() -> None:
    """CLI für den asynchronen Appserver."""
    match asgi:
        case "uvicorn":
            _run_unicorn()
        case "hypercorn":
            _run_hypercorn()
