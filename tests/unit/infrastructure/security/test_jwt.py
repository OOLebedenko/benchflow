from uuid import uuid4

import jwt
import pytest
from jwt.exceptions import InvalidSignatureError

from benchflow.infrastructure.security.jwt import JwtTokenProvider

EXPECTED_ALGORITHM = "HS256"
TEST_SECRET = "a" * 32
CORRECT_SECRET = "b" * 32
WRONG_SECRET = "c" * 32


def test_create_access_token_contains_user_id() -> None:
    """Create an access token containing the user identifier."""

    user_id = uuid4()

    provider = JwtTokenProvider(
        secret=TEST_SECRET,
        algorithm=EXPECTED_ALGORITHM,
        access_token_expire_minutes=15,
    )

    token = provider.create_access_token(user_id)

    payload = jwt.decode(
        token,
        TEST_SECRET,
        algorithms=[EXPECTED_ALGORITHM],
    )

    assert payload["sub"] == str(user_id)
    assert "exp" in payload


def test_create_access_token_is_signed() -> None:
    """Reject an access token decoded with a different secret."""

    provider = JwtTokenProvider(
        secret=CORRECT_SECRET,
        algorithm=EXPECTED_ALGORITHM,
        access_token_expire_minutes=15,
    )

    token = provider.create_access_token(uuid4())

    with pytest.raises(InvalidSignatureError):
        jwt.decode(
            token,
            WRONG_SECRET,
            algorithms=[EXPECTED_ALGORITHM],
        )
