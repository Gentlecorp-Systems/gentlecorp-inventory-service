"""Geschäftslogik zum Lesen von Patientendaten."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Final

from loguru import logger
from openpyxl import Workbook
from sqlalchemy import UUID  # pyright: ignore[reportMissingModuleSource]

from inventory.config import excel_enabled
from inventory.model.entity.inventory import Inventory, InventoryType
from inventory.model.mapper.inventory_mapper import map_inventory_to_dto
from inventory.repository import Pageable, Session, Slice
from inventory.repository import find as find_repo
from inventory.repository import find_by_id as find_by_id_repo
from inventory.error.exceptions import NotAllowedError, NotFoundError
from inventory.service.product_service import get_product_by_id

__all__ = ["find", "find_by_id", "find_nachnamen"]


async def find_by_id(inventory_id: str, token: str) -> Inventory:
    """Suche mit der Patient-ID.

    :param inventory_id: ID für die Suche
    :param user_dto: UserDTO aus dem Token
    :return: Der gefundene Patient
    :rtype: PatientDTO
    :raises NotFoundError: Falls kein Patient gefunden
    :raises NotAllowedError: Falls die Patientendaten nicht gelesen werden dürfen
    """
    logger.debug("inventory_id={}", inventory_id)

    with Session() as session:

        if (
            inventory := find_by_id_repo(inventory_id=inventory_id, session=session)
        ) is None:
            raise NotFoundError(inventory_id)

        logger.debug('inventory={}', inventory)
        inventory_dto: Final = InventoryType(inventory)

        bearer_tokem: Final = "bearer " + token
        try:
            # Produktname vom Product Service holen
            product_data = await get_product_by_id(inventory.product_id, token)
            inventory_dto.product_name = product_data["name"]
        except Exception as e:
            logger.warning("Product Service nicht erreichbar: {}", e)
            inventory_dto.product_name = "Unbekannt"

        session.commit()

    logger.debug("{}", inventory_dto)
    return inventory_dto

def find(searchCriteria: Mapping[str, str], pageable: Pageable) -> Slice[InventoryType]:
    """Suche mit Query-Parameter.

    :param searchCriteria: Query-Parameter
    :return: Liste der gefundenen Patienten
    :rtype: Slice[PatientDTO]
    :raises NotFoundError: Falls keine Patienten gefunden wurden
    """
    logger.debug("{}", searchCriteria)
    with Session() as session:
        inventory_slice: Final = find_repo(
            searchCriteria=searchCriteria, pageable=pageable, session=session
        )
        if len(inventory_slice.content) == 0:
            raise NotFoundError(searchCriteria=searchCriteria)

        inventory_dto: Final = [
            InventoryType(inventory) for inventory in inventory_slice.content
        ]
        session.commit()

    if excel_enabled:
        _create_excelsheet(inventory_dto)
    inventory_dto_slice = Slice(
        content=inventory_dto, total_elements=inventory_slice.total_elements
    )
    logger.debug("{}", inventory_dto_slice)
    return inventory_dto_slice


# def find_nachnamen(teil: str) -> Sequence[str]:
#     """Suche Nachnamen zu einem Teilstring.

#     :param teil: Teilstring der gesuchten Nachnamen
#     :return: Liste der gefundenen Nachnamen oder eine leere Liste
#     :rtype: list[str]
#     :raises NotFoundError: Falls keine Nachnamen gefunden wurden
#     """
#     logger.debug("teil={}", teil)
#     with Session() as session:
#         nachnamen: Final = find_nachnamen_repo(teil=teil, session=session)
#         session.commit()

#     logger.debug("{}", nachnamen)
#     if len(nachnamen) == 0:
#         raise NotFoundError()
#     return nachnamen


def _create_excelsheet(inventories: list[Inventory]) -> None:
    """Ein Excelsheet mit den gefundenen Patienten erstellen.

    :param inventories: Patientendaten für das Excelsheet
    """

    workbook: Final = Workbook()
    worksheet: Final = workbook.active
    if worksheet is None:
        return

    worksheet.append(["skuCode", "quantity", "status", "product_id"])
    for inventory in inventories:
        status = (
            str(inventory.status) if inventory.status is not None else "N/A"
        )
        worksheet.append([inventory.sku_code, inventory.quantity, status, inventory.product_id])

    timestamp: Final = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    workbook.save(f"inventory-{timestamp}.xlsx")
