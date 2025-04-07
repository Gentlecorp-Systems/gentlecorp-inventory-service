"""Entity-Klasse für Inventory data."""

from dataclasses import InitVar
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Final, Self
import uuid
from sqlalchemy.dialects.postgresql import UUID


from loguru import logger
from sqlalchemy import JSON, Identity, String, func
from sqlalchemy.orm import Mapped, mapped_column, reconstructor, relationship
import strawberry

from inventory.model.entity.base import Base
from inventory.model.entity.reserved_item import Reserved_item
from inventory.model.enum.inventory_status_type import InventoryStatusType


@strawberry.type
class InventoryType:
    id: str | None
    version: int
    sku_code: str
    quantity: int
    unit_price: float
    status: InventoryStatusType
    product_id: str | None
    product_name: str | None
    created: datetime
    updated: datetime

    def __init__(self, inventory: "Inventory"):
        """Initialisierung von InventoryType durch ein Entity-Objekt von Inventory.

        :param inventory: Inventory-Objekt mit Decorators zu SQLAlchemy
        """

        self.id = str(inventory.id) if inventory.id else None
        self.version = inventory.version
        self.sku_code = inventory.sku_code
        self.quantity = inventory.quantity
        self.unit_price = float(inventory.unit_price)
        self.status = inventory.status
        self.product_id = inventory.product_id
        self.product_name = None  # ggf. aus Produktservice beziehbar
        self.created = inventory.created
        self.updated = inventory.updated

class Inventory(Base):
    """Entity-Klasse für Inventory data."""

    __tablename__ = "inventory"

    sku_code: Mapped[str]
    """Der SKU-Code."""

    quantity: Mapped[int]
    """Die Menge im Lager."""

    unit_price: Mapped[Decimal]
    """Einzelpreis in Dezimalform."""

    status: Mapped[InventoryStatusType]
    """Der aktuelle Lagerstatus."""

    product_id: Mapped[str]
    """Die ID des zugehörigen Produkts (externer Service)."""

    reserved_items: Mapped[list[Reserved_item]] = relationship(
        back_populates="inventory",
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten ReservedItems."""

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    """Die generierte ID (UUID v4 als String im Format CHAR(36))."""

    version: Mapped[int] = mapped_column(nullable=False, default=1)
    """Die Versionsnummer für optimistische Synchronisation."""

    created: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        default=None,
    )
    """Der Zeitstempel für das initiale INSERT in die DB-Tabelle."""

    updated: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
        default=None,
    )
    """Der Zeitstempel vom letzen UPDATE in der DB-Tabelle."""

    __mapper_args__ = {"version_id_col": version}

    @classmethod
    def from_dict_primitive(cls, inventory_dict: dict[str, Any]) -> Self:
        """Inventory mit primitiven Werten aus einem Dictionary erstellen.

        :param inventory_dict: Inventory data in einem Dictionary
        :return: Das gebaute Inventory-Objekt
        :rtype: Inventory
        """
        logger.debug("inventory_dict={}", inventory_dict)
        status_str: Final = inventory_dict.get("status")
        status_enum: Final = (
            InventoryStatusType(status_str) if status_str is not None else None
        )
        return cls(
            id=None,
            sku_code=inventory_dict["sku_code"],
            quantity=inventory_dict["quantity"],
            unit_price=Decimal(inventory_dict["unit_price"]),
            status=status_enum,
            product_id=inventory_dict["product_id"],
            reserved_items=[],
            created=None,
            updated=None,
        )

    @classmethod
    def from_dict_mit_referenzen(cls, inventory_dict: dict[str, Any]) -> Self:
        """Inventory mit Werten aus einem Dictionary mit Referenzen erstellen.

        :param inventory_dict: Inventory data in einem Dictionary
        :return: Das gebaute Inventory-Objekt
        :rtype: Inventory
        """
        logger.debug("inventory_dict={}", inventory_dict)
        inventory: Final = Inventory.from_dict_primitive(inventory_dict=inventory_dict)
        inventory.reserved_items = [
            Reserved_item.from_dict(reserved_items_dict)
            for reserved_items_dict in inventory_dict.get("reserved_items", [])
        ]
        return inventory  # pyright: ignore[reportReturnType ]

    def set(self, inventory: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param inventory: Inventory-Objekt mit den aktuellen Daten
        """
        self.sku_code = inventory.sku_code
        self.quantity = inventory.quantity
        self.product_id = inventory.product_id
        self.unit_price = inventory.unit_price
        self.status = inventory.status

    def __eq__(self, other: Any) -> bool:
        """Vergleich auf Gleicheit, ohne Joins zu verursachen."""
        # Vergleich der Referenzen: id(self) == id(other)
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    def __repr__(self) -> str:
        """Ausgabe eines Inventorys als String, ohne Joins zu verursachen."""
        return (
            f"Inventory(id={self.id}, version={self.version}, "
            + f"sku_code={self.sku_code}, quantity={self.quantity}, "
            + f"unit_price={self.unit_price},  status={self.status},"
            + f"product_id={self.product_id},"
            + f" created={self. created},  updated={self. updated})"
        )
