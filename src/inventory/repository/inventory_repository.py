"""Repository für persistente Inventory-Daten."""

from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger
from sqlalchemy import UUID, func, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from inventory.model.entity import Inventory
from inventory.repository.pageable import Pageable
from inventory.repository.session import engine
from inventory.repository.slice import Slice

__all__ = [
    "check_db_connection",
    "create",
    "delete_by_id",
    "exists_sku_code",
    "find",
    "find_by_id",
    "find_product_names",
    "update",
]


def find_by_id(inventory_id: str| None, session: Session) -> Inventory | None:
    """Suche mit der Inventory-ID."""
    logger.debug("inventory_id={}", inventory_id)
    if inventory_id is None:
        return None

    statement: Final = select(Inventory).where(Inventory.id == inventory_id)
    inventory: Final = session.scalar(statement)
    logger.debug("{}", inventory)
    return inventory


def find(
    searchCriteria: Mapping[str, str], pageable: Pageable, session: Session
) -> Slice[Inventory]:
    """Suche mit Query-Parametern."""
    logger.debug("{}", searchCriteria)
    if not searchCriteria:
        return _find_all(pageable=pageable, session=session)

    for key, value in searchCriteria.items():
        if key == "sku_code":
            inventory = _find_by_sku_code(sku_code=value, session=session)
            logger.debug("{}", inventory)
            return (
                Slice(content=[inventory], total_elements=1)
                if inventory is not None
                else Slice(content=[], total_elements=0)
            )
        if key == "product_name":
            inventories = _find_by_product_name(
                teil=value, pageable=pageable, session=session
            )
            logger.debug("{}", inventories)
            return inventories
    return Slice(content=[], total_elements=0)


def _find_all(pageable: Pageable, session: Session) -> Slice[Inventory]:
    logger.debug("aufgerufen")
    offset = pageable.number * pageable.size
    statement: Final = (
        select(Inventory).limit(pageable.size).offset(offset)
        if pageable.size != 0
        else select(Inventory)
    )
    inventories: Final = session.scalars(statement).all()
    anzahl: Final = _count_rows(session)
    return Slice(content=inventories, total_elements=anzahl)


def _count_rows(session: Session) -> int:
    statement: Final = select(func.count()).select_from(Inventory)
    count: Final = session.execute(statement).scalar()
    return count if count is not None else 0


def _find_by_sku_code(sku_code: str, session: Session) -> Inventory | None:
    """Einen Inventory anhand des SKU-Codes suchen."""
    logger.debug("sku_code={}", sku_code)
    statement: Final = select(Inventory).where(Inventory.sku_code == sku_code)
    inventory: Final = session.scalar(statement)
    logger.debug("{}", inventory)
    return inventory


def _find_by_product_name(
    teil: str, pageable: Pageable, session: Session
) -> Slice[Inventory]:
    logger.debug("teil={}", teil)
    offset = pageable.number * pageable.size
    statement: Final = (
        select(Inventory)
        .filter(Inventory.product_id.ilike(f"%{teil}%"))
        .limit(pageable.size)
        .offset(offset)
        if pageable.size != 0
        else select(Inventory).filter(Inventory.product_id.ilike(f"%{teil}%"))
    )
    inventories: Final = session.scalars(statement).all()
    anzahl: Final = _count_rows(session)
    return Slice(content=inventories, total_elements=anzahl)


def exists_sku_code(sku_code: str, session: Session) -> bool:
    """Abfrage, ob es den SKU-Code bereits gibt."""
    logger.debug("sku_code={}", sku_code)
    statement: Final = select(func.count()).where(Inventory.sku_code == sku_code)
    anzahl: Final = session.scalar(statement)
    logger.debug("anzahl={}", anzahl)
    return anzahl is not None and anzahl > 0


def exists_sku_code_other_id(
    sku_code: str, inventory_id: str, session: Session
) -> bool:
    """Abfrage, ob es den SKU-Code bei einer anderen Inventory-ID bereits gibt."""
    logger.debug("sku_code={}", sku_code)
    statement: Final = select(Inventory.id).where(Inventory.sku_code == sku_code)
    id_db: Final = session.scalar(statement)
    logger.debug("id_db={}", id_db)
    return id_db is not None and id_db != inventory_id


def create(inventory: Inventory, session: Session) -> Inventory:
    """Speichere einen neuen Inventory-Datensatz."""
    logger.debug("{}", inventory)
    logger.debug("{}", inventory.reserved_items)
    session.add(instance=inventory)
    session.flush(objects=[inventory])
    logger.debug("inventory_id={}", inventory.id)
    return inventory


def update(inventory: Inventory, session: Session) -> Inventory | None:
    """Aktualisiere einen bestehenden Inventory-Datensatz."""
    logger.debug("{}", inventory)
    if (inventory_db := find_by_id(inventory_id=inventory.id, session=session)) is None:
        return None
    logger.debug("{}", inventory_db)
    return inventory_db


def delete_by_id(inventory_id: str, session: Session) -> None:
    """Lösche einen Inventory-Datensatz."""
    logger.debug("inventory_id={}", inventory_id)
    if (inventory := find_by_id(inventory_id=inventory_id, session=session)) is None:
        return
    session.delete(inventory)
    logger.debug("ok")


# def find_product_names(teil: str, session: Session) -> Sequence[str]:
#     """Suche Produktnamen anhand eines Teilstrings (Platzhalterfunktion)."""
#     logger.debug("teil={}", teil)
#     statement: Final = (
#         select(Inventory.product_id)
#         .filter(Inventory.product_id.ilike(f"%{teil}%"))
#         .distinct()
#     )
#     product_names: Final = session.scalars(statement).all()
#     logger.debug("product_names={}", product_names)
#     return product_names


def check_db_connection() -> bool:
    """Überprüfung, ob der DB-Server erreichbar ist."""
    with engine.connect() as connection:
        try:
            connection.execute(text("SELECT 1"))
            connection.commit()
        except OperationalError:
            connection.rollback()
            return False
    return True
