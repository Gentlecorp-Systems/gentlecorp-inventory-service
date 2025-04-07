"""Modul für persistente Patientendaten."""

from inventory.model.entity.base import Base

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "Adresse",
    "Base",
    "Facharzt",
    "Familienstand",
    "Geschlecht",
    "Patient",
    "Rechnung",
]
