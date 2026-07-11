import jwt
from fastapi import Header, HTTPException, status

from app.config import settings


def get_current_user_id(authorization: str = Header(...)) -> str:
    """FastAPI dependency: verifies the Supabase-issued bearer JWT and returns
    the authenticated user's id (the token's `sub` claim)."""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET.get_secret_value(),
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.InvalidTokenError:
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
