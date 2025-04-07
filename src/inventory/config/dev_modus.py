"""Konfiguration für den Entwicklungsmodus."""

from typing import Final

from inventory.config.config import inventory_config

__all__ = ["dev"]


_dev_toml: Final = inventory_config.get("dev", {})

dev: Final[bool] = bool(_dev_toml.get("enabled", False))
"""Flag, ob der Entwicklungsmodus aktiviert ist."""
