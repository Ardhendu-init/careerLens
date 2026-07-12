import ssl

import certifi
import jwt
from fastapi import Header, HTTPException, status

from app.config import settings

# Explicit certifi-backed SSL context: urllib (used internally by PyJWKClient)
# falls back to the system CA store, which python.org's macOS builds ship
# without populating, causing JWKS fetches to fail with a cert verify error.
_ssl_context = ssl.create_default_context(cafile=certifi.where())
_jwks_client = jwt.PyJWKClient(
    f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json",
    ssl_context=_ssl_context,
)


def get_current_user_id(authorization: str = Header(...)) -> str:
    """FastAPI dependency: verifies the Supabase-issued bearer JWT (signed with
    the project's ES256 JWT Signing Key) and returns the authenticated user's
    id (the token's `sub` claim)."""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )

    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    return user_id
