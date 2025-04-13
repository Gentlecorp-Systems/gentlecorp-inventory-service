"""Konfiguration aus der TOML-Datei einlesen."""

from importlib.resources import files
from importlib.resources.abc import Traversable
from tomllib import load
from typing import Any, Final

from loguru import logger

__all__ = ["inventory_config", "resources_path"]

resources_path: Final[str] = "inventory.config.resources"

_resources_traversable: Final[Traversable] = files(resources_path)
_config_file: Final[Traversable] = _resources_traversable / "inventory.toml"
logger.debug("config: _config_file={}", _config_file)


with open(str(_config_file), mode="rb") as reader:
    _root_config: Final[dict[str, Any]] = load(reader)
    inventory_config: Final = _root_config.get("inventory", {})
