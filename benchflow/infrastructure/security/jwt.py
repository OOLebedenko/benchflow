from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError as PyJwtInvalidTokenError

from benchflow.application.ports.token_provider import InvalidTokenError


class JwtTokenProvider:
    """Provide access tokens using JWT."""

    def __init__(
            self,
            secret: str,
            algorithm: str,
            access_token_expire_minutes: int,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(
            self,
            user_id: UUID,
    ) -> str:
        """Create a signed JWT access token."""

        expires_at = datetime.now(UTC) + timedelta(
            minutes=self._access_token_expire_minutes
        )

        payload = {
            "sub": str(user_id),
            "exp": expires_at,
        }

        return jwt.encode(
            payload,
            self._secret,
            algorithm=self._algorithm,
        )

    def validate_access_token(
            self,
            token: str,
    ) -> UUID:
        """Validate a JWT access token and return its user identifier."""

        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={
                    "require": ["sub", "exp"],
                },
            )

            return UUID(payload["sub"])
        except (
                PyJwtInvalidTokenError,
                ValueError,
        ) as error:
            raise InvalidTokenError from error
