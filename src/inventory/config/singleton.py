
"""Modul für den Decorator, um Singleton-Klassen zu erstellen."""

from collections.abc import Callable
from typing import Any, Final


def singleton(cls: type) -> Callable[[], Any]:
    """Funktion als Decorator gemäß GoF nach https://peps.python.org/pep-0318/#examples.

    :param cls: dekorierte Klasse
    :type cls: type
    :return: Objekt von Callable mit beliebiger Signatur
    :rtype: Callable
    """
    instances: Final[dict[type, Any]] = {}

    def getinstance() -> Any:
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance
