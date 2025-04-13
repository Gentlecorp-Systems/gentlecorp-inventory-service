from inventory.client.product_client import ProductGraphQLClient
from typing import Any, Dict

PRODUCT_GRAPHQL_URL = "https://localhost:3000/graphql"  # z. B. via ngrok exposed
REQUIRED_FIELDS = "name"


async def get_product_by_id(product_id: str, token: str) -> Dict[str, Any]:
    query = f"""
    query ($id: ID!) {{
        product(id: $id) {{
            {REQUIRED_FIELDS}
        }}
    }}
    """
    variables = {"id": product_id}
    client = ProductGraphQLClient(token)
    result = await client.execute(query, variables)
    return result["product"]
