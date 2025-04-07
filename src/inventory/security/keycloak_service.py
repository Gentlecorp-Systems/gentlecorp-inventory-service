from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from typing import List
import os
import httpx
from loguru import logger


class KeycloakService:
    """
    Service zur Extraktion und Validierung von JWTs aus Keycloak,
    mit dynamischem Laden des Public Key via JWKS-Endpunkt.
    """

    def __init__(self, request: Request):
        self.request = request
        self.token = self._extract_token()
        self.payload = self._decode_token()

    def _extract_token(self) -> str:
        auth_header = self.request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kein gültiger Bearer-Token gefunden",
            )
        return auth_header.removeprefix("Bearer ").strip()

    def _decode_token(self) -> dict:
        realm = os.getenv("KC_SERVICE_REALM", "gentlecorp")
        host = os.getenv("KC_SERVICE_HOST", "localhost")
        port = os.getenv("KC_SERVICE_PORT", 18080)

        jwks_url = (
            f"http://{host}:{port}/auth/realms/{realm}/protocol/openid-connect/certs"
        )
        logger.debug("Keycloak JWKS URI: {}", jwks_url)

        try:
            response = httpx.get(jwks_url)
            jwks = response.json()

            keys = jwks.get("keys")
            if not keys:
                raise ValueError("JWKS enthält keine Schlüssel")

            unverified_header = jwt.get_unverified_header(self.token)
            for key in keys:
                if key["kid"] == unverified_header["kid"]:
                    return jwt.decode(
                        self.token,
                        key,
                        algorithms=["RS256"],
                        options={"verify_aud": False},  # <- Wichtig!
                    )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kein passender Schlüssel im JWKS gefunden",
            )

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token-Verifikation fehlgeschlagen: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fehler beim Laden des JWKS: {e}",
            )

    def get_roles(self) -> List[str]:
        return self.payload.get("realm_access", {}).get("roles", [])

    def has_role(self, required_roles: List[str]) -> bool:
        return any(role in self.get_roles() for role in required_roles)

    def assert_roles(self, required_roles: List[str]) -> None:
        if not self.has_role(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Zugriff verweigert – Rollen {required_roles} erforderlich",
            )
