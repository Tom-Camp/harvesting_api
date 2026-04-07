import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth.tokens import create_access_token, decode_access_token


def test_create_and_decode_access_token():
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    assert decode_access_token(token) == user_id


def test_decode_access_token_invalid():
    with pytest.raises(jwt.PyJWTError):
        decode_access_token("not.a.valid.token")


def test_decode_access_token_wrong_secret():
    user_id = uuid.uuid4()
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    bad_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(bad_token)


def test_decode_access_token_expired():
    user_id = uuid.uuid4()
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    from app.utils.config import settings

    expired_token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(expired_token)
