import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from networksecurity.exception.exception import NetworkSecurityException

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def authenticate_user(username: str, password: str) -> bool:
    if not AUTH_USERNAME or not AUTH_PASSWORD_HASH:
        raise NetworkSecurityException(
            "AUTH_USERNAME/AUTH_PASSWORD_HASH are not configured in the environment", sys
        )
    if username != AUTH_USERNAME:
        return False
    return verify_password(password, AUTH_PASSWORD_HASH)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if not JWT_SECRET_KEY:
        raise NetworkSecurityException("JWT_SECRET_KEY is not configured in the environment", sys)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not JWT_SECRET_KEY:
        raise NetworkSecurityException("JWT_SECRET_KEY is not configured in the environment", sys)
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
