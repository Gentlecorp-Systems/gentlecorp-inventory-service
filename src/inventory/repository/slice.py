
"""Ausschnitt an gefundenen Daten."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

__all__ = ["Slice"]


T = TypeVar("T")


@dataclass(eq=False, slots=True, kw_only=True)
class Slice[T]:
    """Data class für den Ausschnitt an gefundenen Daten."""

    content: Sequence[T]
    """Ausschnitt der gefundenen Datensätze."""

    total_elements: int
    """Gesamte Anzahl an Datensätzen."""
