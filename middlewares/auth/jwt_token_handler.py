import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from jose.exceptions import JWTError
from models.user_identity import UserIdentity
from settings import SupabaseEnvVars

supabaseEnvVars = SupabaseEnvVars()

SECRET_KEY = supabaseEnvVars.supabase_jwt_secret_key
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise ValueError("SUPABASE_JWT_SECRET_KEY environment variable not set")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> UserIdentity:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_aud": False})
    except JWTError:
        return None

    return UserIdentity(
        email=payload.get("email"),
        id=payload.get("sub"),
    )


def verify_token(token: str):
    payload = decode_access_token(token)
    return payload is not None
