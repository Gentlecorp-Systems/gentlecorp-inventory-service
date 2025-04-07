"""Enum für Fachärzte."""

from enum import StrEnum

import strawberry


@strawberry.enum
class InventoryStatusType(StrEnum):
    """Enum für 30+ Fachrichtungen."""

    DISCONTINUED = "D"
    """Facharzt für Chirurgie."""

    AVAILABLE = "A"
    """Facharzt für Chirurgie."""

    RESERVED = "R"
    """Facharzt für Chirurgie."""

    OUT_OF_STOCK = "O"
    """Facharzt für Chirurgie."""
