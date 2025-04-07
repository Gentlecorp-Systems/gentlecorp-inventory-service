"""Mapper-Funktion zwischen SQLAlchemy-Entity und DTO."""

from inventory.model.entity.inventory import Inventory as InventoryEntity, InventoryType



def map_inventory_to_dto(entity: InventoryEntity) -> InventoryType:
    return InventoryType(
        id=entity.id,
        version=entity.version,
        sku_code=entity.sku_code,
        quantity=entity.quantity,
        unit_price=entity.unit_price,
        status=entity.status,
        product_id=entity.product_id,
        created=entity.created,
        updated=entity.updated,
        reserved_items=[],  # TODO: optional mappen
    )
