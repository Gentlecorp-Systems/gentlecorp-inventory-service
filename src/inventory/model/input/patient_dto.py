"""DTO-Klasse für Inventoryendaten, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass
from datetime import date

import strawberry

__all__ = ["InventoryInput"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class PatientDTO:
    """DTO-Klasse für Patientendaten, insbesondere ohne Decorators für SQLAlchemy."""

    id: str | None
    version: int
    sku_code: str
    quantity: Decimal
    status: InventoryStatusType
    product_id: str

    def __init__(self, inventory: Inventory):
        """Initialisierung von Inventory Input durch ein Entity-Objekt von Inventory.

        :param inventory: Inventory-Objekt mit Decorators zu SQLAlchemy
        """
        self.id = inventory.id
        self.version = inventory.version
        self.sku_code = inventory.sku_code
        self.quantity = inventory.quantity
        self.status = inventory.status
        self.product_id = inventory.product_id
