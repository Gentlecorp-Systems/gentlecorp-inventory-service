# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""HealthRouter."""

from typing import Any, Final

from fastapi import APIRouter

from inventory.repository import check_db_connection

__all__ = ["router"]

router: Final = APIRouter(tags=["Health"])


@router.get("/liveness")
def liveness() -> dict[str, Any]:
    """Überprüfen der Liveness.

    :return: JSON-Datensatz mit der Erfolgsmeldung
    :rtype: dict[str, Any]
    """
    return {"status": "up"}


@router.get("/readiness")
def readiness() -> dict[str, Any]:
    """Überprüfen der Readiness.

    :return: JSON-Datensatz mit der Erfolgsmeldung
    :rtype: dict[str, Any]
    """
    status: Final = "up" if check_db_connection() else "down"
    return {"db": status}
