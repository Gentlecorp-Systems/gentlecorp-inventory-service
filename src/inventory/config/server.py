
"""Konfiguration für ASGI."""

from typing import Final, Literal

from inventory.config.config import inventory_config

__all__ = ["asgi", "host_binding", "port"]


_asgi_toml: Final = inventory_config.get("server", {})
_asgi: Final[str] = _asgi_toml.get("asgi", "uvicorn")

asgi: Literal["hypercorn", "uvicorn"] = _asgi if _asgi == "hypercorn" else "uvicorn"
"""ASGI-Server: uvicorn (default) oder hypercorn."""

host_binding: Final[str] = _asgi_toml.get("host-binding", "127.0.0.1")
"""'Host Binding', z.B. 127.0.0.1 (default) oder 0.0.0.0."""

port: Final[int] = _asgi_toml.get("port", 8000)
"""Port für den Server (default: 8000)."""

reload: Final[bool] = bool(_asgi_toml.get("reload", False))
