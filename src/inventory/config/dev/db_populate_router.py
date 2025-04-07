"""DbPopulateController."""

from typing import Final

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from loguru import logger

from inventory.config.dev.db_populate import db_populate as db_populate_repo

__all__ = ["router"]


router: Final = APIRouter()


# "Dependency Injection" durch Depends
@router.post(
    "/db_populate",
    tags=["Admin"],
    # dependencies=[Depends(RolesAllowed(Role.ADMIN))],
)
def db_populate(request: Request) -> JSONResponse:
    """Die DB mit Testdaten durch einen POST-Request neu zu laden.

    :return: JSON-Datensatz mit der Erfolgsmeldung
    :rtype: dict[str, str]
    """
    # current_user: Final[UserDTO] = request.state.current_user
    # logger.warning(
    #     'REST-Schnittstelle zum Neuladen der DB aufgerufen von "{}"',
    #     current_user.username,
    # )
    db_populate_repo()
    return JSONResponse(content={"db_populate": "success"})
