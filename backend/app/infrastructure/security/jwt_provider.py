from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.application.exceptions import UnauthorizedError
from app.config import settings
from app.domain.interfaces import TokenProvider


class JoseJWTTokenProvider(TokenProvider):
    def create_access_token(self, subject: str) -> str:
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
        expire = datetime.now(timezone.utc) + expires_delta
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def get_subject(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            subject = payload.get("sub")
            if not subject:
                raise UnauthorizedError("Token inválido")
            return str(subject)
        except JWTError as exc:
            raise UnauthorizedError("No autorizado") from exc
