"""Schema für GraphQL."""

from datetime import date
from decimal import Decimal

import strawberry


__all__ = [
    "AdresseInput",
    "CreatePayload",
    "PatientInput",
    "RechnungInput",
    "Suchkriterien",
]

# SDL (schema definition language):
# type Patient {
#     nachname: String!
# }
# type Query {
#     inventory(inventory_id: ID!): Patient!
#     inventoryen(input: Suchkriterien): [Patient!]
# }
# type Mutation {
#     create(inventory_input: InventoryInput!): CreatePayload!
# }


@strawberry.input
class Suchkriterien:
    """Suchkriterien für die Suche nach Inventories."""

    productName: str | None = None
    """Nachname als Suchkriterium."""

    skuCode: str | None = None
    """Emailadresse als Suchkriterium."""

@strawberry.input
class ReservedItemInput:
    """Rechnung zu einem neuen Inventory."""

    betrag: Decimal
    """Betrag."""

    waehrung: str
    """Währung als 3-stellige Zeichenkette."""


@strawberry.input
class InventoryInput:
    """Daten für einen neuen Inventory."""

    skuCode: str
    """Emailadresse."""

    quantity: int
    """Kategorie."""

    unitPrice: Decimal
    """Angabe, ob der Newsletter abonniert ist."""

    productId: str
    """Geburtsdatum."""

    reservedItems: list[ReservedItemInput]
    """Rechnungen."""


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer Patient angelegt wurde."""

    id: int
    """ID des neu angelegten Inventory"""
