from fastapi import Request
import strawberry
from strawberry.fastapi import GraphQLRouter
from inventory.config.graphql import graphql_ide
from inventory.graphql_api.graphql_types import Suchkriterien
from inventory.model.entity.inventory import InventoryType
from typing import Final, List

from inventory.resolver.inventory_query_resolver import resolve_inventories, resolve_inventory
from inventory.security.keycloak_service import KeycloakService


async def get_context(request: Request) -> dict:
    return {
        "request": request,
        "keycloak": KeycloakService(request),
    }


@strawberry.type
class Query:

    @strawberry.field
    async def inventory(
        self,
        inventory_id: strawberry.ID,
        info: strawberry.types.Info = None,
        ) -> InventoryType | None:
        return await resolve_inventory(info=info, inventory_id=inventory_id)

    @strawberry.field
    async def inventories(
        self,
        suchkriterien: Suchkriterien | None = None,
        info: strawberry.types.Info = None,
    ) -> List[InventoryType]:
        return await resolve_inventories(suchkriterien=suchkriterien, info=info)


schema = strawberry.Schema(query=Query)

graphql_router: Final = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
