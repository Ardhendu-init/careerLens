from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from app.auth import get_current_user_id

SECRET = "test-secret-thats-long-enough-for-hs256-32b"


def _make_token(**overrides) -> str:
    payload = {
        "sub": "11111111-1111-1111-1111-111111111111",
        "aud": "authenticated",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        **overrides,
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def test_valid_token_returns_subject(mocker):
    mocker.patch(
        "app.auth.settings.SUPABASE_JWT_SECRET.get_secret_value", return_value=SECRET
    )
    token = _make_token()

    user_id = get_current_user_id(authorization=f"Bearer {token}")

    assert user_id == "11111111-1111-1111-1111-111111111111"


def test_expired_token_raises_401(mocker):
    mocker.patch(
        "app.auth.settings.SUPABASE_JWT_SECRET.get_secret_value", return_value=SECRET
    )
    token = _make_token(exp=datetime.now(timezone.utc) - timedelta(minutes=1))

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(authorization=f"Bearer {token}")

    assert exc_info.value.status_code == 401


def test_wrong_audience_raises_401(mocker):
    mocker.patch(
        "app.auth.settings.SUPABASE_JWT_SECRET.get_secret_value", return_value=SECRET
    )
    token = _make_token(aud="some-other-service")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(authorization=f"Bearer {token}")

    assert exc_info.value.status_code == 401


def test_tampered_signature_raises_401(mocker):
    mocker.patch(
        "app.auth.settings.SUPABASE_JWT_SECRET.get_secret_value", return_value=SECRET
    )
    token = _make_token()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(authorization=f"Bearer {token}not-the-real-signature")

    assert exc_info.value.status_code == 401


def test_missing_bearer_scheme_raises_401(mocker):
    mocker.patch(
        "app.auth.settings.SUPABASE_JWT_SECRET.get_secret_value", return_value=SECRET
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(authorization="not-a-bearer-token")

    assert exc_info.value.status_code == 401
