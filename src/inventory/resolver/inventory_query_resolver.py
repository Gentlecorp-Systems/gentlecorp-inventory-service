from typing import Sequence, Final
from fastapi import Request
from loguru import logger
from strawberry.types import Info

from inventory.error.exceptions import NotFoundError
from inventory.graphql_api.graphql_types import Suchkriterien
from inventory.model.entity.inventory import InventoryType
from inventory.repository.pageable import Pageable
from inventory.security.keycloak_service import KeycloakService
from inventory.service.inventory_read_service import find, find_by_id


# Einzelnes Inventory per ID abfragen
async def resolve_inventory(info: Info, inventory_id: str) -> InventoryType | None:
    logger.debug("inventory_id={}", inventory_id)

    # KeycloakService aus dem Strawberry-Kontext
    keycloak: KeycloakService = info.context["keycloak"]
    keycloak.assert_roles(["Admin", "helper"])

    try:
        inventory: Final = find_by_id(inventory_id=inventory_id)
    except NotFoundError:
        return None

    logger.debug("{}", inventory)
    return inventory


# Alle Inventories mit optionalen Filterkriterien abfragen
async def resolve_inventories(
    info: Info,
    suchkriterien: Suchkriterien | None = None,
) -> Sequence[InventoryType]:
    logger.debug("suchkriterien={}", suchkriterien)

    # Rollenprüfung via Keycloak
    keycloak: KeycloakService = info.context["keycloak"]
    keycloak.assert_roles(["Admin", "helper"])

    # in ein dict umwandeln, leere Felder filtern
    suchkriterien_dict: Final[dict[str, str]] = (
        dict(vars(suchkriterien)) if suchkriterien else {}
    )
    filtered = {key: val for key, val in suchkriterien_dict.items() if val}
    logger.debug("suchkriterien_filtered={}", filtered)

    pageable: Final = Pageable.create(size="0")
    try:
        inventory_dto: Final = find(searchCriteria=filtered, pageable=pageable)
    except NotFoundError:
        return []

    logger.debug("{}", inventory_dto)
    return inventory_dto.content
