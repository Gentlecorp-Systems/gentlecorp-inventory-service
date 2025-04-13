import httpx
from typing import Any, Dict
from loguru import logger

PRODUCT_GRAPHQL_URL = "https://localhost:3000/graphql"
class ProductGraphQLClient:
    """Client zur Kommunikation mit dem Product-Service via GraphQL."""

    def __init__(self, token: str):
        self.graphql_url = PRODUCT_GRAPHQL_URL
        self.token = token

    async def execute(
        self, query: str, variables: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(verify=False) as client:
            try:
                response = await client.post(
                    self.graphql_url,
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                json_data = response.json()
                if "errors" in json_data:
                    logger.error("GraphQL-Fehler: {}", json_data["errors"])
                    raise Exception(f"GraphQL-Fehler: {json_data['errors']}")
                return json_data["data"]
            except Exception as e:
                logger.exception("Fehler bei GraphQL-Anfrage an Product-Service")
                raise
